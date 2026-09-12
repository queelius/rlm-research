"""CPU seal with actual run-to-GPU-guard qualification, no model update."""
import importlib.metadata
import os
import subprocess
import sys
import study

def prepare():
    assert os.environ.get('CUDA_VISIBLE_DEVICES')=='' and not study.READY.exists()
    original=study.original.verify();assert study.read(study.ROOT/'CPU_TESTS.json')['returncode']==0
    rows=study.validate_inputs(study.read(study.INPUTS));assert len(rows)==32
    for name in ('PARENT_BINDING.json','PARENT_CHECKPOINT_QUALIFICATION.json'):
        assert study.sha(study.ROOT/name)==study.sha(study.SOURCE_TRAIN/name)
    study.write_x(study.ROOT/'VERSIONS.json',dict(python=sys.version,executable=sys.executable,
        packages={n:importlib.metadata.version(n) for n in ('torch','transformers','peft','safetensors','numpy')}))
    pins=dict(original['closure_sha256']);pins[str(study.original.READY)]=study.sha(study.original.READY)
    for p in study.ROOT.iterdir():
        if p.is_file():pins[str(p)]=study.sha(p)
    for p,h in pins.items():assert study.sha(p)==h,p
    ready=dict(schema='cp32-fresh8-final-rloo-LR10x-ready-v1',closure_sha256=pins,
        fixed_argv=[str(study.PYTHON),str(study.ROOT/'owner.py'),'run'],
        source_cp32_adapter_sha256=study.ADAPTER_SHA,source_native_batch_sha256=study.sha(study.INPUTS),
        original_recipe_READY_sha256=study.sha(study.original.READY),only_scientific_change='learning_rate1e-5_to1e-4',
        groups=8,trajectories=32,denominator=32,nonzero_final_actions=12,zero_advantage_skipped=20,
        fresh_AdamW_steps=1,learning_rate=study.LEARNING_RATE,initial_rng_seed=study.SEED,
        token_TIS_cap=2.,surrogate_biased=True,selected_action_tokens=5056,zero_loss_action_tokens=16055,
        science_cap_seconds=900,owner_cap_seconds=1100,external_cap_seconds=1200,
        output=str(study.OUTPUT),checkpoint=str(study.OUTPUT/'checkpoint-0001'),expected_root_alias=study.ALIAS,
        checkpoint_selection=False,new_generation_calls=0,heldout_queries=0,CPU_only=True,GPU_admission=False,
        conditional_followup='fixed original training32 and exposed short-held32 regardless training score; not implemented by this owner')
    ready['identity']=study.digest(ready);candidate=study.ROOT/'CPU_CANDIDATE_READY.json';study.write_x(candidate,ready)
    code="import study,train; study.READY=study.ROOT/'CPU_CANDIDATE_READY.json'; train.run(study.OUTPUT,study.SCIENCE_SECONDS)"
    env=dict(os.environ,CUDA_VISIBLE_DEVICES='',PYTHONDONTWRITEBYTECODE='1',TOKENIZERS_PARALLELISM='false')
    result=subprocess.run([str(study.PYTHON),'-c',code],cwd=study.ROOT,env=env,capture_output=True,text=True,timeout=120)
    assert result.returncode!=0 and 'CPU_ENTRY_VERIFIED: MAIN must assign one GPU' in result.stderr,result.stderr
    assert not study.OUTPUT.exists()
    study.write_x(study.ROOT/'CPU_ENTRY.json',dict(returncode=result.returncode,stdout=result.stdout,stderr=result.stderr,
        command=[str(study.PYTHON),'-c',code],actual_run_reached_GPU_guard_after_full_preflight=True,
        output_created=False,GPU_calls=0,research_optimizer_steps=0,candidate_READY_sha256=study.sha(candidate)))
    for p in (candidate,study.ROOT/'CPU_ENTRY.json'):pins[str(p)]=study.sha(p)
    ready.pop('identity');ready['identity']=study.digest(ready);study.write_x(study.READY,ready)
    study.verify();print(dict(identity=ready['identity'],ready_sha256=study.sha(study.READY),pins=len(pins)))

if __name__=='__main__':prepare()
