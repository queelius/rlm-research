"""Qualified trainer/owner entries: synthetic CPU numerics, never live services."""
import copy
from pathlib import Path
import sys
import time
from types import SimpleNamespace
from unittest.mock import patch
import pytest

def test_trainer_entry_exists_and_actual_cli_is_fixed():
    assert Path(__file__).with_name('qs_train.py').exists(),'actual trainer entry absent'
    import qs_train as t
    args=t.implementation().parse_args(['--mode','train','--output','fixture','--deadline','2000000000'])
    assert args.mode=='train' and args.output==Path('fixture')

def exercise_actual_trainer_entry_from_native_teacher(teacher_path,output,monkeypatch):
    import torch
    import torch.nn.functional as F
    from safetensors.torch import save_file
    import qs_study as s
    import qs_learning as l
    import qs_train as t
    model_source=s.read(teacher_path);plan=s.read(s.ROOT/'inputs/TRAIN_PLAN.json');calls=[]
    # Explicit fixture expansion: one genuinely captured native trajectory copied72 times.
    # It is not72 independent captures or scientific evidence; actual masks/IDs stay intact.
    def fixture_corpus(limit=None):
        calls.append(str(teacher_path));source=s.read(teacher_path)
        return [{**copy.deepcopy(source),'episode_id':r['id'],'coordinate':r} for r in plan]
    class Tiny(torch.nn.Module):
        def __init__(self):super().__init__();self.lora_cpu=torch.nn.ParameterList([torch.nn.Parameter(torch.zeros(31)) for _ in range(504)])
        def forward(self,input_ids,attention_mask,use_cache):
            logits=sum(self.lora_cpu)/504;return SimpleNamespace(logits=logits[None,None,:].expand(*input_ids.shape,-1))
        def gradient_checkpointing_enable(self,**kwargs):pass
        def save_pretrained(self,path,safe_serialization):
            save_file({n:p.detach().clone() for n,p in self.named_parameters()},str(path/'adapter_model.safetensors'));s.write(path/'adapter_config.json',dict(cpu_fixture=True,r=8))
    j=s.joint();helper=j.original.plan.private('train.py',view=j.original.plan.old);model=Tiny();module=t.implementation();original_ce=F.cross_entropy;original_losses=l.losses;original_update=l.update
    attempt=output.parent;s.write(attempt/'capture/CORPUS_READY.json',dict(cpu_fixture_expansion=True,real_native_teacher_path=str(teacher_path),sha256=s.sha(teacher_path)))
    with monkeypatch.context() as m:
        m.setattr(s,'ATTEMPT',attempt);m.setattr(s,'verify',lambda:dict(identity='CPU_QS_NATIVE_TO_TRAIN'))
        m.setattr(s,'corpus',fixture_corpus);m.setattr(module,'_qualified_load_model',lambda destination:(model,list(model.parameters()),helper))
        m.setattr(F,'cross_entropy',lambda logits,target,**kw:original_ce(logits,target%31,**kw))
        m.setattr(l,'losses',lambda model,turn,device:original_losses(model,turn,'cpu'))
        m.setattr(l,'update',lambda model,opt,episodes,arm,device,deadline:original_update(model,opt,episodes,arm,'cpu',deadline))
        for key in ('synchronize','reset_peak_memory_stats'):m.setattr(torch.cuda,key,lambda:None)
        for key in ('max_memory_allocated','max_memory_reserved'):m.setattr(torch.cuda,key,lambda:0)
        m.setattr(torch.cuda,'get_rng_state_all',lambda:[])
        m.setattr(sys,'argv',['qs_train.py','--mode','train','--output',str(output),'--deadline',str(time.time()+900)])
        t.main()
        import qs_binding as b
        selected=b.selected('sft6');bound=b.binding('sft6')
        assert selected['step']==6 and bound['models'][bound['role_map']['root']]['path']==str(output/'checkpoint-0006')
        original_read=s.read
        with monkeypatch.context() as reject:
            reject.setattr(s,'read',lambda p:{**original_read(p),'step':5} if Path(p)==output/'SELECTION.json' else original_read(p))
            with pytest.raises(ValueError):b.selected('sft6')
    result=s.read(output/'RESULT.json');assert result['complete'] and result['optimizer_steps']==6 and result['example_exposures']==432 and calls==[str(teacher_path)]
    assert result['root_turn_exposures']==1296 and not result['child_loaded']
    assert len(s.read(output/'PARAMETER_MAPPING.json')['parameters'])==504
    for step in range(1,7):
        checkpoint=output/f'checkpoint-{step:04}';state=s.read(checkpoint/'state.json');optimizer=torch.load(checkpoint/'optimizer.pt',map_location='cpu',weights_only=False)
        assert state['cursor']==0 and state['epoch']==state['step']==step and len(optimizer['state'])==504
        assert {int(v['step']) for v in optimizer['state'].values()}=={step}
        assert (checkpoint/'rng_state.pt').exists()

def test_owner_protects_readout_and_exact160_before_service(tmp_path):
    assert Path(__file__).with_name('qs_owner.py').exists(),'owned160 lifecycle absent'
    import qs_owner as o
    import qs_study as s
    assert o.stage_end('capture',0,7920)==1200
    assert o.stage_end('training',1200,7920)==3300
    assert len(o.inventory(tmp_path))==160
    assert len([x for x in o.inventory(tmp_path) if x['panel']=='protected'])==144

def test_actual_owner_service_wrapper_namespace_and_termination_release(tmp_path,monkeypatch):
    import importlib.util
    import os
    import runpy
    import qs_study as s
    import qs_owner as o
    monkeypatch.setenv('STRICT_RLM_CALIBRATION_API_KEY','AUTHORED_CPU_NOT_CREDENTIAL');monkeypatch.setenv('CUDA_VISIBLE_DEVICES','CPU_INTERCEPT_ONLY')
    suite=o.dependencies();output=tmp_path/'attempt';spawned=[];released=[];loader=importlib.util.spec_from_file_location
    def instrument(name,path,*args,**kwargs):
        spec=loader(name,path,*args,**kwargs)
        if name=='dual_lora_owned_launcher':
            execute=spec.loader.exec_module
            def load(module):
                execute(module);module._port_free=lambda p:True;module._wait_endpoint_model=lambda *a,**k:None;module._load_adapter=lambda d:None;module._stop=lambda p:None
            spec.loader.exec_module=load
        return spec
    def popen(argv,**kwargs):
        spawned.append(argv)
        if len(spawned)==1:
            assert len(s.read(output/'PLANNED_EVALUATION.json'))==160 and len(s.read(output/'PLANNED_CAPTURE.json'))==72
            assert Path(argv[1]).name=='service_wrapper_v2.py'
            with s.aliases({}),patch.object(sys,'argv',argv[1:]),patch('importlib.util.spec_from_file_location',side_effect=instrument):runpy.run_path(argv[1],run_name='__main__')
            raise o.MainTermination('authored CPU stop, no later phase')
        config=s.read(argv[2]);assert Path(argv[0]).name=='inference' and config['vllm']['max_model_len']==8192 and config['vllm']['max_loras']==2
        return SimpleNamespace(pid=999999,returncode=0,poll=lambda:0)
    monkeypatch.setattr(s,'ATTEMPT',output);monkeypatch.setattr(s,'verify',lambda:dict(identity='CPU'))
    monkeypatch.setattr(o,'dependencies',lambda:suite);monkeypatch.setattr(suite.life.v1,'ports_free',lambda *a:True)
    monkeypatch.setattr(suite.subprocess,'Popen',popen);monkeypatch.setattr(suite,'release_service',lambda path:released.append(path))
    result=o.execute(output)
    assert not result['complete'] and result['released'] and len(spawned)==2 and released==[output/'teacher-service']
    assert len(result['readout_inventory'])==160 and all(x['reward'] is None for x in result['readout_inventory'])
    descriptor=s.read(output/'teacher-service/service/endpoint-original.json')
    assert descriptor['adapter']['model_sha256']==s.starting_policy()['adapter_sha256']

def test_training_failure_keeps_baseline_and_uses_exact_trainer_collector_argv(tmp_path,monkeypatch):
    import qs_owner as o
    import qs_study as s
    import qs_collect as c
    output=tmp_path/'attempt';calls=[];start=s.starting_policy()
    class Suite:
        def start_service(self,stage,binding,deadline):calls.append(('start',stage.name))
        def release_service(self,stage):calls.append(('release',stage.name))
        def command(self,stage,label,argv,cap,deadline):
            calls.append(('command',label));assert 0<cap<=deadline-time.time()+1
            if label=='gate-and-six-updates':
                assert Path(argv[0])==s.TRAIN and Path(argv[1])==s.ROOT/'qs_train.py'
                raise RuntimeError('authored training failure')
            args=c.parse_args(argv[2:]);assert args.deadline==deadline and args.binding==stage/'BINDING.json'
    monkeypatch.setenv('CUDA_VISIBLE_DEVICES','CPU_INTERCEPT_ONLY');monkeypatch.setenv('STRICT_RLM_CALIBRATION_API_KEY','CPU')
    monkeypatch.setattr(s,'ATTEMPT',output);monkeypatch.setattr(s,'verify',lambda:dict(identity='CPU'));monkeypatch.setattr(s,'runtime',lambda:None);monkeypatch.setattr(s,'corpus',lambda:[])
    monkeypatch.setattr(o,'dependencies',lambda:Suite());monkeypatch.setattr(o.b,'binding',lambda arm:{})
    def selected(arm):
        if arm=='sft6':raise FileNotFoundError('fixed6 absent; no5 substitution')
        return start
    monkeypatch.setattr(o.b,'selected',selected);result=o.execute(output)
    assert ('command','protected72') in calls and ('command','dev8') in calls
    assert ('start','service-sft6') not in calls and not result['complete']
    assert len(result['readout_inventory'])==160

def test_raw_physical_failure_union_and_missing_result(tmp_path):
    import qs_owner as o
    import qs_study as s
    inventory=o.inventory(tmp_path);directory=Path(inventory[0]['path']).parent
    s.write(directory/'physical/0001.json',dict(physical_request_attempt=True,response={'choices':[{}],'usage':{'prompt_tokens':5,'completion_tokens':2}}))
    s.write(directory/'physical/0002.json',dict(physical_request_attempt=True,status=400,error='context overflow'))
    s.write(directory/'FAILURE.json',dict(type='TimeoutError'))
    s.write(tmp_path/'capture/example/physical/0001.json',dict(physical_request_attempt=True,origin='actual c32',response={'choices':[{}],'usage':{'prompt_tokens':7,'completion_tokens':3}}))
    s.write(tmp_path/'capture/example/physical/0002.json',dict(origin='authored transport; synthetic likelihood not RL',response={'choices':[{}]}))
    rows=o.harvest(tmp_path,inventory);assert rows[0]['reward'] is None and rows[0]['cause']=='attempted_exception_no_result' and len(rows)==160
    allcost=o.ledger(tmp_path);ledger=allcost['full_native'];assert ledger['physical_requests_attempted']==3 and ledger['returned_native_completions']==2
    assert ledger['usage']['unknown']['output']==1
    assert allcost['authored_transport_records_not_model_calls']==1 and len(allcost['records_sha256'])==4

def test_actual_TRAIN_environment_imports_only_no_model_loaded():
    import subprocess,os
    import qs_study as s
    code='import sys;sys.path.insert(0,'+repr(str(s.ROOT))+');import qs_train as t;from peft import PeftModel;from transformers import AutoModelForCausalLM;m=t.implementation();assert m.s.ROOT.name=="root-question-sensitive-sft-v1";assert m.l is t.l;print("qualified trainer imported; no model loaded")'
    result=subprocess.run([str(s.TRAIN),'-c',code],env={**os.environ,'CUDA_VISIBLE_DEVICES':''},capture_output=True,text=True,timeout=60)
    assert result.returncode==0,result.stderr
    assert 'no model loaded' in result.stdout
