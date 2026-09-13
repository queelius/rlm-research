"""One native-action BA-RLOO array-selection update from released base; no generation."""
import argparse
import math
import os
from pathlib import Path
import random
import signal
import time
import traceback
import core
import study as s

def norm(values):return math.sqrt(math.fsum(float(v.double().square().sum()) for v in values))

def preflight():
    ready=s.verify();rows=s.validate_inputs(s.read(s.INPUTS))
    assert core.scorer.study is s and core.scorer.math_core is core.math
    return ready,rows

def run(output,seconds):
    ready,rows=preflight()
    assert Path(output)==s.OUTPUT and seconds==s.SCIENCE_SECONDS
    if not os.environ.get('CUDA_VISIBLE_DEVICES'):
        raise RuntimeError('CPU_ENTRY_VERIFIED: MAIN must assign one GPU before training')
    import numpy as np
    import torch
    from transformers import AutoModelForCausalLM
    from peft import get_peft_model_state_dict
    assert torch.cuda.device_count()==1
    output=Path(output);output.mkdir(parents=True,exist_ok=True)
    assert {p.name for p in output.iterdir()}<={'OWNER_START.json','train.stdout','train.stderr'}
    started=time.monotonic();steps=0;model=None
    def timeout(sig,frame):raise TimeoutError('BA18 one-step science cap')
    signal.signal(signal.SIGALRM,timeout);signal.alarm(seconds)
    s.write_x(output/'START.json',dict(ready_sha256=s.sha(s.READY),input_sha256=s.sha(s.INPUTS),
        init_seed=s.INIT_SEED,seed=s.SEED,numpy_seed=s.NP_SEED,science_seconds=seconds))
    try:
        torch.set_num_threads(4);random.seed(s.SEED);np.random.seed(s.NP_SEED)
        torch.manual_seed(s.SEED);torch.cuda.manual_seed_all(s.SEED)
        torch.backends.cuda.matmul.allow_tf32=False;torch.backends.cudnn.allow_tf32=False
        base=AutoModelForCausalLM.from_pretrained(str(s.BASE),local_files_only=True,
            torch_dtype=torch.bfloat16,attn_implementation='sdpa',device_map={'':'cuda:0'})
        base.config.use_cache=False;model=core.initialize(base)
        model.train()
        for module in model.modules():
            if isinstance(module,torch.nn.Dropout):module.eval()
        model.gradient_checkpointing_enable(gradient_checkpointing_kwargs={'use_reentrant':False})
        model.enable_input_require_grads()
        initial=core.math.snapshot_trainable(model)
        assert all(v.dtype==torch.float32 for v in initial.values())
        torch.save(initial,output/'initial-trainable.pt');core.save_rng(output/'initial-rng.pt',torch)
        model.save_pretrained(output/'initial-adapter')
        first=rows[0]['root_turns'][0]
        enabled=core.selected_logprobs(model,first,require_grad=False)
        with model.disable_adapter():disabled=core.selected_logprobs(model,first,require_grad=False)
        init_error=float((enabled-disabled).abs().max());assert torch.equal(enabled,disabled)
        s.write_x(output/'INITIAL.json',dict(start='released_base_new_zero_B_LoRA',no_cp32_weights_loaded=True,
            init_seed=s.INIT_SEED,config_source_sha256=s.sha(s.CONFIG_SOURCE),all_B_exact_zero=True,
            all_A_nonzero=True,trainable_identity=core.math.snapshot_digest(initial),
            trainable_parameters=sum(v.numel() for v in initial.values()),
            initial_tensor_file_sha256=s.sha(output/'initial-trainable.pt'),initial_rng_sha256=s.sha(output/'initial-rng.pt'),
            disabled_enabled_HF_exact=True,disabled_enabled_max_error=init_error,
            precision='BF16 base / FP32 LoRA',dropout_disabled=True,attention='sdpa',
            no_KV_cache=True,nonreentrant_checkpoint=True,model_training=True))
        # Full native action likelihoods retained, including zero-advantage replies and zero-loss structure.
        baseline=core.scorer._all_logprobs(model,rows)
        weights,qualification=core.scorer._build_token_diagnostics(rows,baseline)
        qualification.update(denominator=18,groups=9,all_actions=18,nonzero_actions=8,zero_actions=10,
            native_HF_equality_required=False,exact_sequence_IS_claim=False,
            policy_scope='prospectively biased token-TIS array selection; full action likelihoods audited')
        s.write_x(output/'PRESTEP_QUALIFICATION.json',qualification)
        s.write_x(output/'PRESTEP_LOGPS.json',dict(episodes=baseline,detached_token_weights=weights,
            native_logprobs=[[r['root_turns'][0]['old_logprobs']] for r in rows]))
        named={n:p for n,p in model.named_parameters() if p.requires_grad}
        model.zero_grad(set_to_none=True);checks=[];objective=0.;perrow=[]
        for i,row in enumerate(rows):
            if row['advantage']==0:
                perrow.append(dict(episode_id=row['episode_id'],advantage=0.,zero_advantage_skipped=True));continue
            values=core.selected_logprobs(model,row['root_turns'][0],require_grad=True)
            replay=core.replay_check(values.detach().cpu().tolist(),baseline[i][0])
            replay.update(episode_id=row['episode_id'],full_action_tokens=values.numel(),
                selected_loss_tokens=sum(row['selection_mask']))
            checks.append(replay)
            if not replay['passed']:
                s.write_x(output/'REPLAY.json',dict(passed=False,checks=checks,optimizer_steps=0))
                raise ValueError('HF gradient replay mismatch; no optimizer step')
            term=core.selection_loss(values,weights[i][0],row['advantage'],row['selection_mask'])
            objective+=float(term.detach());term.backward()
            perrow.append(dict(episode_id=row['episode_id'],advantage=row['advantage'],reward=row['reward'],
                selected_loss_tokens=sum(row['selection_mask']),zero_loss_other_action_tokens=len(row['selection_mask'])-sum(row['selection_mask'])))
            del values,term
        assert len(checks)==8 and len(perrow)==18
        preclip=float(torch.nn.utils.clip_grad_norm_(list(named.values()),1.))
        assert math.isfinite(preclip) and preclip>0
        gradients={n:p.grad.detach().cpu().clone() if p.grad is not None else torch.zeros_like(p,device='cpu') for n,p in named.items()}
        assert all(torch.isfinite(g).all() for g in gradients.values())
        a_norm=norm(g for n,g in gradients.items() if '.lora_A.' in n)
        b_norm=norm(g for n,g in gradients.items() if '.lora_B.' in n)
        assert a_norm==0. and b_norm>0.,'zero-B first step must localize to B'
        torch.save(gradients,output/'gradients.pt')
        s.write_x(output/'REPLAY.json',dict(passed=True,checks=checks,rows=perrow,optimizer_steps=0,
            objective=objective,denominator=18,preclip_gradient_norm=preclip,clip=1.,
            LoRA_A_gradient_norm=a_norm,LoRA_B_gradient_norm=b_norm,localization_expected='zero-B init implies zero A and nonzero B gradients',
            nonzero_actions=8,zero_actions=10,selected_loss_tokens=sum(sum(r['selection_mask']) for r in rows if r['advantage']!=0)))
        core.restore_rng(output/'initial-rng.pt',torch)
        branch=core.math.apply_fresh_adam_branch(model,initial,gradients,learning_rate=s.LEARNING_RATE);steps=1
        updated=core.math.snapshot_trainable(model);delta=norm(updated[n].double()-initial[n].double() for n in initial)
        assert math.isfinite(delta) and delta>0.
        cp=output/'checkpoint-0001';cp.mkdir();model.save_pretrained(cp)
        torch.save(branch['optimizer'].state_dict(),cp/'optimizer.pt');core.save_rng(cp/'rng.pt',torch)
        torch.save(updated,cp/'trainable.pt')
        state=dict(schema='b05-flat18-BA-RLOO-state-v1',status='UPDATED',optimizer_steps=1,
            start='released_base_new_zero_B_LoRA',base=str(s.BASE),initial_config_sha256=s.sha(s.CONFIG_SOURCE),
            init_seed=s.INIT_SEED,learning_rate=s.LEARNING_RATE,denominator=18,groups=9,group_size=2,
            nonzero_actions=8,zero_actions=10,reward='mean recall over present classes',
            baseline='other reply reward; G2 RLOO',gradient_clip=1.,token_TIS_cap=2.,token_TIS_biased=True,
            sequence_IS_unbiased=False,loss_scope='native eligible_ids array-overlap tokens only',
            fresh_AdamW=True,weight_decay=0.,optimizer_state_empty_before_step=branch['optimizer_state_empty_before_step'],
            optimizer_state_steps=branch['optimizer_state_steps'],initial_trainable_identity=core.math.snapshot_digest(initial),
            updated_trainable_identity=core.math.snapshot_digest(updated),adapter_delta_l2=delta,
            source_input_sha256=s.sha(s.INPUTS),held_frozen_sha256=s.sha(s.ROOT/'HELD_PUBLIC.json'),
            elapsed_seconds=time.monotonic()-started,peak_allocated_bytes=torch.cuda.max_memory_allocated(),
            selected_loss_tokens=s.read(output/'REPLAY.json')['selected_loss_tokens'])
        s.write_x(cp/'state.json',state)
        binding=dict(schema='b05-flat-BA18-checkpoint-binding-v1',alias=s.ALIAS,base=str(s.BASE),
            checkpoint=str(cp),adapter_sha256=s.sha(cp/'adapter_model.safetensors'),
            adapter_config_sha256=s.sha(cp/'adapter_config.json'),state_sha256=s.sha(cp/'state.json'),
            source_ready_sha256=s.sha(s.READY),selection='fixed sole step1; not outcome-selected')
        s.write_x(cp/'EVAL_BINDING.json',binding)
        artifacts={str(p):s.sha(p) for p in (cp/'adapter_model.safetensors',cp/'adapter_config.json',cp/'optimizer.pt',cp/'rng.pt',
            cp/'trainable.pt',cp/'state.json',cp/'EVAL_BINDING.json',output/'initial-trainable.pt',output/'initial-rng.pt',
            output/'INITIAL.json',output/'PRESTEP_QUALIFICATION.json',output/'PRESTEP_LOGPS.json',output/'REPLAY.json',output/'gradients.pt')}
        s.write_x(cp/'STEP_COMMIT.json',dict(schema='b05-flat18-single-step-commit-v1',optimizer_steps=1,
            source_ready_sha256=s.sha(s.READY),input_sha256=s.sha(s.INPUTS),artifacts_sha256=artifacts))
        s.write_x(output/'RESULT.json',dict(status='UPDATED',optimizer_steps=1,checkpoint=str(cp),
            state_sha256=s.sha(cp/'state.json'),step_commit_sha256=s.sha(cp/'STEP_COMMIT.json'),
            binding_sha256=s.sha(cp/'EVAL_BINDING.json'),adapter_delta_l2=delta,
            elapsed_seconds=time.monotonic()-started,ready_sha256=s.sha(s.READY)))
    except BaseException as error:
        if not (output/'RESULT.json').exists():s.write_x(output/'RESULT.json',dict(status='FAILED',optimizer_steps=steps,
            error=dict(type=type(error).__name__,message=str(error),traceback=traceback.format_exc()),
            elapsed_seconds=time.monotonic()-started,ready_sha256=s.sha(s.READY)))
        raise
    finally:
        signal.alarm(0)
        if model is not None:del model
        import gc;gc.collect();torch.cuda.empty_cache()

if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--output',type=Path,required=True);parser.add_argument('--seconds',type=int,required=True)
    args=parser.parse_args();run(args.output,args.seconds)
