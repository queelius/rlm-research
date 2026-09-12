import os
from pathlib import Path
import subprocess
import analyze as a

assert os.environ.get('CUDA_VISIBLE_DEVICES')=='' and not (a.ROOT/'CPU_READY.json').exists()
c=a.bindings();command=[str(c.study.NATIVE),'-m','pytest','-q','-p','no:cacheprovider','test_analyze.py']
r=subprocess.run(command,cwd=a.ROOT,capture_output=True,text=True,timeout=120)
a.write(a.ROOT/'CPU_TESTS.json',dict(command=command,returncode=r.returncode,stdout=r.stdout,stderr=r.stderr,
    original_red='Expected failure before analyze.py existed',real_original_native_control=True,GPU_calls=0))
assert r.returncode==0,r.stdout+r.stderr
ready=a.read(a.SIDE/'READY.json');pins=dict(ready['closure_sha256'])
for p in (a.SIDE/'READY.json',a.CORE,a.core.HELPER):pins[str(p)]=a.sha(p)
for p in a.ROOT.iterdir():
    if p.is_file():pins[str(p)]=a.sha(p)
for p,h in pins.items():assert a.sha(p)==h,p
value=dict(schema='fresh8-training-readout-auditor-ready-v1',closure_sha256=pins,source_READY_sha256=a.SOURCE_SHA,
    planned_per_arm=32,context_units=8,GPU_calls=0,optimizer_steps=0,polling=False,
    command=[str(c.study.NATIVE),str(a.ROOT/'analyze.py'),'check','--output',str(a.ROOT/'readout-001.json')])
value['identity']=a.digest(value);a.write(a.ROOT/'CPU_READY.json',value);a.verify()
print(dict(ready_sha256=a.sha(a.ROOT/'CPU_READY.json'),identity=value['identity'],pins=len(pins)))
