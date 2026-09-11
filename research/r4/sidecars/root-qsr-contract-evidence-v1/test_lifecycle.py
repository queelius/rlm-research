import importlib.util
import os
from pathlib import Path
import runpy
import sys
import types
from unittest.mock import patch

def test_actual_owner_to_qualified_service_entry_before_intercepted_model_launch(tmp_path):
    import study as s
    import protocol as p
    with s.aliases({'study':s,'protocol':p}):owner=s.load('contract_evidence_lifecycle_test_owner',s.ROOT/'owner.py',s.sha(s.ROOT/'owner.py'))
    class InterceptedLaunch(BaseException):pass
    spawned=[];real_sha=s.sha;spec_loader=importlib.util.spec_from_file_location
    def instrumented_spec(name,path,*args,**kwargs):
        spec=spec_loader(name,path,*args,**kwargs)
        if name=='dual_lora_owned_launcher':
            execute=spec.loader.exec_module
            def load_helper(module):
                execute(module);module._port_free=lambda port:True;module._wait_endpoint_model=lambda *a,**k:None;module._load_adapter=lambda d:None;module._stop=lambda p:None
            spec.loader.exec_module=load_helper
        return spec
    output=tmp_path/'attempt';stage=output/'service'
    with patch.dict(os.environ,{'STRICT_RLM_CALIBRATION_API_KEY':'cpu-fixture-not-credential'}):suite=owner.dependencies()
    def popen(argv,**kwargs):
        spawned.append(argv)
        if len(spawned)==1:
            rows=s.read(output/'PLANNED_NULL_ENDPOINTS.json');assert len(rows)==24 and all(x['reward'] is None for x in rows)
            assert len(s.read(output/'PLANNED_NULL_ACQUISITIONS.json'))==2
            assert Path(argv[1])==s.RUNTIME/'service_wrapper_v2.py';previous=list(sys.path)
            try:
                with patch.object(sys,'argv',argv[1:]),patch('importlib.util.spec_from_file_location',side_effect=instrumented_spec):runpy.run_path(argv[1],run_name='__main__')
            finally:sys.path[:]=previous
            raise InterceptedLaunch()
        assert Path(argv[0]).name=='inference' and argv[1]=='@'
        config=s.read(argv[2]);assert config['vllm']['max_model_len']==8192 and config['vllm']['max_loras']==2
        assert '580.126.09' not in kwargs['env']['LD_LIBRARY_PATH']
        return types.SimpleNamespace(pid=999999,returncode=0,poll=lambda:0)
    releases=[]
    with patch.dict(os.environ,{'CUDA_VISIBLE_DEVICES':'CPU_INTERCEPT_ONLY','STRICT_RLM_CALIBRATION_API_KEY':'cpu-fixture-not-credential'}),patch.object(s,'sha',side_effect=lambda p:'0'*64 if p==s.ROOT/'READY.json' else real_sha(p)),patch.object(s,'ATTEMPT',output),patch.object(s,'verify',return_value={'identity':'cpu'}),patch.object(suite.life.v1,'ports_free',return_value=True),patch.object(suite.subprocess,'Popen',side_effect=popen),patch.object(suite,'release_service',side_effect=lambda p:releases.append(p)):
        result=owner.execute(output)
    assert not result['complete'] and result['error']['type']=='InterceptedLaunch'
    assert len(spawned)==2 and releases==[stage] and result['active_unreleased_service'] is None
    binding=s.read(stage/'BINDING.json');endpoint=s.read(stage/'service/endpoint-original.json')
    assert binding==s.binding() and endpoint['adapter']['model_sha256']=='66cce4009628ff7d8e047f08e6fb3a29febdbf8fb3ed8303871f69860f1151d5'
    assert endpoint['role_binding_sha256']==s.sha(stage/'BINDING.json')
    assert s.read(stage/'service/SERVER_START.json')['launcher_sha256']==real_sha(s.RUNTIME/'service_wrapper_v2.py')
    assert s.read(output/'COST_LEDGER.json')['total']['physical_request_attempts']==0
