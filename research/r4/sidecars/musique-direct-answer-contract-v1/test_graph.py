import importlib.util
import json
from pathlib import Path
import time
import pytest

ROOT=Path(__file__).resolve().parent


def modules():
    assert (ROOT/'study.py').exists(),'direct answer-contract implementation absent'
    spec=importlib.util.spec_from_file_location('answer_contract_fixture_study',ROOT/'study.py')
    s=importlib.util.module_from_spec(spec);spec.loader.exec_module(s)
    with s.aliases({'study':s},ROOT):
        c=s.load('answer_contract_fixture_collect',ROOT/'collect.py');m=s.load('answer_contract_fixture_metrics',ROOT/'metrics.py')
        with s.aliases({'collect':c,'metrics':m},ROOT):o=s.load('answer_contract_fixture_owner',ROOT/'owner.py')
    return s,c,m,o


def test_frozen_payload_reserialization_changes_no_cached_prompt_bytes():
    s,_,_,_=modules();cache=s.read(s.PREVIOUS/'inputs/host/BASELINE.json')
    by_id={c['record_id']:c for c in cache['direct_calls']}
    for item in s.read(s.PREVIOUS/'inputs/MANIFEST.json')['selected']:
        before=s.read(by_id[item['record_id']]['prompt_path'])
        after=s.final_messages(s.read(item['source_payload_path']))
        assert after==[before[0],{'role':'user','content':before[1]['content']+' '+s.ANSWER_RULE}]


def test_all12_native_requests_change_only_instruction_tokens():
    s,_,_,_=modules()
    from transformers import AutoTokenizer
    tok=AutoTokenizer.from_pretrained(s.MODEL,local_files_only=True)
    cache=s.read(s.INPUTS/'host/BASELINE.json');old={c['record_id']:c for c in cache['direct_calls']}
    rows=s.schedule();assert len(rows)==12
    for index,(item,row) in enumerate(zip(s.selected(),rows)):
        payload=s.read(item['source_payload_path']);before=s.read(old[item['record_id']]['request_path'])
        prompt=s.final_messages(payload);after=s.request(prompt,'concise',row['seed'],item['paragraph_count'],tok)
        assert row['seed']==202609230003+16*index and row['max_tokens']==1024
        assert json.loads(prompt[1]['content'].rsplit('\n\n',1)[0])==payload and len(payload['evidence'])==4
        assert prompt[0]==s.read(old[item['record_id']]['prompt_path'])[0]
        assert before['token_ids']!=after['token_ids']
        assert {k:v for k,v in before.items() if k!='token_ids'}=={k:v for k,v in after.items() if k!='token_ids'}
    binding=s.read(s.FLEX/'outputs/attempt-001/BINDING.json');s.check_binding(binding)
    with pytest.raises(AssertionError):s.check_binding({**binding,'unapproved_checkpoint':'cp32'})


@pytest.mark.parametrize('failure',['none','bad_schema','http'])
def test_actual_owner_one_final_preserves_sources_raw_decode_and_known_vs_unknown(tmp_path,monkeypatch,failure):
    s,c,m,o=modules()
    from transformers import AutoTokenizer
    tok=AutoTokenizer.from_pretrained(s.MODEL,local_files_only=True)
    item=s.selected()[0];payload=s.read(item['source_payload_path']);monkeypatch.setattr(s,'selected',lambda:[item]);seen=[]
    text='{"answer":"  CPU answer  ","support_idxs":[3]}' if failure!='bad_schema' else '{"answer":"CPU answer","support_idxs":[true]}'
    class Wire:
        status=503 if failure=='http' else 200
        def __init__(self,raw):self.raw=raw
        def __enter__(self):return self
        def __exit__(self,*args):pass
        def read(self):return self.raw
    def native(request,timeout):
        body=json.loads(request.data);seen.append(body);ids=tok.encode(text,add_special_tokens=False)+[151645]
        return Wire(json.dumps({'model':s.MODEL_ALIAS,'request_id':'CPU-final',
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
    assert result['physical_started']==len(seen)==1 and result['errors']==[]
    cid=s.schedule()[0]['call_id'];prompt=s.read(tmp_path/'prompts'/(cid+'.json'));call=s.read(tmp_path/'calls'/(cid+'.json'))
    assert json.loads(prompt[1]['content'].rsplit('\n\n',1)[0])==payload
    assert call['text']==text and call['transport_valid'] is (failure!='http')
    rendered=tok.apply_chat_template(prompt,tokenize=True,add_generation_prompt=True,enable_thinking=False)
    assert seen[0]['token_ids']==(rendered['input_ids'] if hasattr(rendered,'keys') else rendered)
    score=current.metrics.summarize(tmp_path,False)
    assert score['new_physical_cost']['physical_started']==1 and score['arms']['direct']['available']==12
    assert score['arms']['concise']['available']==(0 if failure=='http' else 1)
    saved=score['arms']['concise']['scores'][item['record_id']]
    assert saved['answer_em']==(None if failure=='http' else 0.)
    assert saved['valid_json'] is (failure=='none')
    assert score['natural_full_policy_cost']['direct']['planned_calls']==48
    assert score['natural_full_policy_cost']['concise']['planned_calls']==48
