"""Actual authenticated low66c / fixed4 root and unchanged c32 child; no fake LoRA."""
from pathlib import Path
import study as s
old=s.plan.private('binding.py',view=s.plan.old)
validate_descriptor=old.validate_descriptor

def training_source(arm):
    if arm=='unchanged':return s.START.parent
    if arm not in s.ARMS:raise ValueError('unknown arm')
    return s.ROOT/'outputs/attempt-001'/('training-'+arm)

def selected(arm):
    if arm=='unchanged':
        chosen=old.selected('success_sft')
        if chosen['adapter_sha256']!=s.START_SHA:raise ValueError('low66c start changed')
        return chosen
    directory=training_source(arm);result=s.read(directory/'RESULT.json');chosen=result['selected'];path=directory/'checkpoint-0004';episodes,corpus,manifest=s.captured()
    if not result['complete'] or result['identity']!=s.verify()['identity'] or result['arm']!=arm or result['optimizer_steps']!=4 or result['starting_adapter_sha256']!=s.START_SHA or not result['fresh_optimizer'] or result['child_loaded'] or result['child_updated'] or result['corpus_sha256']!=corpus or chosen['checkpoint']!=str(path) or chosen['step']!=4 or s.read(directory/'SELECTION.json')!=chosen:raise ValueError('fixed4 lineage')
    previous=None
    for step in range(1,5):
        p=directory/f'checkpoint-{step:04d}';state=s.read(p/'state.json')
        if state['identity']!=result['identity'] or state['corpus_sha256']!=corpus or state['arm']!=arm or (state['step'],state['epoch'],state['cursor'])!=(step,step,0) or state['previous_state_sha256']!=previous:raise ValueError('Adam checkpoint ancestry')
        for name,h in state['files_sha256'].items():
            if Path(name).name!=name:raise ValueError('member path')
            s.check(p/name,h)
        previous=s.sha(p/'state.json')
    if previous!=chosen['state_sha256'] or state['files_sha256']!=result['files_sha256'] or chosen['adapter_sha256']!=state['files_sha256']['adapter_model.safetensors']:raise ValueError('selected closure')
    return chosen

def binding(arm,chosen):
    value=s.stack().native.initial_binding();value['models'].pop(value['role_map']['root'])
    alias='strict-rlm-qwen3-4b-complete-demo-'+arm.replace('_','-')+'-v1'
    model=dict(path=chosen['checkpoint'],adapter_sha256=chosen['adapter_sha256'],config_sha256=chosen['config_sha256'])
    value['models'][alias]=model;value['role_map']['root']=alias
    state=s.read(Path(chosen['checkpoint'])/'state.json')
    value['campaign_policy']={**model,'step':chosen['step'],'state_sha256':chosen['state_sha256'],'optimizer_sha256':state['files_sha256']['optimizer.pt'],'rng_sha256':state['files_sha256']['rng_state.pt']}
    value['campaign_id']=s.ROOT.name;value.pop('receipt_uptake_study',None)
    selection=training_source(arm)/'SELECTION.json';value['selection_path']=str(selection);value['selection_sha256']=s.sha(selection)
    value['selection_semantics']='unchanged low66c' if arm=='unchanged' else 'fixed4 authored SFT; no validation selection'
    value['complete_demo_study']=dict(arm=arm,ready_sha256=s.sha(s.ROOT/'READY.json'),sampled_root_policy_training=False)
    if value['models'][value['fixed_child']]['adapter_sha256']!=s.CHILD_SHA:raise ValueError('child changed')
    return value
