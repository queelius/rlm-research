import importlib.util
import os
from pathlib import Path
import runpy
import sys
import types
from unittest.mock import patch

def test_actual_owner_service_config_and_release(tmp_path):
    import bg_owner as o
    import bg_study as s
    class Intercepted(BaseException):pass
    spawned=[];original=importlib.util.spec_from_file_location
    def instrument(name,path,*args,**kwargs):
        spec=original(name,path,*args,**kwargs)
        if name=='dual_lora_owned_launcher':
            execute=spec.loader.exec_module
            def load(module):
                execute(module);module._port_free=lambda port:True;module._wait_endpoint_model=lambda *a,**k:None;module._load_adapter=lambda descriptor:None;module._stop=lambda process:None
            spec.loader.exec_module=load
        return spec
    output=tmp_path/'attempt';stage=output/'owned-service'
    with patch.dict(os.environ,{'STRICT_RLM_CALIBRATION_API_KEY':'CPU_FIXTURE'}):suite=s.dependencies()
    def popen(argv,**kwargs):
        spawned.append(argv)
        if len(spawned)==1:
            assert len(s.read(output/'PLANNED.json'))==76
            before=list(sys.path)
            try:
                with patch.object(sys,'argv',argv[1:]),patch('importlib.util.spec_from_file_location',side_effect=instrument):runpy.run_path(argv[1],run_name='__main__')
            finally:sys.path[:]=before
            raise Intercepted()
        config=s.read(argv[2]);assert config['vllm']['max_model_len']==8192
        assert kwargs.get('env',os.environ).get('CUDA_VISIBLE_DEVICES')=='CPU_INTERCEPT_ONLY'
        return types.SimpleNamespace(pid=999999,returncode=0,poll=lambda:0)
    released=[]
    with patch.dict(os.environ,{'CUDA_VISIBLE_DEVICES':'CPU_INTERCEPT_ONLY','STRICT_RLM_CALIBRATION_API_KEY':'CPU_FIXTURE'}),patch.object(s,'ATTEMPT',output),patch.object(s,'verify',return_value={'identity':'CPU'}),patch.object(s,'dependencies',return_value=suite),patch.object(suite.life.v1,'ports_free',return_value=True),patch.object(suite.subprocess,'Popen',side_effect=popen),patch.object(suite,'release_service',side_effect=lambda p:released.append(p)):
        result=o.execute(output)
    assert not result['complete'] and result['released'] and len(spawned)==2 and released==[stage]
    descriptor=s.read(stage/'service/endpoint-original.json')
    assert descriptor['role_binding_sha256']==s.sha(stage/'BINDING.json')
    assert len(result['inventory'])==76

def test_owner_collector_exact_cli(tmp_path):
    import bg_owner as o
    import bg_collect as c
    argv=o.collector_argv(tmp_path/'owned-service',tmp_path/'rollout',1234)
    args=c.parse_args(argv[2:]);assert args.endpoint==tmp_path/'owned-service/service/endpoint-original.json' and args.output==tmp_path/'rollout' and args.deadline==1234
