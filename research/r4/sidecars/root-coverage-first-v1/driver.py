"""Two qualified owned service phases; one shared work clock, no retry."""
import argparse
import os
import time
from pathlib import Path
import study as s

def dependencies():
    with s.aliases({'study':s.original()}):
        old=s.load('coverage_owned_lifecycle',s.OLD/'driver.py',s.old_pins()[str(s.OLD/'driver.py')])
    return old.dependencies()

def run(output):
    started=time.time();owned=started+2670;work=started+2550;spec=s.verify()
    if not os.environ.get('CUDA_VISIBLE_DEVICES') or ',' in os.environ['CUDA_VISIBLE_DEVICES']:raise ValueError('MAIN assigns exactly one free GPU')
    output.mkdir(parents=True,exist_ok=False);suite=dependencies();suite.life.install()
    s.write(output/'RUN.json',{'started_epoch':started,'work_deadline_epoch':work,'owned_deadline_epoch':owned,
        'outer_cap_seconds':2700,'ready_sha256':s.sha(s.ROOT/'READY.json'),'gpu':os.environ['CUDA_VISIBLE_DEVICES'],'phase_order':s.WEIGHTS})
    error=None;phases=[]
    for weight in s.WEIGHTS:
        if time.time()>=work:
            error={'type':'SharedWorkCap','message':'next weight phase unrun'};break
        stage=output/weight/'service-stage';stage.mkdir(parents=True)
        phase={'weight':weight,'started_epoch':time.time(),'error':None}
        try:
            suite.start_service(stage,spec['bindings'][weight],min(work,time.time()+300))
            deadline=min(work,time.time()+900)
            argv=[str(s.NATIVE),str(s.ROOT/'collect.py'),'--weight',weight,'--binding',str(stage/'BINDING.json'),
                '--endpoint',str(stage/'service/endpoint-original.json'),'--output',str(output/weight/'rollout'),'--deadline',str(deadline)]
            suite.command(stage,'collect',argv,930,work)
        except BaseException as caught:phase['error']={'type':type(caught).__name__,'message':str(caught)}
        finally:
            try:suite.release_service(stage)
            except BaseException as caught:phase['error']={'prior':phase['error'],'release_error':{'type':type(caught).__name__,'message':str(caught)}}
        phase['ended_epoch']=time.time();s.write(output/weight/'PHASE_TERMINAL.json',phase);phases.append(phase)
        if phase['error'] is not None:error=phase['error'];break
    terminal={'complete':error is None and len(phases)==2,'error':error,'elapsed_seconds':time.time()-started,
        'owned_deadline_epoch':owned,'planned':48,'phases':phases,'unrun_weights':[w for w in s.WEIGHTS if w not in {p['weight'] for p in phases}],
        'interpretation':'collection/lifecycle completion is not model success; raw failures/NULLs retained'}
    s.write(output/'TERMINAL.json',terminal);return terminal

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('command',choices=('verify','run'));p.add_argument('--output',type=Path,default=s.ROOT/'outputs/attempt-001');a=p.parse_args()
    if a.command=='verify':s.verify();print('CPU verified;48 planned; GPU/model calls0')
    else:
        result=run(a.output);print(result);raise SystemExit(0 if result['complete'] else 1)
