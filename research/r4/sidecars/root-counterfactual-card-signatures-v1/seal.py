"""Freeze only focused CPU qualification and the approved four-cell96 package."""
import os
import subprocess
import time
import cf_study as s

def main():
    if (s.ROOT/'READY.json').exists():raise FileExistsError('already immutable READY')
    started=time.time();s.write(s.ROOT/'BINDING_sft24.json',s.binding())
    tests=['test_task.py','test_inputs.py','test_native.py','test_owner.py']
    argv=[str(s.NATIVE),'-m','pytest','-q','-p','no:cacheprovider',*tests,'--basetemp',str(s.ROOT/'qualification-final-001')]
    begin=time.time();result=subprocess.run(argv,cwd=s.ROOT,env={**os.environ,'CUDA_VISIBLE_DEVICES':'','PYTHONDONTWRITEBYTECODE':'1'},capture_output=True,text=True,timeout=360)
    s.write(s.ROOT/'CPU_REPORT.json',dict(argv=argv,returncode=result.returncode,stdout=result.stdout,stderr=result.stderr,elapsed_seconds=time.time()-begin,scientific_model_calls=0,gpu_calls=0,authored_native_root_calls=12,authored_native_child_calls=4,actual_owner_service_wrapper_intercepted=True,synthetic_fixture_not_scientific_evidence=True,earlier_red_receipts=['RED_TASK_INPUTS.xml','RED_INPUTS_BOUNDARY.xml','RED_NATIVE_OWNER.xml']))
    if result.returncode:raise RuntimeError(result.stdout+result.stderr)
    sources={**s.ph_ready['source_sha256'],str(s.PH/'READY.json'):s.PH_READY_SHA};inputs={**s.ph_ready['input_sha256']}
    proof=s.read(s.ROOT/'inputs/PROVENANCE.json');inputs.update(proof['source_sha256']);inputs.update(proof['seed_inventory_sha256'])
    for stem in ('2026-09-10-counterfactual-operator-signatures','2026-09-10-counterfactual-card96-addendum'):
        for ext in ('md','yaml'):
            path=s.STORE/'ideas'/(stem+'.'+ext);sources[str(path)]=s.sha(path)
    sources.update({str(path):s.sha(path) for path in s.ROOT.iterdir() if path.is_file() and path.name!='READY.json'})
    inputs.update({str(path):s.sha(path) for path in (s.ROOT/'inputs').glob('*.json')})
    inputs.update({str(path):s.sha(path) for path in (s.ROOT/'qualification-final-001').rglob('*') if path.is_file()})
    for path,pin in {**sources,**inputs}.items():s.dose.check(path,pin)
    ready=dict(schema='counterfactual-card-signatures-ready-v1',status='CPU_READY_MAIN_ACCEPTANCE_REQUIRED',source_sha256=sources,input_sha256=inputs,owner_argv=[str(s.NATIVE),str(s.ROOT/'cf_owner.py'),'run','--output',str(s.ATTEMPT)],verify_argv=[str(s.NATIVE),str(s.ROOT/'cf_owner.py'),'verify'],work_seconds=3450,owned_seconds=3570,outer_seconds=3600,startup_seconds=180,collection_seconds=3240,harvest_seconds=30,release_seconds=120,outer_margin_seconds=30,planned_full=96,planned_first_action=0,parent_clusters=8,paired_blocks=24,cells=s.CELLS,policy_order=['sft24'],no_training=True,gate_sha256=s.GATE_SHA,card_sha256=s.sha(s.ROOT/'CARD.txt'),card_tokens=proof['card_tokens'],original_U_native_prefix_and_files_unchanged=True,within_variant_U_P_files_identical=True,counterfactual_weight_text_mirrors_verified=True,explicit_algorithm_instruction_context_package=True,no_primitive_regression_estimand=True,practical_availability_gate='counterfactual_P >= counterfactual_U; original direction reported separately',main_launch_only=True,created_epoch=time.time())
    ready['identity']=s.digest(ready);s.write(s.ROOT/'READY.json',ready);s.verify()
    print(dict(ready_sha256=s.sha(s.ROOT/'READY.json'),identity=ready['identity'],sources=len(sources),inputs=len(inputs),tests=result.stdout,elapsed_seconds=time.time()-started))

if __name__=='__main__':main()
