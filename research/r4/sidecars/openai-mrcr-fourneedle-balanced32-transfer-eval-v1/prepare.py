"""Prepare and seal the fixed two-arm evaluator; never launch it."""
import json,time
from pathlib import Path
import checkpoint,study

def _verified_closure(ready_path):
    ready=study.read(ready_path)
    if ready.get('identity')!=study.digest({k:v for k,v in ready.items() if k!='identity'}):raise ValueError('referenced READY identity changed')
    for p,h in ready['closure_sha256'].items():
        if study.sha(Path(p))!=h:raise ValueError('referenced closure changed: '+p)
    return ready

def build():
    if study.READY.exists():raise FileExistsError(study.READY)
    inputs=study.prepare_inputs(); qualification=checkpoint.verify_checkpoint()
    cp_ready=_verified_closure(study.PARENT/'READY.json')
    lr_ready=_verified_closure(study.SIDE/'openai-mrcr-cp32-fresh8-final-rloo-lr1e4-eval-v1'/'READY.json')
    endpoints={'schema':'mrcr-balanced32-fixed-endpoints-v1','cp32':qualification['cp32'],'lr1e4':qualification['lr1e4'],
      'binding_sha256':qualification['bindings'],'both_arms_required':True,'checkpoint_selection':False}
    study.write_x(checkpoint.RECEIPT,endpoints)
    local=[study.ROOT/n for n in ('DESIGN.md','RUNBOOK.md','study.py','checkpoint.py','collect.py','owner.py','prepare.py','test_eval.py','seal.py')]
    local+=sorted(p for p in study.INPUTS.rglob('*') if p.is_file())+[checkpoint.RECEIPT,study.DATA/'DATA_READY.json']
    closure={}
    for ready in (cp_ready,lr_ready):closure.update(ready['closure_sha256'])
    for p in local:closure[str(p)]=study.sha(p)
    value={'schema':'mrcr-fourneedle-balanced32-transfer-eval-ready-v1','created_epoch':time.time(),
      'question':'Does fixed LR1e-4 differ from cp32 on untouched ordinal-balanced four-needle contexts?',
      'claim_boundary':'same-task exploratory transfer; LR1e-4 was development-selected; not retrieval, decomposition, or pretraining-clean evidence',
      'arms':['cp32','lr1e4'],'both_arms_regardless_score':True,
      'inputs':{'data_ready':str(study.DATA/'DATA_READY.json'),'data_ready_sha256':study.sha(study.DATA/'DATA_READY.json'),
        'data_ready_identity':'35cf255465759a18d359616626d39fef81b2c881c0791dd642f6147fe9556f4d',
        'schedule_sha256':inputs['schedule_sha256'],'records':32,'episodes_per_arm':32,'ordinal_counts':{str(i):8 for i in range(1,5)},
        'seed_namespace':'202609270000+fixed-row-index','gold_in_model_input':False},
      'sampling':{'temperature':.5,'top_p':1.,'top_k':-1,'min_p':0.,'max_tokens_per_action':2048,'max_total_root_child_turns':6,'workers':4},
      'endpoints':{'receipt':str(checkpoint.RECEIPT),'receipt_sha256':study.sha(checkpoint.RECEIPT),
        'cp32_binding_sha256':qualification['bindings']['cp32'],'lr1e4_binding_sha256':qualification['bindings']['lr1e4'],
        'fixed_child_identical':True},
      'terminal_condition':{'name':'terminal-strip-disabled','hooks_sha256':study.sha(study.TERMINAL_HOOK/'hooks.py'),'gold_repair':False},
      'metrics':{'primary':'raw exact official answer bytes','diagnostics':['official SequenceMatcher-based MRCR score','normalized exact','procedure/copy/usage'],'unavailable_not_wrong':True},
      'caps_seconds_per_arm':{'science':900,'owner':1100,'external':1200},'optimizer_steps':0,'model_queries_before_ready':0,'auto_launch':False,
      'outputs':{'cp32':str(study.ROOT/'outputs/cp32-001'),'lr1e4':str(study.ROOT/'outputs/lr1e4-001')},'closure_sha256':closure}
    value['identity']=study.digest(value);study.write_x(study.READY,value);return value

def verify():
    value=study.read(study.READY)
    if value['identity']!=study.digest({k:v for k,v in value.items() if k!='identity'}):raise ValueError('READY identity changed')
    for p,h in value['closure_sha256'].items():
        if study.sha(Path(p))!=h:raise ValueError('closure changed: '+p)
    checkpoint.verify_checkpoint();return value

if __name__=='__main__':
    v=verify() if study.READY.exists() else build();print(json.dumps({'identity':v['identity'],'sha256':study.sha(study.READY)},sort_keys=True))
