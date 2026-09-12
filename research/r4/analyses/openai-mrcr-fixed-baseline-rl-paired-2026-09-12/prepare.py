import os
import subprocess
import time
from pathlib import Path
import analyze as a

def prepare():
    assert os.environ.get('CUDA_VISIBLE_DEVICES')=='' and not (a.ROOT/'READY.json').exists()
    c=a.bindings();assert a.sha(a.SIDE/'READY.json')==a.SOURCE_READY_SHA
    command=[str(c.study.NATIVE),'-m','pytest','-q','-p','no:cacheprovider','test_analyze.py']
    started=time.monotonic()
    result=subprocess.run(command,cwd=a.ROOT,env=dict(os.environ,CUDA_VISIBLE_DEVICES='',PYTHONDONTWRITEBYTECODE='1'),
                          capture_output=True,text=True,timeout=120)
    a.write(a.ROOT/'CPU_TESTS.json',dict(command=command,returncode=result.returncode,stdout=result.stdout,
        stderr=result.stderr,elapsed_seconds=time.monotonic()-started,
        red_green='Missing implementation red; real raw fixture exposed dict/serialized JSON and nameless-invalid-tool conversion, now exercised through actual response_from_generate.',
        GPU_calls=0,generated_programs_executed=False))
    assert result.returncode==0,result.stdout+result.stderr
    ready=a.read(a.SIDE/'READY.json');pins=dict(ready['closure_sha256'])
    from verifiers.v1.clients import train
    for p in (a.SIDE/'READY.json',a.HELPER,Path(train.__file__)):
        pins[str(p)]=a.sha(p)
    for p in a.ROOT.iterdir():
        if p.is_file():pins[str(p)]=a.sha(p)
    for p,h in pins.items():assert a.sha(p)==h,p
    value=dict(schema='fixedbaseline-final-RL-paired-analyzer-ready-v1',closure_sha256=pins,
        source_READY_sha256=a.SOURCE_READY_SHA,planned_per_arm=48,held_contexts=16,held_repeats=2,long_contexts=16,
        one_shot=True,polling=False,GPU_calls=0,generated_programs_executed=False,
        command=[str(c.study.NATIVE),str(a.ROOT/'analyze.py'),'check','--output',str(a.ROOT/'readout-001.json')])
    value['identity']=a.digest(value);a.write(a.ROOT/'READY.json',value)
    a.verify();print({'identity':value['identity'],'READY_sha256':a.sha(a.ROOT/'READY.json'),'pins':len(pins)})

if __name__=='__main__':prepare()
