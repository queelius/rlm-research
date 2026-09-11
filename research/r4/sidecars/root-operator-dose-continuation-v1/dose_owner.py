"""MAIN-only training-first owner:4320outer,4200work,90cleanup; no model service."""
import argparse
import os
from pathlib import Path
import signal
import subprocess
import time
import traceback
import dose_study as s

def check_output(output):
    if output.resolve()!=s.ATTEMPT.resolve():raise ValueError('exact new output only')
    if output.exists():raise FileExistsError('no retry or overwrite')
def training_argv(output,deadline):return [str(s.original().TRAIN),str(s.ROOT/'dose_train.py'),'--output',str(output/'training'),'--deadline',str(float(deadline))]
def error_record(error):return dict(type=type(error).__name__,message=str(error),traceback=traceback.format_exc())
def selected(output):
    result=s.read(output/'training/RESULT.json');chosen=s.read(output/'training/SELECTION.json')
    if not result['complete'] or result['actual_final_adam_step']!=24 or result['added_optimizer_steps']!=18 or result['fresh_optimizer'] or result['child_loaded'] or result['child_updated'] or result['selected']!=chosen:raise ValueError('fixed24 committed completion required')
    previous=s.sha(s.START/'state.json')
    for step in range(7,25):
        path=output/'training'/f'checkpoint-{step:04d}';state=s.read(path/'state.json')
        if (state['step'],state['epoch'],state['cursor'],state['previous_state_sha256'],state['corpus_sha256'])!=(step,step,0,previous,s.CORPUS_SHA):raise ValueError('full checkpoint chain')
        for name,pin in state['files_sha256'].items():
            if Path(name).name!=name:raise ValueError('checkpoint member')
            s.check(path/name,pin)
        previous=s.sha(path/'state.json')
    if chosen['state_sha256']!=previous or Path(chosen['checkpoint'])!=output/'training/checkpoint-0024':raise ValueError('fixed24 selection path')
    return chosen

def execute(output):
    started=time.time();work=started+4200;owned=started+4290;check_output(output)
    gpu=os.environ.get('CUDA_VISIBLE_DEVICES','')
    if not gpu or ',' in gpu:raise ValueError('MAIN must supply one assigned GPU')
    ready=s.verify();suite=s.dependencies();output.mkdir(parents=True,exist_ok=False)
    s.write(output/'PLANNED_EVALUATION.json',s.read(s.ROOT/'inputs/EVALUATION_PLAN.json'))
    s.write(output/'OWNER_RUN.json',dict(identity=ready['identity'],started_epoch=started,work_deadline_epoch=work,owned_deadline_epoch=owned,outer_seconds=4320,gpu=gpu,training_only=True,child_loaded=False,readout_outer_seconds=6480,combined_outer_seconds=10800))
    def expire(signum,frame):raise TimeoutError('MAIN signal or inclusive training owner cap')
    handlers={sig:signal.signal(sig,expire) for sig in (signal.SIGINT,signal.SIGTERM,signal.SIGALRM)}
    signal.setitimer(signal.ITIMER_REAL,max(.001,work-time.time()));process=None;observed=None;errors=[];chosen=None;released=True
    stage=output/'train-stage';stage.mkdir()
    try:
        argv=training_argv(output,work)
        s.write(stage/'COMMAND.json',dict(argv=argv,started_epoch=time.time(),deadline_epoch=work,gpu=gpu,gpu_visible_to_command=True))
        with (stage/'process.log').open('x') as log:
            process=subprocess.Popen(argv,stdout=log,stderr=subprocess.STDOUT,start_new_session=True,env={**os.environ,'PYTHONDONTWRITEBYTECODE':'1'})
            live=suite.life.observe(process.pid)
            if live is None:
                process.wait(timeout=5);raise RuntimeError('training exited before ownership observation')
            observed=suite.life.safe_observation(live);s.write(stage/'PROCESS.json',observed);released=False
            if process.wait(timeout=max(.001,work-time.time())):raise RuntimeError('training failed; no retry or partial24')
            chosen=selected(output)
    except BaseException as error:errors.append(error_record(error))
    finally:
        signal.setitimer(signal.ITIMER_REAL,max(.001,owned-time.time()))
        if process is not None and observed is not None:
            try:suite.stop_child(process,observed);released=True
            except BaseException as error:errors.append(error_record(error))
        s.write(stage/'EXIT.json',dict(returncode=process.returncode if process else None,ended_epoch=time.time(),released=released))
        result=dict(identity=ready['identity'],complete=not errors and chosen is not None,errors=errors,selected=chosen,released=released,elapsed_seconds=time.time()-started,training_only=True,planned_full_endpoints=96,planned_first_actions=24,readout_run=False,no_partial24_substitution=True)
        s.write(output/'OWNER_TERMINAL.json',result)
        signal.setitimer(signal.ITIMER_REAL,0)
        for sig,handler in handlers.items():signal.signal(sig,handler)
    return result

def parse_args(argv=None):
    p=argparse.ArgumentParser();p.add_argument('command',choices=('verify','run'));p.add_argument('--output',type=Path,default=s.ATTEMPT);return p.parse_args(argv)
if __name__=='__main__':
    a=parse_args()
    if a.command=='verify':print(s.verify()['identity'])
    else:
        result=execute(a.output);print(result);raise SystemExit(0 if result['complete'] else 1)
