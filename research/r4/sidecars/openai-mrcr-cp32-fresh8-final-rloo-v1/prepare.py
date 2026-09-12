"""Run two focused CPU fixtures and actual entry, then freeze the complete closure."""
import importlib.metadata
import os
import subprocess
import sys
import time
import study

def prepare():
    assert os.environ.get('CUDA_VISIBLE_DEVICES')=='' and not study.READY.exists()
    data=study.read(study.INPUTS);rows=study.validate_inputs(data)
    env=dict(os.environ,CUDA_VISIBLE_DEVICES='',PYTHONDONTWRITEBYTECODE='1',TOKENIZERS_PARALLELISM='false')
    command=[str(study.PYTHON),'-m','pytest','-q','-p','no:cacheprovider','test_train.py']
    started=time.monotonic();test=subprocess.run(command,cwd=study.ROOT,env=env,capture_output=True,text=True,timeout=120)
    study.write_x(study.ROOT/'CPU_TESTS.json',dict(command=command,returncode=test.returncode,
        stdout=test.stdout,stderr=test.stderr,elapsed_seconds=time.monotonic()-started,
        original_red='Two tests failed because train.py was not implemented; preserved in session receipt.',
        CUDA_VISIBLE_DEVICES='',actual_source_trajectories=32,actual_source_calls=66,
        actual_source_reward_and_native_decode_recomputed=True,real_tiny_HF_PEFT=True,
        zero_advantage_skip_and_fixed32_denominator=True,replay_mismatch_no_step=True))
    assert test.returncode==0,test.stdout+test.stderr
    study.write_x(study.ROOT/'VERSIONS.json',dict(python=sys.version,executable=sys.executable,
        packages={n:importlib.metadata.version(n) for n in ('torch','transformers','peft','safetensors','numpy')}))
    pins=dict(data['source_sha256'])
    for path in (study.OLD/'READY.json',study.SCREEN/'READY.json'):
        r=study.read(path);pins.update(r['closure_sha256']);pins[str(path)]=study.sha(path)
    for p in (study.PYTHON,study.NATIVE,study.REVIEW/'analyze.py'):
        pins[str(p)]=study.sha(p)
    for p in study.ROOT.iterdir():
        if p.is_file():pins[str(p)]=study.sha(p)
    for p,h in pins.items():assert study.sha(p)==h,p
    ready=dict(schema='cp32-fresh8-final-rloo-ready-v1',closure_sha256=pins,
        fixed_argv=[str(study.PYTHON),str(study.ROOT/'owner.py'),'run'],
        source_cp32_adapter_sha256=study.ADAPTER_SHA,source_native_batch_sha256=study.sha(study.INPUTS),
        source_report_sha256=study.REPORT_SHA,groups=8,trajectories=32,rewards={'correct':7,'incorrect':25},
        advantage='(4*reward-group reward sum)/3',denominator=32,nonzero_final_actions=12,zero_advantage_skipped=20,
        fresh_AdamW_steps=1,learning_rate=1e-5,token_TIS_cap=2.,surrogate_biased=True,
        selected_action_tokens=data['selected_action_tokens'],zero_loss_action_tokens=data['unselected_root_action_tokens'],
        science_cap_seconds=900,owner_cap_seconds=1100,external_cap_seconds=1200,
        output=str(study.OUTPUT),checkpoint=str(study.OUTPUT/'checkpoint-0001'),
        expected_root_alias=study.ALIAS,new_generation_calls=0,heldout_queries=0,CPU_only=True,GPU_admission=False)
    ready['identity']=study.digest(ready)
    candidate=study.ROOT/'CPU_CANDIDATE_READY.json';study.write_x(candidate,ready)
    code="import study,train; study.READY=study.ROOT/'CPU_CANDIDATE_READY.json'; train.run(study.OUTPUT,study.SCIENCE_SECONDS)"
    entry=subprocess.run([str(study.PYTHON),'-c',code],cwd=study.ROOT,env=env,capture_output=True,text=True,timeout=120)
    assert entry.returncode!=0 and 'CPU_ENTRY_VERIFIED: MAIN must assign one GPU' in entry.stderr,entry.stderr
    assert not study.OUTPUT.exists()
    study.write_x(study.ROOT/'CPU_ENTRY.json',dict(command=[str(study.PYTHON),'-c',code],returncode=entry.returncode,
        stdout=entry.stdout,stderr=entry.stderr,actual_run_reached_CPU_guard_after_full_preflight=True,
        output_created=False,candidate_ready_sha256=study.sha(candidate)))
    for p in (candidate,study.ROOT/'CPU_ENTRY.json'):pins[str(p)]=study.sha(p)
    ready.pop('identity');ready['identity']=study.digest(ready);study.write_x(study.READY,ready)
    verified=study.verify();print({'identity':verified['identity'],'ready_sha256':study.sha(study.READY),'pins':len(pins)})

if __name__=='__main__':prepare()
