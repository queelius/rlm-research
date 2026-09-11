"""Authentic unchanged low66c or fixed4 corrective/producer adapter with fixed c32 child."""
from pathlib import Path
import study as s
with s.aliases({'study':s.original}):
    old=s.load('corrective_complete_binding',s.SOURCE/'binding.py','865e84908e4f8f198c81587605a37c003fe7f02c69bf1bbbd0fc8c495c18afd1')

def training_source(arm):return s.START.parent if arm=='unchanged' else s.ATTEMPT/('training-'+arm)

def selected(arm):
    if arm=='unchanged':return old.selected('unchanged')
    if arm not in s.ARMS:raise ValueError('unknown arm')
    directory=training_source(arm);result=s.read(directory/'RESULT.json');chosen=result['selected'];path=directory/'checkpoint-0004'
    corpus=s.sha(s.ATTEMPT/'capture/CORPUS_READY.json')
    if not result['complete'] or result['identity']!=s.verify()['identity'] or result['arm']!=arm or result['optimizer_steps']!=4 or result['starting_adapter_sha256']!=s.START_SHA or not result['fresh_optimizer'] or result['child_loaded'] or result['child_updated'] or result['corpus_sha256']!=corpus or chosen['checkpoint']!=str(path) or chosen['step']!=4 or s.read(directory/'SELECTION.json')!=chosen:raise ValueError('fixed4 actual lineage')
    previous=None
    for step in range(1,5):
        path=directory/f'checkpoint-{step:04}';state=s.read(path/'state.json')
        if state['identity']!=result['identity'] or state['corpus_sha256']!=corpus or state['arm']!=arm or (state['step'],state['epoch'],state['cursor'])!=(step,step,0) or state['previous_state_sha256']!=previous:raise ValueError('optimizer checkpoint ancestry')
        if not {'adapter_model.safetensors','adapter_config.json','optimizer.pt','rng_state.pt'}<=state['files_sha256'].keys():raise ValueError('checkpoint members missing')
        for name,pin in state['files_sha256'].items():
            if Path(name).name!=name or s.sha(path/name)!=pin:raise ValueError('checkpoint member changed')
        previous=s.sha(path/'state.json')
    if previous!=chosen['state_sha256'] or state['files_sha256']!=result['files_sha256'] or chosen['adapter_sha256']!=state['files_sha256']['adapter_model.safetensors'] or chosen['config_sha256']!=state['files_sha256']['adapter_config.json']:raise ValueError('selected closure')
    return chosen

def binding(arm,chosen):
    value=s.stack().native.initial_binding();value['models'].pop(value['role_map']['root'])
    alias='strict-rlm-qwen3-4b-corrective-reduction-'+arm.replace('_','-')+'-v1'
    model=dict(path=chosen['checkpoint'],adapter_sha256=chosen['adapter_sha256'],config_sha256=chosen['config_sha256'])
    value['models'][alias]=model;value['role_map']['root']=alias
    state=s.read(Path(chosen['checkpoint'])/'state.json')
    value['campaign_policy']={**model,'step':chosen['step'],'state_sha256':chosen['state_sha256'],'optimizer_sha256':state['files_sha256']['optimizer.pt'],'rng_sha256':state['files_sha256']['rng_state.pt']}
    value['campaign_id']=s.ROOT.name;value.pop('receipt_uptake_study',None)
    selection=training_source(arm)/'SELECTION.json';value['selection_path']=str(selection);value['selection_sha256']=s.sha(selection)
    value['selection_semantics']='unchanged low66c' if arm=='unchanged' else 'fixed4 current-action authored SFT; no validation selection'
    value['corrective_reduction_study']=dict(arm=arm,ready_sha256=s.sha(s.ROOT/'READY.json'),terminal_weight=0.)
    if value['models'][value['fixed_child']]['adapter_sha256']!=s.CHILD_SHA:raise ValueError('child changed')
    return value

def validate(value,descriptor,path):
    arm=value['corrective_reduction_study']['arm']
    if value!=binding(arm,selected(arm)):raise ValueError('actual root binding changed')
    old.validate_descriptor(value,descriptor,s.sha(path))
