"""Exact new factorial attempt with proven restart lifecycle and shared3000s clock."""
import argparse
import functools
import os
from pathlib import Path
import signal
import time
import study as s
import protocol as p

@functools.lru_cache(maxsize=1)
def dependencies():
    old=s.source().original.plan.old.row
    with s.source().aliases({'study':old}):launcher=s.load('restart_qualified_owner_dependencies',old.ROOT/'launch.py','62d7d0049b5e3303f6e68247038290c7cde0d74e3394b4856fea0e3e138d6b46')
    suite=launcher.dependencies();_,adapter=s.runtime();adapter.install(suite);return suite

def check_output(output):
    if output.resolve()!=s.ATTEMPT.resolve():raise ValueError('only exact new outputs/attempt-001 authorized')
    if output.exists():raise FileExistsError('attempt exists; no retry or overwrite')

def collector_argv(stage,destination,deadline):
    return [str(s.NATIVE),str(s.ROOT/'collect.py'),'--binding',str(stage/'BINDING.json'),
        '--endpoint',str(stage/'service/endpoint-original.json'),'--output',str(destination),'--deadline',str(deadline)]

def execute(output):
    started=time.time();work=started+2700;owned=started+2880
    check_output(output);ready=s.verify();s.runtime() # private credential preflight, before output/process work
    gpu=os.environ.get('CUDA_VISIBLE_DEVICES','')
    if not gpu or ',' in gpu:raise ValueError('MAIN must assign one GPU under MAIN lock')
    suite=dependencies();output.mkdir(parents=True,exist_ok=False);stage=output/'owned-service';stage.mkdir()
    plan=s.read(s.ROOT/'inputs/PLAN.json')
    s.write(output/'OWNER_RUN.json',dict(identity=ready['identity'],ready_sha256=s.sha(s.ROOT/'READY.json'),started_epoch=started,work_deadline_epoch=work,owned_deadline_epoch=owned,outer_seconds=3000,gpu=gpu,credential_present=True,credential_value_logged=False))
    s.write(output/'PLANNED_NULL_ENDPOINTS.json',[p.null_row(row,'planned before service launch') for row in plan])
    def expired(_sig,_frame):raise TimeoutError('owned2880s inclusive deadline or MAIN termination')
    previous={sig:signal.signal(sig,expired) for sig in (signal.SIGINT,signal.SIGTERM,signal.SIGALRM)}
    signal.setitimer(signal.ITIMER_REAL,max(.001,owned-time.time()));error=None;release_error=None;released=False;terminal=None
    try:
        suite.start_service(stage,s.read(s.ROOT/'inputs/BINDING.json'),min(work,started+300))
        deadline=min(work,time.time()+2400)
        suite.command(stage,'state-content64',collector_argv(stage,output/'rollout',deadline),max(.001,deadline-time.time()),deadline)
        terminal=s.read(output/'rollout/TERMINAL.json')
        if terminal['planned']!=64 or terminal['recorded']!=64:raise ValueError('incomplete planned endpoint accounting')
    except BaseException as caught:error=dict(type=type(caught).__name__,message=str(caught))
    finally:
        try:suite.release_service(stage);released=True
        except BaseException as caught:release_error=dict(type=type(caught).__name__,message=str(caught))
        signal.setitimer(signal.ITIMER_REAL,0)
        for sig,handler in previous.items():signal.signal(sig,handler)
    result=dict(complete=error is None and released,error=error,release_error=release_error,released=released,collector_terminal=terminal,
        planned=64,elapsed_seconds=time.time()-started,outer_seconds=3000,work_deadline_epoch=work,owned_deadline_epoch=owned,
        main_owns_gpu_and_lock=True,no_retry=True,missing_endpoint_reward=None)
    s.write(output/'OWNER_TERMINAL.json',result);return result

def parse_args(argv=None):
    ap=argparse.ArgumentParser();ap.add_argument('command',choices=('verify','run'));ap.add_argument('--output',type=Path,default=s.ATTEMPT);return ap.parse_args(argv)

if __name__=='__main__':
    args=parse_args()
    if args.command=='verify':print(s.verify()['identity'])
    else:
        result=execute(args.output);print(dict(complete=result['complete'],error=result['error'],released=result['released']));raise SystemExit(0 if result['complete'] else 1)
