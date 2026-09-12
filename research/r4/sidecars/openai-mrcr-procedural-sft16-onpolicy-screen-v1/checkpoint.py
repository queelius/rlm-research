"""Authenticate actual intermediate cp16; never relabel cp32 as this endpoint."""
from pathlib import Path
import torch
import study

SOURCE=study.load('cp16_original_full_continuation_checkpoint',study.ORIGINAL/'checkpoint.py')
CHECKPOINT=study.TRAIN_OUTPUT/'checkpoint-0016'
RECEIPT=study.ROOT/'CHECKPOINT_READY.json'
EXPECTED_ADAPTER='9f68605f023d637bfecc088e169eea0a31d0ea2b4e88a9db56a3e5d74dc2c9e5'

def qualify():
    parent=SOURCE.verify_checkpoint() # actual existing complete cp4->cp32 lineage and file checks
    state=study.read(CHECKPOINT/'state.json');commit=study.read(CHECKPOINT/'STEP_COMMIT.json')
    lineage=next(r for r in parent['training']['lineage'] if r['step']==16)
    assert lineage['commit_sha256']==study.sha(CHECKPOINT/'STEP_COMMIT.json')
    assert lineage['state_sha256']==study.sha(CHECKPOINT/'state.json')
    assert commit['identity']==study.digest({k:v for k,v in commit.items() if k!='identity'})
    assert state['step']==state['optimizer_steps']==commit['step']==commit['optimizer_steps']==16
    assert state['additional_optimizer_steps']==12
    for name,h in commit['files_sha256'].items():assert study.sha(CHECKPOINT/name)==h,name
    assert study.sha(CHECKPOINT/'adapter_model.safetensors')==EXPECTED_ADAPTER
    bound=study.read(CHECKPOINT/'EVAL_BINDING.json')
    assert bound['step']==16 and bound['fixed_primary_step']==32 # source run's primary, preserved honestly
    assert bound['root_only_update'] is True and bound['policy_alias']==study.ADAPTED_ALIAS
    assert bound['root']['adapter']==str(CHECKPOINT)
    assert bound['root']['adapter_model_sha256']==EXPECTED_ADAPTER
    assert bound['root']['adapter_config_sha256']==study.sha(CHECKPOINT/'adapter_config.json')
    assert bound['child']['adapter'] is None
    opt=torch.load(CHECKPOINT/'optimizer.pt',map_location='cpu',weights_only=True)
    rng=torch.load(CHECKPOINT/'rng.pt',map_location='cpu',weights_only=False)
    steps=sorted({int(v['step']) for v in opt['state'].values()})
    assert len(opt['state'])==504 and steps==[16]
    assert set(rng)=={'python','numpy','torch_cpu','torch_cuda'} and len(rng['torch_cuda'])==1
    return {'schema':'fixed-intermediate-cp16-qualification-v1','selected_step':16,
            'source_run_fixed_primary_step':32,'selection':'MAIN predetermined midpoint before cp16 model outputs',
            'source_training_receipt_sha256':study.sha(SOURCE.RECEIPT),
            'source_training_result_sha256':parent['training']['training_result_sha256'],
            'source_training_ready_sha256':parent['training']['training_ready_sha256'],
            'checkpoint':str(CHECKPOINT),'adapter_sha256':EXPECTED_ADAPTER,
            'config_sha256':study.sha(CHECKPOINT/'adapter_config.json'),
            'step_commit_sha256':study.sha(CHECKPOINT/'STEP_COMMIT.json'),
            'files_sha256':commit['files_sha256'],'optimizer_state_steps':steps,'optimizer_slots':504,
            'parent_checkpoint4_commit_sha256':parent['training']['parent_checkpoint4_commit_sha256'],
            'lineage_through16':[r for r in parent['training']['lineage'] if r['step']<=16],
            'zero_adapter':parent['zero_adapter'],'new_optimizer_steps':0,'model_queries':0}

def seal():
    value=qualify();value['identity']=study.digest(value);study.write_x(RECEIPT,value);return value

def verify_checkpoint():
    value=study.read(RECEIPT)
    assert value['identity']==study.digest({k:v for k,v in value.items() if k!='identity'})
    assert {k:v for k,v in value.items() if k!='identity'}==qualify()
    return value

def binding(arm):
    if arm!='checkpoint16':raise ValueError('only the fixed checkpoint16 arm is valid')
    value=verify_checkpoint();zero=value['zero_adapter']
    return {'schema':'cp16-fixed-root-child-binding-v1','selected_step':16,'source_run_fixed_primary_step':32,
            'models':{study.BASE_ALIAS:{'path':zero['path'],'adapter_sha256':zero['adapter_model_sha256'],'config_sha256':zero['adapter_config_sha256']},
                      study.ADAPTED_ALIAS:{'path':str(CHECKPOINT),'adapter_sha256':value['adapter_sha256'],'config_sha256':value['config_sha256']}},
            'role_map':{'root':study.ADAPTED_ALIAS,'children':[study.BASE_ALIAS]},'fixed_child':study.BASE_ALIAS,
            'selection_path':str(RECEIPT),'selection_sha256':study.sha(RECEIPT),
            'selection_semantics':'predeclared intermediate step16, not original step32 primary or outcome-selected checkpoint',
            'post_training_or_evaluation_checkpoint_selection':False}

