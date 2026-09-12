"""MAIN-only bounded service owner, reusing the accepted native base service."""
import argparse
import json
import os
from pathlib import Path
import signal
import time
import traceback
import musique_study as s


def execute(output,outer_seconds):
    if output.resolve()!=s.ATTEMPT.resolve() or output.exists():raise ValueError('exact unused attempt-001 required')
    if outer_seconds!=s.OWNER_SECONDS:raise ValueError('fixed 1700-second owner cap required')
    ready=s.verify();gpu=os.environ.get('CUDA_VISIBLE_DEVICES','')
    if not gpu or ',' in gpu or not os.environ.get('STRICT_RLM_CALIBRATION_API_KEY'):
        raise ValueError('one MAIN-owned GPU and inherited private credential required')
    started=time.time();deadline=started+s.OWNER_SECONDS;work=deadline-90
    output.mkdir(parents=True);stage=output/'owned-service';stage.mkdir()
    s.write_x(output/'OWNER_RUN.json',{'started_epoch':started,'owner_seconds':s.OWNER_SECONDS,
        'science_seconds':s.SCIENCE_SECONDS,'ready_identity':ready['identity'],'planned_episodes':48,
        'global_physical_call_upper_bound':228,'root_and_child_same_pretrained_model':True,'optimizer_steps':0})
    suite=None;released=False;errors=[]
    def stop(*_):raise TimeoutError('owner signal')
    previous={sig:signal.signal(sig,stop) for sig in (signal.SIGALRM,signal.SIGTERM,signal.SIGINT)}
    signal.setitimer(signal.ITIMER_REAL,s.OWNER_SECONDS-15)
    try:
        suite=s.dependencies();suite.start_service(stage,s.binding(),min(started+240,work))
        endpoint=stage/'service/endpoint-original.json';science_deadline=min(work,time.time()+s.SCIENCE_SECONDS)
        argv=[str(s.NATIVE),str(s.ROOT/'collect.py'),'--endpoint',str(endpoint),'--output',str(output/'science'),
              '--deadline',str(float(science_deadline))]
        suite.command(stage,'musique-depth-pilot',argv,max(1,science_deadline-time.time()),science_deadline)
    except BaseException as error:
        errors.append({'type':type(error).__name__,'message':str(error),'traceback':traceback.format_exc()})
    finally:
        signal.setitimer(signal.ITIMER_REAL,max(1,deadline-time.time()))
        if suite is not None:
            try:suite.release_service(stage);released=True
            except BaseException as error:errors.append({'stage':'release','type':type(error).__name__,'message':str(error)})
        else:released=True
        path=output/'science/RESULT.json';result=s.read(path) if path.exists() else None
        terminal={'complete':not errors and released and bool(result and result['complete']),
            'released':released,'errors':errors,'result_sha256':s.sha(path) if result else None,
            'recorded':result['recorded'] if result else None,'elapsed_seconds':time.time()-started,
            'optimizer_steps':0,'no_retry':True}
        s.write_x(output/'OWNER_TERMINAL.json',terminal)
        signal.setitimer(signal.ITIMER_REAL,0)
        for sig,handler in previous.items():signal.signal(sig,handler)
    return terminal


if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('command',choices=['verify','run'])
    parser.add_argument('--output',type=Path,default=s.ATTEMPT);parser.add_argument('--outer-seconds',type=int,default=s.OWNER_SECONDS)
    args=parser.parse_args()
    if args.command=='verify':print(s.verify()['identity'])
    else:
        result=execute(args.output,args.outer_seconds);print(json.dumps(result));raise SystemExit(0 if result['complete'] else 1)
