"""One actual dual-adapter service, exact attempt and inclusive1800 envelope."""
import argparse
import functools
import os
from pathlib import Path
import signal
import time
import traceback
import cl_study as s
import cl_protocol as p

@functools.lru_cache(maxsize=1)
def dependencies():
    old=s.load('cl_qualified_lifecycle_owner',s.CE/'owner.py','8967d888d38428c273d2b60a993183f28887a3ca9b2ee67eb331e9ac7bb28d03',{'study':s,'protocol':p})
    return old.dependencies()
def remaining(deadline,cap):
    value=min(cap,deadline-time.time())
    if value<=0:raise TimeoutError('shared stage/work deadline')
    return value
def check_output(output):
    if output.resolve()!=s.ATTEMPT.resolve():raise ValueError('exact fresh attempt')
    if output.exists():raise FileExistsError('no repeat/overwrite')
def validate_paths(args):
    if args.output.resolve()!=(s.ATTEMPT/'rollout').resolve() or args.binding.resolve()!=(s.ATTEMPT/'service/BINDING.json').resolve() or args.endpoint.resolve()!=(s.ATTEMPT/'service/service/endpoint-original.json').resolve():raise ValueError('collector attempt namespace')
    if not isinstance(args.deadline,(float,int)):raise ValueError('deadline')
def inventory(output):return [{**p.null(row,'planned_before_service'),'path':str(output/'rollout/rows'/(row['id']+'.json'))} for row in s.read(s.ROOT/'inputs/PLAN.json')]
def collector_argv(output,deadline):
    return [str(s.NATIVE),str(s.ROOT/'cl_collect.py'),'--binding',str(output/'service/BINDING.json'),'--endpoint',str(output/'service/service/endpoint-original.json'),'--output',str(output/'rollout'),'--deadline',str(deadline)]
def execute(output):
    started=time.time();work=started+1650;owned=started+1770;check_output(output);s.runtime();ready=s.verify()
    gpu=os.environ.get('CUDA_VISIBLE_DEVICES','')
    if not gpu or ',' in gpu:raise ValueError('MAIN assigns one GPU')
    suite=dependencies();output.mkdir(parents=True,exist_ok=False);planned=inventory(output)
    if len(planned)!=48:raise ValueError('fixed48')
    s.write(output/'PLANNED_NULL_ENDPOINTS.json',planned);s.write(output/'REUSED_SOURCE_INVENTORY.json',[dict(coordinate=r,reused=True,new_physical_request_attempt=False) for r in s.read(s.ROOT/'inputs/ACQUISITION_PLAN.json')])
    s.write(output/'OWNER_RUN.json',dict(identity=ready['identity'],ready_sha256=s.sha(s.ROOT/'READY.json'),started_epoch=started,work_deadline_epoch=work,owned_deadline_epoch=owned,outer_seconds=1800,cleanup_seconds=120,outer_margin_seconds=30,new_source_acquisitions=0,historical_source_acquisitions=8,root_cap_reserved_seconds=1440,closure_reserved_seconds=30,startup_seconds=180,caps_not_waits=True,credential_present=True,credential_value_logged=False,gpu=gpu,no_training=True))
    def expired(_sig,_frame):raise TimeoutError('owned1770 inclusive or MAIN termination')
    previous={sig:signal.signal(sig,expired) for sig in (signal.SIGINT,signal.SIGTERM,signal.SIGALRM)};signal.setitimer(signal.ITIMER_REAL,remaining(owned,1770))
    stage=output/'service';stage.mkdir();active=stage;error=None;release_error=None
    try:
        suite.start_service(stage,s.binding(),time.time()+remaining(work-1470,180))
        suite.command(stage,'canonical-loader48',collector_argv(output,work),remaining(work,1650),work)
    except BaseException as caught:error=dict(type=type(caught).__name__,message=str(caught),traceback=traceback.format_exc())
    finally:
        signal.setitimer(signal.ITIMER_REAL,max(.001,min(owned,time.time()+120)-time.time()))
        try:suite.release_service(stage);active=None
        except BaseException as caught:release_error=dict(type=type(caught).__name__,message=str(caught))
    try:
        import cl_collect as collector
        for row in planned:
            path=Path(row['path'])
            if path.exists():
                actual=s.read(path);row.update(recorded=True,available=actual['available'],reward=actual['reward'],operational_success=actual['operational_success'],cause=actual.get('cause'),result_sha256=s.sha(path))
            else:row.update(recorded=False,cause='unrun_or_interrupted_retained')
        s.write(output/'COST_LEDGER.json',collector.ledger(output))
        result=dict(complete=error is None and release_error is None,error=error,release_error=release_error,readout_inventory=planned,planned=48,planned_acquisitions=0,reused_acquisitions=8,elapsed_seconds=time.time()-started,active_unreleased_service=str(active) if active else None,no_training=True,no_retry=True,main_owns_gpu_and_lock=True,orchestrator_complete_does_not_imply_native_final=True,cost_ledger_sha256=s.sha(output/'COST_LEDGER.json'))
        s.write(output/'OWNER_TERMINAL.json',result);return result
    finally:
        signal.setitimer(signal.ITIMER_REAL,0)
        for sig,handler in previous.items():signal.signal(sig,handler)
def parse_args(argv=None):
    ap=argparse.ArgumentParser();ap.add_argument('command',choices=('verify','run'));ap.add_argument('--output',type=Path,default=s.ATTEMPT);return ap.parse_args(argv)
if __name__=='__main__':
    args=parse_args()
    if args.command=='verify':print(s.verify()['identity'])
    else:
        result=execute(args.output);print(dict(complete=result['complete'],error=result['error'],elapsed_seconds=result['elapsed_seconds']));raise SystemExit(0 if result['complete'] else 1)
