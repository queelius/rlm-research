"""MAIN-only three fixed phases, inclusive1800s envelope; no policy training/retry."""
import argparse
import functools
import os
from pathlib import Path
import signal
import time
import traceback
import study as s
import protocol as p
class MainTermination(BaseException):pass
@functools.lru_cache(maxsize=1)
def dependencies():
    root=s.SIDE/'root-fixed-policy-transfer-v1'
    st=s.load('warm_reference_lifecycle_study',root/'transfer_study.py','73933aa65df7c8bf16352ee7395585e5c9bd5c95c2b4cb223d561bf80904ee37')
    with s.aliases({'transfer_study':st}):binding=s.load('warm_reference_lifecycle_binding',root/'transfer_binding.py','58809cddef515740fff4e4973ea12c2f174bd650dc6d7bd21419b54cfda5b34d')
    with s.aliases({'transfer_study':st,'transfer_binding':binding}):old=s.load('warm_reference_lifecycle_owner',root/'owner.py','47d536a9f34bdee060d4d63f8c5f05bab4e0f86f07073193ca639191fbe4d4f4')
    return old.dependencies()
def remaining(deadline,cap):
    value=min(cap,deadline-time.time())
    if value<=0:raise TimeoutError('shared inclusive deadline')
    return value
def phase_deadlines(start,work):return dict(phase=min(start+480,work),startup=min(start+180,work))
def collection_deadline(now,phase,work):return min(now+300,phase,work)
def alarm(deadline):signal.setitimer(signal.ITIMER_REAL,max(.001,deadline-time.time()))
def check_output(output):
    if output.resolve()!=s.ATTEMPT.resolve():raise ValueError('exact new attempt only')
    if output.exists():raise FileExistsError('attempt preserved; no reroll')
def validate_paths(args):
    if args.root not in s.ROOTS:raise ValueError('unknown fixed root')
    phase=s.ATTEMPT/args.root
    if args.output.resolve()!=(phase/'rollout').resolve() or args.binding.resolve()!=(phase/'service/BINDING.json').resolve() or args.endpoint.resolve()!=(phase/'service/service/endpoint-original.json').resolve():raise ValueError('collector attempt-path mismatch')
    if not isinstance(args.deadline,(float,int)):raise ValueError('deadline')
def inventory(output):return [{**p.null(row,'planned_before_service'),'path':str(output/row['root']/'rollout/rows'/(row['id']+'.json'))} for row in p.build()['PLAN.json']]
def collector_argv(output,arm,deadline):
    phase=output/arm
    return [str(s.NATIVE),str(s.ROOT/'collect.py'),'--root',arm,'--binding',str(phase/'service/BINDING.json'),'--endpoint',str(phase/'service/service/endpoint-original.json'),'--output',str(phase/'rollout'),'--deadline',str(deadline)]
def execute(output):
    started=time.time();work=started+1650;owned=started+1770;check_output(output);s.runtime();ready=s.verify()
    gpu=os.environ.get('CUDA_VISIBLE_DEVICES','')
    if not gpu or ',' in gpu:raise ValueError('MAIN assigns one GPU')
    suite=dependencies();output.mkdir(parents=True,exist_ok=False);planned=inventory(output)
    s.write(output/'PLANNED_NULL_ENDPOINTS.json',planned)
    s.write(output/'OWNER_RUN.json',dict(identity=ready['identity'],ready_sha256=s.sha(s.ROOT/'READY.json'),started_epoch=started,work_deadline_epoch=work,owned_deadline_epoch=owned,outer_seconds=1800,cleanup_seconds=120,outer_margin_seconds=30,phase_inclusive_startup_collection_seconds=480,startup_seconds=180,collection_seconds=300,each_release_seconds=90,nominal_three_phase_plus_release_seconds=1710,phase_order=p.phase_order(),credential_present=True,credential_value_logged=False,gpu=gpu,no_training=True))
    def expired(sig,_frame):
        if sig in (signal.SIGINT,signal.SIGTERM):raise MainTermination('MAIN termination; no later phases')
        raise TimeoutError('active phase/release/owned deadline')
    previous={sig:signal.signal(sig,expired) for sig in (signal.SIGINT,signal.SIGTERM,signal.SIGALRM)};alarm(owned)
    active=None;phases=[];errors=[];terminate=False
    try:
        for arm in p.phase_order():
            if terminate or time.time()>=work:break
            limits=phase_deadlines(time.time(),work);phase=output/arm;phase.mkdir();stage=phase/'service';stage.mkdir();active=stage
            status=dict(root=arm,started_epoch=time.time(),phase_deadline=limits['phase'],startup_deadline=limits['startup'],error=None,release_error=None)
            try:
                alarm(limits['startup']);suite.start_service(stage,s.binding(arm),limits['startup'])
                end=collection_deadline(time.time(),limits['phase'],work);status['collection_deadline']=end;alarm(end)
                suite.command(stage,'warm-reference-'+arm,collector_argv(output,arm,end),remaining(end,300),end)
            except BaseException as caught:
                status['error']=dict(type=type(caught).__name__,message=str(caught),traceback=traceback.format_exc());errors.append(dict(root=arm,**status['error']))
                if isinstance(caught,MainTermination) or not isinstance(caught,Exception):terminate=True
            finally:
                release_end=min(owned,time.time()+90);status['release_deadline']=release_end;alarm(release_end)
                try:suite.release_service(stage);active=None
                except BaseException as caught:
                    status['release_error']=dict(type=type(caught).__name__,message=str(caught));errors.append(dict(root=arm,release_failed=True,**status['release_error']));terminate=True
                status['ended_epoch']=time.time();s.write(phase/'PHASE_TERMINAL.json',status);phases.append(status);alarm(owned)
            if active is not None:break
    finally:
        # A failed bounded release is not retried or hidden; MAIN sees active ownership.
        with s.aliases({'study':s,'protocol':p}):native=s.load('warm_reference_owner_native',s.ROOT/'native.py',s.sha(s.ROOT/'native.py'))
        with s.aliases({'study':s,'protocol':p,'native':native}):collector=s.load('warm_reference_owner_collector',s.ROOT/'collect.py',s.sha(s.ROOT/'collect.py'))
        for row in planned:
            path=Path(row['path'])
            if path.exists():
                actual=s.read(path);row.update(recorded=True,available=actual['available'],reward=actual['reward'],operational_success=actual['operational_success'],cause=actual.get('cause'),result_sha256=s.sha(path))
            else:row.update(recorded=False,cause='unrun_or_interrupted_retained')
        s.write(output/'COST_LEDGER.json',collector.ledger(output))
        result=dict(complete=not errors and len(phases)==3 and all(r.get('recorded') for r in planned),errors=errors,phases=phases,readout_inventory=planned,planned=24,elapsed_seconds=time.time()-started,active_unreleased_service=str(active) if active else None,no_training=True,no_retry=True,main_owns_gpu_and_lock=True,orchestrator_complete_does_not_imply_native_final=True,cost_ledger_sha256=s.sha(output/'COST_LEDGER.json'))
        s.write(output/'OWNER_TERMINAL.json',result)
        signal.setitimer(signal.ITIMER_REAL,0)
        for sig,handler in previous.items():signal.signal(sig,handler)
    return result
def parse_args(argv=None):
    ap=argparse.ArgumentParser();ap.add_argument('command',choices=('verify','run'));ap.add_argument('--output',type=Path,default=s.ATTEMPT);return ap.parse_args(argv)
if __name__=='__main__':
    args=parse_args()
    if args.command=='verify':print(s.verify()['identity'])
    else:
        result=execute(args.output);print(dict(complete=result['complete'],errors=result['errors'],elapsed_seconds=result['elapsed_seconds']));raise SystemExit(0 if result['complete'] else 1)
