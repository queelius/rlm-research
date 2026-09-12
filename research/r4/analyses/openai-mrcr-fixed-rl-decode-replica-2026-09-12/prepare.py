"""One focused directory/seed test plus sealed inherited native-audit source."""
import json
import os
import subprocess
import time
import analyze as m

assert os.environ.get('CUDA_VISIBLE_DEVICES')==''
assert not (m.ROOT/'CPU_READY.json').exists()
m.verify()
command=['/project/alex_phd/envs/prime-rl-5990b1b/bin/python','-m','pytest','-q','-p','no:cacheprovider',str(m.ROOT/'test_analyze.py')]
started=time.time();result=subprocess.run(command,capture_output=True,text=True,timeout=120)
tests=dict(command=command,returncode=result.returncode,stdout=result.stdout,stderr=result.stderr,
    elapsed_seconds=time.time()-started,original_red='missing analyze.py assertion,1failed; then1passed',GPU_calls=0)
with (m.ROOT/'CPU_TESTS.json').open('x') as f:json.dump(tests,f,indent=2,sort_keys=True);f.write('\n')
assert result.returncode==0,result.stdout+result.stderr
paths=[m.ROOT/name for name in ('analyze.py','prepare.py','test_analyze.py','CPU_TESTS.json','RUNBOOK.md')]
paths += [m.SIDE/'READY.json',m.PRIOR/'READY.json']
ready=dict(schema='fixed-rl-decode-replica-analysis-ready-v1',created_epoch=time.time(),
    closure_sha256={str(p):m.sha(p) for p in paths},
    reused_audit='Exact reviewed stage function with only arm directory projection; rawdecode/mapping/score/cost code unchanged',
    native_or_model_calls=0,polling=False,main_owns_execution=True)
with (m.ROOT/'CPU_READY.json').open('x') as f:json.dump(ready,f,indent=2,sort_keys=True);f.write('\n')
print(dict(CPU_READY_sha256=m.sha(m.ROOT/'CPU_READY.json'),tests=result.stdout.strip()))
