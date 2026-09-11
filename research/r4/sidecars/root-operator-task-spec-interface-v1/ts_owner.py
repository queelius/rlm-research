"""Single fixed24 phase, full72 inventory and explicit3900/3870/3720 caps."""
import argparse
import functools
import os
from pathlib import Path
import signal
import time
import traceback
import ts_study as s

class MainTermination(BaseException):pass
@functools.lru_cache(maxsize=1)
def prior():return s.load('task_spec_qualified_owner',s.SS/'ss_owner.py',s.ss_ready['source_sha256'][str(s.SS/'ss_owner.py')],{'ss_study':s.ss})
def ledger(output):return prior().ledger(output)
def harvest(output,plan):return prior().harvest(output,plan)
def dependencies():return prior().dependencies()
def remaining(deadline,cap):
    value=min(cap,deadline-time.time())
    if value<=0:raise TimeoutError('task-spec stage/shared cap')
    return value
def collector_argv(stage,destination,deadline):return [str(s.NATIVE),str(s.ROOT/'ts_collect.py'),'--mode','free','--plan','FREE_PLAN.json','--start','0','--stop','72','--binding',str(stage/'BINDING.json'),'--endpoint',str(stage/'service/endpoint-original.json'),'--output',str(destination),'--deadline',str(float(deadline))]
def execute(output):
    started=time.time();work=started+3720;owned=started+3870
    if output.resolve()!=s.ATTEMPT.resolve() or output.exists():raise ValueError('exact unused task-spec attempt only')
    ready=s.verify();s.runtime();gpu=os.environ.get('CUDA_VISIBLE_DEVICES','')
    if not gpu or ',' in gpu:raise ValueError('MAIN assigns one GPU')
    output.mkdir(parents=True);plan=s.read(s.ROOT/'inputs/EVALUATION_PLAN.json');suite=dependencies();stage=output/'service-sft24';stage.mkdir()
    s.write(output/'PLANNED_EVALUATION.json',plan)
    s.write(output/'OWNER_RUN.json',dict(identity=ready['identity'],started_epoch=started,work_deadline_epoch=work,owned_deadline_epoch=owned,outer_seconds=3900,policy_order=['sft24'],gpu=gpu,no_training=True,model_action_tokens=2048,context_tokens=8192,selected=s.selected()))
    def expired(sig,frame):
        if sig in (signal.SIGTERM,signal.SIGINT):raise MainTermination('MAIN termination')
        raise TimeoutError('task-spec stage/shared cap')
    handlers={sig:signal.signal(sig,expired) for sig in (signal.SIGTERM,signal.SIGINT,signal.SIGALRM)};active=True;errors=[];status=dict(started_epoch=time.time(),policy='sft24')
    try:
        startup=time.time()+remaining(work-90,180);signal.setitimer(signal.ITIMER_REAL,remaining(startup,180));suite.start_service(stage,s.binding(),startup)
        end=time.time()+remaining(work-90,3450);signal.setitimer(signal.ITIMER_REAL,remaining(end,3450))
        suite.command(stage,'free72',collector_argv(stage,output/'sft24/free',end),remaining(end,3450),end);status['work_complete']=True
    except BaseException as error:errors.append(dict(type=type(error).__name__,message=str(error),traceback=traceback.format_exc()))
    finally:
        signal.setitimer(signal.ITIMER_REAL,max(.001,min(owned,time.time()+150)-time.time()))
        try:suite.release_service(stage);active=False
        except BaseException as error:errors.append(dict(stage='release',type=type(error).__name__,message=str(error)))
        status['ended_epoch']=time.time();status['errors']=errors;s.write(stage/'PHASE_TERMINAL.json',status)
        signal.setitimer(signal.ITIMER_REAL,max(.001,owned-time.time()))
        rows=harvest(output,plan);s.write(output/'COST_LEDGER.json',ledger(output))
        result=dict(identity=ready['identity'],complete=not errors,error=errors or None,released=not active,active_unreleased_service=str(stage) if active else None,planned_full=72,planned_first_action=0,readout_inventory=rows,phase=status,elapsed_seconds=time.time()-started,native_availability_not_implied_by_orchestrator_completion=True,no_retry=True,no_training=True)
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
