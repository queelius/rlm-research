"""Two fixed model stages; existing V2 ownership, no scheduler or new retries."""
import argparse
import importlib.util
import os
import signal
import sys
import time
from pathlib import Path
import study as s
import service

PYTHON='/project/alex_phd/envs/prime-rl-5990b1b/bin/python'
LIFE=s.SPARSE/'owned.py'
LIFE_SHA='84788b145dddff5847edb9ee6e924ae5cbf2cefa909e6fecd08e2992b88fc68b'


def load_suite():
    if s.sha(LIFE)!=LIFE_SHA:raise ValueError('qualified lifecycle adapter changed')
    loader=importlib.util.spec_from_file_location('qwen35_private_lifecycle',LIFE);module=importlib.util.module_from_spec(loader);sys.modules[loader.name]=module;loader.loader.exec_module(module)
    suite=module.load_suite()
    # These globals are private to this process. V2 authenticates the new exact
    # source/serve.py path and SHA through c.ROLE; all ownership checks remain.
    suite.c.ROLE=s.ROOT;suite.SERVE=s.ROOT/'source/serve.py'
    suite.preflight=preflight
    return suite


def preflight(directory,binding):
    import httpx
    endpoint=s.read(directory/'endpoint-original.json');model=s.MODELS[binding['model']];service.validate_descriptor(endpoint,model)
    actual=s.read(directory/'inference.json');expected=service.config(model,directory,os.environ[endpoint['api_key_env']])
    if actual!=expected:raise ValueError('actual service config changed')
    url=f"http://{endpoint['host']}:{endpoint['port']}"
    with httpx.Client(headers={'Authorization':'Bearer '+os.environ[endpoint['api_key_env']]},trust_env=False,timeout=15) as client:
        v=client.get(url+'/version');v.raise_for_status()
        if v.json().get('version')!='0.28.0':raise ValueError('live version')
        r=client.get(url+'/v1/models');r.raise_for_status();service.validate_models(r.json(),model)
    s.write_once(directory.parent/'PREFLIGHT.json',dict(version=v.json(),models=r.json(),config_sha256=s.sha(directory/'inference.json')))


def execute(directory,suite,started):
    directory.mkdir(parents=True,exist_ok=False);work_deadline=started+2400;stages=[]
    s.write_once(directory/'ATTEMPT.json',dict(started_epoch=started,work_deadline_epoch=work_deadline,
        owned_deadline_epoch=started+2640,ready_sha256=s.sha(s.ROOT/'READY.json'),model_order=list(s.MODELS)))
    for model,checkpoint in s.MODELS.items():
        stage=directory/model;stage.mkdir();error=None;released=False
        try:
            binding=dict(model=model,checkpoint=checkpoint,weights_sha256=s.sha(s.ROOT/'WEIGHTS.json'),adapter=None)
            suite.start_service(stage,binding,min(work_deadline,time.time()+300))
            until=min(work_deadline,time.time()+900)
            if until<=time.time():raise TimeoutError('no new stage after work cap')
            argv=[PYTHON,str(s.ROOT/'driver.py'),'run','--model',model,'--endpoint',str(stage/'service/endpoint-original.json'),
                '--output',str(s.ROOT/'outputs'/model),'--deadline',str(until)]
            suite.command(stage,model+'-run',argv,930,min(work_deadline,until+30))
        except BaseException as exc:
            error=dict(type=type(exc).__name__,message=str(exc));s.write_once(stage/'ERROR.json',error)
        finally:
            try:suite.release_service(stage);released=True
            finally:
                result=dict(model=model,error=error,owned_release_completed=released,ended_epoch=time.time())
                s.write_once(stage/'FINISH.json',result);stages.append(result)
        if error or not released:break
    terminal=dict(complete=len(stages)==2 and all(x['error'] is None and x['owned_release_completed'] for x in stages),
        stages=stages,elapsed_seconds=time.time()-started,owned_cap_exceeded=time.time()>started+2640)
    s.write_once(directory/'TERMINAL.json',terminal);return terminal


def main():
    started=time.time();p=argparse.ArgumentParser();p.add_argument('--directory',type=Path,default=s.ROOT/'owned/attempt-001');p.add_argument('--verify',action='store_true');a=p.parse_args()
    import driver
    driver.verify(s.read(s.ROOT/'SPEC.json'));suite=load_suite()
    if a.verify:print('verified source, shard stat identities, base lifecycle seam; no GPU calls');return
    if a.directory.resolve().parent!=s.ROOT/'owned' or a.directory.exists() or (s.ROOT/'outputs').exists():raise ValueError('new owned namespace only')
    gpu=os.environ.get('CUDA_VISIBLE_DEVICES','')
    if not gpu or ',' in gpu or not os.environ.get('STRICT_RLM_CALIBRATION_API_KEY'):raise ValueError('parent exclusive GPU/API environment required')
    def interrupted(sig,frame):raise KeyboardInterrupt('owned signal '+str(sig))
    signal.signal(signal.SIGTERM,interrupted);signal.signal(signal.SIGINT,interrupted)
    terminal=execute(a.directory.resolve(),suite,started);raise SystemExit(0 if terminal['complete'] else 1)


if __name__=='__main__':main()
