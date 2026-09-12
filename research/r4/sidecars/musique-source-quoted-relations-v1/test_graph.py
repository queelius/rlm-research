import importlib.util
import json
from pathlib import Path
import time
import pytest

ROOT=Path(__file__).resolve().parent


def modules():
    assert (ROOT/'study.py').exists(),'quoted-relations implementation absent'
    spec=importlib.util.spec_from_file_location('relation_fixture_study',ROOT/'study.py')
    s=importlib.util.module_from_spec(spec);spec.loader.exec_module(s)
    with s.aliases({'study':s},ROOT):
        c=s.load('relation_fixture_collect',ROOT/'collect.py');m=s.load('relation_fixture_metrics',ROOT/'metrics.py')
        with s.aliases({'collect':c,'metrics':m},ROOT):o=s.load('relation_fixture_owner',ROOT/'owner.py')
    return s,c,m,o


def test_exact_quote_does_not_certify_wrong_person_relation():
    s,_,_,_=modules();paragraphs=[{'idx':2,'title':'Mayor','paragraph_text':'Jerome Cavanagh died in Lexington, Kentucky.'}]
    data={'relations':[{'subject':'Anne Marie Carl-Nielsen','relation':'died in','object':'Lexington, Kentucky',
                       'paragraph_id':2,'quote':'Jerome Cavanagh died in Lexington, Kentucky.'}],'missing_links':[]}
    value=s.report({'transport_valid':True,'text':json.dumps(data)},paragraphs)
    assert value['valid'] and value['quote_substrings_verified'] and value['relation_truth_verified'] is False
    assert value['data']==data
    data['relations'][0]['quote']='unsupported quote'
    assert not s.report({'transport_valid':True,'text':json.dumps(data)},paragraphs)['valid']
    data['relations'][0]['quote']=paragraphs[0]['paragraph_text'];data['relations'][0]['paragraph_id']=99
    assert not s.report({'transport_valid':True,'text':json.dumps(data)},paragraphs)['valid']


@pytest.mark.parametrize('failure',['none','bad_quote','malformed'])
def test_actual_owner_entrypoint_keeps_raw_four_sources_when_report_invalid(tmp_path,monkeypatch,failure):
    s,c,m,o=modules()
    from transformers import AutoTokenizer
    tok=AutoTokenizer.from_pretrained(s.MODEL,local_files_only=True)
    item=s.selected()[0];payload=s.read(item['source_payload_path']);original=payload['evidence'][0]
    monkeypatch.setattr(s,'selected',lambda:[item]);seen=[]
    class Wire:
        status=200
        def __init__(self,raw):self.raw=raw
        def __enter__(self):return self
        def __exit__(self,*args):pass
        def read(self):return self.raw
    def native(request,timeout):
        body=json.loads(request.data);seen.append(body)
        if len(seen)==1:
            quote='NOT AN ORIGINAL QUOTE' if failure=='bad_quote' else original['paragraph_text'][:40]
            text='not JSON' if failure=='malformed' else json.dumps({'relations':[{'subject':'Unverified entity','relation':'has text','object':'unverified object','paragraph_id':original['idx'],'quote':quote}],'missing_links':[]})
        else:text='{"answer":"fixture answer","support_idxs":[]}'
        ids=tok.encode(text,add_special_tokens=False)+[151645]
        return Wire(json.dumps({'model':s.MODEL_ALIAS,'request_id':'CPU-'+str(len(seen)),
                    'choices':[{'token_ids':ids,'finish_reason':'stop'}],
                    'usage':{'prompt_tokens':len(body['token_ids']),'completion_tokens':len(ids)}}).encode())
    monkeypatch.setattr(c.source,'urlopen',native);monkeypatch.setenv('STRICT_RLM_CALIBRATION_API_KEY','SYNTHETIC-NOT-A-SERVICE-KEY')
    current=o.implementation();assert current.study is s and current.collect is c and current.metrics is m
    saved_read=s.read
    def blind(path):
        assert 'GOLD' not in str(path) and '/host/' not in str(path)
        return saved_read(path)
    with monkeypatch.context() as scope:
        scope.setattr(s,'read',blind);result=current.collect.execute('http://fixture.invalid',tmp_path,time.time()+90)
    assert result['physical_started']==len(seen)==2 and result['errors']==[]
    assert seen[0]['sampling_params']['seed']==202609240000 and seen[1]['sampling_params']['seed']==202609230003
    final=s.read(tmp_path/'prompts'/(s.schedule()[1]['call_id']+'.json'))
    body=json.loads(final[1]['content'].rsplit('\n\n',1)[0]);report=body.pop('relation_report')
    assert body==payload and len(body['evidence'])==4 and final[1]['content'].endswith(s.FINAL)
    assert report['relation_truth_verified'] is False
    if failure=='none':assert report['relations'] and report['error'] is None
    else:assert report['relations']==[] and report['error']
    score=current.metrics.summarize(tmp_path,False)
    assert score['new_physical_cost']['physical_started']==2 and score['arms']['relations']['available']==1
    assert score['arms']['direct']['available']==12
