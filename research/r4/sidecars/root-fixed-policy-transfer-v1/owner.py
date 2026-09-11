"""Readout only, all48 slots pre-inventoried; fixed policies and one inclusive2400 clock."""
import argparse
import functools
import os
from pathlib import Path
import signal
import time
import traceback
import transfer_study as s
import transfer_binding as b

@functools.lru_cache(maxsize=1)
def dependencies():
    with s.aliases({'joint_study':s.source,'joint_binding':s.original_binding(),'joint_protocol':s.original_protocol()}):
        old=s.load('transfer_qualified_joint_owner',s.OLD/'owner.py','5b4793c31b78d2cd0dbca2b6f756a0935b18b2f28b6b3cb15775836e8d5d04ed')
    return old.dependencies()
def remaining(deadline,cap):
    value=min(cap,deadline-time.time())
    if value<=0:raise TimeoutError('shared work/stage deadline')
    return value
def check_output(output):
    if output.resolve()!=s.ATTEMPT.resolve():raise ValueError('exact new attempt only')
    if output.exists():raise FileExistsError('attempt exists; no retry/overwrite')
def collector_argv(stage,destination,deadline):
    return [str(s.NATIVE),str(s.ROOT/'collect.py'),'--mode','free','--plan','FREE_PLAN.json','--start','0','--stop','16','--binding',str(stage/'BINDING.json'),'--endpoint',str(stage/'service/endpoint-original.json'),'--output',str(destination),'--deadline',str(deadline)]
def planned_inventory(output):
    return [dict(arm=arm,mode='free',coordinate=row,path=str(output/arm/'free'/row['id']/'RESULT.json'),available=False,reward=None,operational_success=0,reason='planned before any service launch') for arm in s.ARMS for row in s.read(s.ROOT/'inputs/FREE_PLAN.json')]
def execute(output):
    started=time.time();work=started+2100;owned=started+2280
    check_output(output);s.runtime();ready=s.verify()
    gpu=os.environ.get('CUDA_VISIBLE_DEVICES','')
    if not gpu or ',' in gpu:raise ValueError('MAIN assigns one GPU under MAIN lock')
    suite=dependencies();output.mkdir(parents=True,exist_ok=False);inventory=planned_inventory(output)
    if len(inventory)!=48:raise ValueError('exact48 inventory')
    s.write(output/'PLANNED_NULL_ENDPOINTS.json',inventory)
    s.write(output/'OWNER_RUN.json',dict(identity=ready['identity'],ready_sha256=s.sha(s.ROOT/'READY.json'),started_epoch=started,work_deadline_epoch=work,owned_deadline_epoch=owned,outer_seconds=2400,cleanup_reserve_seconds=180,outer_margin_seconds=120,gpu=gpu,phase_order=s.phases(),credential_present=True,credential_value_logged=False,no_training=True))
    stop_requested=False
    def expired(_sig,_frame):
        nonlocal stop_requested
        stop_requested=True
        raise TimeoutError('owned2280s inclusive cap or MAIN termination')
    previous={sig:signal.signal(sig,expired) for sig in (signal.SIGINT,signal.SIGTERM,signal.SIGALRM)}
    signal.setitimer(signal.ITIMER_REAL,remaining(owned,2280));stages=[];error=None;release_errors=[];active=None
    try:
        for arm in s.phases():
            remaining(work,180);stage=output/('service-'+arm);stage.mkdir();active=stage
            try:
                suite.start_service(stage,b.binding(arm,b.selected(arm)),time.time()+remaining(work,180))
                deadline=time.time()+remaining(work,480);destination=output/arm/'free'
                suite.command(stage,'free',collector_argv(stage,destination,deadline),remaining(deadline,480),deadline)
                stages.append(dict(arm=arm,complete=True,output=str(destination)))
            except Exception as caught:
                if stop_requested:raise
                stages.append(dict(arm=arm,complete=False,error=dict(type=type(caught).__name__,message=str(caught),traceback=traceback.format_exc())))
                # No reroll. A released failed phase does not remove other policies' planned slots.
            finally:
                try:suite.release_service(stage);active=None
                except BaseException as caught:release_errors.append(dict(stage=str(stage),type=type(caught).__name__,message=str(caught)));raise
    except BaseException as caught:error=dict(type=type(caught).__name__,message=str(caught),traceback=traceback.format_exc())
    finally:
        signal.setitimer(signal.ITIMER_REAL,0)
        for sig,handler in previous.items():signal.signal(sig,handler)
    from collect import ledger
    for row in inventory:
        path=Path(row['path'])
        if path.exists():
            actual=s.read(path);row.update(recorded=True,available=actual['available'],reward=actual['reward'],operational_success=int(actual['reward']==1),reason=actual.get('reason'),result_sha256=s.sha(path))
        else:row.update(recorded=False,reason='unrun/incomplete; retained phase/episode failures')
    cost=ledger(output);s.write(output/'COST_LEDGER.json',cost)
    result=dict(complete=error is None and not release_errors and len(stages)==3 and all(x['complete'] for x in stages),error=error,release_errors=release_errors,stages=stages,readout_inventory=inventory,planned=48,elapsed_seconds=time.time()-started,work_deadline_epoch=work,owned_deadline_epoch=owned,outer_seconds=2400,no_retry=True,no_training=True,main_owns_gpu_and_lock=True,active_unreleased_service=str(active) if active else None,orchestrator_complete_does_not_imply_model_final=True,cost_ledger_sha256=s.sha(output/'COST_LEDGER.json'))
    s.write(output/'OWNER_TERMINAL.json',result);return result
def parse_args(argv=None):
    ap=argparse.ArgumentParser();ap.add_argument('command',choices=('verify','run'));ap.add_argument('--output',type=Path,default=s.ATTEMPT);return ap.parse_args(argv)
if __name__=='__main__':
    args=parse_args()
    if args.command=='verify':print(s.verify()['identity'])
    else:
        result=execute(args.output);print(dict(complete=result['complete'],error=result['error'],elapsed_seconds=result['elapsed_seconds']));raise SystemExit(0 if result['complete'] else 1)
