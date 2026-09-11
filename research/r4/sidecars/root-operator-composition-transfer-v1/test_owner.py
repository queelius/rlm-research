"""Actual owner/service seam and exact collector entry; external processes intercepted."""
import importlib.util
import os
from pathlib import Path
import runpy
import sys
import types
from unittest.mock import patch

def test_actual_owner_service_entry_and_two_lora_config(tmp_path):
    assert Path(__file__).with_name('ct_owner.py').exists(),'readout owner missing'
    import ct_study as s
    import ct_owner as o
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
    output=tmp_path/'attempt';policy=s.read(s.ROOT/'inputs/EVALUATION_PLAN.json')['policy_order'][0];stage=output/('service-'+policy)
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
    with patch.dict(os.environ,{'CUDA_VISIBLE_DEVICES':'CPU_INTERCEPT_ONLY','STRICT_RLM_CALIBRATION_API_KEY':'CPU_FIXTURE_NOT_CREDENTIAL'}),patch.object(s,'ATTEMPT',output),patch.object(s,'verify',return_value={'identity':'CPU'}),patch.object(suite.life.v1,'ports_free',return_value=True),patch.object(suite.subprocess,'Popen',side_effect=popen),patch.object(suite,'release_service',side_effect=lambda p:releases.append(p)),patch.object(o,'training_receipt',return_value={'cpu_fixture':True}):
        result=o.execute(output)
    assert not result['complete'] and result['released'] and len(spawned)==2 and releases==[stage]
    endpoint=s.read(stage/'service/endpoint-original.json')
    assert endpoint['adapter']['model_sha256']==s.selected(policy)['adapter_sha256'] and endpoint['role_binding_sha256']==s.sha(stage/'BINDING.json')

def test_exact_collector_argv_namespaces_and_six_operator_truth(tmp_path,monkeypatch):
    assert Path(__file__).with_name('ct_owner.py').exists(),'readout owner missing'
    import ct_study as s
    import ct_owner as o
    import ct_collect as c
    from types import SimpleNamespace
    stage=tmp_path/'service-sft6';destination=tmp_path/'sft6/free';argv=o.collector_argv(stage,destination,123.)
    module=c.implementation();args=module.parse_args(argv[2:]);assert args.output==destination and (args.start,args.stop,args.mode)==(0,48,'free')
    seen=[]
    async def fake(args):
        import od_study,od_binding
        assert od_study is s and od_binding is s;seen.append(args)
    monkeypatch.setattr(module,'run',fake);monkeypatch.setattr(sys,'argv',argv[1:]);c.main();assert len(seen)==1

def test_ledger_retains_attempt_without_result_and_unknown_usage(tmp_path):
    import ct_study as s
    import ct_owner as o
    base=tmp_path/'sft24/free/missing-result/physical'
    s.write(base/'0001.json',dict(physical_request_attempt=True,response={'choices':[{}],'usage':{'prompt_tokens':5,'completion_tokens':2}}))
    s.write(base/'0002.json',dict(physical_request_attempt=True,status=400,error='context length'))
    result=o.ledger(tmp_path)['full_native']
    assert result['physical_requests_attempted']==2 and result['returned_native_completions']==1
    assert result['usage']=={'known':{'input':5,'output':2,'cached':0},'unknown':{'input':1,'output':1,'cached':2}}
