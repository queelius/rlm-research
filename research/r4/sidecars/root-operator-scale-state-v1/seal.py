"""Freeze exact immutable scale24 sources, inputs and bounded CPU fixtures."""
import os
from pathlib import Path
import subprocess
import time
import ss_study as s

def main():
    if (s.ROOT/'READY.json').exists():raise FileExistsError('already sealed')
    started=time.time();plan=s.read(s.ROOT/'inputs/EVALUATION_PLAN.json');native=s.read(s.ROOT/'CPU_INPUT_NATIVE.json');oracle=s.read(s.ROOT/'CPU_SOURCE_CHILD.json')
    assert len(plan['full'])==24 and plan['first_action']==[] and len(native['rows'])==24 and oracle['rows_verified']==1024
    s.write(s.ROOT/'BINDING_sft24.json',s.binding())
    argv=[str(s.NATIVE),'-m','pytest','-q','-p','no:cacheprovider','test_plan.py','test_runtime.py','--basetemp',str(s.ROOT/'qualification-final-001')]
    tested=time.time();result=subprocess.run(argv,cwd=s.ROOT,env={**os.environ,'CUDA_VISIBLE_DEVICES':'','PYTHONDONTWRITEBYTECODE':'1'},capture_output=True,text=True,timeout=180)
    s.write(s.ROOT/'CPU_REPORT.json',dict(argv=argv,returncode=result.returncode,stdout=result.stdout,stderr=result.stderr,elapsed_seconds=time.time()-tested,gpu_calls=0,scientific_model_calls=0,authored_native_root_calls=4,authored_native_child_calls=2,actual_owner_service_wrapper_intercepted=True,earlier_receipts=['RED.xml','GREEN_PLAN.xml','CPU_TESTS.xml','CPU_ENTRY.xml'],initial_failure='Two test-first missing modules; later entry teardown mock replaced by inherited dependency reinstallation, fixture only fixed. No scientific source/input change.'))
    if result.returncode:raise RuntimeError(result.stdout+result.stderr)
    sources={**s.ct_ready['source_sha256'],str(s.CT/'READY.json'):s.CT_READY_SHA};inputs={**s.ct_ready['input_sha256']}
    provenance=s.read(s.ROOT/'inputs/PROVENANCE.json');inputs.update(provenance['source_sha256']);inputs.update(oracle['source_sha256'])
    for name in ('2026-09-10-operator-scale-state24.md','2026-09-10-operator-scale-state24.yaml'):
        path=s.STORE/'ideas'/name;sources[str(path)]=s.sha(path)
    sources.update({str(path):s.sha(path) for path in s.ROOT.iterdir() if path.is_file() and path.name!='READY.json'})
    inputs.update({str(path):s.sha(path) for path in (s.ROOT/'inputs').glob('*.json')})
    inputs.update({str(path):s.sha(path) for path in (s.ROOT/'qualification-final-001').rglob('*') if path.is_file()})
    for path,pin in {**sources,**inputs}.items():s.dose.check(path,pin)
    ready=dict(schema='operator-scale-state-ready-v1',status='CPU_READY_MAIN_ACCEPTANCE_REQUIRED',source_sha256=sources,input_sha256=inputs,owner_argv=[str(s.NATIVE),str(s.ROOT/'ss_owner.py'),'run','--output',str(s.ATTEMPT)],verify_argv=[str(s.NATIVE),str(s.ROOT/'ss_owner.py'),'verify'],work_seconds=2220,owned_seconds=2370,outer_seconds=2400,startup_seconds=180,collection_seconds=1950,harvest_seconds=90,release_emergency_seconds=150,outer_margin_seconds=30,planned_full=24,planned_first_action=0,parent_clusters=4,selected_unique_groups=1024,nested_sizes=[16,128,256],policy_order=['sft24'],no_training=True,no_new_external_asset_acquisition=True,optional_child_acquisition_permitted=True,main_launch_only=True,cpu_only=True,created_epoch=time.time())
    ready['identity']=s.digest(ready);s.write(s.ROOT/'READY.json',ready);s.verify()
    print(dict(ready_sha256=s.sha(s.ROOT/'READY.json'),identity=ready['identity'],sources=len(sources),inputs=len(inputs),tests=result.stdout,elapsed_seconds=time.time()-started))
if __name__=='__main__':main()
