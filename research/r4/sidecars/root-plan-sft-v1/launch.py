"""Two authored training arms plus three native16 readouts; one owned clock."""
import argparse
import os
import signal
import subprocess
import time
import traceback
from pathlib import Path
import study as s
import binding as b

inherited=s.private('launch.py',extra={'binding':b})
dependencies=inherited.dependencies
remaining=inherited.remaining


def execute(output):
    started=time.time();ready=s.verify()
    if output!=s.ROOT/'outputs/attempt-001':raise ValueError('exact prepared attempt only')
    gpu=os.environ.get('CUDA_VISIBLE_DEVICES','')
    if not gpu or ',' in gpu:raise ValueError('MAIN assigns one empty GPU')
    output.mkdir(parents=True,exist_ok=False);deadline=started+2400;work=started+2280
    s.write(output/'RUN.json',dict(identity=ready['identity'],ready_sha256=s.sha(s.ROOT/'READY.json'),started_epoch=started,
      deadline_epoch=deadline,work_deadline_epoch=work,gpu=gpu,training_order=s.training_order(),phase_order=s.phase_order(),planned=48))
    def expired(_sig,_frame):raise TimeoutError('2400s inclusive envelope or parent termination')
    for sig in (signal.SIGINT,signal.SIGTERM,signal.SIGALRM):signal.signal(sig,expired)
    signal.setitimer(signal.ITIMER_REAL,remaining(deadline,2400));stages=[];error=None
    try:
        suite=dependencies()
        for arm in s.training_order():
            directory=b.training_source(arm)
            argv=[str(s.TRAIN),str(s.ROOT/'train.py'),'run','--arm',arm,'--output',str(directory)]
            cap=remaining(work,360)
            s.write(output/f'TRAIN_COMMAND_{arm}.json',dict(argv=argv,cap_seconds=cap,started_epoch=time.time()))
            with (output/f'training-{arm}.log').open('x') as log:
                process=subprocess.Popen(argv,stdout=log,stderr=subprocess.STDOUT,start_new_session=True,env={**os.environ,'PYTHONDONTWRITEBYTECODE':'1'})
                observation=suite.life.observe(process.pid)
                if observation is None:raise RuntimeError('owned training identity unavailable')
                owner=suite.life.safe_observation(observation);s.write(output/f'TRAIN_PROCESS_{arm}.json',owner)
                try:
                    if process.wait(timeout=cap):raise RuntimeError('training nonzero; no checkpoint substitution')
                finally:
                    suite.stop_child(process,owner);s.write(output/f'TRAIN_EXIT_{arm}.json',dict(returncode=process.returncode,ended_epoch=time.time()))
        selected={arm:b.selected(arm) for arm in s.phase_order()}
        for arm in s.phase_order():
            stage=output/arm;stage.mkdir()
            try:
                suite.start_service(stage,b.binding(arm,selected[arm]),time.time()+remaining(work,180))
                argv=[str(s.NATIVE),str(s.ROOT/'readout.py'),'--weight',arm,'--training',str(b.training_source(arm)),
                  '--binding',str(stage/'BINDING.json'),'--endpoint',str(stage/'service/endpoint-original.json'),
                  '--output',str(stage/'rollout'),'--deadline',str(time.time()+remaining(work,420))]
                suite.command(stage,'collect',argv,450,work)
                terminal=s.read(stage/'rollout/TERMINAL.json')
                if terminal['planned']!=16 or terminal['recorded']!=16 or not terminal['complete']:raise ValueError('incomplete native16; retain nulls')
                stages.append(dict(arm=arm,terminal=terminal))
            finally:suite.release_service(stage)
    except BaseException as caught:error=dict(type=type(caught).__name__,message=str(caught),traceback=traceback.format_exc())
    finally:signal.setitimer(signal.ITIMER_REAL,0)
    terminal=dict(complete=error is None,error=error,stages=stages,planned=48,elapsed_seconds=time.time()-started,
      deadline_epoch=deadline,independent_analysis_deferred_until_after_release=True,
      null_accounting='all48 planned coordinates retained; missing and infrastructure-unavailable are NULL, completed empty is0')
    s.write(output/'TERMINAL.json',terminal);return terminal


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('command',choices=('verify','run'));p.add_argument('--output',type=Path,default=s.ROOT/'outputs/attempt-001');a=p.parse_args()
    if a.command=='verify':print({'identity':s.verify()['identity'],'gpu_calls':0})
    else:
        result=execute(a.output.resolve());print(result);raise SystemExit(0 if result['complete'] else 1)
