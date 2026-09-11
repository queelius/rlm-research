"""MAIN-only exact attempt; serial owned GPU phases with one inclusive clock."""
import argparse
import functools
import os
from pathlib import Path
import signal
import subprocess
import time
import traceback
import study as s
import binding as b
import protocol as p

@functools.lru_cache(maxsize=1)
def dependencies():
    old=s.original.plan.old.row
    with s.aliases({'study':old}):launcher=s.load('corrective_qualified_lifecycle_dependencies',old.ROOT/'launch.py','62d7d0049b5e3303f6e68247038290c7cde0d74e3394b4856fea0e3e138d6b46')
    suite=launcher.dependencies();_,adapter=s.runtime();adapter.install(suite);return suite

def remaining(deadline,cap):
    value=min(cap,deadline-time.time())
    if value<=0:raise TimeoutError('shared work/stage ceiling reached')
    return value

def gpu_command(suite,stage,argv,deadline):
    stage.mkdir();cap=remaining(deadline,600)
    s.write(stage/'COMMAND.json',dict(argv=argv,deadline_epoch=deadline,cap_seconds=cap,started_epoch=time.time(),gpu=os.environ['CUDA_VISIBLE_DEVICES']))
    with (stage/'process.log').open('x') as log:
        process=subprocess.Popen(argv,stdout=log,stderr=subprocess.STDOUT,start_new_session=True,env={**os.environ,'PYTHONDONTWRITEBYTECODE':'1'})
        observed=suite.life.observe(process.pid)
        if observed is None:
            process.wait(timeout=5)
            s.write(stage/'EXIT.json',dict(returncode=process.returncode,ended_epoch=time.time(),already_exited=True))
            raise RuntimeError('training/gate process exited before owner observation')
        owner=suite.life.safe_observation(observed);s.write(stage/'PROCESS.json',owner)
        try:
            if process.wait(timeout=cap):raise RuntimeError('gate/training nonzero; no retry or checkpoint substitution')
        finally:
            suite.stop_child(process,owner);s.write(stage/'EXIT.json',dict(returncode=process.returncode,ended_epoch=time.time()))

def execute(output):
    # No output/owned process can exist before private credential and exact input checks.
    s.runtime();ready=s.verify()
    if output.resolve()!=s.ATTEMPT.resolve() or output.exists():raise ValueError('exact fresh attempt only; no overwrite/retry')
    gpu=os.environ.get('CUDA_VISIBLE_DEVICES','')
    if not gpu or ',' in gpu:raise ValueError('MAIN must assign one GPU under MAIN lock')
    suite=dependencies();started=time.time();work=started+6900;owned=started+7080
    output.mkdir(parents=True,exist_ok=False)
    s.write(output/'OWNER_RUN.json',dict(identity=ready['identity'],ready_sha256=s.sha(s.ROOT/'READY.json'),started_epoch=started,work_deadline_epoch=work,owned_deadline_epoch=owned,outer_seconds=7200,gpu=gpu,training_order=s.order(),phase_order=s.phases(),credential_present=True,credential_value_logged=False))
    def expired(_sig,_frame):raise TimeoutError('owned7080s inclusive cap or MAIN termination')
    previous={sig:signal.signal(sig,expired) for sig in (signal.SIGINT,signal.SIGTERM,signal.SIGALRM)}
    signal.setitimer(signal.ITIMER_REAL,remaining(owned,7080))
    stages=[];error=None;release_errors=[];budgets={'capture':1800.,'readiness':900.};active=None
    def service(name,arm,body):
        nonlocal active
        stage=output/name;stage.mkdir();active=stage
        try:
            begin=time.time()
            try:suite.start_service(stage,b.binding(arm,b.selected(arm)),time.time()+remaining(work,min(180,budgets['readiness'])))
            finally:budgets['readiness']-=time.time()-begin
            body(stage)
        finally:
            try:suite.release_service(stage);active=None
            except BaseException as caught:
                release_errors.append(dict(stage=str(stage),type=type(caught).__name__,message=str(caught)));raise
    def collect(stage,label,mode,plan,start,stop,destination,cap):
        deadline=time.time()+remaining(work,cap)
        argv=[str(s.NATIVE),str(s.ROOT/'collect.py'),'--mode',mode,'--plan',plan,'--start',str(start),'--stop',str(stop),'--binding',str(stage/'BINDING.json'),'--endpoint',str(stage/'service/endpoint-original.json'),'--output',str(destination),'--deadline',str(deadline)]
        suite.command(stage,label,argv,remaining(deadline,cap),deadline)
        stages.append(dict(stage=label,complete=True,output=str(destination)))
    def capture(stage,label,plan,start,stop,destination):
        begin=time.time()
        try:collect(stage,label,'capture',plan,start,stop,destination,budgets['capture'])
        finally:budgets['capture']-=time.time()-begin
    try:
        service('teacher-first8','unchanged',lambda stage:capture(stage,'capture-first8','TRAIN_PLAN.json',0,8,output/'capture'))
        deadline=time.time()+remaining(work,300)
        gpu_command(suite,output/'gate-stage',[str(s.TRAIN),str(s.ROOT/'train.py'),'--mode','gate','--output',str(output/'gate'),'--deadline',str(deadline)],deadline)
        gate=s.read(output/'gate/RESULT.json');stages.append(dict(stage='first8_objective_cost_gate',result=gate))
        if not gate['pass_gate']:raise ValueError('predeclared objective/cost gate failed; no large capture/training')
        required=sum(gate['projected_training_seconds_per_arm'].values())+budgets['capture']+2250+max(0,budgets['readiness'])
        if required>work-time.time():raise TimeoutError('measured gate projection exceeds remaining shared envelope')
        def rest(stage):
            capture(stage,'capture-rest24','TRAIN_PLAN.json',8,32,output/'capture');s.corpus()
            capture(stage,'capture-controlled-source','CONTROLLED_PLAN.json',0,16,output/'controlled-source')
            records=[s.read(p) for p in (output/'controlled-source').glob('*/physical/*.json')]
            paid=[r for r in records if r['paid_model_call']]
            s.write(output/'CONTROLLED_SHARED_COST.json',dict(shared_actual_cost=p.physical_cost(records),shared_actual_acquisition_calls=len(paid),hypothetical_standalone_acquisition_calls_each_policy=len(paid),hypothetical_all_three_calls=3*len(paid),physical_saved_by_sharing=2*len(paid),origin='actual heldout c32 acquisition once; transport replays are NOT additional model calls',elapsed_source_seconds=sum(s.read(path)['elapsed_seconds'] for path in (output/'controlled-source').glob('*/TEACHER.json')),physical_paths=[str(path) for path in (output/'controlled-source').glob('*/physical/*.json')]))
        service('teacher-rest','unchanged',rest)
        for arm in s.order():
            deadline=time.time()+remaining(work,600)
            gpu_command(suite,output/('train-stage-'+arm),[str(s.TRAIN),str(s.ROOT/'train.py'),'--mode','train','--arm',arm,'--output',str(b.training_source(arm)),'--deadline',str(deadline)],deadline)
            b.selected(arm);stages.append(dict(stage='training',arm=arm,complete=True))
        for arm in s.phases():
            def readouts(stage,arm=arm):
                collect(stage,'free','free','FREE_PLAN.json',0,32,output/arm/'free',450)
                collect(stage,'controlled','controlled','CONTROLLED_PLAN.json',0,16,output/arm/'controlled',300)
            service('service-'+arm,arm,readouts)
    except BaseException as caught:error=dict(type=type(caught).__name__,message=str(caught),traceback=traceback.format_exc())
    finally:
        # release_service was already attempted exactly at its owned boundary, even on error.
        signal.setitimer(signal.ITIMER_REAL,0)
        for sig,handler in previous.items():signal.signal(sig,handler)
    inventory=[]
    for arm in ('unchanged',*s.ARMS):
        for mode,plan in (('free','FREE_PLAN.json'),('controlled','CONTROLLED_PLAN.json')):
            for row in s.read(s.ROOT/'inputs'/plan):
                path=output/arm/mode/row['id']/'RESULT.json'
                inventory.append(dict(arm=arm,mode=mode,coordinate_id=row['id'],path=str(path),recorded=path.exists(),reward=s.read(path)['reward'] if path.exists() else None))
    result=dict(complete=error is None and not release_errors,error=error,release_errors=release_errors,stages=stages,readout_inventory=inventory,planned_free=96,planned_controlled=48,elapsed_seconds=time.time()-started,remaining_stage_budgets=budgets,no_retry=True,main_owns_gpu_and_lock=True,unrun_primary_reward=None,active_unreleased_service=str(active) if active else None)
    s.write(output/'OWNER_TERMINAL.json',result);return result

if __name__=='__main__':
    ap=argparse.ArgumentParser();ap.add_argument('command',choices=('verify','run'));ap.add_argument('--output',type=Path,default=s.ATTEMPT);args=ap.parse_args()
    if args.command=='verify':print(s.verify()['identity'])
    else:
        result=execute(args.output);print(dict(complete=result['complete'],error=result['error'],elapsed_seconds=result['elapsed_seconds']));raise SystemExit(0 if result['complete'] else 1)
