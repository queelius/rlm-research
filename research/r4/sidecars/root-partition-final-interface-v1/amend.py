"""Seal only the additive wrong-route scoring/owner amendment."""
import os
import subprocess
import study as s

def main():
    original=s.verify()
    argv=[str(s.NATIVE),'-m','unittest','-v','test_scoring_v2']
    result=subprocess.run(argv,cwd=s.ROOT,capture_output=True,text=True,timeout=60,env={**os.environ,'CUDA_VISIBLE_DEVICES':'','PYTHONDONTWRITEBYTECODE':'1'})
    sources={str(s.ROOT/name):s.sha(s.ROOT/name) for name in ('scoring_v2.py','owner_v2.py','collect_v2.py','test_scoring_v2.py','amend.py','SCORING_AMENDMENT.md','READY.json')}
    reference=s.AUDIT.parent/'leaf-free-id-live-2026-09-09/details.py';sources[str(reference)]=s.sha(reference)
    s.write(s.ROOT/'CPU_TESTS_V2.json',dict(argv=argv,returncode=result.returncode,stdout=result.stdout,stderr=result.stderr,source_sha256=sources,gpu_calls=0,service_calls=0))
    if result.returncode:raise ValueError('amendment focused regression failed')
    sources[str(s.ROOT/'CPU_TESTS_V2.json')]=s.sha(s.ROOT/'CPU_TESTS_V2.json')
    value=dict(status='CPU_READY_SCORING_AMENDMENT_FOR_MAIN_ACCEPTANCE',original_ready_sha256=s.sha(s.ROOT/'READY.json'),original_identity=original['identity'],source_sha256=sources,
        argv=[str(s.NATIVE),str(s.ROOT/'owner_v2.py'),'run','--output',str(s.ATTEMPT)],outer_seconds=900,planned_calls=24,
        protocol_prompts_seeds_and_output_namespace_unchanged=True,verified_wrong_route='observed invalid0; no execution',inconsistent_native_identity='NULL',gpu_calls=0,service_calls=0)
    value['identity']=s.digest(value);s.write(s.ROOT/'READY_V2.json',value);print(s.sha(s.ROOT/'READY_V2.json'))

if __name__=='__main__':main()
