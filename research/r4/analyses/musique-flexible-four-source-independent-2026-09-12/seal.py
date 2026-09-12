"""Focused CPU tests and source pins; exactly one non-polling pending check."""
import os
import subprocess
import time
import analyze as m

assert os.environ.get('CUDA_VISIBLE_DEVICES')=='' and m.a.sha(m.s.READY)==m.READY_SHA
command=[str(m.s.NATIVE),'-m','pytest','-q','-p','no:cacheprovider','test_analyze.py']
result=subprocess.run(command,cwd=m.ROOT,capture_output=True,text=True,timeout=120)
m.a.write_x(m.ROOT/'CPU_TESTS.json',{'command':command,'returncode':result.returncode,'stdout':result.stdout,'stderr':result.stderr,
             'new_GPU_or_model_calls':0,'fixtures':'Actual saved native owner→collector fixtures; valid4+0, shared-selector error, planner-only error and deliberate cross-arm payload mutation.'})
assert result.returncode==0,result.stdout+result.stderr
paths=list(m.ROOT.glob('*.py'))+[m.ROOT/'RUNBOOK.md',m.ROOT/'CPU_TESTS.json',m.PRIOR,m.s.READY,
       m.s.PRIOR/'study.py',m.s.SERVICE_ROOT/'study.py',m.s.SERVICE_ROOT/'inputs/host/HOST_GOLD.json']
paths+=list(m.SIDE.glob('*.py'))+list(m.s.INPUTS.glob('*.json'))+[m.Path(v['public_path']) for v in m.s.selected()]
paths+=list((m.SIDE/'cpu-fixture-001').rglob('*.json'))
paths+=[p for p in m.s.MODEL.iterdir() if p.suffix in ('.json','.txt','.jinja')]
source=m.a.read(m.s.READY)['closure_sha256']
for path in paths:
    if str(path) in source:assert m.a.sha(path)==source[str(path)],path
ready={'schema':'musique-flexible-four-source-independent-cpu-ready-v1','created_epoch':time.time(),
       'accepted_owner_READY_sha256':m.READY_SHA,'input_sha256':{str(p):m.a.sha(p) for p in paths},
       'command':[str(m.s.NATIVE),str(m.ROOT/'analyze.py')],'questions':12,'calls':60,'finals':24,
       'natural_calls':{'fixed':36,'flexible':48},'requires_terminal':True,'polling':False,'GPU_or_model_calls':0,
       'claim':'Independent raw-input/scoring/allocation audit; relation review inert after completion, not novel/learned routing.'}
ready['identity']=m.a.digest(ready);m.a.write_x(m.ROOT/'CPU_READY.json',ready)
pending={'checked_epoch':time.time(),'owner_terminal_present':(m.s.ATTEMPT/'OWNER_TERMINAL.json').exists(),
         'attempt':str(m.s.ATTEMPT),'check_count':1,'further_checks':'Stop until MAIN follow-up; MAIN monitors.'}
m.a.write_x(m.ROOT/'PENDING_CHECK.json',pending)
print({'READY_sha256':m.a.sha(m.ROOT/'CPU_READY.json'),'identity':ready['identity'],'pins':len(ready['input_sha256']),
       'pending_check':pending,'test_result':result.stdout})
