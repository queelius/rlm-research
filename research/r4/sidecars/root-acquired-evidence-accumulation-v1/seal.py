"""Freeze this CPU-qualified32-root package; no launch authority."""
import os
import subprocess
import time
import ae_study as s

def main():
    if (s.ROOT/'READY.json').exists():raise FileExistsError('already immutable READY')
    started=time.time();s.write(s.ROOT/'BINDING_sft24.json',s.binding())
    tests=['test_decoder.py','test_inputs.py','test_runtime.py','test_owner.py']
    argv=[str(s.NATIVE),'-m','pytest','-q','-p','no:cacheprovider',*tests,'--basetemp',str(s.ROOT/'qualification-final-001')]
    begin=time.time();result=subprocess.run(argv,cwd=s.ROOT,env={**os.environ,'CUDA_VISIBLE_DEVICES':'','PYTHONDONTWRITEBYTECODE':'1'},capture_output=True,text=True,timeout=240)
    s.write(s.ROOT/'CPU_REPORT.json',dict(argv=argv,returncode=result.returncode,stdout=result.stdout,stderr=result.stderr,elapsed_seconds=time.time()-begin,scientific_model_calls=0,gpu_calls=0,authored_native_root_calls=6,authored_native_child_calls=4,actual_owner_service_wrapper_intercepted=True,ledger_not_in_root_prompt_or_observations=True,synthetic_fixture_not_scientific_evidence=True,earlier_red_receipts=['RED_DECODER.xml','RED_RUNTIME.xml','RED_OWNER.xml']))
    if result.returncode:raise RuntimeError(result.stdout+result.stderr)
    sources={**s.ss_ready['source_sha256'],str(s.SS/'READY.json'):s.SS_READY_SHA};inputs={**s.ss_ready['input_sha256']}
    proof=s.read(s.ROOT/'inputs/PROVENANCE.json');inputs.update(proof['source_sha256']);inputs.update(proof['seed_inventory_sha256'])
    for name in ('2026-09-10-acquired-evidence-accumulation-design.md','2026-09-10-acquired-evidence-accumulation-design.yaml'):
        path=s.STORE/'ideas'/name;sources[str(path)]=s.sha(path)
    sources.update({str(path):s.sha(path) for path in s.ROOT.iterdir() if path.is_file() and path.name!='READY.json'})
    inputs.update({str(path):s.sha(path) for path in (s.ROOT/'inputs').glob('*.json')})
    inputs.update({str(path):s.sha(path) for path in (s.ROOT/'qualification-final-001').rglob('*') if path.is_file()})
    for path,pin in {**sources,**inputs}.items():s.dose.check(path,pin)
    ready=dict(schema='acquired-evidence-accumulation-ready-v1',status='CPU_READY_MAIN_ACCEPTANCE_REQUIRED',source_sha256=sources,input_sha256=inputs,owner_argv=[str(s.NATIVE),str(s.ROOT/'ae_owner.py'),'run','--output',str(s.ATTEMPT)],verify_argv=[str(s.NATIVE),str(s.ROOT/'ae_owner.py'),'verify'],work_seconds=1650,owned_seconds=1770,outer_seconds=1800,startup_seconds=180,collection_seconds=1440,harvest_seconds=30,release_seconds=120,outer_margin_seconds=30,planned_full=32,planned_first_action=0,parent_clusters=4,paired_blocks=16,sizes=[128,256],arms=['B','C'],policy_order=['sft24'],no_training=True,structural_decoder_admission_not_authenticated_source=True,post_rollout_ledger_is_runtime_writable=True,main_launch_only=True,created_epoch=time.time())
    ready['identity']=s.digest(ready);s.write(s.ROOT/'READY.json',ready);s.verify()
    print(dict(ready_sha256=s.sha(s.ROOT/'READY.json'),identity=ready['identity'],sources=len(sources),inputs=len(inputs),tests=result.stdout,elapsed_seconds=time.time()-started))

if __name__=='__main__':main()
