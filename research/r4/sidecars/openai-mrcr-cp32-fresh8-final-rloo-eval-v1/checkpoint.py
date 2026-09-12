"""Authenticate actual completed one-step tensors, source, replay, Adam and binding."""
from functools import lru_cache
import math
from pathlib import Path
import study

OUTPUT=study.train.OUTPUT;CHECKPOINT=OUTPUT/'checkpoint-0001'
RECEIPT=CHECKPOINT/'STEP_COMMIT.json'

def validate_state_binding(state,binding):
    required={'status':'UPDATED','optimizer_steps':1,'fresh_AdamW':True,'optimizer_state_steps':[1],
        'optimizer_state_empty_before_step':True,'parent_sft_step':32,'groups':8,'trajectories':32,
        'exact_reward_positive':7,'exact_reward_negative':25,'baseline':'group mean; G/(G-1) correction','denominator':32,
        'actual_final_tokens':5056,'zero_loss_other_root_tokens':16055,'child_loss_tokens':0,
        'nonzero_advantages':12,'zero_advantage_trajectories':20,'mixed_groups':3,'zero_advantage_skipped_exactly':True,
        'replay_passed':True,'replay_actions':12,'learning_rate':1e-5,'token_TIS_cap':2.,
        'token_TIS_biased':True,'mixed_group_gate':False,'parent_adapter_sha256':study.train.ADAPTER_SHA}
    for k,v in required.items():assert state[k]==v,(k,state[k],v)
    assert math.isfinite(state['adapter_delta_l2']) and state['adapter_delta_l2']>0
    assert binding['role_map']=={'root':study.ADAPTED_ALIAS,'children':[study.BASE_ALIAS]}
    assert set(binding['models'])=={study.ADAPTED_ALIAS,study.BASE_ALIAS}
    assert Path(binding['models'][study.ADAPTED_ALIAS]['path'])==CHECKPOINT
    parent=study.read(study.TRAINING/'PARENT_BINDING.json')
    assert binding['models'][study.BASE_ALIAS]==parent['models'][study.BASE_ALIAS]


def verify_replay(rows,pre,replay):
    assert len(rows)==len(pre['episodes'])==len(pre['detached_token_weights'])==len(replay['episodes'])==32
    assert replay['passed'] and replay['optimizer_steps']==0 and len(replay['replay'])==12
    assert replay['zero_advantage_skipped']==20 and replay['nonzero_final_actions']==12
    checks={r['episode_id']:r for r in replay['replay']};assert len(checks)==12
    token_math=study.load('fresh8rloo_eval_replay_math',study.train.PRIOR/'math_core.py')
    for i,(row,actual) in enumerate(zip(rows,replay['episodes'],strict=True)):
        assert actual['episode_id']==row['episode_id']
        assert actual['reward']==row['reward'] and actual['advantage']==row['advantage']
        if row['advantage']==0:
            assert row['root_turns']==[] and actual['zero_advantage_skipped']
            assert actual['selected_HF_logprobs']==pre['episodes'][i]==pre['detached_token_weights'][i]==[]
            assert row['episode_id'] not in checks
            continue
        check=checks.pop(row['episode_id']);assert check['passed'] and check['index']==i
        a=actual['selected_HF_logprobs'];b=pre['episodes'][i][0]
        assert len(a)==len(b)==check['tokens']==len(row['root_turns'][0]['action_ids'])
        assert all(math.isfinite(x) and x<=0 for x in a+b)
        assert max(abs(x-y) for x,y in zip(a,b,strict=True))<=1e-5 and abs(math.fsum(a)-math.fsum(b))<=1e-4
        weights=token_math.token_tis([b],[row['root_turns'][0]['old_logprobs']],cap=2.)['weights']
        assert weights==pre['detached_token_weights'][i][0]
    assert not checks


@lru_cache(maxsize=1)
def verify_checkpoint():
    import torch
    from safetensors.torch import load_file
    torch.set_num_threads(2)
    source=study.train.verify();result=study.read(OUTPUT/'RESULT.json');terminal=study.read(OUTPUT/'OWNER_TERMINAL.json')
    assert result['status']=='UPDATED' and result['optimizer_steps']==1
    assert terminal['complete'] and terminal['owned_process_reaped'] and terminal['subprocess_exit_code']==0
    assert terminal['result_sha256']==study.sha(OUTPUT/'RESULT.json')
    assert result['ready_sha256']==study.sha(study.train.READY) and result['ready_identity']==source['identity']
    assert result['checkpoint']==str(CHECKPOINT) and result['step_commit_sha256']==study.sha(RECEIPT)
    commit=study.read(RECEIPT)
    for p,h in commit['files_sha256'].items():assert study.sha(p)==h,p
    state=study.read(CHECKPOINT/'state.json');binding=study.read(CHECKPOINT/'EVAL_BINDING.json')
    validate_state_binding(state,binding)
    assert result['state_sha256']==study.sha(CHECKPOINT/'state.json') and result['binding_sha256']==study.sha(CHECKPOINT/'EVAL_BINDING.json')
    assert commit['ready_sha256']==study.sha(study.train.READY) and commit['input_sha256']==study.sha(study.train.INPUTS)
    refs={'initial_sha256':OUTPUT/'INITIAL.json','initial_rng_sha256':OUTPUT/'initial-rng.pt',
        'gradient_receipt_sha256':OUTPUT/'gradient/REPLAY.json','gradient_sha256':OUTPUT/'gradient/gradients.pt',
        'prestep_qualification_sha256':OUTPUT/'PRESTEP_QUALIFICATION.json','prestep_logps_sha256':OUTPUT/'PRESTEP_LOGPS.json',
        'poststep_logps_sha256':OUTPUT/'POSTSTEP_LOGPS.json','adapter_sha256':CHECKPOINT/'adapter_model.safetensors',
        'adapter_config_sha256':CHECKPOINT/'adapter_config.json','optimizer_sha256':CHECKPOINT/'optimizer.pt',
        'rng_sha256':CHECKPOINT/'rng.pt','parent_binding_sha256':study.TRAINING/'PARENT_BINDING.json',
        'parent_qualification_sha256':study.TRAINING/'PARENT_CHECKPOINT_QUALIFICATION.json'}
    for k,p in refs.items():assert state[k]==study.sha(p),(k,p)
    replay=study.read(OUTPUT/'gradient/REPLAY.json');pre=study.read(OUTPUT/'PRESTEP_LOGPS.json')
    rows=study.train.validate_inputs(study.read(study.train.INPUTS))
    verify_replay(rows,pre,replay)
    token_math=study.load('fresh8rloo_eval_token_math',study.train.PRIOR/'math_core.py')
    initial=torch.load(OUTPUT/'initial-trainable.pt',map_location='cpu',weights_only=True)
    gradients=torch.load(OUTPUT/'gradient/gradients.pt',map_location='cpu',weights_only=True)
    initial_receipt=study.read(OUTPUT/'INITIAL.json')
    assert study.sha(OUTPUT/'initial-trainable.pt')==initial_receipt['initial_tensor_file_sha256']
    assert token_math.snapshot_digest(initial)==state['initial_tensor_identity']==initial_receipt['trainable_identity']
    parent=load_file(str(study.train.CHECKPOINT/'adapter_model.safetensors'))
    updated=load_file(str(CHECKPOINT/'adapter_model.safetensors'))
    assert {n.replace('.default.','.') for n in initial}==set(parent)==set(updated)
    assert all(torch.equal(v,parent[n.replace('.default.','.')]) for n,v in initial.items())
    assert set(initial)==set(gradients)
    final={n:updated[n.replace('.default.','.')] for n in initial}
    assert token_math.snapshot_digest(final)==state['updated_tensor_identity']
    delta=math.sqrt(math.fsum(float((final[n].double()-v.double()).square().sum()) for n,v in initial.items()))
    assert math.isclose(delta,state['adapter_delta_l2'],rel_tol=1e-10,abs_tol=1e-12)
    optimizer=torch.load(CHECKPOINT/'optimizer.pt',map_location='cpu',weights_only=True)
    assert len(optimizer['param_groups'])==1
    pg=optimizer['param_groups'][0]
    assert pg['lr']==1e-5 and pg['weight_decay']==0 and tuple(pg['betas'])==(.9,.999) and pg['eps']==1e-8
    assert len(pg['params'])==len(initial)==len(optimizer['state'])
    for n,ident in zip(initial,pg['params'],strict=True):
        a=optimizer['state'][ident];g=gradients[n]
        assert torch.isfinite(g).all() and int(a['step'])==1
        assert torch.allclose(a['exp_avg'],g*.1,atol=1e-9,rtol=1e-5)
        assert torch.allclose(a['exp_avg_sq'],g.square()*.001,atol=1e-11,rtol=1e-5)
    for p in (OUTPUT/'initial-rng.pt',CHECKPOINT/'rng.pt'):
        rng=torch.load(p,map_location='cpu',weights_only=False);assert set(rng)=={'python','numpy','torch','cuda'}
    for alias,item in binding['models'].items():
        p=Path(item['path']);assert study.sha(p/'adapter_model.safetensors')==item['adapter_sha256']
        assert study.sha(p/'adapter_config.json')==item['config_sha256']
    return dict(eligible=True,checkpoint=str(CHECKPOINT),step_commit_sha256=study.sha(RECEIPT),
        state_sha256=study.sha(CHECKPOINT/'state.json'),binding_sha256=study.sha(CHECKPOINT/'EVAL_BINDING.json'),
        training_result_sha256=study.sha(OUTPUT/'RESULT.json'),source_ready_sha256=study.sha(study.train.READY),
        actual_initial_tensors_match_cp32=True,actual_saved_gradient_Adam_moments_match=True,
        replay_actions=12,zero_advantage_skipped=20,optimizer_steps=1,adapter_delta_l2=delta,
        no_rollout_manipulation_gate=True,not_independent_HF_reexecution=True)

def binding(arm):
    if arm!='updated':raise ValueError('only the fixed updated endpoint')
    verify_checkpoint();return study.read(CHECKPOINT/'EVAL_BINDING.json')
