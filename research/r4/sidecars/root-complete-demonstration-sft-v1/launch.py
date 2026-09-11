"""One owned serial capture→two trainings→three readouts, shared absolute budget."""
import argparse
import os
import signal
import subprocess
import time
import traceback
from pathlib import Path
import study as s
import binding as b

old=s.plan.private('launch.py',view=s.plan.old,extra={'binding':b})
dependencies=old.dependencies
remaining=old.remaining

def execute(output):
    started=time.time();ready=s.verify()
    if output.resolve()!=s.ROOT/'outputs/attempt-001':raise ValueError('exact new attempt only')
    gpu=os.environ.get('CUDA_VISIBLE_DEVICES','')
    if not gpu or ',' in gpu:raise ValueError('MAIN assigns one GPU')
    output.mkdir(parents=True,exist_ok=False);work=started+3450;deadline=started+3570
    s.write(output/'RUN.json',dict(identity=ready['identity'],ready_sha256=s.sha(s.ROOT/'READY.json'),started_epoch=started,work_deadline_epoch=work,deadline_epoch=deadline,gpu=gpu,training_order=s.training_order(),phase_order=s.phase_order(),planned=48))
    def expired(_sig,_frame):raise TimeoutError('owned3570s inclcleanup / MAIN termination')
    for sig in (signal.SIGINT,signal.SIGTERM,signal.SIGALRM):signal.signal(sig,expired)
    signal.setitimer(signal.ITIMER_REAL,remaining(deadline,3570));stages=[];error=None
    try:
        suite=dependencies();capture=output/'teacher-service';capture.mkdir()
        try:
            suite.start_service(capture,b.binding('unchanged',b.selected('unchanged')),time.time()+remaining(work,180))
            argv=[str(s.NATIVE),str(s.ROOT/'capture.py'),'--binding',str(capture/'BINDING.json'),'--endpoint',str(capture/'service/endpoint-original.json'),'--output',str(output/'capture'),'--deadline',str(time.time()+remaining(work,1080))]
            suite.command(capture,'capture',argv,1110,work)
            s.captured();stages.append(dict(stage='actual_child_capture',complete=True))
        finally:suite.release_service(capture)
        for arm in s.training_order():
            stage=output/('train-stage-'+arm);stage.mkdir()
            argv=[str(s.TRAIN),str(s.ROOT/'train.py'),'--arm',arm,'--output',str(b.training_source(arm))]
            cap=remaining(work,510)
            s.write(stage/'COMMAND.json',dict(argv=argv,cap_seconds=cap,started_epoch=time.time(),gpu=gpu))
            with (stage/'training.log').open('x') as log:
                process=subprocess.Popen(argv,stdout=log,stderr=subprocess.STDOUT,start_new_session=True,env={**os.environ,'PYTHONDONTWRITEBYTECODE':'1'})
                observed=suite.life.observe(process.pid)
                if observed is None:raise RuntimeError('owned training identity unavailable')
                owner=suite.life.safe_observation(observed);s.write(stage/'PROCESS.json',owner)
                try:
                    if process.wait(timeout=cap):raise RuntimeError('training nonzero; no checkpoint substitution')
                finally:suite.stop_child(process,owner);s.write(stage/'EXIT.json',dict(returncode=process.returncode,ended_epoch=time.time()))
            b.selected(arm);stages.append(dict(stage='training',arm=arm,complete=True))
        for arm in s.phase_order():
            stage=output/arm;stage.mkdir()
            try:
                suite.start_service(stage,b.binding(arm,b.selected(arm)),time.time()+remaining(work,180))
                argv=[str(s.NATIVE),str(s.ROOT/'readout.py'),'--weight',arm,'--training',str(b.training_source(arm)),'--binding',str(stage/'BINDING.json'),'--endpoint',str(stage/'service/endpoint-original.json'),'--output',str(stage/'rollout'),'--deadline',str(time.time()+remaining(work,420))]
                suite.command(stage,'collect',argv,450,work)
                terminal=s.read(stage/'rollout/TERMINAL.json')
                if terminal['planned']!=16 or terminal['recorded']!=16 or not terminal['complete']:raise ValueError('partial16; preserve nulls')
                stages.append(dict(stage='readout',arm=arm,terminal=terminal))
            finally:suite.release_service(stage)
    except BaseException as caught:error=dict(type=type(caught).__name__,message=str(caught),traceback=traceback.format_exc())
    finally:signal.setitimer(signal.ITIMER_REAL,0)
    result=dict(complete=error is None,error=error,stages=stages,planned=48,elapsed_seconds=time.time()-started,
      null_accounting='all48 predeclared; missing/infrastructure/unrun NULL; completed empty/malformed0',no_reroll=True)
    plan=s.read(s.ROOT/'prepared/EVAL_PLAN_FINAL.json')
    result['readout_inventory']=[dict(arm=arm,coordinate_id=row['id'],row_path=str(output/arm/'rollout/rows'/(row['id']+'.json')),
      recorded=(output/arm/'rollout/rows'/(row['id']+'.json')).exists(),unrecorded_primary=None) for arm in s.phase_order() for row in plan]
    s.write(output/'TERMINAL.json',result);return result

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('command',choices=('verify','run'));p.add_argument('--output',type=Path,default=s.ROOT/'outputs/attempt-001');a=p.parse_args()
    if a.command=='verify':print({'identity':s.verify()['identity'],'gpu_calls':0})
    else:result=execute(a.output.resolve());print(result);raise SystemExit(0 if result['complete'] else 1)
