import importlib
from pathlib import Path
import pytest
import os
import runpy
import sys
import types
from unittest.mock import patch
import od_study as s

def test_composed_argv_inventory_and_early_deadlines():
    o=importlib.import_module('od_owner');c=importlib.import_module('od_collect').implementation()
    stage=Path('/tmp/od-no-launch')
    for mode,plan,n in [('capture','TRAIN_PLAN.json',72),('free','FREE_PLAN.json',24)]:
        args=c.parse_args(o.collector_argv(stage,stage/'rows',123.,mode,plan,n)[2:])
        assert (args.mode,args.plan,args.stop)==(mode,plan,n)
        assert args.binding==stage/'BINDING.json' and args.endpoint==stage/'service/endpoint-original.json'
    assert len(o.inventory(stage))==48 and all(r['reward'] is None for r in o.inventory(stage))
    assert o.stage_end('capture',100,8200)==1900
    assert o.stage_end('training',200,8200)==3800
    assert o.stage_end('unchanged',210,8200)==1410
    assert o.stage_end('sft6',220,8200)==1420
    assert o.stage_end('training',7000,8200)==5500
    with pytest.raises(ValueError):o.check_output(stage)

def test_real_owner_service_config_descriptor_intercepted_popen(tmp_path,monkeypatch):
    o=importlib.import_module('od_owner');original_sha=s.sha;loader=importlib.util.spec_from_file_location
    monkeypatch.setenv('STRICT_RLM_CALIBRATION_API_KEY','cpu-fixture-not-credential')
    suite=o.dependencies();output=tmp_path/'attempt';spawned=[];released=[]
    class InterceptedLaunch(Exception):pass
    def instrument(name,path,*args,**kwargs):
        spec=loader(name,path,*args,**kwargs)
        if name=='dual_lora_owned_launcher':
            execute=spec.loader.exec_module
            def load(module):
                execute(module);module._port_free=lambda port:True;module._wait_endpoint_model=lambda *a,**k:None;module._load_adapter=lambda d:None;module._stop=lambda p:None
            spec.loader.exec_module=load
        return spec
    def popen(argv,**kwargs):
        spawned.append(argv)
        if Path(argv[0]).name!='inference':
            assert len(s.read(output/'PLANNED_NULL_ENDPOINTS.json'))==48
            assert len(s.read(output/'PLANNED_CAPTURE_SLOTS.json'))==72
            assert Path(argv[0])==s.NATIVE and Path(argv[1]).name=='service_wrapper_v2.py'
            with s.aliases({}),patch.object(sys,'argv',argv[1:]),patch('importlib.util.spec_from_file_location',side_effect=instrument):runpy.run_path(argv[1],run_name='__main__')
            raise InterceptedLaunch('CPU interception, no process')
        config=s.read(argv[2]);assert config['vllm']['max_model_len']==8192 and config['vllm']['max_loras']==2
        assert '580.126.09' not in kwargs['env'].get('LD_LIBRARY_PATH','')
        return types.SimpleNamespace(pid=999999,returncode=0,poll=lambda:0)
    monkeypatch.setenv('CUDA_VISIBLE_DEVICES','CPU_INTERCEPT_ONLY');monkeypatch.setenv('STRICT_RLM_CALIBRATION_API_KEY','cpu-fixture-not-credential')
    monkeypatch.setattr(s,'ATTEMPT',output);monkeypatch.setattr(s,'verify',lambda:{'identity':'cpu-fixture'})
    monkeypatch.setattr(s,'sha',lambda path:'0'*64 if Path(path)==s.ROOT/'READY_v2.json' else original_sha(path))
    monkeypatch.setattr(suite.life.v1,'ports_free',lambda *a:True)
    monkeypatch.setattr(suite.subprocess,'Popen',popen);monkeypatch.setattr(suite,'release_service',lambda path:released.append(path))
    result=o.execute(output)
    assert len(spawned)==4 and released==[output/'teacher-service',output/'service-unchanged']
    assert result['active_unreleased_service'] is None and not result['complete']
    assert result['errors'][0]['type']=='InterceptedLaunch'
    assert any(x.get('planned_treatment_unavailable') and x['stage']=='sft6' for x in result['errors'])
    endpoint=s.read(output/'teacher-service/service/endpoint-original.json')
    assert endpoint['adapter']['model_sha256']==s.starting_policy()['adapter_sha256']
    o.b.validate(o.b.binding('unchanged'),endpoint,output/'teacher-service/BINDING.json')

def test_training_failure_still_attempts_both_readout_policies(tmp_path,monkeypatch):
    o=importlib.import_module('od_owner');output=tmp_path/'attempt';calls=[]
    class Suite:
        def start_service(self,stage,binding,deadline):calls.append(('start',stage.name))
        def release_service(self,stage):calls.append(('release',stage.name))
        def command(self,stage,label,argv,cap,deadline):
            calls.append(('command',label))
            if label=='gate-and-six-updates':raise RuntimeError('scientific gate failure')
    monkeypatch.setattr(o,'dependencies',lambda:Suite());monkeypatch.setattr(s,'ATTEMPT',output);monkeypatch.setattr(s,'runtime',lambda:None)
    monkeypatch.setattr(s,'verify',lambda:{'identity':'cpu'});original_sha=s.sha;monkeypatch.setattr(s,'sha',lambda p:'0'*64 if Path(p)==s.ROOT/'READY_v2.json' else original_sha(p))
    monkeypatch.setattr(s,'corpus',lambda:[]);monkeypatch.setattr(o.b,'selected',lambda arm:dict());monkeypatch.setattr(o.b,'binding',lambda arm:dict())
    monkeypatch.setenv('CUDA_VISIBLE_DEVICES','CPU');monkeypatch.setenv('STRICT_RLM_CALIBRATION_API_KEY','CPU')
    result=o.execute(output)
    assert ('command','free24-unchanged') in calls and ('command','free24-sft6') in calls
    assert not result['complete'] and len(result['readout_inventory'])==48
