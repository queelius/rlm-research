"""Freeze actual completed endpoint plus unchanged two-panel readout closures."""
import os
from pathlib import Path
import subprocess
import time
import checkpoint
import study

def prepare():
    assert os.environ.get('CUDA_VISIBLE_DEVICES')=='' and not study.READY.exists()
    qualification=checkpoint.verify_checkpoint()
    study.write_x(study.ROOT/'CHECKPOINT_QUALIFICATION.json',qualification)
    command=[str(study.NATIVE),'-m','pytest','-q','-p','no:cacheprovider','test_eval.py']
    env=dict(os.environ,CUDA_VISIBLE_DEVICES='',PYTHONDONTWRITEBYTECODE='1',TOKENIZERS_PARALLELISM='false')
    started=time.monotonic();result=subprocess.run(command,cwd=study.ROOT,env=env,capture_output=True,text=True,timeout=120)
    study.write_x(study.ROOT/'CPU_TESTS.json',dict(command=command,returncode=result.returncode,
        stdout=result.stdout,stderr=result.stderr,elapsed_seconds=time.monotonic()-started,
        actual_completed_checkpoint_qualification=qualification,original_red='2 tests failed before study.py existed',CUDA_VISIBLE_DEVICES=''))
    assert result.returncode==0,result.stdout+result.stderr
    pins={};descriptors=[study.train.READY,study.SHORT/'CPU_READY.json',study.LONG/'READY_V2.json']
    for p in descriptors:
        r=study.read(p);pins.update(r.get('closure_sha256',{}));pins[str(p)]=study.sha(p)
    for p in checkpoint.OUTPUT.rglob('*'):
        if p.is_file():pins[str(p)]=study.sha(p)
    inputs={};baselines={}
    for phase,count in [('held',32),('long',16)]:
        assert len(study.schedule(phase))==count
        for p in study.input_dir(phase).rglob('*'):
            if p.is_file():pins[str(p)]=study.sha(p)
        source=study.BASELINES[phase];terminal=study.read(source/'OWNER_TERMINAL.json')
        r=study.read(source/'science/RESULT.json')
        assert terminal['complete'] and terminal['released'] and not terminal.get('errors')
        assert r['complete'] and r['recorded']==r['planned']==count and r['scientifically_available']==count
        assert r['all_causal_mappings_complete'] and r['all_initial_root_prefixes_verified'] and r['all_action_caps_respected']
        assert r['child_actions']==0
        contract=study.read(source/'science/TERMINAL_STRIP_CONTRACT.json');assert contract['condition']=='terminal-strip-disabled'
        for p in (source/'science').rglob('*'):
            if p.is_file():pins[str(p)]=study.sha(p)
        for p in (source/'OWNER_RUN.json',source/'OWNER_TERMINAL.json',source/'owned-service/BINDING.json',source/'owned-service/PREFLIGHT.json'):
            pins[str(p)]=study.sha(p)
        inputs[phase]=dict(schedule_sha256=study.digest(study.schedule(phase)),planned=count,
            unique_contexts=len({x['record_id'] for x in study.schedule(phase)}),input_dir=str(study.input_dir(phase)))
        baselines[phase]=dict(output=str(source),result_sha256=study.sha(source/'science/RESULT.json'),
            owner_terminal_sha256=study.sha(source/'OWNER_TERMINAL.json'),available=count,correct=r['raw_exact'],
            immutable_qualified_prior=True,new_baseline_queries=0)
    for p in study.ROOT.iterdir():
        if p.is_file():pins[str(p)]=study.sha(p)
    for p,h in pins.items():assert study.sha(p)==h,p
    ready=dict(schema='fixedbaseline-final-RL-two-panel-eval-ready-v1',closure_sha256=pins,
        inputs=inputs,baselines=baselines,checkpoint_qualification=qualification,
        fixed_argv={phase:[str(study.NATIVE),str(study.ROOT/'owner.py'),'run','--phase',phase] for phase in study.CAPS},
        caps=study.CAPS,temperature=.5,max_action_tokens=2048,total_actions=6,children=0,
        planned=48,short_contexts=16,short_repeats=2,long_contexts=16,
        no_outcome_manipulation_gate=True,endpoint_selection=False,
        terminal_condition='terminal-strip-disabled',GPU_admission=False)
    ready['identity']=study.digest(ready);study.write_x(study.READY,ready)
    study.verify();print({'identity':ready['identity'],'ready_sha256':study.sha(study.READY),'pins':len(pins)})

if __name__=='__main__':prepare()
