"""Single fixed24 phase with explicit2400/2370/2220 clocks and complete24 inventory."""
import argparse
import functools
import os
from pathlib import Path
import signal
import time
import traceback
import ss_study as s

class MainTermination(BaseException):pass
@functools.lru_cache(maxsize=1)
def old_owner():return s.load('scale_qualified_ledger',s.CT/'ct_owner.py',s.ct_ready['source_sha256'][str(s.CT/'ct_owner.py')],{'ct_study':s.ct})
def ledger(output):return old_owner().ledger(output)
def dependencies():return s.dose.dependencies()
def remaining(deadline,cap):
    value=min(cap,deadline-time.time())
    if value<=0:raise TimeoutError('scale inclusive stage deadline')
    return value
def collector_argv(stage,destination,deadline):return [str(s.NATIVE),str(s.ROOT/'ss_collect.py'),'--mode','free','--plan','FREE_PLAN.json','--start','0','--stop','24','--binding',str(stage/'BINDING.json'),'--endpoint',str(stage/'service/endpoint-original.json'),'--output',str(destination),'--deadline',str(float(deadline))]
def harvest(output,plan):
    rows=[]
    for row in plan['full']:
        directory=output/'sft24/free'/row['coordinate']['id'];path=directory/'RESULT.json';failure=directory/'FAILURE.json';physical=list((directory/'physical').glob('*.json'))
        result=dict(row,recorded=False,available=False,reward=None,operational_success=0,result_path=str(path),physical_records=len(physical),cause='not_started_no_artifacts')
        if path.exists():
            value=s.read(path);result.update(recorded=True,available=value['available'],reward=value['reward'],operational_success=int(value['available'] and value['reward']==1),result_sha256=s.sha(path),cause='native_final' if value['available'] else 'attempted_native_no_final')
        elif failure.exists() or physical:result.update(cause='attempted_exception_no_result' if failure.exists() else 'attempted_interrupted_no_result',failure_sha256=s.sha(failure) if failure.exists() else None)
        elif directory.exists():result['cause']='started_no_physical_receipt'
        rows.append(result)
    return rows
def execute(output):
    started=time.time();work=started+2220;owned=started+2370
    if output.resolve()!=s.ATTEMPT.resolve() or output.exists():raise ValueError('exact unused scale attempt only')
    ready=s.verify();s.runtime();gpu=os.environ.get('CUDA_VISIBLE_DEVICES','')
    if not gpu or ',' in gpu:raise ValueError('MAIN assigns one GPU')
    output.mkdir(parents=True);plan=s.read(s.ROOT/'inputs/EVALUATION_PLAN.json');suite=dependencies();stage=output/'service-sft24';stage.mkdir()
    s.write(output/'PLANNED_EVALUATION.json',plan)
    s.write(output/'OWNER_RUN.json',dict(identity=ready['identity'],started_epoch=started,work_deadline_epoch=work,owned_deadline_epoch=owned,outer_seconds=2400,policy_order=['sft24'],gpu=gpu,no_training=True,model_action_tokens=2048,context_tokens=8192,selected=s.selected()))
    def expired(sig,frame):
        if sig in (signal.SIGTERM,signal.SIGINT):raise MainTermination('MAIN termination')
        raise TimeoutError('scale stage/shared cap')
    handlers={sig:signal.signal(sig,expired) for sig in (signal.SIGTERM,signal.SIGINT,signal.SIGALRM)}
    active=True;errors=[];status=dict(started_epoch=time.time(),policy='sft24')
    try:
        startup=time.time()+remaining(work-90,180);signal.setitimer(signal.ITIMER_REAL,remaining(startup,180));suite.start_service(stage,s.binding(),startup)
        end=time.time()+remaining(work-90,1950);signal.setitimer(signal.ITIMER_REAL,remaining(end,1950))
        suite.command(stage,'free24',collector_argv(stage,output/'sft24/free',end),remaining(end,1950),end);status['work_complete']=True
    except BaseException as error:errors.append(dict(type=type(error).__name__,message=str(error),traceback=traceback.format_exc()))
    finally:
        signal.setitimer(signal.ITIMER_REAL,max(.001,min(owned,time.time()+150)-time.time()))
        try:suite.release_service(stage);active=False
        except BaseException as error:errors.append(dict(stage='release',type=type(error).__name__,message=str(error)))
        status['ended_epoch']=time.time();status['errors']=errors;s.write(stage/'PHASE_TERMINAL.json',status)
        signal.setitimer(signal.ITIMER_REAL,max(.001,owned-time.time()))
        rows=harvest(output,plan);s.write(output/'COST_LEDGER.json',ledger(output))
        result=dict(identity=ready['identity'],complete=not errors,error=errors or None,released=not active,active_unreleased_service=str(stage) if active else None,planned_full=24,planned_first_action=0,readout_inventory=rows,phase=status,elapsed_seconds=time.time()-started,native_availability_not_implied_by_orchestrator_completion=True,no_retry=True,no_training=True)
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
