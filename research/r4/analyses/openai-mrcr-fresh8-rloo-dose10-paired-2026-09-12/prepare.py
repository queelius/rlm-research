import os
import subprocess
import analyze as a

assert os.environ.get('CUDA_VISIBLE_DEVICES')=='' and not (a.ROOT/'CPU_READY.json').exists()
c=a.bindings();command=[str(c.study.NATIVE),'-m','pytest','-q','-p','no:cacheprovider','test_analyze.py']
r=subprocess.run(command,cwd=a.ROOT,capture_output=True,text=True,timeout=120)
a.write(a.ROOT/'CPU_TESTS.json',dict(command=command,returncode=r.returncode,stdout=r.stdout,stderr=r.stderr,
    original_red='Expected assertion before analyze.py existed',actual_LR1e5_native_control_and_path_helper=True,GPU_calls=0))
assert r.returncode==0,r.stdout+r.stderr
source=a.read(a.SIDE/'READY.json');pins=dict(source['closure_sha256'])
for p in (a.SIDE/'READY.json',a.PRIOR,a.PATHS,a.prior.CORE,a.core.HELPER):pins[str(p)]=a.sha(p)
for p in a.ROOT.iterdir():
    if p.is_file():pins[str(p)]=a.sha(p)
for p,h in pins.items():assert a.sha(p)==h,p
ready=dict(schema='fresh8-RLOO-dose10-three-arm-auditor-v1',closure_sha256=pins,source_READY_sha256=a.SOURCE_SHA,
    phases=['train','held'],arms=['cp32','LR1e5','LR1e4'],planned_per_arm_phase=32,context_units={'train':8,'held':16},
    GPU_calls=0,optimizer_steps=0,polling=False,
    command=[str(c.study.NATIVE),str(a.ROOT/'analyze.py'),'check','--output',str(a.ROOT/'readout-001.json')])
ready['identity']=a.digest(ready);a.write(a.ROOT/'CPU_READY.json',ready);a.verify()
print(dict(ready_sha256=a.sha(a.ROOT/'CPU_READY.json'),identity=ready['identity'],pins=len(pins)))
