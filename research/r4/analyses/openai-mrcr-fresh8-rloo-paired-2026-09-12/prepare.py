"""Freeze CPU audit closure and completed saved-gradient diagnostics; no polling."""
import os
from pathlib import Path
import subprocess
import time
import analyze as a

def prepare():
    assert os.environ.get('CUDA_VISIBLE_DEVICES')=='' and not (a.ROOT/'CPU_READY.json').exists()
    c=a.bindings();assert a.sha(a.SIDE/'READY.json')==a.SOURCE_READY_SHA
    env=dict(os.environ,CUDA_VISIBLE_DEVICES='',PYTHONDONTWRITEBYTECODE='1',TOKENIZERS_PARALLELISM='false')
    command=[str(c.study.NATIVE),'-m','pytest','-q','-p','no:cacheprovider','test_analyze.py']
    started=time.monotonic();r=subprocess.run(command,cwd=a.ROOT,env=env,capture_output=True,text=True,timeout=120)
    a.write(a.ROOT/'CPU_TESTS.json',dict(command=command,returncode=r.returncode,stdout=r.stdout,stderr=r.stderr,
        elapsed_seconds=time.monotonic()-started,original_red='Two tests failed before analyze.py existed',
        real_fresh_seed_cp32_native_control=True,clip_component_fixture=True,GPU_calls=0))
    assert r.returncode==0,r.stdout+r.stderr
    import gradient
    gradient.run()
    ready=a.read(a.SIDE/'READY.json');pins=dict(ready['closure_sha256']);pins.update(a.PINS)
    from verifiers.v1.clients import train
    for p in (a.SIDE/'READY.json',a.CORE,a.core.HELPER,Path(train.__file__)):
        pins[str(p)]=a.sha(p)
    for p in a.ROOT.iterdir():
        if p.is_file():pins[str(p)]=a.sha(p)
    for p,h in pins.items():assert a.sha(p)==h,p
    value=dict(schema='fresh8-rloo-independent-readout-CPU-ready-v1',closure_sha256=pins,
        source_READY_sha256=a.SOURCE_READY_SHA,planned_new_outputs=64,
        comparisons={'held':['cp32','fixed_baseline_RL'],'long':['cp32'],'fourneedle':['cp32']},
        context_units_per_panel=16,short_repeats=2,one_completion_check=True,polling=False,
        GPU_calls=0,backward_calls=0,optimizer_steps=0,
        command=[str(c.study.NATIVE),str(a.ROOT/'analyze.py'),'check','--output',str(a.ROOT/'readout-001.json')])
    value['identity']=a.digest(value);a.write(a.ROOT/'CPU_READY.json',value);a.verify()
    print({'READY_sha256':a.sha(a.ROOT/'CPU_READY.json'),'identity':value['identity'],'pins':len(pins)})

if __name__=='__main__':prepare()
