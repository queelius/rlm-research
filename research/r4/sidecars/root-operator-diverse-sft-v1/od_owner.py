"""MAIN-only exact attempt; stage caps advance early and protect both final policies."""
import argparse
import functools
import os
from pathlib import Path
import signal
import time
import traceback
import od_study as s
import od_binding as b
import od_protocol as p
class MainTermination(BaseException):pass

@functools.lru_cache(maxsize=1)
def dependencies():
    j=s.joint();old=j.original.plan.old.row
    launcher=s.load('od_qualified_owner_dependencies',old.ROOT/'launch.py','62d7d0049b5e3303f6e68247038290c7cde0d74e3394b4856fea0e3e138d6b46',{'study':old})
    suite=launcher.dependencies();_,adapter=s.runtime();adapter.install(suite);return suite

def remaining(deadline):
    value=deadline-time.time()
    if value<=0:raise TimeoutError('stage/shared cap exhausted')
    return value
def stage_end(name,now,work):
    cap,reserve={'capture':(1800,6300),'training':(3600,2700),'unchanged':(1200,1500),'sft6':(1200,300)}[name]
    return min(now+cap,work-reserve)
def alarm(deadline):signal.setitimer(signal.ITIMER_REAL,max(.001,deadline-time.time()))
def check_output(output):
    if output.resolve()!=s.ATTEMPT.resolve():raise ValueError('exact owned new attempt only')
    if output.exists():raise FileExistsError('no retry, overwrite, or partial-corpus continuation')
def inventory(output):
    return [dict(arm=arm,coordinate=row,path=str(output/arm/'free'/row['id']/'RESULT.json'),reward=None,available=False,reason='planned before any service') for arm in ('unchanged','sft6') for row in s.read(s.ROOT/'inputs/FREE_PLAN.json')]
def collector_argv(stage,destination,deadline,mode,plan,stop):
    return [str(s.NATIVE),str(s.ROOT/'od_collect.py'),'--mode',mode,'--plan',plan,'--start','0','--stop',str(stop),'--binding',str(stage/'BINDING.json'),'--endpoint',str(stage/'service/endpoint-original.json'),'--output',str(destination),'--deadline',str(deadline)]
def error(caught):return dict(type=type(caught).__name__,message=str(caught),traceback=traceback.format_exc())
def ledger(output):
    paths=sorted(output.glob('**/physical/*.json'));records=[s.read(path) for path in paths]
    attempted=[r for r in records if r.get('physical_request_attempt')]
    return dict(physical_requests_attempted=len(attempted),physical_responses_returned=sum(isinstance(r.get('response'),dict) for r in attempted),
        authored_transport_calls=sum(r.get('origin','').startswith('authored') for r in records),physical_usage=p.physical_cost(attempted),
        billing_unknown=True,record_sha256={str(path):s.sha(path) for path in paths})

def execute(output):
    started=time.time();work=started+8100;owned=started+8280;check_output(output);s.runtime();ready=s.verify()
    gpu=os.environ.get('CUDA_VISIBLE_DEVICES','')
    if not gpu or ',' in gpu:raise ValueError('MAIN assigns exactly one GPU')
    if not os.environ.get('STRICT_RLM_CALIBRATION_API_KEY'):raise ValueError('private credential preflight failed')
    suite=dependencies();output.mkdir(parents=True,exist_ok=False);planned=inventory(output)
    s.write(output/'PLANNED_NULL_ENDPOINTS.json',planned);s.write(output/'PLANNED_CAPTURE_SLOTS.json',[dict(coordinate=r,teacher=None,reason='planned before any service') for r in s.read(s.ROOT/'inputs/TRAIN_PLAN.json')])
    s.write(output/'OWNER_RUN.json',dict(identity=ready['identity'],ready_sha256=s.sha(s.ROOT/'READY_v2.json'),started_epoch=started,work_deadline_epoch=work,owned_deadline_epoch=owned,outer_seconds=8400,cleanup_reserve_seconds=180,outer_margin_seconds=120,stage_caps=dict(capture=1800,training=3600,unchanged=1200,sft6=1200,finalize=300),caps_not_waits=True,phase_order=['unchanged','sft6'],credential_present=True,credential_value_logged=False,gpu=gpu,starting=s.starting_policy()))
    def expired(sig,_frame):
        if sig in (signal.SIGINT,signal.SIGTERM):raise MainTermination('MAIN termination, no later stages')
        raise TimeoutError('active stage/owned deadline')
    previous={sig:signal.signal(sig,expired) for sig in (signal.SIGINT,signal.SIGTERM,signal.SIGALRM)};alarm(owned)
    active=None;stages=[];errors=[];terminate=False;capture_ok=False
    def service(name,arm,deadline,body):
        nonlocal active,terminate
        stage=output/name;stage.mkdir();active=stage;status=dict(stage=name,started_epoch=time.time(),deadline_epoch=deadline)
        try:
            # 90 seconds belongs to this stage for release, not added to its work cap.
            startup=min(time.time()+180,deadline-90);remaining(startup);alarm(startup)
            suite.start_service(stage,b.binding(arm),startup)
            collection=deadline-90;remaining(collection);alarm(collection);body(stage,collection);status['work_complete']=True
        except BaseException as caught:
            status['error']=error(caught);errors.append(dict(stage=name,**status['error']))
            if isinstance(caught,MainTermination) or not isinstance(caught,Exception):terminate=True
        finally:
            release=min(owned,time.time()+90,deadline if time.time()<deadline else owned);alarm(release)
            try:suite.release_service(stage);active=None
            except BaseException as caught:status['release_error']=error(caught);errors.append(dict(stage=name,release_failed=True,**status['release_error']));terminate=True
            status['ended_epoch']=time.time();s.write(stage/'PHASE_TERMINAL.json',status);stages.append(status);alarm(owned)
        return status.get('work_complete',False) and active is None
    try:
        def capture(stage,deadline):
            suite.command(stage,'capture72',collector_argv(stage,output/'capture',deadline,'capture','TRAIN_PLAN.json',72),remaining(deadline),deadline);s.corpus()
        capture_ok=service('teacher-service','unchanged',stage_end('capture',time.time(),work),capture)
        if capture_ok and not terminate:
            deadline=stage_end('training',time.time(),work);stage=output/'train-stage';stage.mkdir();status=dict(stage='training',started_epoch=time.time(),deadline_epoch=deadline)
            try:
                remaining(deadline);alarm(deadline)
                argv=[str(s.TRAIN),str(s.ROOT/'od_train.py'),'--mode','train','--output',str(output/'training'),'--deadline',str(deadline)]
                suite.command(stage,'gate-and-six-updates',argv,remaining(deadline),deadline)
                b.selected('sft6');status['work_complete']=True
            except BaseException as caught:
                status['error']=error(caught);errors.append(dict(stage='training',**status['error']))
                if isinstance(caught,MainTermination) or not isinstance(caught,Exception):terminate=True
            finally:status['ended_epoch']=time.time();s.write(stage/'PHASE_TERMINAL.json',status);stages.append(status);alarm(owned)
        # Ordinary capture/gate/learning failure cannot bypass the baseline or fixed6 availability check.
        for arm in ('unchanged','sft6'):
            if terminate or active is not None:break
            try:b.selected(arm)
            except Exception as caught:
                errors.append(dict(stage=arm,planned_treatment_unavailable=True,**error(caught)));continue
            def readout(stage,deadline,arm=arm):
                suite.command(stage,'free24-'+arm,collector_argv(stage,output/arm/'free',deadline,'free','FREE_PLAN.json',24),remaining(deadline),deadline)
            service('service-'+arm,arm,stage_end(arm,time.time(),work),readout)
    finally:
        alarm(min(owned,work))
        for row in planned:
            path=Path(row['path'])
            if path.exists():
                result=s.read(path);row.update(recorded=True,available=result['available'],reward=result['reward'],reason=result.get('reason'),result_sha256=s.sha(path))
            else:row.update(recorded=False,reason='unrun/incomplete or missing fixed SFT6; retained original failures')
        s.write(output/'COST_LEDGER.json',ledger(output))
        result=dict(complete=not errors and all(r.get('recorded') for r in planned),errors=errors,stages=stages,readout_inventory=planned,planned=48,capture_complete=capture_ok,elapsed_seconds=time.time()-started,active_unreleased_service=str(active) if active else None,orchestrator_complete_does_not_imply_native_final=True,no_retry=True,no_partial_sft6_substitution=True,main_owns_gpu_and_lock=True,cost_ledger_sha256=s.sha(output/'COST_LEDGER.json'))
        s.write(output/'OWNER_TERMINAL.json',result);signal.setitimer(signal.ITIMER_REAL,0)
        for sig,handler in previous.items():signal.signal(sig,handler)
    return result

def parse_args(argv=None):
    ap=argparse.ArgumentParser();ap.add_argument('command',choices=('verify','run'));ap.add_argument('--output',type=Path,default=s.ATTEMPT);return ap.parse_args(argv)
if __name__=='__main__':
    args=parse_args()
    if args.command=='verify':print(s.verify()['identity'])
    else:
        result=execute(args.output);print(dict(complete=result['complete'],errors=result['errors'],elapsed_seconds=result['elapsed_seconds']));raise SystemExit(0 if result['complete'] else 1)
