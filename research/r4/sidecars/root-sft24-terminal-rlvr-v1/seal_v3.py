"""CPU-only write-once V3 closure; all original scientific files remain untouched."""
import os
from pathlib import Path
import subprocess
import time
import warm_resume_v3 as r
import warm_wire_v3 as wire

s=r.study
def main():
    if any((s.ROOT/name).exists() for name in ('READY_v3.json','RESUME_BINDING_v3.json','CPU_REPORT_v3.json')):
        raise FileExistsError('V3 seal already exists')
    proof=r.source_proof();s.write(s.ROOT/'RESUME_BINDING_v3.json',proof)
    tests=[s.ROOT/'test_v3.py',wire.SOURCE.with_name('test_wire_ledger.py')]
    argv=[str(s.NATIVE),'-m','pytest','-q','-p','no:cacheprovider',*map(str,tests)]
    begin=time.time();run=subprocess.run(argv,cwd=s.ROOT,env={**os.environ,'CUDA_VISIBLE_DEVICES':'','PYTHONDONTWRITEBYTECODE':'1'},text=True,capture_output=True,timeout=120)
    report=dict(argv=argv,returncode=run.returncode,elapsed_seconds=time.time()-begin,stdout=run.stdout,stderr=run.stderr,
                gpu_calls=0,model_loads=0,native_original_replay='V3_PREFLIGHT.json',no_recapture=True)
    s.write(s.ROOT/'CPU_REPORT_v3.json',report)
    if run.returncode:raise RuntimeError('focused V3 tests failed; receipt retained')
    old=s.read(s.ROOT/'READY_v2.json');qualification=s.read(s.ROOT/'V2_QUALIFICATION.json');campaign=s.read(s.ROOT/'CAMPAIGN.json')
    sources={**campaign['source_sha256'],**qualification['source_sha256'],**old['source_sha256']}
    inputs={**campaign['input_sha256'],**qualification['input_sha256'],**old['input_sha256']}
    for name in ('warm_resume_v3.py','warm_wire_v3.py','warm_owner_v3.py','test_v3.py','seal_v3.py','RESUME_DESIGN_v3.md','PLAN_v3.md'):
        path=s.ROOT/name;sources[str(path)]=s.sha(path)
    sources[str(wire.SOURCE)]=wire.SOURCE_SHA
    sources[str(wire.SOURCE.with_name('test_wire_ledger.py'))]=s.sha(wire.SOURCE.with_name('test_wire_ledger.py'))
    for path in (r.ORIGINAL/'window-01/collection').rglob('*'):
        if path.is_file():inputs[str(path)]=s.sha(path)
    inputs.update(proof['source_sha256'])
    for name in ('READY_v2.json','V2_QUALIFICATION.json','RESUME_BINDING_v3.json','V3_PREFLIGHT.json','CPU_REPORT_v3.json'):
        path=s.ROOT/name;inputs[str(path)]=s.sha(path)
    cleanup=s.ROOT/'V3_EXTERNAL_CLEANUP.json'
    if cleanup.exists():
        inputs[str(cleanup)]=s.sha(cleanup)
        for path,pin in s.read(cleanup)['source_sha256'].items():s.check(path,pin);inputs[path]=pin
    for path,pin in {**sources,**inputs}.items():s.check(path,pin)
    ready=dict(schema='warm-terminal-rlvr-resume-v3',attempt=str(r.ATTEMPT),
        source_sha256=sources,input_sha256=inputs,previous_ready_sha256=s.sha(s.ROOT/'READY_v2.json'),
        resume_binding_sha256=s.sha(s.ROOT/'RESUME_BINDING_v3.json'),
        owner_argv=[str(s.NATIVE),str(s.ROOT/'warm_owner_v3.py'),'run','--output',str(r.ATTEMPT)],
        verify_argv=[str(s.NATIVE),str(s.ROOT/'warm_owner_v3.py'),'verify'],
        outer_seconds=10419,owned_seconds=10299,work_seconds=10119,training_side_seconds=5019,final_seconds=5100,
        original_seconds_charged=381,combined_active_outer_seconds=10800,release_seconds=90,fresh_window_guard_seconds=1380,
        scheduled_windows=8,planned_training=192,original_training_slots_reused=24,new_training_slots_max=168,planned_readout=96,
        original_readout_dispatches=0,no_reacquisition=True,no_training_done_in_original=True,
        original_immutable_unreleased_receipt_preserved=True,external_cleanup_receipt=str(cleanup) if cleanup.exists() else None,
        author='runtime_port',independent_reviewers=['question_cards','MAIN'],main_launch_only=True,created_epoch=time.time())
    ready['identity']=s.digest(ready);s.write(s.ROOT/'READY_v3.json',ready);r.verify()
    print(dict(identity=ready['identity'],ready_sha256=s.sha(s.ROOT/'READY_v3.json'),sources=len(sources),inputs=len(inputs),tests=run.stdout))
if __name__=='__main__':main()
