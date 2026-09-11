"""Bounded authored native fixture and intercepted actual service entry, CPU only."""
import asyncio
import importlib.util
import json
import os
from pathlib import Path
import runpy
import sys
import time
import types
from unittest.mock import patch

def test_actual_owner_service_entry(tmp_path):
    assert Path(__file__).with_name('cf_owner.py').exists(), 'bounded96 owner not implemented'
    import cf_study as s
    import cf_owner as o
    class InterceptedLaunch(BaseException):pass
    spawned=[];original_spec=importlib.util.spec_from_file_location
    def instrument(name,path,*a,**kw):
        spec=original_spec(name,path,*a,**kw)
        if name=='dual_lora_owned_launcher':
            execute=spec.loader.exec_module
            def load(m):
                execute(m);m._port_free=lambda p:True;m._wait_endpoint_model=lambda *a,**k:None;m._load_adapter=lambda d:None;m._stop=lambda p:None
            spec.loader.exec_module=load
        return spec
    output=tmp_path/'attempt';stage=output/'service-sft24'
    with patch.dict(os.environ,{'STRICT_RLM_CALIBRATION_API_KEY':'CPU_FIXTURE_NOT_CREDENTIAL'}):suite=o.dependencies()
    def popen(argv,**kwargs):
        spawned.append(argv)
        if len(spawned)==1:
            assert len(s.read(output/'PLANNED_EVALUATION.json')['full'])==96
            assert Path(argv[1]).name=='service_wrapper_v2.py';previous=list(sys.path)
            try:
                with patch.object(sys,'argv',argv[1:]),patch('importlib.util.spec_from_file_location',side_effect=instrument):runpy.run_path(argv[1],run_name='__main__')
            finally:sys.path[:]=previous
            raise InterceptedLaunch()
        config=s.read(argv[2]);assert Path(argv[0]).name=='inference'
        assert config['vllm']['max_model_len']==8192 and config['vllm']['max_loras']==2
        return types.SimpleNamespace(pid=999999,returncode=0,poll=lambda:0)
    releases=[]
    with patch.dict(os.environ,{'CUDA_VISIBLE_DEVICES':'CPU_INTERCEPT_ONLY','STRICT_RLM_CALIBRATION_API_KEY':'CPU_FIXTURE_NOT_CREDENTIAL'}),patch.object(s,'ATTEMPT',output),patch.object(s,'verify',return_value={'identity':'CPU'}),patch.object(o,'dependencies',return_value=suite),patch.object(suite.life.v1,'ports_free',return_value=True),patch.object(suite.subprocess,'Popen',side_effect=popen),patch.object(suite,'release_service',side_effect=lambda p:releases.append(p)):
        result=o.execute(output)
    assert not result['complete'] and result['released'] and len(spawned)==2 and releases==[stage]
    assert s.read(output/'OWNER_RUN.json')['model_action_tokens']==2048
    endpoint=s.read(stage/'service/endpoint-original.json')
    assert endpoint['adapter']['model_sha256']==s.selected()['adapter_sha256'] and endpoint['role_binding_sha256']==s.sha(stage/'BINDING.json')
    assert len(result['readout_inventory'])==96

def test_missing_result_and_late_physical_never_erase_cost(tmp_path):
    assert Path(__file__).with_name('cf_owner.py').exists(), 'bounded96 owner not implemented'
    import cf_study as s
    import cf_owner as o
    plan=s.read(s.ROOT/'inputs/EVALUATION_PLAN.json');rows=plan['full']
    directory=tmp_path/'sft24/free'/rows[0]['coordinate']['id']
    s.write(directory/'RESULT.json',dict(available=True,reward=0))
    s.write(directory/'physical/0001.json',dict(physical_request_attempt=True,response={'choices':[{}],'usage':{'prompt_tokens':5,'completion_tokens':2}}))
    s.write(directory/'physical/0002.json',dict(physical_request_attempt=True,status=400,error='context length'))
    second=tmp_path/'sft24/free'/rows[1]['coordinate']['id'];s.write(second/'FAILURE.json',{'error':'interrupted'})
    inventory=o.harvest(tmp_path,plan);cost=o.ledger(tmp_path)['full_native']
    assert len(inventory)==96 and sum(r['available'] for r in inventory)==1
    assert inventory[0]['reward']==0 and inventory[1]['reward'] is None
    assert inventory[1]['cause']=='attempted_exception_no_result'
    assert cost['physical_requests_attempted']==2 and cost['returned_native_completions']==1
    assert cost['usage']=={'known':{'input':5,'output':2,'cached':0},'unknown':{'input':1,'output':1,'cached':2}}
