import importlib.util
import json
from pathlib import Path
import time

import pytest

ROOT=Path(__file__).resolve().parent


def module():
    path=ROOT/'study.py'
    assert path.exists(),'evidence screen implementation absent'
    spec=importlib.util.spec_from_file_location('evidence_fixture_study',path)
    value=importlib.util.module_from_spec(spec);spec.loader.exec_module(value);return value


def test_selected_paragraphs_are_exact_and_bad_ids_fail_closed():
    s=module()
    half=[{'idx':2,'title':'A','paragraph_text':'EXACT  source\n'},
          {'idx':4,'title':'B','paragraph_text':'UNSELECTED_SECRET'}]
    good=s.selection({'transport_valid':True,'text':'{"paragraph_ids":[2]}'},half)
    assert good['valid'] and good['paragraphs']==[half[0]]
    assert s.summary_messages({'question':'Which?'},good)[1]['content'].find('UNSELECTED_SECRET')==-1
    for text in ('{"paragraph_ids":[99]}','{"paragraph_ids":[2,2]}','{"paragraph_ids":[true]}',
                 '{"paragraph_ids":[2],"extra":"x"}','{"paragraph_ids":[2],"paragraph_ids":[4]}'):
        bad=s.selection({'transport_valid':True,'text':text},half)
        assert not bad['valid'] and bad['paragraphs']==[] and bad['model_error']
        payload=s.final_payload({'question':'Which?'},[good,bad],['left','right'],'verbatim')
        assert payload['evidence']==[] and payload['selection_error']


@pytest.mark.parametrize('invalid',[False,True])
def test_actual_six_call_graph_keeps_unselected_sources_out_of_summaries(tmp_path,monkeypatch,invalid):
    s=module()
    from transformers import AutoTokenizer
    tok=AutoTokenizer.from_pretrained(s.MODEL,local_files_only=True)
    with s.aliases({'study':s},s.ROOT):
        c=s.load('evidence_fixture_collect',s.ROOT/'collect.py')
        metrics=s.load('evidence_fixture_metrics',s.ROOT/'metrics.py')
    item=s.selected()[0];public=s.read(item['public_path']);halves=s.partition(public,item['record_id'])
    requests=[]
    class Wire:
        status=200
        def __init__(self,raw):self.raw=raw
        def __enter__(self):return self
        def __exit__(self,*args):pass
        def read(self):return self.raw
    def native(request,timeout):
        body=json.loads(request.data);requests.append(body)
        offset=body['sampling_params']['seed']-202609220000
        if offset in (0,1):
            ids=[halves[offset][0]['idx']] if not(invalid and offset==0) else [999]
            text=json.dumps({'paragraph_ids':ids})
        elif offset in (2,3):text='A selected-source summary.'
        else:text='{"answer":"fixture answer","support_idxs":[]}'
        ids=tok.encode(text,add_special_tokens=False)+[151645]
        return Wire(json.dumps({'model':s.MODEL_ALIAS,'request_id':'CPU-'+str(len(requests)),
            'choices':[{'token_ids':ids,'finish_reason':'stop'}],
            'usage':{'prompt_tokens':len(body['token_ids']),'completion_tokens':len(ids)}}).encode())
    monkeypatch.setattr(c.source,'urlopen',native)
    monkeypatch.setenv('STRICT_RLM_CALIBRATION_API_KEY','SYNTHETIC-NOT-A-SERVICE-KEY')
    worker=c.Collector('http://fixture.invalid',tmp_path,time.time()+90,tok)
    old_read=s.read
    def blind_read(path):
        assert 'GOLD' not in str(path),'annotation reached model acquisition'
        return old_read(path)
    with monkeypatch.context() as blind:
        blind.setattr(s,'read',blind_read)
        result=worker.question(0,item)
    assert worker.physical==len(requests)==6 and result['all_planned_roles_accounted']
    assert requests[-1]['sampling_params']['seed']==requests[-2]['sampling_params']['seed']==202609220004
    prompts={row['role']:s.read(tmp_path/'prompts'/(row['call_id']+'.json')) for row in s.schedule() if row['record_id']==item['record_id']}
    for side,label in enumerate(('left','right')):
        payload=json.loads(prompts['summary_'+label][1]['content'].split('\n\n')[0])
        assert payload['paragraphs']==([] if invalid and side==0 else [halves[side][0]])
    finals=[json.loads(prompts[arm][1]['content'].split('\n\n')[0]) for arm in s.ARMS]
    if invalid:
        assert finals[0]['evidence']==finals[1]['evidence']==[]
        assert finals[0]['selection_error']==finals[1]['selection_error']
    else:
        assert finals[0]['selected_ids']==finals[1]['selected_ids']
        assert finals[1]['evidence']==[halves[0][0],halves[1][0]]
        assert finals[0]['evidence']==['A selected-source summary.']*2
    assert prompts['summary'][-1]['content'].endswith(s.FINAL)
    assert prompts['verbatim'][-1]['content'].endswith(s.FINAL)
    score=metrics.summarize(tmp_path,False)
    assert score['physical_cost']['physical_started']==6
    assert score['arms']['verbatim']['natural_policy_cost']['physical_started']==3
    assert score['arms']['summary']['natural_policy_cost']['physical_started']==5
    assert score['planned_physical_calls']==72 and score['planned_terminal_slots']==24
    assert not score['complete'] and score['paired']['planned']==12
