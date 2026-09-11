"""Bounded non-reroll window1 continuation; qualified90-second release envelope."""
import argparse
import os
from pathlib import Path
import signal
import subprocess
import time
import traceback
import warm_resume_v3 as r
import warm_owner_v2 as v2
import warm_common as common
import warm_wire_v3 as wire

s=r.study
MainTermination=v2.v1.MainTermination
def budget(start):return dict(started=start,training_end=start+5019,work=start+10119,owned=start+10299,outer=start+10419)
def learning_allowed(deadline,now=None):return deadline-(time.time() if now is None else now)>=1380
def release_deadline(now,end,owned):return min(now+90,end,owned)
def dependencies():return v2.v1.dependencies()
def trainer_argv(stage,group,generation,deadline):
    return [str(s.TRAIN),str(s.ROOT/'warm_train_v2.py'),'--group',str(group),'--generation',str(generation),
            '--output',str(stage/'training'),'--deadline',str(float(deadline))]
def train(suite,stage,group,generation_path,cutoff,generation):
    cap=v2.v1.remaining(cutoff-60,480);deadline=time.time()+min(240,cap)
    argv=trainer_argv(stage,group,generation_path,deadline)
    s.write(stage/'TRAIN_COMMAND.json',dict(argv=argv,started_epoch=time.time(),process_cap_seconds=cap,
        gpu_visible_to_command=bool(os.environ.get('CUDA_VISIBLE_DEVICES')),source_group_sha256=s.sha(group)))
    with (stage/'training.log').open('x') as log:
        process=subprocess.Popen(argv,stdout=log,stderr=subprocess.STDOUT,start_new_session=True,
                                 env={**os.environ,'PYTHONDONTWRITEBYTECODE':'1'})
        observed=suite.life.observe(process.pid)
        if observed is None:process.wait(timeout=5);raise RuntimeError('trainer exited before owner observation')
        owner=suite.life.safe_observation(observed);s.write(stage/'TRAIN_OWNER.json',owner)
        try:
            if process.wait(timeout=cap)!=0:raise RuntimeError('trainer failed; no retry')
        finally:
            suite.stop_child(process,owner);s.write(stage/'TRAIN_EXIT.json',dict(returncode=process.returncode,ended_epoch=time.time()))
    return common.c.checkpoint_policy(stage/'training',generation)
def account(output):return wire.combined(r.ORIGINAL,output)
def harvest(output,inventory):
    cache={};rows=[]
    for row in inventory:
        value=dict(row);path=Path(row['export'])
        if path.exists():
            if path not in cache:cache[path]={x['episode_id']:x for x in s.read(path)}
            result=cache[path][row['coordinate']['id']]
            value.update(available=result['terminal_observable'],reward=result['endpoint_reward'],training_reward=result['reward'],reason=result['invalid_reason'],export_sha256=s.sha(path))
        rows.append(value)
    return rows

def execute(output):
    started=time.time();limits=budget(started);output=Path(output)
    if output.resolve()!=r.ATTEMPT.resolve() or output.exists():raise ValueError('exact unused attempt003 only')
    ready,proof=r.verify();s.runtime()
    if not os.environ.get('CUDA_VISIBLE_DEVICES') or ',' in os.environ['CUDA_VISIBLE_DEVICES']:raise ValueError('MAIN assigns one GPU')
    suite=dependencies();output.mkdir(parents=True)
    inventory=v2.v1.planned_inventory(output)
    for row in inventory:
        if row.get('window')==1:row['export']=str(r.ORIGINAL/'window-01/collection/export/EPISODES.json')
    s.write(output/'PLANNED_NULL_ENDPOINTS.json',inventory)
    s.write(output/'OWNER_RUN.json',dict(identity=ready['identity'],**limits,original_seconds_charged=381,
        combined_active_outer_seconds=10800,original_source=proof,
        calendar_since_original_start=started-proof['original_started_epoch'],automatic_resume=False))
    state=dict(policy=s.fixed_start(),completed_windows=0);active=None;errors=[];training_stop=None;readouts={}
    def expired(sig,frame):
        if sig in (signal.SIGTERM,signal.SIGINT):raise MainTermination('MAIN termination')
        raise TimeoutError('V3 stage/shared cap')
    handlers={sig:signal.signal(sig,expired) for sig in (signal.SIGALRM,signal.SIGINT,signal.SIGTERM)}
    def release(end):
        nonlocal active
        if active is None:return
        v2.v1.alarm(release_deadline(time.time(),end,limits['owned']))
        suite.release_service(active)
        active=None
    def update(stage,generation,group,generation_path):
        v2.v1.alarm(limits['training_end'])
        try:return train(suite,stage,group,generation_path,limits['training_end'],generation)
        except Exception:
            if (stage/'training'/f"checkpoint-{generation['round']}"/'state.json').exists():
                v2.v1.recover_commit_on_stop(stage,generation,state)
            raise
    try:
        try:
            first=output/'window-01';first.mkdir();generation=proof['generation']
            s.write(first/'REUSED_SOURCE.json',proof)
            new=update(first,generation,Path(proof['source_group']),Path(proof['source_generation'])) if proof['selected'] else None
            cursor=common.transition(0,state['policy'],1,new);state.update(policy=cursor['policy'],completed_windows=1)
            s.write(first/'WINDOW_RESULT.json',dict(cursor,source_reused=True,generation=generation))
            for window in range(2,9):
                if not learning_allowed(limits['training_end']):break
                stage=output/f'window-{window:02d}';stage.mkdir();generation=common.generation(window,state['policy'])
                s.write(stage/'GENERATION.json',generation)
                if active is not None:raise RuntimeError('prior service not released')
                service=stage/'service-stage';service.mkdir();active=service
                try:
                    startup=min(limits['training_end'],time.time()+180);v2.v1.alarm(startup)
                    suite.start_service(service,v2.collect.binding_for(state['policy']),startup)
                    result=v2.collection_stage(suite,service,stage/'collection',f'window-{window}',limits['training_end']-600,generation,600)
                finally:release(limits['training_end'])
                if not result['complete'] or result['integrity_failures']:raise RuntimeError('incomplete/invalid window; no partial update')
                new=update(stage,generation,stage/'collection/export/GROUP.json',stage/'GENERATION.json') if result['training_group_episodes'] else None
                cursor=common.transition(state['completed_windows'],state['policy'],window,new);state.update(policy=cursor['policy'],completed_windows=window)
                s.write(stage/'WINDOW_RESULT.json',dict(cursor,generation=generation))
        except Exception as error:
            training_stop=dict(type=type(error).__name__,message=str(error),traceback=traceback.format_exc())
            s.write(output/'TRAINING_STOP.json',training_stop)
        s.write(output/'SELECTION.json',dict(state,rule='last committed RL checkpoint including zero'))
        if active is not None:raise RuntimeError('unreleased training service; no next service or trainer')
        for arm,policy in (('unchanged',s.fixed_start()),('trained',state['policy'])):
            if active is not None:raise RuntimeError('unreleased prior service')
            end=min(limits['work'],time.time()+2550);service=output/('final-'+arm);service.mkdir();active=service
            try:
                startup=min(end-90,time.time()+180);v2.v1.alarm(startup)
                suite.start_service(service,v2.collect.binding_for(policy),startup)
                readouts[arm]=v2.collection_stage(suite,service,output/('readout-'+arm),'readout-'+arm,end-90,None,v2.v1.remaining(end-90,2340))
            except Exception as error:
                errors.append(dict(arm=arm,type=type(error).__name__,message=str(error)))
            finally:release(end)
    except (MainTermination,Exception) as error:errors.append(dict(type=type(error).__name__,message=str(error)))
    finally:
        if active is not None:
            try:release(limits['owned']-30)
            except BaseException as error:errors.append(dict(stage='cleanup',type=type(error).__name__,message=str(error)))
        v2.v1.alarm(min(limits['owned'],time.time()+30))
        try:
            rows=harvest(output,inventory);s.write(output/'COST_LEDGER_V3.json',account(output))
            result=dict(identity=ready['identity'],complete=set(readouts)=={'unchanged','trained'} and not errors and all(v['complete'] for v in readouts.values()),
                released=active is None,active_unreleased_service=str(active) if active else None,errors=errors,training_stop=training_stop,
                selection=state,readouts=readouts,inventory=rows,elapsed_seconds=time.time()-started,
                combined_active_seconds_charged=381+time.time()-started,original_attempt=str(r.ORIGINAL),no_reacquisition_window1=True)
            s.write(output/'OWNER_TERMINAL.json',result)
        finally:
            signal.setitimer(signal.ITIMER_REAL,0)
            for sig,handler in handlers.items():signal.signal(sig,handler)
    return result

def parse_args(argv=None):
    parser=argparse.ArgumentParser();parser.add_argument('command',choices=('verify','run'));parser.add_argument('--output',type=Path,default=r.ATTEMPT);return parser.parse_args(argv)
if __name__=='__main__':
    args=parse_args()
    if args.command=='verify':print(r.verify()[0]['identity'])
    else:
        result=execute(args.output);print(dict(complete=result['complete'],selection=result['selection'],released=result['released']));raise SystemExit(0 if result['complete'] else 1)
