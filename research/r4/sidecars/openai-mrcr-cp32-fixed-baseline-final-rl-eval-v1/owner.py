"""Two fixed stages, accepted service lifecycle, no outcome manipulation gate."""
import argparse
import json
import os
from pathlib import Path
import signal
import sys
import time
import traceback
import checkpoint
import study

old={n:sys.modules.get(n) for n in ('study','checkpoint')};sys.modules.update(study=study,checkpoint=checkpoint)
try:prior=study.load('fixedRL_eval_service_owner_seam',study.SOURCE_EVAL/'owner.py')
finally:
    for n,v in old.items():
        if v is None:sys.modules.pop(n,None)
        else:sys.modules[n]=v

def verify(phase):
    assert phase in study.CAPS
    r=study.verify();q=checkpoint.verify_checkpoint()
    assert q==study.read(study.ROOT/'CHECKPOINT_QUALIFICATION.json')
    study.terminal_hooks();return r

def execute(phase):
    ready=verify(phase);caps=study.CAPS[phase];output=study.ROOT/f'outputs/{phase}-001'
    gpu=os.environ.get('CUDA_VISIBLE_DEVICES','')
    assert gpu and ',' not in gpu and os.environ.get('STRICT_RLM_CALIBRATION_API_KEY')
    assert not output.exists();output.mkdir(parents=True)
    started=time.time();deadline=started+caps['owner'];work=deadline-60
    service=output/'owned-service';service.mkdir();binding=checkpoint.binding('updated')
    study.write_x(output/'OWNER_RUN.json',dict(phase=phase,arm='updated',started_epoch=started,
        caps=caps,planned=len(study.schedule(phase)),ready_identity=ready['identity'],
        ready_sha256=study.sha(study.READY),checkpoint_qualification=checkpoint.verify_checkpoint(),
        baseline_output=str(study.BASELINES[phase]),no_outcome_manipulation_gate=True))
    errors=[];suite=None;released=False
    def stop(*_):raise TimeoutError('fixed RL evaluation owner signal')
    handlers={sig:signal.signal(sig,stop) for sig in (signal.SIGALRM,signal.SIGTERM,signal.SIGINT)}
    signal.setitimer(signal.ITIMER_REAL,caps['owner']-15)
    try:
        suite=study.dependencies();suite.preflight=prior.preflight
        suite.start_service(service,binding,min(started+240,work))
        science_deadline=min(work,time.time()+caps['science'])
        argv=[str(study.NATIVE),str(study.ROOT/'collect.py'),'--phase',phase,'--arm','updated',
              '--endpoint',str(service/'service/endpoint-original.json'),'--output',str(output/'science'),
              '--deadline',str(science_deadline)]
        suite.command(service,'fixed-RL-'+phase,argv,
                      min(caps['science'],max(1,science_deadline-time.time())),science_deadline)
    except BaseException as e:
        errors.append(dict(type=type(e).__name__,message=str(e),traceback=traceback.format_exc()))
    finally:
        signal.setitimer(signal.ITIMER_REAL,max(1,deadline-time.time()))
        if suite is not None:
            try:suite.release_service(service);released=True
            except BaseException as e:errors.append(dict(stage='release',type=type(e).__name__,message=str(e)))
        else:released=True
        rp=output/'science/RESULT.json';hp=output/'science/TERMINAL_STRIP_CONTRACT.json'
        result=study.read(rp) if rp.exists() else None
        complete=bool(not errors and released and result and result.get('complete') and
            result.get('planned')==len(study.schedule(phase)) and result.get('all_causal_mappings_complete') and
            result.get('all_initial_root_prefixes_verified') and result.get('all_action_caps_respected') and
            result.get('child_actions')==0 and hp.exists() and study.read(hp).get('condition')=='terminal-strip-disabled')
        terminal=dict(complete=complete,released=released,errors=errors or None,phase=phase,
            result=str(rp) if result else None,result_sha256=study.sha(rp) if result else None,
            recorded=result.get('recorded') if result else None,
            scientifically_available=result.get('scientifically_available') if result else None,
            elapsed_seconds=time.time()-started,ready_sha256=study.sha(study.READY),
            no_outcome_manipulation_gate=True,no_retry=True,optimizer_steps=0)
        study.write_x(output/'OWNER_TERMINAL.json',terminal)
        signal.setitimer(signal.ITIMER_REAL,0)
        for sig,handler in handlers.items():signal.signal(sig,handler)
    return terminal

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('command',choices=['verify','run']);p.add_argument('--phase',choices=tuple(study.CAPS),required=True);a=p.parse_args()
    if a.command=='verify':print(verify(a.phase)['identity'])
    else:
        value=execute(a.phase);print(json.dumps(value,sort_keys=True));raise SystemExit(0 if value['complete'] else 1)
