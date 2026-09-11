import importlib
import os
from pathlib import Path
import tempfile
import runpy
import sys
import types
import unittest
from unittest.mock import patch
import qsr_study as s

class EntryTests(unittest.TestCase):
    def owner(self):
        self.assertTrue((s.ROOT/'owner.py').exists(),'actual owner not implemented')
        return importlib.import_module('owner')
    def test_owner_collector_and_trainer_real_cli_namespaces(self):
        o=self.owner();import qsr_collect as collect;import qsr_train as train
        stage=Path('/tmp/no-launch');argv=o.collector_argv(stage,1234.)
        args=collect.parse_args(argv[2:]);self.assertEqual(args.spec,stage/'CAPTURE_SPEC.json');self.assertEqual(args.output,stage/'rollout');self.assertEqual(args.deadline,1234.)
        args=train.parse_args(o.trainer_argv(stage,4321.)[2:]);self.assertEqual(args.group,stage/'collection/export/GROUP.json');self.assertEqual(args.generation,stage/'GENERATION.json')
    def test_initial384_nulls_and_adam_independent_training_reserve(self):
        o=self.owner();rows=o.planned_inventory(Path('/tmp/no-launch'))
        self.assertEqual(len(rows),384);self.assertTrue(all(r['reward'] is None for r in rows))
        self.assertFalse(o.learning_window_allowed(9000,now=7800));self.assertTrue(o.learning_window_allowed(9000,now=7000))
        self.assertEqual(o.final_policies(dict(step=0),dict(step=0)),{'unchanged':dict(step=0),'trained':dict(step=0)})
    def test_recovered_commit_records_consumed_window_and_adam_cursor_together(self):
        o=self.owner();self.assertTrue(hasattr(o,'recover_commit_on_stop'),'recovered committed-window cursor missing')
        old=dict(step=1,adapter_sha256='old');new=dict(step=2,adapter_sha256='new');state=dict(policy=old,completed_windows=2)
        with tempfile.TemporaryDirectory() as tmp,patch.object(o.common.c,'checkpoint_policy',return_value=new):
            stage=Path(tmp);o.recover_commit_on_stop(stage,dict(candidate_window=3,round=2),state)
            receipt=s.read(stage/'COMMIT_RECOVERED_ON_STOP.json')
        self.assertEqual(state,dict(policy=new,completed_windows=3));self.assertEqual(receipt['optimizer_steps'],2);self.assertEqual(receipt['completed_windows'],3);self.assertTrue(receipt['no_second_update'])
    def test_full_membership_rejects_partial_stale_and_heldout_updates(self):
        self.owner();import qsr_train as train
        plan=s.candidate_plan(1);g=dict(generation_id='fixture')
        rows=[dict(episode_id=r['id'],coordinate=r,split='training',qualification_only=False,generation_id='fixture') for r in plan]
        train.check_members(rows,plan,g)
        with self.assertRaises(ValueError):train.check_members(rows[:-1],plan,g)
        rows[0]['split']='readout'
        with self.assertRaises(ValueError):train.check_members(rows,plan,g)
    def test_learning_exception_still_attempts_both_final_policies(self):
        o=self.owner();from types import SimpleNamespace
        stages=[];released=[]
        suite=SimpleNamespace(start_service=lambda stage,binding,deadline:stages.append(stage.name),release_service=lambda stage:released.append(stage.name))
        with tempfile.TemporaryDirectory() as tmp,patch.object(s,'ATTEMPT',Path(tmp)/'attempt'),patch.object(s,'verify_prepared',return_value=dict(campaign_id='fixture')),patch.object(s,'runtime',return_value=(None,None)),patch.object(s,'sha',return_value='fixture'),patch.object(o,'dependencies',return_value=suite),patch.object(o.common,'starting_decision',return_value=(None,None,dict(step=0))),patch.object(o.collect,'binding_for',return_value={}),patch.object(o,'learning',side_effect=ValueError('retained failed learning')),patch.object(o,'collection_stage',return_value=dict(complete=True,integrity_failures=[],endpoint_available=0)),patch.dict(os.environ,{'CUDA_VISIBLE_DEVICES':'CPU_INTERCEPT_ONLY'}):
            result=o.execute(s.ATTEMPT)
        self.assertEqual(set(stages),{'final-unchanged','final-trained'});self.assertEqual(set(released),set(stages));self.assertEqual(result['selection']['policy']['step'],0)
        self.assertEqual(set(result['readouts']),{'unchanged','trained'});self.assertEqual(result['training_stop']['message'],'retained failed learning')
    def test_unreleased_learning_service_prevents_new_service_launch(self):
        o=self.owner();from types import SimpleNamespace
        launched=[];suite=SimpleNamespace(start_service=lambda *a:launched.append(a),release_service=lambda stage:None)
        def failed(output,suite,state,cutoff,owned):state['active_service']=Path('/tmp/owned-unreleased');raise RuntimeError('release unresolved')
        with tempfile.TemporaryDirectory() as tmp,patch.object(s,'ATTEMPT',Path(tmp)/'attempt'),patch.object(s,'verify_prepared',return_value=dict(campaign_id='fixture')),patch.object(s,'runtime',return_value=(None,None)),patch.object(s,'sha',return_value='fixture'),patch.object(o,'dependencies',return_value=suite),patch.object(o.common,'starting_decision',return_value=(None,None,dict(step=0))),patch.object(o.collect,'binding_for',return_value={}),patch.object(o,'learning',side_effect=failed),patch.dict(os.environ,{'CUDA_VISIBLE_DEVICES':'CPU_INTERCEPT_ONLY'}):
            result=o.execute(s.ATTEMPT)
        self.assertEqual(launched,[]);self.assertFalse(result['complete'])

    def test_actual_owner_service_config_descriptor_and_intercepted_popen(self):
        o=self.owner();original_sha=s.sha;loader=importlib.util.spec_from_file_location
        class InterceptedLaunch(Exception):pass
        spawns=[];released=[]
        def instrument(name,path,*args,**kwargs):
            spec=loader(name,path,*args,**kwargs)
            if name=='dual_lora_owned_launcher':
                run=spec.loader.exec_module
                def loaded(module):
                    run(module);module._port_free=lambda port:True;module._wait_endpoint_model=lambda *a,**k:None;module._load_adapter=lambda descriptor:None;module._stop=lambda process:None
                spec.loader.exec_module=loaded
            return spec
        with tempfile.TemporaryDirectory() as tmp,patch.dict(os.environ,{'CUDA_VISIBLE_DEVICES':'CPU_INTERCEPT_ONLY','STRICT_RLM_CALIBRATION_API_KEY':'cpu-fixture-not-credential'}):
            output=Path(tmp)/'attempt';suite=o.dependencies()
            def popen(argv,**kwargs):
                spawns.append(argv)
                if Path(argv[1])==s.RUNTIME/'service_wrapper_v2.py':
                    ledger=s.read(output/'PLANNED_NULL_ENDPOINTS.json');self.assertEqual(len(ledger),384);self.assertTrue(all(r['reward'] is None for r in ledger))
                    self.assertEqual(Path(argv[0]),s.NATIVE);saved=list(sys.path)
                    try:
                        with patch.object(sys,'argv',argv[1:]),patch('importlib.util.spec_from_file_location',side_effect=instrument):runpy.run_path(argv[1],run_name='__main__')
                    finally:sys.path[:]=saved
                    raise InterceptedLaunch('no GPU process launched')
                self.assertEqual(Path(argv[0]).name,'inference');self.assertEqual(argv[1],'@')
                config=s.read(Path(argv[2]));self.assertEqual(config['vllm']['max_loras'],2);self.assertEqual(config['vllm']['max_model_len'],8192)
                self.assertNotIn('580.126.09',kwargs['env']['LD_LIBRARY_PATH'])
                return types.SimpleNamespace(pid=999999,returncode=0,poll=lambda:0)
            fake_generation=lambda window,policy:dict(candidate_window=window,round=1,previous_policy=policy)
            with patch.object(s,'ATTEMPT',output),patch.object(s,'verify_prepared',return_value=dict(campaign_id='cpu-fixture')),patch.object(s,'sha',side_effect=lambda path:'0'*64 if Path(path)==s.ROOT/'READY.json' else original_sha(path)),patch.object(o.common,'generation',side_effect=fake_generation),patch.object(suite.life.v1,'ports_free',return_value=True),patch.object(suite.subprocess,'Popen',side_effect=popen),patch.object(suite,'release_service',side_effect=lambda stage:released.append(stage)):
                result=o.execute(output)
            self.assertEqual(len(spawns),6);self.assertEqual(len(released),3)
            self.assertEqual(result['training_stop']['type'],'InterceptedLaunch');self.assertEqual(len(result['errors']),2);self.assertIsNone(result['active_unreleased_service'])
            for stage in released:
                endpoint=s.read(stage/'service/endpoint-original.json');binding=s.read(stage/'BINDING.json')
                o.collect.validate_descriptor(binding,endpoint,s.sha(stage/'BINDING.json'),s.read(s.ROOT/'RECIPE.json')['base_manifest_sha256'])
                self.assertEqual(endpoint['adapter']['model_sha256'],s.fixed_start()['adapter_sha256'])
                self.assertEqual(s.read(stage/'service/SERVER_START.json')['launcher_sha256'],original_sha(s.RUNTIME/'service_wrapper_v2.py'))

if __name__=='__main__':unittest.main()
