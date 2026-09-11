"""Freeze qualified composition sources, immutable allocation and exact fixed checkpoints."""
import os
from pathlib import Path
import subprocess
import time
import ct_study as s

def main():
    started=time.time()
    if (s.ROOT/'READY.json').exists():raise FileExistsError('already sealed')
    native=s.read(s.ROOT/'CPU_INPUT_NATIVE.json');plan=s.read(s.ROOT/'inputs/EVALUATION_PLAN.json');collision=s.read(s.ROOT/'CPU_COLLISION_RECEIPT.json')
    if len(native['rows'])!=48 or len(plan['full'])!=96 or plan['first_action'] or collision['record_id_collisions'] or collision['native_context_id_collisions']:raise ValueError('exact qualification inventory')
    for policy in plan['policy_order']:s.write(s.ROOT/('BINDING_'+policy+'.json'),s.binding(policy))
    argv=[str(s.NATIVE),'-m','pytest','-q','-p','no:cacheprovider','test_protocol.py','test_inputs.py','test_owner.py','test_native.py','--basetemp',str(s.ROOT/'qualification-final-001')]
    tested=time.time();result=subprocess.run(argv,cwd=s.ROOT,env={**os.environ,'CUDA_VISIBLE_DEVICES':'','PYTHONDONTWRITEBYTECODE':'1'},capture_output=True,text=True,timeout=180)
    s.write(s.ROOT/'CPU_REPORT.json',dict(argv=argv,returncode=result.returncode,stdout=result.stdout,stderr=result.stderr,elapsed_seconds=time.time()-tested,gpu_calls=0,scientific_model_calls=0,authored_native_fixture=True,actual_owner_service_wrapper_intercepted=True,initial_test_receipt='test_protocol import initially failed before implementation; then5unitpassed. First combined8 passed27.72s under qualification-001. Final fixture uses a nonzero cross-category total.',old_sources_unchanged=True))
    if result.returncode:raise RuntimeError(result.stdout+result.stderr)
    ancestor=s.read(s.DR/'READY.json');sources={**ancestor['source_sha256'],str(s.DR/'READY.json'):s.DR_READY_SHA}
    inputs={**ancestor['input_sha256']}
    receipt=s.read(s.ROOT/'inputs/PROVENANCE.json');inputs.update(receipt['source_sha256']);inputs.update(receipt['seed_inventory_sha256']);inputs.update(collision['source_sha256'])
    for policy in plan['policy_order']:
        chosen=s.selected(policy);directory=Path(chosen['checkpoint'])
        for name in ('adapter_model.safetensors','adapter_config.json','state.json','optimizer.pt','rng_state.pt'):inputs[str(directory/name)]=s.sha(directory/name)
    for name in ('2026-09-10-operator-dose-fresh-composition96.md','2026-09-10-operator-dose-fresh-composition96.yaml'):
        path=s.STORE/'ideas'/name;sources[str(path)]=s.sha(path)
    sources.update({str(path):s.sha(path) for path in s.ROOT.iterdir() if path.is_file() and path.name!='READY.json'})
    inputs.update({str(path):s.sha(path) for path in (s.ROOT/'inputs').glob('*.json')})
    inputs.update({str(path):s.sha(path) for path in (s.ROOT/'qualification-final-001').rglob('*') if path.is_file()})
    for path,pin in {**sources,**inputs}.items():s.dose.check(path,pin)
    ready=dict(schema='operator-composition-transfer-ready-v1',status='CPU_READY_MAIN_ACCEPTANCE_REQUIRED',source_sha256=sources,input_sha256=inputs,owner_argv=[str(s.NATIVE),str(s.ROOT/'ct_owner.py'),'run','--output',str(s.ATTEMPT)],verify_argv=[str(s.NATIVE),str(s.ROOT/'ct_owner.py'),'verify'],work_seconds=6300,owned_seconds=6450,outer_seconds=6480,phase_seconds=3000,startup_seconds=180,collection_seconds=2730,release_seconds=90,harvest_work_seconds=300,owned_emergency_seconds=150,outer_margin_seconds=30,planned_full=96,planned_first_action=0,context_clusters=8,selected_groups=128,policy_order=plan['policy_order'],base_source=s.DR.name,no_training=True,no_new_acquisition=True,physical_cost_scope='new attempted/returned native requests; unknown usage and billing retained',main_launch_only=True,cpu_only=True,created_epoch=time.time())
    ready['identity']=s.digest(ready);s.write(s.ROOT/'READY.json',ready);s.verify()
    print(dict(ready_sha256=s.sha(s.ROOT/'READY.json'),identity=ready['identity'],sources=len(sources),inputs=len(inputs),tests=result.stdout,elapsed_seconds=time.time()-started))
if __name__=='__main__':main()
