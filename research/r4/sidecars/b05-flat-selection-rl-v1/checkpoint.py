"""Conditional CPU endpoint qualification; actual source/replay/Adam/weights, never accuracy."""
from pathlib import Path
import math
import study as s

def endpoint():
    import torch
    from safetensors.torch import load_file
    s.verify();root=s.OUTPUT;cp=root/'checkpoint-0001'
    terminal=s.read(root/'OWNER_TERMINAL.json');result=s.read(root/'RESULT.json')
    assert terminal['complete'] and terminal['owned_process_reaped'] and terminal['subprocess_exit_code']==0
    assert terminal['result_sha256']==s.sha(root/'RESULT.json')
    assert result['status']=='UPDATED' and result['optimizer_steps']==1
    assert result['ready_sha256']==s.sha(s.READY)
    assert result['step_commit_sha256']==s.sha(cp/'STEP_COMMIT.json')
    commit=s.read(cp/'STEP_COMMIT.json')
    assert commit['source_ready_sha256']==s.sha(s.READY) and commit['input_sha256']==s.sha(s.INPUTS)
    for p,h in commit['artifacts_sha256'].items():assert s.sha(p)==h,p
    state=s.read(cp/'state.json');init=s.read(root/'INITIAL.json');replay=s.read(root/'REPLAY.json')
    for key,value in dict(optimizer_steps=1,learning_rate=1e-4,denominator=18,groups=9,group_size=2,
        nonzero_actions=8,zero_actions=10,token_TIS_cap=2.,token_TIS_biased=True,fresh_AdamW=True,
        optimizer_state_empty_before_step=True,optimizer_state_steps=[1]).items():assert state[key]==value,key
    assert init['no_cp32_weights_loaded'] and init['disabled_enabled_HF_exact'] and init['disabled_enabled_max_error']==0.
    assert replay['passed'] and len(replay['checks'])==8 and replay['denominator']==18
    rows=s.validate_inputs(s.read(s.INPUTS));active=[r['episode_id'] for r in rows if r['advantage']!=0]
    assert [r['episode_id'] for r in replay['checks']]==active
    assert all(r['passed'] and r['max_token_error']<=1e-5 and r['sequence_error']<=1e-4 for r in replay['checks'])
    assert replay['selected_loss_tokens']==sum(sum(r['selection_mask']) for r in rows if r['advantage']!=0)==1845
    assert replay['LoRA_A_gradient_norm']==0. and replay['LoRA_B_gradient_norm']>0.
    initial=torch.load(root/'initial-trainable.pt',map_location='cpu',weights_only=True)
    grad=torch.load(root/'gradients.pt',map_location='cpu',weights_only=True)
    updated=torch.load(cp/'trainable.pt',map_location='cpu',weights_only=True)
    optimizer=torch.load(cp/'optimizer.pt',map_location='cpu',weights_only=True)
    assert list(initial)==list(grad)==list(updated)
    group=optimizer['param_groups'];assert len(group)==1 and group[0]['lr']==1e-4 and group[0]['weight_decay']==0.
    assert group[0]['betas']==(.9,.999) and group[0]['eps']==1e-8
    assert group[0]['params']==list(range(len(initial)))
    errors=[]
    for index,(name,start) in enumerate(initial.items()):
        g=grad[name];end=updated[name];slot=optimizer['state'][index]
        assert int(slot['step'])==1 and torch.isfinite(g).all()
        assert torch.allclose(slot['exp_avg'],g*.1,rtol=1e-5,atol=1e-9)
        assert torch.allclose(slot['exp_avg_sq'],g.square()*.001,rtol=1e-5,atol=1e-11)
        expected=start-1e-4*(g/(g.abs()+1e-8))
        error=float((end-expected).abs().max());assert error<=1e-7;errors.append(error)
        if '.lora_A.' in name:assert torch.equal(start,end) and torch.count_nonzero(g)==0
        else:assert '.lora_B.' in name and torch.count_nonzero(start)==0
    disk=load_file(str(cp/'adapter_model.safetensors'))
    remap={k.replace('.default.','.'):v for k,v in updated.items()}
    assert disk.keys()==remap.keys() and all(torch.equal(disk[k],remap[k]) for k in disk)
    import core
    logps=s.read(root/'PRESTEP_LOGPS.json')
    weights,diagnostics=core.scorer._build_token_diagnostics(rows,logps['episodes'])
    assert weights==logps['detached_token_weights']
    saved=s.read(root/'PRESTEP_QUALIFICATION.json')
    for key,value in diagnostics.items():assert saved[key]==value,key
    delta=math.sqrt(math.fsum(float((updated[k].double()-v.double()).square().sum()) for k,v in initial.items()))
    assert math.isclose(delta,state['adapter_delta_l2'],rel_tol=1e-10) and delta>0
    assert core.math.snapshot_digest(initial)==state['initial_trainable_identity']
    assert core.math.snapshot_digest(updated)==state['updated_trainable_identity']
    binding=s.read(cp/'EVAL_BINDING.json')
    assert binding['alias']==s.ALIAS and binding['base']==str(s.BASE)
    assert binding['adapter_sha256']==s.sha(cp/'adapter_model.safetensors')
    assert binding['adapter_config_sha256']==s.sha(cp/'adapter_config.json')
    assert binding['state_sha256']==s.sha(cp/'state.json')
    return dict(eligible=True,checkpoint=str(cp),binding=binding,binding_sha256=s.sha(cp/'EVAL_BINDING.json'),
        state_sha256=s.sha(cp/'state.json'),step_commit_sha256=s.sha(cp/'STEP_COMMIT.json'),
        result_sha256=s.sha(root/'RESULT.json'),training_ready_sha256=s.sha(s.READY),
        Adam_formula_max_error=max(errors),all18_source_actions_qualified=True,all8_replays_pass=True,zero_actions10=True,
        selection='fixed sole step1; no accuracy qualification')
