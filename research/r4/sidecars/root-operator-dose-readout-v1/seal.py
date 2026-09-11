"""Freeze future readout code without observing/selecting a final training result."""
import os
import subprocess
import time
import dr_study as s

def main():
    started=time.time();training=s.dose.verify()
    if (s.ROOT/'READY.json').exists():raise ValueError('already sealed')
    receipt=s.read(s.ROOT/'INPUT_RECEIPT.json')
    for r in receipt['files']:
        if s.sha(r['source'])!=r['sha256'] or s.sha(r['target'])!=r['sha256']:raise ValueError('fixed planned input bytes changed')
    native=s.read(s.ROOT/'CPU_INPUT_NATIVE.json');plan=s.read(s.ROOT/'inputs/EVALUATION_PLAN.json')
    if len(native['rows'])!=48 or len(plan['full'])!=96 or len(plan['first_action'])!=24:raise ValueError('complete prepared native inventory')
    # Pin only the fixed6 source now. Future fixed24 is authenticated at launch, never selected by outcome.
    control=s.binding('sft6');s.write(s.ROOT/'CONTROL_BINDING.json',control)
    argv=[str(s.NATIVE),'-m','pytest','-q','-p','no:cacheprovider','test_protocol.py','test_probe_transport.py','test_owner.py','test_native.py','--basetemp',str(s.ROOT/'qualification-final-001')]
    test=subprocess.run(argv,cwd=s.ROOT,env={**os.environ,'CUDA_VISIBLE_DEVICES':'','PYTHONDONTWRITEBYTECODE':'1'},text=True,capture_output=True,timeout=180)
    evidence=dict(argv=argv,returncode=test.returncode,stdout=test.stdout,stderr=test.stderr,gpu_calls=0,authored_native_fixture=True,scientific_model_calls=0,actual_owner_service_wrapper_intercepted=True,first_action_programs_never_executed=True,preparation_failure='Initial histogram JSON reserialization changed numeric key ordering; preserved under preparation-attempt-001, corrected to byte-copy. First native fixture caught unresolved original lazy protocol namespace; preserved under qualification-native-001 and fixed by resolving against original study before new aliases.',elapsed_seconds=time.time()-started)
    s.write(s.ROOT/'CPU_REPORT.json',evidence)
    if test.returncode:raise RuntimeError(test.stdout+test.stderr)
    sources={**training['source_sha256'],str(s.TRAINING/'READY.json'):s.TRAIN_READY_SHA}
    sources.update({str(p):s.sha(p) for p in s.ROOT.iterdir() if p.is_file() and p.name!='READY.json'})
    inputs={**training['input_sha256'],**{str(p):s.sha(p) for p in (s.ROOT/'inputs').glob('*.json')}}
    artifacts={str(p):s.sha(p) for p in (s.ROOT/'qualification-final-001').rglob('*') if p.is_file()}
    inputs.update(artifacts)
    for path,pin in {**sources,**inputs}.items():s.dose.check(path,pin)
    ready=dict(schema='operator-dose-readout-ready-v1',status='CPU_READY_PENDING_FIXED24_COMPLETION',source_sha256=sources,input_sha256=inputs,training_ready_sha256=s.TRAIN_READY_SHA,training_dependency=str(s.dose.ATTEMPT/'OWNER_TERMINAL.json'),require_training_complete_released=True,future24_pin_policy='all18 committed checkpoint links plus fixed24 selected artifact hashes authenticated before any service; no outcome selection or partial substitution',owner_argv=[str(s.NATIVE),str(s.ROOT/'dr_owner.py'),'run','--output',str(s.ATTEMPT)],verify_argv=[str(s.NATIVE),str(s.ROOT/'dr_owner.py'),'verify'],work_seconds=6300,owned_seconds=6450,outer_seconds=6480,prior_training_outer_seconds=4320,combined_outer_seconds=10800,planned_full=96,planned_first_action=24,policy_order=plan['policy_order'],no_training=True,no_new_data_acquisition=True,prepared_catalog_child_training_exposure_disclosed=True,main_launch_only=True,cpu_only=True)
    ready['identity']=s.digest(ready);s.write(s.ROOT/'READY.json',ready);s.verify()
    print(dict(ready_sha256=s.sha(s.ROOT/'READY.json'),identity=ready['identity'],source_pins=len(sources),input_pins=len(inputs),cpu_report_sha256=s.sha(s.ROOT/'CPU_REPORT.json'),tests=test.stdout,elapsed_seconds=time.time()-started))

if __name__=='__main__':main()
