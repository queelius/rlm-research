"""Parent-only launch; unchanged qualified owned service lifecycle."""
import argparse
import os
import time
from pathlib import Path
import study as s

def dependencies():
    st=s.stack();sources=s.read(s.PRIOR/'READY.json')['source_sha256']
    with s.aliases({'study':st.prior,'native':st.native}):
        launch=s.load('ledger_pinned_lifecycle',s.PRIOR/'launch.py',sources[str(s.PRIOR/'launch.py')])
    return launch.dependencies()

def run(output):
    started=time.time();owned=started+1770;work=started+1650;spec=s.verify()
    if not os.environ.get('CUDA_VISIBLE_DEVICES') or ',' in os.environ['CUDA_VISIBLE_DEVICES']:raise ValueError('MAIN assigns exactly one free GPU')
    output.mkdir(parents=True,exist_ok=False);suite=dependencies();suite.life.install();stage=output/'service-stage';stage.mkdir()
    s.write(output/'RUN.json',{'started_epoch':started,'work_deadline_epoch':work,'owned_deadline_epoch':owned,
            'outer_cap_seconds':1800,'ready_sha256':s.sha(s.ROOT/'READY.json'),'gpu':os.environ['CUDA_VISIBLE_DEVICES']})
    error=None
    try:
        suite.start_service(stage,spec['binding'],min(work,time.time()+300))
        deadline=min(work,time.time()+1200)
        argv=[str(s.NATIVE),str(s.ROOT/'collect.py'),'--binding',str(stage/'BINDING.json'),
              '--endpoint',str(stage/'service/endpoint-original.json'),'--output',str(output/'rollout'),'--deadline',str(deadline)]
        suite.command(stage,'collect',argv,1230,work)
    except BaseException as caught:error={'type':type(caught).__name__,'message':str(caught)}
    finally:
        try:suite.release_service(stage)
        except BaseException as caught:
            error={'prior':error,'release_error':{'type':type(caught).__name__,'message':str(caught)}}
    terminal={'complete':error is None,'error':error,'elapsed_seconds':time.time()-started,
              'owned_deadline_epoch':owned,'planned':16}
    s.write(output/'TERMINAL.json',terminal);return terminal

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('command',choices=('verify','run'));p.add_argument('--output',type=Path,default=s.ROOT/'outputs/attempt-001');a=p.parse_args()
    if a.command=='verify':s.verify();print('CPU verified; 16 planned; GPU/model calls0')
    else:
        result=run(a.output);print(result);raise SystemExit(0 if result['complete'] else 1)
