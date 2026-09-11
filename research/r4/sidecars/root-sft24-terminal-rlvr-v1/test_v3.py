"""Narrow V3 tests; only authored CPU state and intercepted process identities."""
from pathlib import Path
import importlib
import signal
import types
import pytest

def modules():
    assert Path(__file__).with_name('warm_owner_v3.py').exists(),'V3 owner not implemented'
    return importlib.import_module('warm_owner_v3'),importlib.import_module('warm_resume_v3')

def test_combined_budget_preserves_finals_and_window_guard():
    o,r=modules();b=o.budget(1000.)
    assert b['training_end']==6019 and b['work']==11119 and b['owned']==11299 and b['outer']==11419
    assert b['work']-b['training_end']==5100 and r.CHARGED_SECONDS+10419==10800
    assert o.learning_allowed(2380,1000) and not o.learning_allowed(2379.9,1000)

def test_resume_source_is_original_complete_group_and_no_earlier_readout(tmp_path):
    o,r=modules();proof=r.source_proof()
    assert proof['generation']['candidate_window']==1 and proof['generation']['previous_policy']['step']==0
    assert proof['selected']==13 and proof['source_group']==str(r.ORIGINAL/'window-01/collection/export/GROUP.json')
    r.study.write(tmp_path/'readout-unchanged/rollout/role-audit/x-request.json',{'request_id':'x'})
    with pytest.raises(ValueError,match='readout'):r.no_previous_readout(tmp_path)

def test_release_allows_real_qualified_escalation_without_real_signals(tmp_path,monkeypatch):
    monkeypatch.setenv('STRICT_RLM_CALIBRATION_API_KEY','CPU_FIXTURE_NOT_CREDENTIAL')
    o,r=modules();life=o.v2.v1.dependencies().life
    clock=[0.];signals=[];record={'pid':123,'uid':456,'pgid':123,'start_ticks':789}
    owner={'process':record,'command':['fixture']}
    monkeypatch.setattr(life,'claim_service',lambda service:owner)
    monkeypatch.setattr(life,'owned_records',lambda service,owner:[record])
    monkeypatch.setattr(life,'live_owned',lambda records:[] if signal.SIGKILL in signals else records)
    monkeypatch.setattr(life,'snapshot_descendants',lambda *args:None)
    monkeypatch.setattr(life,'observe',lambda pid:record)
    monkeypatch.setattr(life,'validate_start_observation',lambda *args:True)
    monkeypatch.setattr(life.os,'killpg',lambda pgid,sig:signals.append(sig))
    monkeypatch.setattr(life.os,'kill',lambda pid,sig:signals.append(sig))
    monkeypatch.setattr(life.time,'monotonic',lambda:clock[0])
    monkeypatch.setattr(life.time,'sleep',lambda seconds:clock.__setitem__(0,clock[0]+seconds))
    monkeypatch.setattr(life.v1,'ports_free',lambda:True)
    monkeypatch.setattr(life.c,'read',lambda path:{})
    monkeypatch.setattr(life.c,'file_hash',lambda path:'CPU')
    monkeypatch.setattr(life.c,'write_once',lambda *args:None)
    life.stop_service(tmp_path/'service')
    assert signals==[signal.SIGINT,signal.SIGTERM,signal.SIGKILL]
    assert 50<=clock[0]<60 and o.release_deadline(1000,5000,6000)==1090

def test_failed_release_stops_next_service_and_keeps_original_pointer(tmp_path,monkeypatch):
    o,r=modules();output=tmp_path/'attempt003';starts=[];releases=[]
    monkeypatch.setenv('CUDA_VISIBLE_DEVICES','CPU_ONLY_INTERCEPT')
    monkeypatch.setattr(r,'ATTEMPT',output)
    proof=r.source_proof()
    monkeypatch.setattr(r,'verify',lambda:({'identity':'CPU'},proof))
    monkeypatch.setattr(r.study,'runtime',lambda:None)
    suite=types.SimpleNamespace(start_service=lambda stage,binding,deadline:starts.append(stage))
    def release(stage):releases.append(stage);raise RuntimeError('authored release failure')
    suite.release_service=release
    monkeypatch.setattr(o,'dependencies',lambda:suite)
    monkeypatch.setattr(o,'train',lambda *args:None)
    monkeypatch.setattr(o.v2,'collection_stage',lambda *args,**kwargs:{'complete':True,'integrity_failures':[],'training_group_episodes':0})
    monkeypatch.setattr(o,'account',lambda output:{})
    monkeypatch.setattr(o,'harvest',lambda *args:[])
    result=o.execute(output)
    assert len(starts)==1 and all(p==starts[0] for p in releases)
    assert not result['released'] and result['active_unreleased_service']==str(starts[0])
    assert not result['readouts'] and result['selection']['completed_windows']==1

def test_trainer_argv_reuses_original_source_and_new_output(tmp_path):
    o,r=modules();proof=r.source_proof();stage=tmp_path/'window-01'
    argv=o.trainer_argv(stage,proof['source_group'],proof['source_generation'],123.)
    assert argv[argv.index('--group')+1]==proof['source_group']
    assert argv[argv.index('--generation')+1]==proof['source_generation']
    assert argv[argv.index('--output')+1]==str(stage/'training')

def test_actual_train_popen_preserves_assigned_gpu_and_source(tmp_path,monkeypatch):
    o,r=modules();proof=r.source_proof();stage=tmp_path/'window-01';stage.mkdir();spawned=[]
    monkeypatch.setenv('CUDA_VISIBLE_DEVICES','CPU_INTERCEPT_MIG_ID')
    process=types.SimpleNamespace(pid=987654,returncode=0,wait=lambda **kw:0)
    def popen(argv,**kwargs):spawned.append((argv,kwargs));return process
    monkeypatch.setattr(o.subprocess,'Popen',popen)
    life=types.SimpleNamespace(observe=lambda pid:{'pid':pid},safe_observation=lambda x:x)
    suite=types.SimpleNamespace(life=life,stop_child=lambda *args:None)
    monkeypatch.setattr(o.common.c,'checkpoint_policy',lambda *args:{'step':1})
    result=o.train(suite,stage,Path(proof['source_group']),Path(proof['source_generation']),o.time.time()+500,proof['generation'])
    assert result['step']==1 and len(spawned)==1
    argv,kwargs=spawned[0]
    assert kwargs['env']['CUDA_VISIBLE_DEVICES']=='CPU_INTERCEPT_MIG_ID'
    assert argv[argv.index('--group')+1]==proof['source_group']
    assert argv[argv.index('--generation')+1]==proof['source_generation']
    assert argv[0]==str(r.study.TRAIN) and Path(argv[1]).name=='warm_train_v2.py'
