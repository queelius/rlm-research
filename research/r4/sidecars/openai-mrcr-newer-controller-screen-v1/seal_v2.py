"""Additive seal after the observed CPU-cost repair; no GPU/model launch."""
import os
import time
import study_v2 as s
import owner_v2
import collect_v2

def main():
    assert os.environ.get('CUDA_VISIBLE_DEVICES')=='' and not s.READY.exists() and not s.ATTEMPT.exists()
    old=s.previous.verify();test=s.read(s.ROOT/'CPU_TESTS_V2.json');timing=s.read(s.ROOT/'CPU_TIMING_V2.json')
    assert test['exit_code']==0 and test['passed']==4
    assert timing['full_repaired_native_validation_seconds']<2 and timing['actual_tokens_validated']==882
    files=list((s.ROOT/'cpu-v2-001').rglob('*.json'))
    derived=[s.read(p) for p in files if p.name=='DERIVED.json'];assert len(derived)==1
    d=derived[0];assert d['known_model_outcome'] and d['terminal_class']=='model_no_final_within_two_turns'
    assert d['root_actions_returned']==2 and d['child_actions_returned']==0 and d['initial_prefix_verified']
    assert owner_v2.s is s and collect_v2.s is s
    assert owner_v2.s.ATTEMPT==s.ROOT/'outputs/attempt-002'
    owner_v2.dependencies()
    failed=s.ROOT/'outputs/attempt-001';terminal=s.read(failed/'OWNER_TERMINAL.json')
    assert terminal['released'] and not terminal['complete']
    paths=[s.ROOT/name for name in ('READY.json','study_v2.py','native_capture_v2.py','collect_v2.py','owner_v2.py',
        'test_validator_v2.py','seal_v2.py','REPAIR_V2.md','CPU_TESTS_V2.json','CPU_TIMING_V2.json')]
    paths+=files+[failed/'OWNER_TERMINAL.json',s.STORE/'operations/2026-09-12-newer-controller-validator-stop/STOP_REQUEST.json',
        failed/'qwen3/science/native-calls/0000-result.json']
    closure=dict(old['closure_sha256'])
    for p in paths:closure[str(p)]=s.sha(p)
    for p,want in closure.items():assert s.sha(p)==want,p
    value={k:v for k,v in old.items() if k not in ('identity','created_epoch','closure_sha256')}
    value.update(schema='released-controller-screen-ready-v2',created_epoch=time.time(),
        source_READY_sha256=s.sha(s.ROOT/'READY.json'),closure_sha256=closure,
        fixed_argv=[str(s.NATIVE),str(s.ROOT/'owner_v2.py'),'run'],output=str(s.ATTEMPT),
        repair='Hoist tokenizer size once; preserve all native token bounds/EOS/usage/model checks',
        original_attempt_instrumentation_compromised=True,original_attempt_preserved_and_released=True,
        scientific_schedule_unchanged=s.digest(s.plan())==old['schedule_sha256'],
        CPU_timing_sha256=s.sha(s.ROOT/'CPU_TIMING_V2.json'),CPU_evidence_V2_sha256=s.sha(s.ROOT/'CPU_TESTS_V2.json'),
        CPU_fixture_V2_sha256={str(p):s.sha(p) for p in files})
    value['identity']=s.digest(value);s.write_x(s.READY,value);s.verify()
    print({'READY_V2_sha256':s.sha(s.READY),'identity':value['identity'],'pins':len(closure),'argv':value['fixed_argv']})

if __name__=='__main__':main()
