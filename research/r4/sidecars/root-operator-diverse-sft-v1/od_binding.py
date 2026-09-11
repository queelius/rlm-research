"""Exact released-reference857 or fixed SFT6, with unchanged c32 transport."""
from pathlib import Path
import od_study as s

def selected(arm):
    if arm=='unchanged':return s.starting_policy()
    if arm!='sft6':raise ValueError('fixed policy')
    directory=s.ATTEMPT/'training';result=s.read(directory/'RESULT.json');chosen=s.read(directory/'SELECTION.json');start=s.starting_policy()
    if not result['complete'] or result['identity']!=s.verify()['identity'] or result['optimizer_steps']!=6 or result['selected']!=chosen or chosen['step']!=6 or result['starting_adapter_sha256']!=start['adapter_sha256'] or not result['fresh_optimizer'] or result['child_loaded'] or result['child_updated']:raise ValueError('fixed SFT6 required; no partial substitution')
    previous=None;corpus=s.sha(s.ATTEMPT/'capture/CORPUS_READY.json')
    for step in range(1,7):
        path=directory/f'checkpoint-{step:04}';state=s.read(path/'state.json')
        if (state['step'],state['epoch'],state['cursor'])!=(step,step,0) or state['previous_state_sha256']!=previous or state['identity']!=result['identity'] or state['corpus_sha256']!=corpus:raise ValueError('checkpoint ancestry')
        if not {'adapter_model.safetensors','adapter_config.json','optimizer.pt','rng_state.pt'}<=state['files_sha256'].keys():raise ValueError('checkpoint members')
        for name,pin in state['files_sha256'].items():
            if Path(name).name!=name or s.sha(path/name)!=pin:raise ValueError('checkpoint member changed')
        previous=s.sha(path/'state.json')
    if chosen['checkpoint']!=str(path) or chosen['state_sha256']!=previous or chosen['adapter_sha256']!=state['files_sha256']['adapter_model.safetensors'] or chosen['config_sha256']!=state['files_sha256']['adapter_config.json']:raise ValueError('selection closure')
    return chosen

def binding(arm,chosen=None):
    chosen=chosen or selected(arm);receipt=s.read(s.ROOT/'inputs/START_BINDING.json');value=s.read(receipt['lineage_receipt_path'])
    value['models'].pop(value['role_map']['root']);alias='strict-rlm-qwen3-4b-operator-diverse-'+arm+'-v1'
    model=dict(path=chosen['checkpoint'],adapter_sha256=chosen['adapter_sha256'],config_sha256=chosen['config_sha256'])
    value['models'][alias]=model;value['role_map']['root']=alias
    value.pop('diagnostic_no_training',None);value.pop('fixed_root',None)
    value['study']=s.ROOT.name;value['operator_diverse']=dict(arm=arm,starting_adapter_sha256=s.starting_policy()['adapter_sha256'],fixed_updates=6,ready_sha256=s.sha(s.ROOT/'READY_v2.json'))
    if value['models'][value['fixed_child']]['adapter_sha256']!=s.CHILD_SHA:raise ValueError('fixed child')
    return value

def validate(value,descriptor,path):
    if value!=binding(value['operator_diverse']['arm']):raise ValueError('binding differs')
    j=s.joint()
    old=s.load('od_qualified_descriptor',j.SOURCE/'binding.py','865e84908e4f8f198c81587605a37c003fe7f02c69bf1bbbd0fc8c495c18afd1',{'study':j.original})
    old.validate_descriptor(value,descriptor,s.sha(path))
