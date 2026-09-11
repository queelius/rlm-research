"""Focused CPU closure; no scientific GPU gate or model acquisition."""
import os
import subprocess
import time
import qs_study as s
def main():
    if (s.ROOT/'READY.json').exists():raise FileExistsError('immutable READY')
    started=time.time();tests=['test_problem.py','test_inputs.py','test_capture_training.py','test_train_owner.py']
    argv=[str(s.NATIVE),'-m','pytest','-q','-p','no:cacheprovider',*tests,'--basetemp',str(s.ROOT/'qualification-final-002')]
    result=subprocess.run(argv,cwd=s.ROOT,env={**os.environ,'CUDA_VISIBLE_DEVICES':'','PYTHONDONTWRITEBYTECODE':'1'},capture_output=True,text=True,timeout=600)
    s.write(s.ROOT/'CPU_REPORT_v2.json',dict(argv=argv,returncode=result.returncode,stdout=result.stdout,stderr=result.stderr,elapsed_seconds=time.time()-started,scientific_model_calls=0,gpu_calls=0,authored_native_child_responses=3,authored_native_root_targets=9,trainer_entry_native_teacher_expansion='one actual authored native trajectory copied72 times for CPU linkage only',tiny_numerical_vocabulary='31-way modulo targets; original captured IDs/masks/lengths preserved until CE backend',tiny_trainable_tensors=504,tiny_real_optimizer_updates=6,actual_TRAIN_import_no_model=True,actual_owner_service_wrapper_intercepted=True,real_GPU_cost_gate_not_executed=True,prior_failed_receipt='CPU_REPORT.json; unsorted fixture glob selected later root as first, no scientific source/input change'))
    if result.returncode:raise RuntimeError(result.stdout+result.stderr)
    sources={**s.cf_ready['source_sha256'],str(s.CF/'READY.json'):s.CF_READY_SHA};inputs={**s.cf_ready['input_sha256']}
    proof=s.read(s.ROOT/'inputs/PROVENANCE.json');inputs.update(proof['source_sha256'])
    for stem in ('2026-09-10-question-sensitive-sft72-allocation-proposal','2026-09-10-card-to-question-sensitive-training-options'):
        for suffix in ('md','yaml'):
            path=s.STORE/'ideas'/(stem+'.'+suffix)
            if path.exists():sources[str(path)]=s.sha(path)
    sources.update({str(path):s.sha(path) for path in s.ROOT.iterdir() if path.is_file() and path.name!='READY.json'})
    inputs.update({str(path):s.sha(path) for path in (s.ROOT/'inputs').glob('*.json')})
    for directory in ('qualification-final-001','qualification-final-002'):inputs.update({str(path):s.sha(path) for path in (s.ROOT/directory).rglob('*') if path.is_file()})
    for path,pin in {**sources,**inputs}.items():
        if s.sha(path)!=pin:raise ValueError('active closure changed '+path)
    ready=dict(schema='question-sensitive-sft72-ready-v1',status='CPU_READY_MAIN_ACCEPTANCE_REQUIRED',source_sha256=sources,input_sha256=inputs,owner_argv=[str(s.NATIVE),str(s.ROOT/'qs_owner.py'),'run','--output',str(s.ATTEMPT)],verify_argv=[str(s.NATIVE),str(s.ROOT/'qs_owner.py'),'verify'],outer_seconds=8100,owned_seconds=8070,work_seconds=7920,training_trajectories=72,actual_child_acquisitions_planned=72,authored_current_root_actions_planned=216,full_updates=6,fresh_adam=True,trainable_tensors=504,planned_protected=144,planned_dev=16,planned_full=160,parent_protected_clusters=8,source_contexts=20,source_groups=320,source_pool_eligible=proof['eligible'],no_test_card=True,no_retry=True,no_gold_repair=True,no_partial_fixed6_substitution=True,gate='approved six predetermined finite/native-mask/memory/cost only; actual GPU measurement pending MAIN launch',all_available_semantic_review_required=True,no_GPU_or_service_launched=True,main_launch_only=True,created_epoch=time.time())
    ready['identity']=s.digest(ready);s.write(s.ROOT/'READY.json',ready);s.verify()
    print(dict(ready_sha256=s.sha(s.ROOT/'READY.json'),identity=ready['identity'],source_pins=len(sources),input_pins=len(inputs),tests=result.stdout,elapsed_seconds=time.time()-started))
if __name__=='__main__':main()
