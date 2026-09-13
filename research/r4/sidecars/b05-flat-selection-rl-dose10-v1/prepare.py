"""Seal the single dose branch and exercise actual CPU entry; no model load."""
import json
import os
from pathlib import Path
import study as s
import train
import checkpoint

def main():
    assert os.environ.get('CUDA_VISIBLE_DEVICES')=='' and not s.READY.exists()
    assert s.sha(s.original.READY)=='7a2fe51f53402604ad3c3f437fd61d96ff347423417859b99916e720c85d6aa5'
    s.original.verify();assert s.read(s.ROOT/'CPU_TESTS.json')['returncode']==0
    original_result=s.read(s.original.OUTPUT/'RESULT.json');assert original_result['status']=='UPDATED'
    cp=s.original.OUTPUT/'checkpoint-0001'
    assert s.read(cp/'state.json')['initial_trainable_identity']==s.read(s.original.OUTPUT/'INITIAL.json')['trainable_identity']
    compile(checkpoint.qualified_source(),str(s.ROOT/'checkpoint.py')+':prospective-LR','exec')
    source=s.read(s.original.READY);closure=dict(source['closure_sha256']);closure[str(s.original.READY)]=s.sha(s.original.READY)
    for p,h in s.read(cp/'STEP_COMMIT.json')['artifacts_sha256'].items():closure[p]=h
    for p in [cp/'STEP_COMMIT.json',s.original.OUTPUT/'RESULT.json',s.original.OUTPUT/'OWNER_TERMINAL.json',
        s.ROOT/'PLAN.md',s.ROOT/'RUNBOOK.md',s.ROOT/'CPU_TESTS.json',*s.ROOT.glob('*.py')]:closure[str(p)]=s.sha(p)
    for p,h in closure.items():assert s.sha(p)==h,p
    ready=dict(schema='BA18-same-start-single-dose10-ready-v1',status='CPU_READY_MAIN_ADMISSION_REQUIRED',
        original_ready_sha256=s.sha(s.original.READY),original_initial_tensor_sha256=s.sha(s.INITIAL_REFERENCE),
        input_sha256=s.sha(s.INPUTS),held_source_sha256=s.sha(s.ORIGINAL/'HELD_PUBLIC.json'),
        learning_rate=1e-3,original_learning_rate=1e-4,optimizer_steps=1,denominator=18,nonzero_actions=8,zero_actions=10,
        unchanged_native_actions=True,unchanged_seed=s.SEED,exact_initial_tensor_gate=True,continuation=False,
        token_TIS_cap=2.,biased_token_TIS=True,replay_token_tolerance=1e-5,replay_sequence_tolerance=1e-4,
        science_seconds=900,owner_seconds=1100,external_seconds=1200,
        argv=[str(s.PYTHON),str(s.ROOT/'owner.py'),'run'],output=str(s.OUTPUT),
        source_sha256={p.name:s.sha(p) for p in s.ROOT.glob('*.py')},closure_sha256=dict(sorted(closure.items())))
    ready['identity']=s.digest(ready);s.write_x(s.READY,ready)
    try:train.run(s.OUTPUT,s.SCIENCE_SECONDS)
    except RuntimeError as e:assert str(e)=='CPU_ENTRY_VERIFIED: MAIN must assign one GPU before training'
    else:raise AssertionError('no CPU guard')
    assert not s.OUTPUT.exists()
    proof=dict(status='PASS',ready_sha256=s.sha(s.READY),identity=ready['identity'],pins=len(closure),
        actual_train_full_unmocked_preflight=True,stopped_before_model_load=True,GPU_calls=0)
    s.write_x(s.ROOT/'ENTRY_PROOF.json',proof);print(json.dumps(proof))

if __name__=='__main__':main()
