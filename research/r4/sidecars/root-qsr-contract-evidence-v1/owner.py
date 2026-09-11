"""MAIN-owned single-service diagnostic; immutable attempt and inclusive clocks."""
import argparse
import functools
import os
from pathlib import Path
import signal
import time
import traceback
import study as s
import protocol as p

@functools.lru_cache(maxsize=1)
def dependencies():
    root=s.SIDE/'root-fixed-policy-transfer-v1'
    st=s.load('contract_evidence_lifecycle_study',root/'transfer_study.py','73933aa65df7c8bf16352ee7395585e5c9bd5c95c2b4cb223d561bf80904ee37')
    with s.aliases({'transfer_study':st}):binding=s.load('contract_evidence_lifecycle_binding',root/'transfer_binding.py','58809cddef515740fff4e4973ea12c2f174bd650dc6d7bd21419b54cfda5b34d')
    with s.aliases({'transfer_study':st,'transfer_binding':binding}):old=s.load('contract_evidence_lifecycle_owner',root/'owner.py','47d536a9f34bdee060d4d63f8c5f05bab4e0f86f07073193ca639191fbe4d4f4')
    return old.dependencies()
def remaining(deadline,cap):
    value=min(cap,deadline-time.time())
    if value<=0:raise TimeoutError('shared inclusive work/owned deadline')
    return value
def check_output(output):
    if output.resolve()!=s.ATTEMPT.resolve():raise ValueError('exact new attempt only')
    if output.exists():raise FileExistsError('attempt exists; no overwrite or retry')
def validate_paths(args):
    if args.output.resolve()!=(s.ATTEMPT/'rollout').resolve() or args.binding.resolve()!=(s.ATTEMPT/'service/BINDING.json').resolve() or args.endpoint.resolve()!=(s.ATTEMPT/'service/service/endpoint-original.json').resolve():raise ValueError('collector attempt-path mismatch')
    if not isinstance(args.deadline,(float,int)):raise ValueError('deadline')
def inventory(output):return [{**p.null(row,'planned_before_service'),'path':str(output/'rollout/rows'/(row['id']+'.json'))} for row in p.build()['PLAN.json']]
def collector_argv(output,deadline):
    return [str(s.NATIVE),str(s.ROOT/'collect.py'),'--binding',str(output/'service/BINDING.json'),'--endpoint',str(output/'service/service/endpoint-original.json'),'--output',str(output/'rollout'),'--deadline',str(deadline)]
def execute(output):
    started=time.time();work=started+1080;owned=started+1170;check_output(output);s.runtime();ready=s.verify()
    gpu=os.environ.get('CUDA_VISIBLE_DEVICES','')
    if not gpu or ',' in gpu:raise ValueError('MAIN assigns one GPU under MAIN lock')
    suite=dependencies();output.mkdir(parents=True,exist_ok=False);planned=inventory(output)
    if len(planned)!=24:raise ValueError('24-slot inventory')
    s.write(output/'PLANNED_NULL_ENDPOINTS.json',planned);s.write(output/'PLANNED_NULL_ACQUISITIONS.json',[dict(coordinate=r,available=False,physical_request_attempt=False) for r in p.build()['ACQUISITION_PLAN.json']])
    s.write(output/'OWNER_RUN.json',dict(identity=ready['identity'],ready_sha256=s.sha(s.ROOT/'READY.json'),started_epoch=started,work_deadline_epoch=work,owned_deadline_epoch=owned,outer_seconds=1200,cleanup_seconds=90,outer_margin_seconds=30,credential_present=True,credential_value_logged=False,gpu=gpu,no_training=True))
    def expired(_sig,_frame):raise TimeoutError('owned1170s inclusive cap or MAIN termination')
    previous={sig:signal.signal(sig,expired) for sig in (signal.SIGINT,signal.SIGTERM,signal.SIGALRM)};signal.setitimer(signal.ITIMER_REAL,remaining(owned,1170))
    stage=output/'service';stage.mkdir();active=stage;error=None;release_error=None
    try:
        suite.start_service(stage,s.binding(),time.time()+remaining(work,180))
        suite.command(stage,'diagnostic24',collector_argv(output,work),remaining(work,1080),work)
    except BaseException as caught:error=dict(type=type(caught).__name__,message=str(caught),traceback=traceback.format_exc())
    finally:
        try:suite.release_service(stage);active=None
        except BaseException as caught:release_error=dict(type=type(caught).__name__,message=str(caught))
        signal.setitimer(signal.ITIMER_REAL,0)
        for sig,handler in previous.items():signal.signal(sig,handler)
    # Dependencies may adjust sys.path; bind current native/collector explicitly.
    with s.aliases({'study':s,'protocol':p}):native=s.load('contract_evidence_owner_native',s.ROOT/'native.py',s.sha(s.ROOT/'native.py'))
    with s.aliases({'study':s,'protocol':p,'native':native}):collector=s.load('contract_evidence_owner_collector',s.ROOT/'collect.py',s.sha(s.ROOT/'collect.py'))
    for row in planned:
        path=Path(row['path'])
        if path.exists():
            actual=s.read(path);row.update(recorded=True,available=actual['available'],reward=actual['reward'],operational_success=actual['operational_success'],cause=actual.get('cause'),result_sha256=s.sha(path))
        else:row.update(recorded=False,cause='unrun_or_interrupted_retained')
    s.write(output/'COST_LEDGER.json',collector.ledger(output))
    result=dict(complete=error is None and release_error is None,error=error,release_error=release_error,readout_inventory=planned,planned=24,planned_acquisitions=2,elapsed_seconds=time.time()-started,active_unreleased_service=str(active) if active else None,no_training=True,no_retry=True,main_owns_gpu_and_lock=True,orchestrator_complete_does_not_imply_native_final=True,cost_ledger_sha256=s.sha(output/'COST_LEDGER.json'))
    s.write(output/'OWNER_TERMINAL.json',result);return result
def parse_args(argv=None):
    ap=argparse.ArgumentParser();ap.add_argument('command',choices=('verify','run'));ap.add_argument('--output',type=Path,default=s.ATTEMPT);return ap.parse_args(argv)
if __name__=='__main__':
    args=parse_args()
    if args.command=='verify':print(s.verify()['identity'])
    else:
        result=execute(args.output);print(dict(complete=result['complete'],error=result['error'],elapsed_seconds=result['elapsed_seconds']));raise SystemExit(0 if result['complete'] else 1)
