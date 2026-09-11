"""MAIN-only owned14400s run; learning stop cannot skip both final-policy attempts."""
import argparse
import functools
import os
from pathlib import Path
import signal
import subprocess
import time
import traceback
import qsr_study as s
import qsr_common as common
import qsr_collect as collect
import qsr_export as export
import qsr_native as n

class MainTermination(BaseException):pass
@functools.lru_cache(maxsize=1)
def dependencies():
    st=n.stack();path=s.PRIOR/'launch.py';pin=s.read(s.PRIOR/'READY.json')['source_sha256'][str(path)]
    with s.aliases({'study':st.prior,'native':st.native}):launcher=s.load('qsr_qualified_owner_dependencies',path,pin)
    suite=launcher.dependencies();suite.life.install();_,adapter=s.runtime();adapter.install(suite);return suite
def remaining(deadline,cap):
    value=min(cap,deadline-time.time())
    if value<=0:raise TimeoutError('shared stage/work deadline')
    return value
def alarm(deadline):signal.setitimer(signal.ITIMER_REAL,max(.001,deadline-time.time()))
def learning_window_allowed(cutoff,now=None):return cutoff-(time.time() if now is None else now)>=1440
def final_policies(initial,policy):return dict(unchanged=initial,trained=policy)
def check_output(output):
    if output.resolve()!=s.ATTEMPT.resolve():raise ValueError('exact fresh output namespace only')
    if output.exists():raise FileExistsError('existing attempt retained; no implicit resume/reroll')
def collector_argv(stage,deadline):return [str(s.NATIVE),str(s.ROOT/'qsr_collect.py'),'--spec',str(stage/'CAPTURE_SPEC.json'),'--output',str(stage/'rollout'),'--deadline',str(deadline)]
def trainer_argv(stage,deadline):return [str(s.TRAIN),str(s.ROOT/'qsr_train.py'),'--group',str(stage/'collection/export/GROUP.json'),'--generation',str(stage/'GENERATION.json'),'--output',str(stage/'training'),'--deadline',str(deadline)]
def planned_inventory(output):
    plans=s.read(s.ROOT/'inputs/PLANS.json');rows=[]
    for window,coordinates in plans['training'].items():
        rows.extend(dict(phase='training',window=int(window),coordinate=r,export=str(output/f'window-{int(window):02d}'/'collection/export/EPISODES.json'),reward=None,available=False,reason='planned before service') for r in coordinates)
    for arm in ('unchanged','trained'):rows.extend(dict(phase='readout',arm=arm,coordinate=r,export=str(output/('readout-'+arm)/'export/EPISODES.json'),reward=None,available=False,reason='planned before service') for r in plans['readout'])
    return rows

def collection_stage(suite,service,stage,phase,deadline,generation=None,cap=600):
    stage.mkdir(parents=True,exist_ok=False);end=time.time()+remaining(deadline,cap)
    collect.prepare_spec(phase,service/'BINDING.json',service/'service/endpoint-original.json',stage/'CAPTURE_SPEC.json',remaining(end,cap),generation)
    error=None
    try:suite.command(service,'collect-'+phase,collector_argv(stage,end),remaining(end,cap),end)
    except Exception as caught:error=dict(type=type(caught).__name__,message=str(caught))
    # Even a nonzero/capped collector keeps its partial native evidence and all
    # planned NULL rows. No partial window group is ever allowed into Adam.
    if not (stage/'rollout/SPEC.json').exists():
        s.write(stage/'COLLECTION_FAILURE.json',dict(error=error,reason='collector produced no spec'));raise RuntimeError('collector returned no native attempt')
    result=export.export_attempt(stage/'rollout',stage/'export')
    s.write(stage/'COLLECTION_RESULT.json',dict(command_error=error,manifest_sha256=s.sha(stage/'export/MANIFEST.json')))
    return result

def train_window(suite,stage,cutoff,generation):
    cap=remaining(cutoff-60,480);deadline=time.time()+min(240,cap);argv=trainer_argv(stage,deadline)
    s.write(stage/'TRAIN_COMMAND.json',dict(argv=argv,process_cap_seconds=cap,all_authentication_load_math_checkpoint_charged=True,started_epoch=time.time()))
    with (stage/'training.log').open('x') as log:
        process=subprocess.Popen(argv,stdout=log,stderr=subprocess.STDOUT,start_new_session=True,env={**os.environ,'PYTHONDONTWRITEBYTECODE':'1'})
        observed=suite.life.observe(process.pid)
        if observed is None:
            process.wait(timeout=5);raise RuntimeError('training exited before owned observation')
        owner=suite.life.safe_observation(observed);s.write(stage/'TRAIN_OWNER.json',owner)
        try:
            if process.wait(timeout=cap)!=0:raise RuntimeError('training nonzero; retained state/no retry')
        finally:suite.stop_child(process,owner);s.write(stage/'TRAIN_EXIT.json',dict(returncode=process.returncode,ended_epoch=time.time()))
    return common.c.checkpoint_policy(stage/'training',generation)

def recover_commit_on_stop(stage,generation,state):
    policy=common.c.checkpoint_policy(stage/'training',generation)
    cursor=common.transition(state['completed_windows'],state['policy'],generation['candidate_window'],policy)
    state.update(policy=policy,completed_windows=cursor['completed_windows'])
    s.write(stage/'COMMIT_RECOVERED_ON_STOP.json',{**cursor,'generation':generation,'no_second_update':True,'semantics':'actual committed update consumes this complete window even without normal WINDOW_RESULT'})

def learning(output,suite,state,cutoff,owned):
    active=None
    try:
        for window in range(1,13):
            if not learning_window_allowed(cutoff):break
            alarm(cutoff-120);stage=output/f'window-{window:02d}';stage.mkdir();generation=common.generation(window,state['policy']);s.write(stage/'GENERATION.json',generation)
            service=stage/'service-stage';service.mkdir();active=service;state['active_service']=service
            try:
                suite.start_service(service,collect.binding_for(state['policy']),time.time()+remaining(cutoff-120,180))
                result=collection_stage(suite,service,stage/'collection',f'window-{window}',cutoff-660,generation,600)
            finally:
                alarm(min(owned,cutoff));suite.release_service(service);active=None;state['active_service']=None
            if not result['complete'] or result['integrity_failures']:raise RuntimeError('incomplete/integrity-failed window preserved; no partial update')
            new=None;alarm(cutoff-60)
            if result['training_group_episodes']:
                try:new=train_window(suite,stage,cutoff-60,generation)
                except Exception:
                    checkpoint=stage/'training'/f'checkpoint-{generation["round"]}'/'state.json'
                    if checkpoint.exists():
                        recover_commit_on_stop(stage,generation,state)
                    raise
            cursor=common.transition(state['completed_windows'],state['policy'],window,new)
            state.update(policy=cursor['policy'],completed_windows=window)
            s.write(stage/'WINDOW_RESULT.json',{**cursor,'generation':generation,'export_manifest_sha256':s.sha(stage/'collection/export/MANIFEST.json'),'ended_epoch':time.time()})
    finally:
        alarm(min(owned,cutoff))
        if active is not None:
            suite.release_service(active);state['active_service']=None

def execute(output):
    started=time.time();training_end=started+9000;work=started+14100;owned=started+14280
    check_output(output);s.runtime();manifest=s.verify_prepared();initial=common.starting_decision()[2]
    gpu=os.environ.get('CUDA_VISIBLE_DEVICES','')
    if not gpu or ',' in gpu:raise ValueError('MAIN assigns one GPU under MAIN lock')
    suite=dependencies();output.mkdir(parents=True,exist_ok=False);inventory=planned_inventory(output)
    s.write(output/'PLANNED_NULL_ENDPOINTS.json',inventory)
    s.write(output/'OWNER_RUN.json',dict(campaign_id=manifest['campaign_id'],ready_sha256=s.sha(s.ROOT/'READY.json'),started_epoch=started,training_side_deadline_epoch=training_end,work_deadline_epoch=work,owned_deadline_epoch=owned,outer_seconds=14400,cleanup_seconds=180,outer_margin_seconds=120,gpu=gpu,final_order=s.final_order(),credential_present=True,credential_value_logged=False,automatic_resume=False))
    def expired(sig,frame):
        if sig in (signal.SIGTERM,signal.SIGINT):raise MainTermination('MAIN termination; no new work')
        raise TimeoutError('active phase/owned shared clock')
    previous={sig:signal.signal(sig,expired) for sig in (signal.SIGINT,signal.SIGTERM,signal.SIGALRM)};alarm(owned)
    state=dict(policy=initial,completed_windows=0);training_stop=None;readouts={};errors=[];active=None
    try:
        try:learning(output,suite,state,training_end,owned)
        except Exception as caught:
            training_stop=dict(type=type(caught).__name__,message=str(caught),traceback=traceback.format_exc());s.write(output/'TRAINING_STOP.json',training_stop)
        alarm(owned)
        if state.get('active_service') is not None:
            active=state['active_service'];raise RuntimeError('learning service release unresolved; no new service can launch')
        selection=dict(rule='last actually committed root; no validation/heldout selection',policy=state['policy'],completed_windows=state['completed_windows'],actual_optimizer_step=state['policy']['step'])
        s.write(output/'SELECTION.json',selection)
        final_end=min(work,time.time()+5100);policies=final_policies(initial,state['policy'])
        for arm in s.final_order():
            block_end=min(final_end,time.time()+2550);service=output/('final-'+arm);service.mkdir();active=service
            try:
                alarm(block_end-90)
                suite.start_service(service,collect.binding_for(policies[arm]),time.time()+remaining(block_end-90,180))
                readouts[arm]=collection_stage(suite,service,output/('readout-'+arm),'readout-'+arm,block_end-90,None,remaining(block_end-90,2280))
            except Exception as caught:
                errors.append(dict(arm=arm,type=type(caught).__name__,message=str(caught)));s.write(output/('READOUT_FAILURE-'+arm+'.json'),errors[-1])
            finally:
                alarm(owned)
                try:suite.release_service(service);active=None
                except Exception as caught:
                    errors.append(dict(arm=arm,type=type(caught).__name__,message=str(caught),release_failed=True));break
    except (MainTermination,Exception) as caught:errors.append(dict(type=type(caught).__name__,message=str(caught)))
    finally:
        if active is not None:
            try:suite.release_service(active);active=None
            except BaseException as caught:errors.append(dict(type=type(caught).__name__,message=str(caught),release_failed=True))
        signal.setitimer(signal.ITIMER_REAL,0)
        for sig,handler in previous.items():signal.signal(sig,handler)
    cache={};hashes={}
    for row in inventory:
        path=Path(row['export'])
        if path.exists():
            if str(path) not in cache:cache[str(path)]={r['episode_id']:r for r in s.read(path)};hashes[str(path)]=s.sha(path)
            result=cache[str(path)][row['coordinate']['id']];row.update(available=result['terminal_observable'],reward=result['endpoint_reward'],training_reward=result['reward'],reason=result['invalid_reason'],export_sha256=hashes[str(path)])
        else:row['reason']='unreturned/unrun; raw partial artifacts retained if present'
    result=dict(complete=set(readouts)=={'unchanged','trained'} and not errors and all(r['complete'] for r in readouts.values()),selection=dict(policy=state['policy'],completed_windows=state['completed_windows'],actual_optimizer_step=state['policy']['step']),training_stop=training_stop,readouts=readouts,errors=errors,inventory=inventory,planned_training=288,planned_final=96,elapsed_seconds=time.time()-started,active_unreleased_service=str(active) if active else None,orchestrator_complete_does_not_imply_model_final=True)
    from qsr_metrics import paired_summary
    result['paired_readout']=paired_summary(inventory)
    s.write(output/'OWNER_TERMINAL.json',result);return result

def parse_args(argv=None):
    p=argparse.ArgumentParser();p.add_argument('command',choices=('verify','run'));p.add_argument('--output',type=Path,default=s.ATTEMPT);return p.parse_args(argv)
if __name__=='__main__':
    a=parse_args()
    if a.command=='verify':print(s.verify_prepared()['campaign_id'])
    else:
        r=execute(a.output);print(dict(complete=r['complete'],actual_optimizer_step=r['selection']['actual_optimizer_step'],elapsed_seconds=r['elapsed_seconds']));raise SystemExit(0 if r['complete'] else 1)
