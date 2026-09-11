"""Removing actual __file__ rebinding must recreate the observed ownership failure."""
import importlib.util
import importlib.machinery
import os
import sys
from pathlib import Path
from types import SimpleNamespace
import pytest

ROOT=Path(__file__).resolve().parent
SCIENCE=ROOT.parent/'leaf-fresh-correspondence-v1'

def load(name,path):
    spec=importlib.util.spec_from_file_location(name,path);module=importlib.util.module_from_spec(spec);sys.modules[name]=module;spec.loader.exec_module(module);return module

def test_actual_main_records_the_actual_launcher_hash(tmp_path,monkeypatch):
    scientific=load('fresh_test_scientific',SCIENCE/'study.py')
    with scientific.aliases({'study':scientific}):service=load('fresh_test_service',SCIENCE/'service.py')
    source=(SCIENCE if os.environ.get('RECOVERY_EXPECT_OLD') else ROOT)/'source/serve.py'
    with scientific.aliases({'study':scientific,'service':service}):module=load('fresh_test_launcher',source)
    inherited=module.inherited;s=inherited.s
    binding={'model':'qwen3','checkpoint':s.MODELS['qwen3'],'weights_sha256':s.sha(SCIENCE/'WEIGHTS.json'),'adapter':None}
    binding_path=tmp_path/'BINDING.json';s.write_once(binding_path,binding)
    destination=tmp_path/'service'
    monkeypatch.setattr(sys,'argv',[str(source),'--binding',str(binding_path),'--run-dir',str(destination)])
    monkeypatch.setenv('CUDA_VISIBLE_DEVICES','CPU-QUALIFICATION-NO-GPU');monkeypatch.setenv('STRICT_RLM_CALIBRATION_API_KEY','CPU-FIXTURE-NOT-A-CREDENTIAL')
    original_spec=importlib.util.spec_from_file_location
    class HelperLoader:
        def create_module(self,spec):return None
        def exec_module(self,helper):
            helper.PRIME_ENV=Path('/project/alex_phd/envs/prime-rl-5990b1b')
            helper._port_free=lambda _port:True
            helper._environment=lambda:{}
            helper._server_environment=lambda env,index:dict(env)
            helper._wait_endpoint_model=lambda endpoint,process,alias,timeout:None
    def helper_spec(name,path,*a,**kw):
        if name=='base_service_environment':return importlib.machinery.ModuleSpec(name,HelperLoader())
        return original_spec(name,path,*a,**kw)
    monkeypatch.setattr(importlib.util,'spec_from_file_location',helper_spec)
    monkeypatch.setattr(inherited.subprocess,'Popen',lambda *a,**kw:SimpleNamespace(pid=424242))
    with s.aliases({'study':s,'service':inherited.service}):inherited.main()
    start=s.read(destination/'SERVER_START.json')
    assert start['launcher_sha256']==s.sha(source)
    assert start['command']==['/project/alex_phd/envs/prime-rl-5990b1b/bin/inference','@',str(destination/'inference.json')]
    assert s.read(destination/'BINDING.json')==binding and s.read(destination/'SERVER_READY.json')['pid']==424242

def test_actual_suite_binds_same_new_owner_root_and_launcher():
    import recovery as r
    suite=r.load_suite()
    assert suite.c.ROLE==ROOT and suite.life.c.ROLE==ROOT
    assert suite.SERVE==ROOT/'source/serve.py'
    assert suite.life.claim_service.__code__.co_filename.endswith('campaign_lifecycle_v2.py')

def test_existing_outputs_or_owned_attempt_are_not_retryable(tmp_path):
    import recovery as r
    with pytest.raises(ValueError):r.validate_destination(tmp_path/'elsewhere',False)
    with pytest.raises(ValueError):r.validate_destination(ROOT/'owned/attempt-001',True)
