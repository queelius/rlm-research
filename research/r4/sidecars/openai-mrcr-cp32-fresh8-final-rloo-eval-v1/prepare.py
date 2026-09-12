"""Seal only actual fixed cp1 and complete immutable source controls; no model queries."""
import os
from pathlib import Path
import checkpoint
import study

def prepare():
    assert os.environ.get('CUDA_VISIBLE_DEVICES')=='' and not study.READY.exists()
    q=checkpoint.verify_checkpoint()
    test=study.read(study.ROOT/'CPU_INPUT_TESTS.json');assert test['returncode']==0
    pins={};inputs={};controls={}
    for p in (study.train.READY,study.REPLICA/'READY.json',study.prior.LONG/'READY_V2.json',study.FOUR/'READY.json'):
        r=study.read(p);pins.update(r['closure_sha256']);pins[str(p)]=study.sha(p)
    for p in checkpoint.OUTPUT.rglob('*'):
        if p.is_file():pins[str(p)]=study.sha(p)
    expected_cp32=study.read(study.TRAINING/'PARENT_BINDING.json')
    expected_fixed=study.read(study.prior.TRAINING/'outputs/attempt-001/checkpoint-0001/EVAL_BINDING.json')
    for phase,count in [('held',32),('long',16),('fourneedle',16)]:
        plan=study.schedule(phase);assert len(plan)==count
        planmap={v['id']:v for v in plan}
        for p in study.input_dir(phase).rglob('*'):
            if p.is_file():pins[str(p)]=study.sha(p)
        inputs[phase]=dict(planned=count,unique_contexts=16,schedule_sha256=study.digest(plan),input_dir=str(study.input_dir(phase)))
        controls[phase]={}
        for arm,source in study.CONTROLS[phase].items():
            terminal=study.read(source/'OWNER_TERMINAL.json');r=study.read(source/'science/RESULT.json')
            assert terminal['complete'] and terminal['released'] and not terminal.get('errors')
            assert r['complete'] and r['planned']==r['recorded']==count
            assert r['all_causal_mappings_complete'] and r['all_initial_root_prefixes_verified'] and r['all_action_caps_respected']
            assert r['child_actions']==0
            assert study.read(source/'science/TERMINAL_STRIP_CONTRACT.json')['condition']=='terminal-strip-disabled'
            assert study.read(source/'owned-service/BINDING.json')==(expected_cp32 if arm=='cp32' else expected_fixed)
            episodes=list((source/'science/episodes').glob('*.json'));assert len(episodes)==count
            for p in episodes:
                item=study.read(p);assert item['coordinate']==planmap[item['coordinate']['id']]
                assert study.digest(item['episode'])==item['episode_sha256']
            for p in (source/'science').rglob('*'):
                if p.is_file():pins[str(p)]=study.sha(p)
            for p in (source/'OWNER_RUN.json',source/'OWNER_TERMINAL.json',source/'owned-service/BINDING.json',source/'owned-service/PREFLIGHT.json'):
                pins[str(p)]=study.sha(p)
            controls[phase][arm]=dict(output=str(source),result_sha256=study.sha(source/'science/RESULT.json'),
                owner_terminal_sha256=study.sha(source/'OWNER_TERMINAL.json'),planned=count,
                available=r['scientifically_available'],correct=r['raw_exact'],new_control_queries=0)
    supplement=study.ROOT.parents[1]/'analyses/openai-mrcr-fourneedle-ordinal-transfer-independent-2026-09-12/native-validation-v2/RESULTS.json'
    pins[str(supplement)]=study.sha(supplement)
    study.write_x(study.ROOT/'CHECKPOINT_QUALIFICATION.json',q)
    for p in study.ROOT.iterdir():
        if p.is_file():pins[str(p)]=study.sha(p)
    for p,h in pins.items():assert study.sha(p)==h,p
    ready=dict(schema='fresh8-rloo-three-panel-eval-ready-v1',closure_sha256=pins,
        inputs=inputs,controls=controls,checkpoint_qualification=q,planned=64,
        fixed_argv={phase:[str(study.NATIVE),str(study.ROOT/'owner.py'),'run','--phase',phase] for phase in study.CAPS},
        caps=study.CAPS,temperature=.5,max_action_tokens=2048,total_actions=6,children=0,
        short_contexts=16,short_repeats=2,long_contexts=16,fourneedle_contexts=16,
        all_phases_regardless_score=True,no_outcome_manipulation_gate=True,endpoint_selection=False,
        terminal_condition='terminal-strip-disabled',GPU_admission=False)
    ready['identity']=study.digest(ready);study.write_x(study.READY,ready)
    study.verify();print({'identity':ready['identity'],'ready_sha256':study.sha(study.READY),'pins':len(pins)})

if __name__=='__main__':prepare()
