"""One fresh8 conditional-final RLOO step; all 32 denominators, exact zero skipping."""
import argparse
import math
import os
from pathlib import Path
import random
import signal
import time
import traceback

import core
import study


def qualify(model, rows):
    active = [r for r in rows if r['advantage'] != 0]
    selected = core.scorer._all_logprobs(model, active)
    active_weights, diagnostics = core.scorer._build_token_diagnostics(active, selected)
    diagnostics['conditional_final_sequence_diagnostics'] = diagnostics.pop('full_trajectory_diagnostics')
    diagnostics.update(objective='fresh8_conditional_final_RLOO', baseline='group mean with G/(G-1)',
        denominator=32, all_source_trajectories=32, zero_advantage_skipped=20,
        exact_sequence_IS_claim=False, full_RLM_IS_claim=False,
        native_HF_equality_required=False, mixed_group_gate=False,
        qualified_nonzero_final_actions=len(active))
    baseline=[]; weights=[]; cursor=0
    for row in rows:
        if row['advantage'] == 0:
            assert row['root_turns'] == []
            baseline.append([]); weights.append([])
        else:
            baseline.append(selected[cursor]); weights.append(active_weights[cursor]); cursor+=1
    assert cursor == len(active)
    return baseline, weights, diagnostics


def tensor_norm(values):
    return math.sqrt(math.fsum(float(v.double().square().sum()) for v in values))


def accumulate(model, rows, baseline, weights, output):
    """Stream one final-action graph; never construct an optimizer before all replay gates."""
    import torch
    output = Path(output); output.mkdir(parents=True, exist_ok=False)
    assert len(rows) == len(baseline) == len(weights) == 32
    named = {n:p for n,p in model.named_parameters() if p.requires_grad}
    model.zero_grad(set_to_none=True)
    replay = []; component = {}; objective = 0.; per_episode = []
    for i, row in enumerate(rows):
        assert row['advantage'] == (4*row['reward']-4*row['baseline'])/3
        if row['advantage'] == 0:
            assert row['root_turns'] == [] and baseline[i] == [] and weights[i] == []
            per_episode.append(dict(episode_id=row['episode_id'], reward=row['reward'],
                advantage=0., selected_HF_logprobs=[], zero_advantage_skipped=True))
            continue
        assert len(row['root_turns']) == 1
        turn = row['root_turns'][0]
        values = core.selected_logprobs(model, turn, require_grad=True)
        selected = values.detach().cpu().tolist()
        check = core.replay_check(selected, baseline[i][0])
        check.update(episode_id=row['episode_id'], index=i, tokens=len(selected))
        replay.append(check)
        if not check['passed']:
            model.zero_grad(set_to_none=True)
            receipt = dict(passed=False, optimizer_steps=0, reason='HF_REPLAY_MISMATCH', replay=replay)
            study.write_x(output/'REPLAY.json', receipt)
            return receipt
        loss = core.loss(values, weights[i][0], row['advantage'])
        objective += float(loss.detach())
        part_rows = {}
        if row['advantage'] < 0:
            parts = turn['diagnostic_token_parts']
            present = [key for key in ('body','whitespace','eos') if key in parts]
            for j, key in enumerate(present):
                indices = [k for k, part in enumerate(parts) if part == key]
                term = core.loss(values[indices], [weights[i][0][k] for k in indices], row['advantage'])
                grads = torch.autograd.grad(term, tuple(named.values()),
                    retain_graph=j < len(present)-1, allow_unused=True)
                part_rows[key] = dict(tokens=len(indices), objective=float(term.detach()),
                                      parameter_gradient_l2=tensor_norm(g for g in grads if g is not None))
                aggregate = component.setdefault(key, {})
                for (name, p), g in zip(named.items(), grads, strict=True):
                    if g is None: continue
                    g = g.detach()
                    if p.grad is None: p.grad = g.clone()
                    else: p.grad.add_(g)
                    cpu = g.cpu().clone()
                    if name in aggregate: aggregate[name].add_(cpu)
                    else: aggregate[name] = cpu
                del grads, term
        else:
            loss.backward()
        per_episode.append(dict(episode_id=row['episode_id'], reward=row['reward'],
            advantage=row['advantage'], selected_HF_logprobs=selected,
            negative_final_component_gradients=part_rows))
        del values, loss
    norm = float(torch.nn.utils.clip_grad_norm_(list(named.values()), 1.0))
    passed = math.isfinite(norm) and norm > 0
    gradients = {n:(p.grad.detach().cpu().clone() if p.grad is not None else torch.zeros_like(p,device='cpu'))
                 for n,p in named.items()}
    passed = passed and all(torch.isfinite(g).all().item() for g in gradients.values())
    receipt = dict(passed=passed, optimizer_steps=0, replay=replay, objective=objective,
        gradient_norm_before_clip=norm if math.isfinite(norm) else None, clipping_norm=1.,
        negative_component_gradient_l2={k:tensor_norm(v.values()) for k,v in component.items()},
        localization='Actual parameter gradients of negative-sample token subsets; all subsets are summed, not separately optimized.',
        episodes=per_episode, denominator=32, mixed_group_gate=False,
        zero_advantage_skipped=sum(r['advantage']==0 for r in rows),
        nonzero_final_actions=len(replay))
    study.write_x(output/'REPLAY.json', receipt)
    torch.save(component, output/'negative-component-gradients.pt')
    torch.save(gradients, output/'gradients.pt')
    if not passed: model.zero_grad(set_to_none=True)
    return dict(receipt, gradients=gradients)


def preflight():
    ready = study.verify()
    rows = study.validate_inputs(study.read(study.INPUTS))
    assert core.scorer.study is study and core.scorer.math_core is core.math
    return ready, rows


def run(output, seconds):
    ready, rows = preflight()
    data = study.read(study.INPUTS)
    assert seconds == study.SCIENCE_SECONDS and Path(output) == study.OUTPUT
    if not os.environ.get('CUDA_VISIBLE_DEVICES'):
        raise RuntimeError('CPU_ENTRY_VERIFIED: MAIN must assign one GPU before training')
    import numpy as np
    import torch
    from peft import PeftModel, get_peft_model_state_dict
    from safetensors.torch import load_file
    from transformers import AutoModelForCausalLM
    assert torch.cuda.device_count() == 1
    output = Path(output); output.mkdir(parents=True, exist_ok=True)
    assert {p.name for p in output.iterdir()} <= {'OWNER_START.json','train.stdout','train.stderr'}
    started = time.monotonic(); model = None; optimizer_steps = 0
    def timeout(signum, frame): raise TimeoutError('fixed-baseline science wall cap')
    signal.signal(signal.SIGALRM, timeout); signal.alarm(seconds)
    study.write_x(output/'START.json', dict(ready_sha256=study.sha(study.READY),
        ready_identity=ready['identity'], input_sha256=study.sha(study.INPUTS),
        seed=study.SEED, numpy_seed=study.NP_SEED, science_seconds=seconds))
    try:
        torch.set_num_threads(4); random.seed(study.SEED); np.random.seed(study.NP_SEED)
        torch.manual_seed(study.SEED); torch.cuda.manual_seed_all(study.SEED)
        torch.backends.cuda.matmul.allow_tf32=False; torch.backends.cudnn.allow_tf32=False
        base = AutoModelForCausalLM.from_pretrained(str(study.BASE), local_files_only=True,
            torch_dtype=torch.bfloat16, attn_implementation='sdpa', device_map={'':'cuda:0'})
        base.config.use_cache=False
        model = PeftModel.from_pretrained(base, str(study.CHECKPOINT), is_trainable=True,
                                         autocast_adapter_dtype=True)
        disk = load_file(str(study.CHECKPOINT/'adapter_model.safetensors'))
        actual = get_peft_model_state_dict(model)
        assert actual.keys() == disk.keys()
        assert all(torch.equal(actual[k].detach().cpu(), disk[k]) for k in disk)
        model.train()
        for module in model.modules():
            if isinstance(module, torch.nn.Dropout): module.eval()
        model.gradient_checkpointing_enable(gradient_checkpointing_kwargs={'use_reentrant':False})
        model.enable_input_require_grads()
        initial = core.math.snapshot_trainable(model)
        assert all(v.dtype == torch.float32 for v in initial.values())
        torch.save(initial, output/'initial-trainable.pt'); core.save_rng(output/'initial-rng.pt', torch)
        study.write_x(output/'INITIAL.json', dict(parent_adapter_sha256=study.ADAPTER_SHA,
            loaded_adapter_exact=True, trainable_identity=core.math.snapshot_digest(initial),
            trainable_tensors=len(initial), trainable_parameters=sum(v.numel() for v in initial.values()),
            initial_tensor_file_sha256=study.sha(output/'initial-trainable.pt'),
            initial_rng_sha256=study.sha(output/'initial-rng.pt'), precision='BF16 base / FP32 LoRA',
            attention='sdpa', no_KV_cache=True, dropout_disabled=True, model_training=True,
            nonreentrant_checkpoint=True))
        baseline, weights, diagnostics = qualify(model, rows)
        study.write_x(output/'PRESTEP_QUALIFICATION.json', diagnostics)
        study.write_x(output/'PRESTEP_LOGPS.json', dict(episodes=baseline, detached_token_weights=weights))
        gradient = accumulate(model, rows, baseline, weights, output/'gradient')
        if not gradient['passed']:
            study.write_x(output/'RESULT.json', dict(status='NO_UPDATE', optimizer_steps=0,
                reason=gradient.get('reason','ZERO_OR_NONFINITE_GRADIENT'),
                ready_identity=ready['identity'], elapsed_seconds=time.monotonic()-started))
            return
        core.restore_rng(output/'initial-rng.pt', torch)
        branch = core.math.apply_fresh_adam_branch(model, initial, gradient['gradients'], learning_rate=study.LEARNING_RATE)
        optimizer_steps = 1
        current = core.math.snapshot_trainable(model)
        delta = tensor_norm(current[n].double()-initial[n].double() for n in initial)
        assert math.isfinite(delta) and delta > 0
        post = core.scorer._all_logprobs(model, rows)
        study.write_x(output/'POSTSTEP_LOGPS.json', dict(episodes=post, diagnostic_only=True,
            not_rollout_accuracy=True, conditioning_on_frozen_source_observations=True))
        cp = output/'checkpoint-0001'; cp.mkdir()
        model.save_pretrained(cp); torch.save(branch['optimizer'].state_dict(),cp/'optimizer.pt')
        core.save_rng(cp/'rng.pt',torch)
        state = dict(schema='cp32-fresh8-final-RLOO-state-v1', status='UPDATED',
            parent_sft_step=32, optimizer_steps=1, fresh_AdamW=True, optimizer_state_steps=branch['optimizer_state_steps'],
            optimizer_state_empty_before_step=branch['optimizer_state_empty_before_step'], learning_rate=study.LEARNING_RATE,
            weight_decay=0., betas=[.9,.999], eps=1e-8, gradient_clip=1., baseline='group mean; G/(G-1) correction', denominator=32,
            groups=8, trajectories=32, exact_reward_positive=7, exact_reward_negative=25,
            nonzero_advantages=12, zero_advantage_trajectories=20, mixed_groups=3,
            actual_final_tokens=data['selected_action_tokens'],
            zero_loss_other_root_tokens=data['unselected_root_action_tokens'], child_loss_tokens=0,
            policy_objective='conditional final sampled tokens, within-group leave-one-out advantage',
            token_TIS_cap=2., token_TIS_biased=True, exact_sequence_IS_claim=False,
            terminal_shared_weights_caveat=True, replay_passed=all(x['passed'] for x in gradient['replay']),
            replay_actions=12, mixed_group_gate=False,
            zero_advantage_skipped_exactly=True, all_source_native_returns=66, parent_adapter_sha256=study.ADAPTER_SHA,
            source_ready_sha256=study.sha(study.READY), ready_identity=ready['identity'],
            input_sha256=study.sha(study.INPUTS), initial_tensor_identity=core.math.snapshot_digest(initial),
            updated_tensor_identity=core.math.snapshot_digest(current), adapter_delta_l2=delta,
            gradient_norm_before_clip=gradient['gradient_norm_before_clip'],
            parent_binding_sha256=study.sha(study.ROOT/'PARENT_BINDING.json'),
            parent_qualification_sha256=study.sha(study.ROOT/'PARENT_CHECKPOINT_QUALIFICATION.json'),
            initial_sha256=study.sha(output/'INITIAL.json'), initial_rng_sha256=study.sha(output/'initial-rng.pt'),
            gradient_receipt_sha256=study.sha(output/'gradient/REPLAY.json'),
            gradient_sha256=study.sha(output/'gradient/gradients.pt'),
            prestep_qualification_sha256=study.sha(output/'PRESTEP_QUALIFICATION.json'),
            prestep_logps_sha256=study.sha(output/'PRESTEP_LOGPS.json'), poststep_logps_sha256=study.sha(output/'POSTSTEP_LOGPS.json'),
            adapter_sha256=study.sha(cp/'adapter_model.safetensors'), adapter_config_sha256=study.sha(cp/'adapter_config.json'),
            optimizer_sha256=study.sha(cp/'optimizer.pt'), rng_sha256=study.sha(cp/'rng.pt'),
            elapsed_seconds=time.monotonic()-started, peak_GPU_GiB=torch.cuda.max_memory_allocated()/2**30)
        study.write_x(cp/'state.json', state)
        binding = study.read(study.ROOT/'PARENT_BINDING.json')
        old_alias=binding['role_map']['root']; entry=dict(binding['models'].pop(old_alias))
        entry.update(path=str(cp), adapter_sha256=state['adapter_sha256'],
                     config_sha256=state['adapter_config_sha256'])
        binding['models'][study.ALIAS]=entry; binding['role_map']['root']=study.ALIAS
        binding.update(schema='cp32-fresh8-final-RLOO-binding-v1',
                       selection='one fixed step; no outcome checkpoint selection', parent_sft_step=32,
                       selection_path=str(cp/'state.json'), selection_sha256=study.sha(cp/'state.json'),
                       selection_semantics='Adaptively proposed fresh8 RLOO after complete source audit; fixed one-step endpoint.',
                       post_training_or_evaluation_checkpoint_selection=True,
                       endpoint_chosen_by_result=False, new_optimizer_steps=1,
                       state_sha256=study.sha(cp/'state.json'))
        study.write_x(cp/'EVAL_BINDING.json',binding)
        files={str(p):study.sha(p) for p in sorted(cp.iterdir()) if p.is_file()}
        study.write_x(cp/'STEP_COMMIT.json',dict(step=1, parent_sft_step=32, files_sha256=files,
            ready_sha256=study.sha(study.READY), input_sha256=study.sha(study.INPUTS)))
        study.write_x(output/'RESULT.json',dict(status='UPDATED', optimizer_steps=1,
            checkpoint=str(cp), step_commit_sha256=study.sha(cp/'STEP_COMMIT.json'),
            state_sha256=study.sha(cp/'state.json'), binding_sha256=study.sha(cp/'EVAL_BINDING.json'),
            ready_identity=ready['identity'], ready_sha256=study.sha(study.READY),
            adapter_delta_l2=delta, elapsed_seconds=time.monotonic()-started,
            peak_GPU_GiB=torch.cuda.max_memory_allocated()/2**30))
    except BaseException as e:
        study.write_x(output/'FAILURE.json',dict(type=type(e).__name__, message=str(e),
            traceback=traceback.format_exc(), optimizer_steps=optimizer_steps,
            elapsed_seconds=time.monotonic()-started))
        if not (output/'RESULT.json').exists():
            study.write_x(output/'RESULT.json',dict(status='FAILED',optimizer_steps=optimizer_steps,
                ready_identity=ready['identity'],elapsed_seconds=time.monotonic()-started))
        raise
    finally:
        signal.alarm(0)


if __name__ == '__main__':
    parser=argparse.ArgumentParser(); parser.add_argument('--output',type=Path,default=study.OUTPUT)
    parser.add_argument('--seconds',type=int,default=study.SCIENCE_SECONDS)
    args=parser.parse_args(); run(args.output,args.seconds)
