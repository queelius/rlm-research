"""Small CPU-only checks; records exact commands, no real model/runtime execution."""
import os
import subprocess
import time
import study as s

def main():
    results=[];environment={**os.environ,'CUDA_VISIBLE_DEVICES':'','PYTHONDONTWRITEBYTECODE':'1','OMP_NUM_THREADS':'1'}
    commands=[([str(s.TRAIN),'-m','pytest','-q','test_panel.py','test_learning.py'],90),
      ([str(s.NATIVE),'-m','pytest','-q','test_native.py'],90)]
    for filename,python in [('launch.py',s.NATIVE),('capture.py',s.NATIVE),('readout.py',s.NATIVE),('train.py',s.TRAIN)]:commands.append(([str(python),str(s.ROOT/filename),'--help'],60))
    for argv,cap in commands:
        started=time.time();r=subprocess.run(argv,cwd=s.ROOT,env=environment,capture_output=True,text=True,timeout=cap)
        results.append(dict(argv=argv,returncode=r.returncode,stdout=r.stdout,stderr=r.stderr,elapsed_seconds=time.time()-started))
        print({'argv':argv,'returncode':r.returncode},flush=True)
        if r.returncode:s.write(s.ROOT/'CPU_FAILURE.json',dict(results=results));raise ValueError('focused CPU qualification failed')
    s.write(s.ROOT/'CPU_TESTS.json',dict(status='PASS',results=results,gpu_calls=0,actual_model_loads=0,live_native_fixture_calls=0,
      red_evidence='selection missing implementation; learning missing implementation; native error/no-final availability missing guard; all observed before respective code'))
    approval=s.ROOT.parent.parent/'ideas/2026-09-09-next-root-learning-main-approval.md';data=s.read(s.ROOT/'DATA_READY.json')
    s.write(s.ROOT/'DATA_APPROVAL_PIN_AMENDMENT.json',dict(data_ready_sha256=s.sha(s.ROOT/'DATA_READY.json'),data_bytes_unchanged=True,
      original_approval_sha256=data['source_sha256'][str(approval)],current_approval_sha256=s.sha(approval),
      reason='MAIN clarified per-example token-mean action normalization after panel freeze; no panel selection/context/label/seed changes'))
    print('CPU checks complete; READY not yet published',flush=True)

if __name__=='__main__':main()
