"""Fixed input pairing and native first-response parsing; no sampled code execution."""
import importlib.util
from pathlib import Path
import pytest

def module():
    path=Path(__file__).with_name('dr_probe.py');assert path.exists(),'first-action probe not implemented'
    spec=importlib.util.spec_from_file_location('dr_probe_test',path);m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);return m

def test_first_request_changes_only_alias_and_seed():
    m=module();source=dict(model='old',token_ids=[1,2,3],sampling_params=dict(seed=1,max_tokens=2048,top_p=1.,temperature=.5,logprobs=1),cache_salt='0')
    body=m.request_body(source,'new',44)
    assert body=={**source,'model':'new','sampling_params':{**source['sampling_params'],'seed':44}}
    assert source['model']=='old' and source['sampling_params']['seed']==1

def test_native_logprob_token_mismatch_rejected():
    m=module()
    raw=dict(request_id='fixture',choices=[dict(token_ids=[151645],finish_reason='stop',logprobs=dict(content=[dict(token='token_id:7',logprob=-.5)]))])
    with pytest.raises(ValueError):m.authenticate(raw,None,[])

def test_authored_native_tool_probe_is_intent_not_execution():
    m=module();import dr_study as s
    renderer=s.stack().native.renderer();tokenizer=renderer._tokenizer
    code='from rlm.api import run as rlm\nreply=await rlm("classify this")'
    ids=tokenizer.encode(s.stack().native.tool_action(code),add_special_tokens=False)+[151645]
    raw=dict(request_id='CPU_SINGLE_ACTION',choices=[dict(token_ids=ids,finish_reason='stop',logprobs=dict(content=[dict(token=f'token_id:{v}',logprob=-.5) for v in ids]))])
    value=m.authenticate(raw,renderer,[])
    assert value['syntactic_acquisition_intent'] and value['no_code_execution'] and value['executed_acquisition'] is False
    assert value['programs'][0]['code']==code
