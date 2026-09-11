"""Seal an additive executable correction; original scientific identity remains exact."""
import os
import subprocess
import time
import study as s

PIN='6c511ac8ef9aec636175a79b9a76a2b776999b24a9e2e64348fbb90d40ef2a4a'
s.check(s.ROOT/'READY.json',PIN);original=s.verify()
argv=[str(s.NATIVE),'-m','pytest','-q',str(s.ROOT/'test_contract.py'),str(s.ROOT/'test_runtime.py'),str(s.ROOT/'test_entrypoints_v2.py')]
result=subprocess.run(argv,cwd=s.ROOT,capture_output=True,text=True,timeout=90,env={**os.environ,'CUDA_VISIBLE_DEVICES':'','PYTHONDONTWRITEBYTECODE':'1','OMP_NUM_THREADS':'1'})
s.write(s.ROOT/'CPU_TESTS_V2.json',dict(argv=argv,returncode=result.returncode,stdout=result.stdout,stderr=result.stderr,gpu_calls=0))
if result.returncode:raise ValueError('corrected executable tests failed')
names=['readout_v2.py','launch_v2.py','seal_v2.py','test_entrypoints_v2.py','ENTRYPOINT_AMENDMENT_V2.md','ENTRYPOINT_FAILURE_V1.json','CPU_TESTS_V2.json','READY.json']
source={**original['source_sha256'],**{str(s.ROOT/name):s.sha(s.ROOT/name) for name in names}}
value={**original,'source_sha256':source,'input_sha256':original['input_sha256'],
 'status':'CPU_READY_ADDITIVE_ENTRYPOINT_CORRECTION_FOR_MAIN_ACCEPTANCE',
 'original_ready_sha256':PIN,'scientific_identity':original['identity'],'prepared_epoch':time.time(),
 'argv':[str(s.NATIVE),str(s.ROOT/'launch_v2.py'),'run','--output',str(s.ROOT/'outputs/attempt-001')],
 'verify_argv':[str(s.NATIVE),str(s.ROOT/'launch_v2.py'),'verify'],
 'correction':'flat exact entrypoints; both PLAN references point to prepared-v2; scientific inputs/identity unchanged'}
value.pop('identity');value['identity']=s.digest(value);s.write(s.ROOT/'READY_V2.json',value)
print({'ready_v2_sha256':s.sha(s.ROOT/'READY_V2.json'),'identity':value['identity'],'scientific_identity':original['identity']},flush=True)
