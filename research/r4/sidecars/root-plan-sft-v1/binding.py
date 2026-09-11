"""Exact unchanged low8 or complete authored final4; fixed c32 child."""
from pathlib import Path
import study as s
old_binding=s.private('binding.py',view=s.old)
validate_descriptor=old_binding.validate_descriptor


def training_source(arm):
    if arm=='unchanged':return s.START.parent
    if arm not in s.ARMS:raise ValueError('unknown arm')
    return s.ROOT/'outputs/attempt-001'/('training-'+arm)


def selected(arm):
    if arm=='unchanged':
        chosen=old_binding.selected('success_sft')
        if chosen['adapter_sha256']!=s.START_SHA:raise ValueError('fixed start changed')
        return chosen
    directory=training_source(arm);result=s.read(directory/'RESULT.json');chosen=result['selected'];path=directory/'checkpoint-0004'
    if (not result['complete'] or result['arm']!=arm or result['identity']!=s.verify()['identity'] or result['optimizer_steps']!=4
        or chosen['step']!=4 or chosen['checkpoint']!=str(path) or result['starting_adapter_sha256']!=s.START_SHA
        or not result['fresh_optimizer'] or result['child_loaded'] or result['child_updated']
        or (result['example_exposures'],result['root_turn_exposures'])!=(64,64) or s.read(directory/'SELECTION.json')!=chosen):raise ValueError('complete fixed4 required')
    s.check(path/'state.json',chosen['state_sha256']);state=s.read(path/'state.json')
    if (state['identity']!=result['identity'] or state['arm']!=arm or state['corpus_sha256']!=s.sha(s.ROOT/'prepared-v2'/f'ROWS_{arm}.json')
        or (state['step'],state['epoch'],state['cursor'])!=(4,4,0) or state['files_sha256']!=result['files_sha256']):raise ValueError('fixed4 cursor/state')
    expected=4*sum(s.validate_authored(r) for r in s.read(s.ROOT/'prepared-v2'/f'ROWS_{arm}.json'))
    if result['target_token_exposures']!=expected:raise ValueError('target exposure total')
    for name,h in state['files_sha256'].items():
        if Path(name).name!=name:raise ValueError('checkpoint path')
        s.check(path/name,h)
    if chosen['adapter_sha256']!=state['files_sha256']['adapter_model.safetensors'] or chosen['config_sha256']!=state['files_sha256']['adapter_config.json']:raise ValueError('selected weights')
    return chosen


def binding(arm,chosen):
    value=s.stack().native.initial_binding();value['models'].pop(value['role_map']['root'])
    alias='strict-rlm-qwen3-4b-root-plan-'+arm.replace('_','-')+'-v1'
    model=dict(path=chosen['checkpoint'],adapter_sha256=chosen['adapter_sha256'],config_sha256=chosen['config_sha256'])
    value['models'][alias]=model;value['role_map']['root']=alias
    state=s.read(Path(chosen['checkpoint'])/'state.json')
    value['campaign_policy']={**model,'step':chosen['step'],'state_sha256':chosen['state_sha256'],
      'optimizer_sha256':state['files_sha256']['optimizer.pt'],'rng_sha256':state['files_sha256']['rng_state.pt']}
    value['campaign_id']=s.ROOT.name;value.pop('receipt_uptake_study',None)
    source=training_source(arm)/'SELECTION.json';value['selection_path']=str(source);value['selection_sha256']=s.sha(source)
    value['selection_semantics']='unchanged low success8' if arm=='unchanged' else 'authored first-action fixed4; no selection'
    value['plan_sft_study']=dict(arm=arm,root_ready_sha256=s.sha(s.ROOT/'READY.json'),authored_ce_not_rl=True)
    if value['models'][value['fixed_child']]['adapter_sha256']!=s.CHILD_SHA:raise ValueError('child changed')
    return value
