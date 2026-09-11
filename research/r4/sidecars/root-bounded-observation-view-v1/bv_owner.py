"""One fixed24 phase with explicit1800/1770/1650 clocks and complete32 inventory."""
import argparse
import functools
import os
from pathlib import Path
import signal
import time
import traceback
import bv_study as s

class MainTermination(BaseException):pass
@functools.lru_cache(maxsize=1)
def old_owner():return s.load('bounded_view_base_owner',s.BASE/'ae_owner.py',s.base_ready['source_sha256'][str(s.BASE/'ae_owner.py')],{'ae_study':s})
def ledger(output):return old_owner().ledger(output)
def dependencies():return old_owner().dependencies()
def remaining(deadline,cap):
    value=min(cap,deadline-time.time())
    if value<=0:raise TimeoutError('bounded-view inclusive stage deadline')
    return value
def collector_argv(stage,destination,deadline):return [str(s.NATIVE),str(s.ROOT/'bv_collect.py'),'--mode','free','--plan','FREE_PLAN.json','--start','0','--stop','32','--binding',str(stage/'BINDING.json'),'--endpoint',str(stage/'service/endpoint-original.json'),'--output',str(destination),'--deadline',str(float(deadline))]
def harvest(output,plan):
    rows=[]
    for planned in plan['full']:
        row=planned['coordinate'];directory=output/'sft24/free'/row['id'];path=directory/'RESULT.json';failure=directory/'FAILURE.json';episode=directory/'EPISODE.json';physical=list((directory/'physical').glob('*.json'))
        result=dict(planned,recorded=False,available=False,reward=None,cause='not_started_no_artifacts',result_path=str(path),physical_records=len(physical),episode_recorded=episode.exists())
        if path.exists():
            value=s.read(path);result.update(recorded=True,available=value['available'],reward=value['reward'],cause='native_final' if value['available'] else 'attempted_native_no_final',result_sha256=s.sha(path))
        elif failure.exists() or physical:result.update(cause='attempted_exception_no_result' if failure.exists() else 'attempted_interrupted_no_result',failure_sha256=s.sha(failure) if failure.exists() else None)
        elif directory.exists():result['cause']='started_no_physical_receipt'
        rows.append(result)
    return rows
def execute(output):
    started=time.time();work=started+1650;owned=started+1770
    if output.resolve()!=s.ATTEMPT.resolve() or output.exists():raise ValueError('exact unused bounded-view attempt only')
    ready=s.verify();s.runtime();gpu=os.environ.get('CUDA_VISIBLE_DEVICES','')
    if not gpu or ',' in gpu:raise ValueError('MAIN assigns one GPU')
    output.mkdir(parents=True);plan=s.read(s.ROOT/'inputs/EVALUATION_PLAN.json');suite=dependencies();stage=output/'service-sft24';stage.mkdir();s.write(output/'PLANNED_EVALUATION.json',plan)
    s.write(output/'OWNER_RUN.json',dict(identity=ready['identity'],started_epoch=started,work_deadline_epoch=work,owned_deadline_epoch=owned,outer_seconds=1800,model_action_tokens=2048,context_tokens=8192,gpu=gpu,no_training=True,conditional_mechanism_gate=s.read(s.ROOT/'inputs/MECHANISM_GATE.json')))
    def expired(sig,frame):
        if sig in (signal.SIGTERM,signal.SIGINT):raise MainTermination('MAIN termination')
        raise TimeoutError('bounded-view stage/shared cap')
    handlers={sig:signal.signal(sig,expired) for sig in (signal.SIGTERM,signal.SIGINT,signal.SIGALRM)};active=True;errors=[];status=dict(started_epoch=time.time(),policy='sft24')
    try:
        startup=time.time()+remaining(work-30,180);signal.setitimer(signal.ITIMER_REAL,remaining(startup,180));suite.start_service(stage,s.binding(),startup)
        end=time.time()+remaining(work-30,1440);signal.setitimer(signal.ITIMER_REAL,remaining(end,1440));suite.command(stage,'free32',collector_argv(stage,output/'sft24/free',end),remaining(end,1440),end);status['work_complete']=True
    except BaseException as error:errors.append(dict(type=type(error).__name__,message=str(error),traceback=traceback.format_exc()))
    finally:
        signal.setitimer(signal.ITIMER_REAL,max(.001,min(owned,time.time()+120)-time.time()))
        try:suite.release_service(stage);active=False
        except BaseException as error:errors.append(dict(stage='release',type=type(error).__name__,message=str(error)))
        status.update(ended_epoch=time.time(),errors=errors);s.write(stage/'PHASE_TERMINAL.json',status)
        signal.setitimer(signal.ITIMER_REAL,max(.001,min(30,owned-time.time())))
        rows=harvest(output,plan);s.write(output/'COST_LEDGER.json',ledger(output))
        result=dict(identity=ready['identity'],complete=not errors,error=errors or None,released=not active,active_unreleased_service=str(stage) if active else None,planned_full=32,readout_inventory=rows,phase=status,elapsed_seconds=time.time()-started,native_availability_not_implied_by_orchestrator_completion=True,no_retry=True,no_training=True)
        s.write(output/'OWNER_TERMINAL.json',result);signal.setitimer(signal.ITIMER_REAL,0)
        for sig,handler in handlers.items():signal.signal(sig,handler)
    return result
def parse_args():
    parser=argparse.ArgumentParser();parser.add_argument('command',choices=('verify','run'));parser.add_argument('--output',type=Path,default=s.ATTEMPT);return parser.parse_args()
if __name__=='__main__':
    args=parse_args()
    if args.command=='verify':print(s.verify()['identity'])
    else:
        result=execute(args.output);print(dict(complete=result['complete'],errors=result['error']));raise SystemExit(0 if result['complete'] else 1)
