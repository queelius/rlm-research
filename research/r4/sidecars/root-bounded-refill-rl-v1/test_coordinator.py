from types import SimpleNamespace
import pytest
import study as s
import coordinator as run

def test_global_training_cutoff_reserves_real_final_readout():
    assert run.group_cap(1000,0)==300
    assert run.group_cap(450,0)==150
    with pytest.raises(TimeoutError):run.group_cap(300,0)
    assert run.optimizer_budget(300,0)==240
    assert run.optimizer_budget(120,0)==60
    with pytest.raises(TimeoutError):run.optimizer_budget(119,0)

def test_actual_coordinator_four_noops_dispatches128_and48_without_trainer(tmp_path,monkeypatch):
    old={'step':0,'adapter_sha256':'synthetic-only'};calls=[];clock=[1000.]
    monkeypatch.setattr(run.time,'time',lambda:clock[0]);monkeypatch.setattr(run.s,'verify_prepared',lambda:{'campaign_id':'fixture'})
    monkeypatch.setattr(run.s,'sha',lambda p:'fixture');monkeypatch.setattr(run.common,'starting_decision',lambda:(None,None,old))
    monkeypatch.setenv('CUDA_VISIBLE_DEVICES','CPU-FIXTURE-NO-REAL-SERVICE')
    monkeypatch.setattr(run.signal,'signal',lambda *a:None);monkeypatch.setattr(run.signal,'setitimer',lambda *a:None)
    def start(path,binding,deadline):calls.append(('start',deadline));clock[0]+=1
    def release(path):calls.append(('release',str(path)))
    suite=SimpleNamespace(start_service=start,release_service=release)
    monkeypatch.setattr(run,'dependencies',lambda:suite);monkeypatch.setattr(run.collect,'binding_for',lambda p:{'policy':p})
    monkeypatch.setattr(run.common,'generation',lambda w,p:{'candidate_window':w,'round':p['step']+1,'previous_policy':p})
    def stage(path,phase,service,deadline,cap,generation=None):
        calls.append(('phase',phase));clock[0]+=1
        return {'recorded':8 if generation else 24,'training_group_episodes':0}
    monkeypatch.setattr(run,'stage',stage)
    monkeypatch.setattr(run.export,'export_union',lambda paths,g,out:{'recorded':8*len(paths),'training_group_episodes':0})
    monkeypatch.setattr(run,'train_window',lambda *a:pytest.fail('genuine no-op must never call trainer'))
    result=run.execute(tmp_path/'run')
    assert result['optimizer_steps']==0 and result['training_attempts']==128
    assert len(result['candidate_windows'])==4 and result['selection']['policy'] is old
    phases=[v[1] for v in calls if v[0]=='phase']
    assert phases[0]=='readout-before' and phases[-1]=='readout-after' and len(phases)==18
    assert sum(v[0]=='start' for v in calls)==1 and sum(v[0]=='release' for v in calls)==1

def test_dispatch_cap_preserves_prevented_unrun_slots():
    import asyncio,time
    async def check():
        started=[];finished=[]
        async def one(row):
            started.append(row)
            try:await asyncio.sleep(2)
            finally:finished.append(row)
        result=await run.collect.dispatch(list(range(8)),one,time.time()+.02)
        assert result=='collection_wall_cap' and started==[0,1,2,3] and sorted(finished)==started
    asyncio.run(check())
