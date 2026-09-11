"""MAIN-only exact attempt, all84 slots planned before launch, one inclusive5400 clock."""
import argparse
import functools
import os
from pathlib import Path
import signal
import subprocess
import time
import traceback
import joint_study as s
import joint_binding as b
import joint_protocol as p

@functools.lru_cache(maxsize=1)
def dependencies():
    old=s.original.plan.old.row
    with s.aliases({'study':old}):launcher=s.load('joint_qualified_owner_dependencies',old.ROOT/'launch.py','62d7d0049b5e3303f6e68247038290c7cde0d74e3394b4856fea0e3e138d6b46')
    suite=launcher.dependencies();_,adapter=s.runtime();adapter.install(suite);return suite

def remaining(deadline,cap):
    value=min(cap,deadline-time.time())
    if value<=0:raise TimeoutError('shared work/stage deadline')
    return value

def check_output(output):
    if output.resolve()!=s.ATTEMPT.resolve():raise ValueError('exact new attempt only')
    if output.exists():raise FileExistsError('attempt exists; no retry/overwrite')

def collector_argv(stage,destination,deadline,mode,plan,start,stop):
    return [str(s.NATIVE),str(s.ROOT/'collect.py'),'--mode',mode,'--plan',plan,'--start',str(start),'--stop',str(stop),'--binding',str(stage/'BINDING.json'),'--endpoint',str(stage/'service/endpoint-original.json'),'--output',str(destination),'--deadline',str(deadline)]

def planned_inventory(output):
    return [dict(arm=arm,mode=mode,coordinate=row,path=str(output/arm/mode/row['id']/'RESULT.json'),available=False,reward=None,reason='planned before any service launch')
        for arm in ('unchanged',*s.ARMS) for mode,plan in (('free','FREE_PLAN.json'),('controlled','CONTROLLED_PLAN.json'),('training_diagnostic','DIAGNOSTIC_PLAN.json')) for row in s.read(s.ROOT/'inputs'/plan)]

def gpu_command(suite,stage,argv,deadline):
    stage.mkdir();cap=remaining(deadline,600)
    s.write(stage/'COMMAND.json',dict(argv=argv,deadline_epoch=deadline,cap_seconds=cap,started_epoch=time.time(),gpu=os.environ['CUDA_VISIBLE_DEVICES']))
    with (stage/'process.log').open('x') as log:
        process=subprocess.Popen(argv,stdout=log,stderr=subprocess.STDOUT,start_new_session=True,env={**os.environ,'PYTHONDONTWRITEBYTECODE':'1'})
        observed=suite.life.observe(process.pid)
        if observed is None:
            process.wait(timeout=5);s.write(stage/'EXIT.json',dict(returncode=process.returncode,already_exited=True,ended_epoch=time.time()))
            raise RuntimeError('gate/train exited before owner observation')
        owner=suite.life.safe_observation(observed);s.write(stage/'PROCESS.json',owner)
        try:
            if process.wait(timeout=cap):raise RuntimeError('gate/train nonzero; no retry')
        finally:suite.stop_child(process,owner);s.write(stage/'EXIT.json',dict(returncode=process.returncode,ended_epoch=time.time()))

def execute(output):
    started=time.time();work=started+5100;owned=started+5280
    check_output(output);s.runtime();ready=s.verify()
    gpu=os.environ.get('CUDA_VISIBLE_DEVICES','')
    if not gpu or ',' in gpu:raise ValueError('MAIN assigns one GPU under MAIN lock')
    suite=dependencies();output.mkdir(parents=True,exist_ok=False)
    inventory=planned_inventory(output)
    if len(inventory)!=84:raise ValueError('exact84 inventory')
    s.write(output/'PLANNED_NULL_ENDPOINTS.json',inventory)
    s.write(output/'OWNER_RUN.json',dict(identity=ready['identity'],ready_sha256=s.sha(s.ROOT/'READY.json'),started_epoch=started,work_deadline_epoch=work,owned_deadline_epoch=owned,outer_seconds=5400,cleanup_reserve_seconds=180,outer_margin_seconds=120,gpu=gpu,training_order=s.order(),phase_order=s.phases(),credential_present=True,credential_value_logged=False))
    def expired(_sig,_frame):raise TimeoutError('owned5280s inclusive cap or MAIN termination')
    previous={sig:signal.signal(sig,expired) for sig in (signal.SIGINT,signal.SIGTERM,signal.SIGALRM)}
    signal.setitimer(signal.ITIMER_REAL,remaining(owned,5280))
    stages=[];error=None;release_errors=[];active=None;capture_budget=900.
    def collect(stage,label,mode,plan,destination,stop,cap):
        deadline=time.time()+remaining(work,cap)
        suite.command(stage,label,collector_argv(stage,destination,deadline,mode,plan,0,stop),remaining(deadline,cap),deadline)
        stages.append(dict(stage=label,complete=True,output=str(destination)))
    def service(name,arm,body):
        nonlocal active
        stage=output/name;stage.mkdir();active=stage
        try:
            suite.start_service(stage,b.binding(arm,b.selected(arm)),time.time()+remaining(work,180));body(stage)
        finally:
            try:suite.release_service(stage);active=None
            except BaseException as caught:release_errors.append(dict(stage=str(stage),type=type(caught).__name__,message=str(caught)));raise
    def capture(stage):
        nonlocal capture_budget
        for label,plan,destination,stop in (('capture16','TRAIN_PLAN.json',output/'capture',16),('controlled-source8','CONTROLLED_PLAN.json',output/'controlled-source',8)):
            before=time.time()
            try:collect(stage,label,'capture',plan,destination,stop,capture_budget)
            finally:capture_budget-=time.time()-before
        s.corpus()
        records=[s.read(path) for path in (output/'controlled-source').glob('*/physical/*.json')]
        paths=list((output/'controlled-source').glob('*/physical/*.json'));cost=p.physical_cost(records)
        s.write(output/'CONTROLLED_SHARED_COST.json',dict(shared_actual_cost=cost,hypothetical_standalone_calls_all_three=3*cost['calls'],origin='actual heldout acquisitions once; exact transport replay is not a new model call',source_physical_sha256={str(path):s.sha(path) for path in paths},elapsed_source_seconds=sum(s.read(path)['elapsed_seconds'] for path in (output/'controlled-source').glob('*/TEACHER.json'))))
    try:
        service('teacher-service','unchanged',capture)
        deadline=time.time()+remaining(work,180)
        gpu_command(suite,output/'gate-stage',[str(s.TRAIN),str(s.ROOT/'train.py'),'--mode','gate','--output',str(output/'gate'),'--deadline',str(deadline)],deadline)
        gate=s.read(output/'gate/RESULT.json');stages.append(dict(stage='fixed4_forward_gate',result=gate))
        if not gate['pass_gate']:raise ValueError('predeclared objective/cost gate stop; no gradient')
        if sum(gate['projected_training_seconds_per_arm'].values())+2520+540>work-time.time():raise TimeoutError('measured gate projection leaves insufficient shared readout envelope')
        training_deadline=min(work,time.time()+1200)
        for arm in s.order():
            deadline=time.time()+remaining(training_deadline,600)
            gpu_command(suite,output/('train-stage-'+arm),[str(s.TRAIN),str(s.ROOT/'train.py'),'--mode','train','--arm',arm,'--output',str(b.training_source(arm)),'--deadline',str(deadline)],deadline)
            b.selected(arm);stages.append(dict(stage='training',arm=arm,complete=True))
        for arm in s.phases():
            def readouts(stage,arm=arm):
                collect(stage,'free','free','FREE_PLAN.json',output/arm/'free',16,480)
                collect(stage,'controlled','controlled','CONTROLLED_PLAN.json',output/arm/'controlled',8,240)
                collect(stage,'training-diagnostic','controlled','DIAGNOSTIC_PLAN.json',output/arm/'training_diagnostic',4,120)
            service('service-'+arm,arm,readouts)
    except BaseException as caught:error=dict(type=type(caught).__name__,message=str(caught),traceback=traceback.format_exc())
    finally:
        signal.setitimer(signal.ITIMER_REAL,0)
        for sig,handler in previous.items():signal.signal(sig,handler)
    for row in inventory:
        path=Path(row['path'])
        if path.exists():
            actual=s.read(path);row.update(recorded=True,available=actual['available'],reward=actual['reward'],reason=actual.get('reason'),result_sha256=s.sha(path))
        else:row.update(recorded=False,reason='unrun/incomplete; retained phase/episode failures')
    result=dict(complete=error is None and not release_errors,error=error,release_errors=release_errors,stages=stages,readout_inventory=inventory,planned=84,heldout=72,training_diagnostic=12,elapsed_seconds=time.time()-started,work_deadline_epoch=work,owned_deadline_epoch=owned,outer_seconds=5400,no_retry=True,main_owns_gpu_and_lock=True,active_unreleased_service=str(active) if active else None,orchestrator_complete_does_not_imply_model_final=True)
    s.write(output/'OWNER_TERMINAL.json',result);return result

def parse_args(argv=None):
    ap=argparse.ArgumentParser();ap.add_argument('command',choices=('verify','run'));ap.add_argument('--output',type=Path,default=s.ATTEMPT);return ap.parse_args(argv)

if __name__=='__main__':
    args=parse_args()
    if args.command=='verify':print(s.verify()['identity'])
    else:
        result=execute(args.output);print(dict(complete=result['complete'],error=result['error'],elapsed_seconds=result['elapsed_seconds']));raise SystemExit(0 if result['complete'] else 1)
