"""Eight complete physical-root SFT passes, explicit episode/turn/token weights."""
import argparse
import importlib.metadata
import math
import os
import random
import time
import traceback
import uuid
from pathlib import Path

import study as s

with s.aliases({'study': s.prior()}):
    inherited = s.load('success_original_train_helpers', s.PRIOR / 'train.py', s.row.PINS[s.PRIOR / 'train.py'])
old, data = inherited.old, inherited.data


def contribution(ce, count, turns, episodes):
    if min(count, turns, episodes) <= 0:
        raise ValueError('zero action/turn/episode denominator')
    coefficient = ce.new_tensor(1. / (episodes * turns * count))
    return ce * coefficient, float(coefficient.detach())


def update(model, optimizer, episodes, device, deadline=None):
    import torch
    if not episodes or any(not e['turns'] for e in episodes):
        raise ValueError('empty full-corpus pass')
    optimizer.zero_grad(set_to_none=True)
    ledger, total_ce, objective, targets = [], 0., 0., 0
    for episode in episodes:
        for turn in episode['turns']:
            if deadline is not None and time.monotonic() >= deadline:
                raise TimeoutError('training cap before full-pass completion; no partial step')
            batch = {k: v.to(device) for k, v in data.collate([turn], 0).items()}
            result = model(input_ids=batch['input_ids'], attention_mask=batch['attention_mask'], use_cache=False)
            ce, count = old.loss_sum(result.logits, batch['labels'])
            if count != len(turn['input_ids']) - turn['prompt_length'] or not torch.isfinite(ce):
                raise ValueError('shifted target count/nonfinite CE')
            weighted, coefficient = contribution(ce, count, len(episode['turns']), len(episodes))
            weighted.backward()
            value, raw = float(weighted.detach()), float(ce.detach())
            ledger.append(dict(episode_id=episode['episode_id'], turn_id=turn['id'], target_tokens=count,
                coefficient_fp32=coefficient, actual_turn_mass=coefficient * count,
                nominal_turn_mass=1. / (len(episodes) * len(episode['turns'])), ce_sum=raw, weighted_ce=value))
            total_ce += raw
            objective += value
            targets += count
    norm = torch.nn.utils.clip_grad_norm_([p for p in model.parameters() if p.requires_grad], 1.)
    if not torch.isfinite(norm) or norm <= 0 or not math.isfinite(objective):
        raise ValueError('nonfinite/zero gradient or objective')
    if deadline is not None and time.monotonic() >= deadline:
        raise TimeoutError('training cap before optimizer step')
    optimizer.step()
    return dict(weighted_ce=objective, token_nll=total_ce / targets, target_tokens=targets,
                episodes=len(episodes), root_turns=len(ledger), gradient_norm=float(norm),
                mass_sum=sum(r['actual_turn_mass'] for r in ledger), turn_losses=ledger)


def checkpoint_state(path, identity, corpus):
    state = s.read(path / 'state.json')
    if (state['identity'] != identity or state['corpus_sha256'] != corpus or state['cursor'] != 0
            or state['epoch'] != state['step'] or not 1 <= state['step'] <= 8
            or path.name != f"checkpoint-{state['step']:04d}"):
        raise ValueError('full-pass checkpoint identity/cursor changed')
    required = {'adapter_model.safetensors', 'adapter_config.json', 'optimizer.pt', 'rng_state.pt'}
    if not required <= state['files_sha256'].keys():
        raise ValueError('checkpoint missing members')
    for name, expected in state['files_sha256'].items():
        if Path(name).name != name:
            raise ValueError('invalid checkpoint member')
        s.check(path / name, expected)
    return state


def restore_optimizer(optimizer, path, device, step):
    import torch
    optimizer.load_state_dict(torch.load(path / 'optimizer.pt', map_location=device, weights_only=True))
    if {int(v['step']) for v in optimizer.state.values()} != {step}:
        raise ValueError('saved Adam step differs from full-pass cursor')
    for group in optimizer.param_groups:
        if (group['lr'], group['weight_decay'], group['betas'], group['eps']) != (2e-5, 0., (.9, .999), 1e-8):
            raise ValueError('saved Adam recipe differs')
    rng = torch.load(path / 'rng_state.pt', map_location='cpu', weights_only=True)
    torch.set_rng_state(rng['torch'])
    random.setstate(rng['python'])
    if str(device).startswith('cuda'):
        torch.cuda.set_rng_state_all(rng['cuda'])


def verify():
    ready = s.verify()
    episodes = s.read(s.ROOT / 'prepared/EPISODES.json')
    candidate_ids = s.read(s.SCREEN / 'CANDIDATES.json')['confirmed_coordinate_ids']
    if (len(episodes) != 27 or {e['episode_id'] for e in episodes} != set(candidate_ids)
            or sum(len(e['turns']) for e in episodes) != 114
            or sum(s.validate_turn(t) for e in episodes for t in e['turns']) != 15256):
        raise ValueError('exact27/114/15256 corpus differs')
    return ready, episodes, s.sha(s.ROOT / 'prepared/EPISODES.json')


def _run(output, resume, spent, started, invocation):
    import torch
    from peft import PeftModel
    from transformers import AutoModelForCausalLM
    ready, episodes, corpus = verify()
    identity = ready['identity']
    if not os.environ.get('CUDA_VISIBLE_DEVICES') or not torch.cuda.is_available() or torch.cuda.device_count() != 1:
        raise ValueError('MAIN must assign exactly one GPU')
    states, step, elapsed = [], 0, 0.
    if resume is None:
        output.mkdir(parents=True, exist_ok=False)
        s.write(output / 'RUN.json', dict(identity=identity, corpus_sha256=corpus, seed=s.TRAIN_SEED,
            starting_adapter_sha256=s.CONTROL_SHA, fresh_optimizer=True, started_epoch=time.time()))
    else:
        if s.read(output / 'RUN.json')['identity'] != identity:
            raise ValueError('resume run identity differs')
        paths = sorted(output.glob('checkpoint-*'))
        if not paths or resume.resolve() != paths[-1].resolve():
            raise ValueError('resume must use latest committed full pass in this attempt')
        previous = None
        for expected, path in enumerate(paths, 1):
            state = checkpoint_state(path, identity, corpus)
            if state['step'] != expected or state.get('previous_state_sha256') != previous:
                raise ValueError('noncontiguous checkpoint chain')
            previous = s.sha(path / 'state.json')
            states.append(state)
        step, elapsed = states[-1]['step'], states[-1]['elapsed_training_seconds']
        s.write(output / ('RESUME-' + uuid.uuid4().hex + '.json'), dict(checkpoint=str(resume), state_sha256=previous,
                cumulative_seconds=elapsed, identity=identity, fresh_optimizer=False, recorded_epoch=time.time()))
        if step == 8 and (output / 'RESULT.json').exists():
            return s.read(output / 'RESULT.json')
    s.write(output / ('INVOCATION_OPEN-' + invocation + '.json'),
            dict(identity=identity, started_epoch=time.time(), prior_seconds=spent))
    deadline = started + max(0, 1200 - spent)
    if time.monotonic() >= deadline:
        raise TimeoutError('cumulative training invocation cap exhausted')
    manifest = s.read(s.prior().BASE / 'local-research-manifest.json')
    for filename, expected in manifest['files'].items():
        s.check(s.prior().BASE / filename, expected)
    random.seed(s.TRAIN_SEED)
    torch.manual_seed(s.TRAIN_SEED)
    torch.cuda.manual_seed_all(s.TRAIN_SEED)
    base = AutoModelForCausalLM.from_pretrained(s.prior().BASE, local_files_only=True, dtype=torch.bfloat16,
                                               attn_implementation='sdpa', device_map={'': 'cuda:0'})
    loaded = resume if resume is not None else s.START
    model = PeftModel.from_pretrained(base, loaded, is_trainable=True, autocast_adapter_dtype=True)
    audit = old.audit(model, loaded)
    s.write(output / ('LOAD_AUDIT.json' if resume is None else 'LOAD_AUDIT-' + uuid.uuid4().hex + '.json'), audit)
    params = [p for p in model.parameters() if p.requires_grad]
    if (not params or not all(p.dtype == torch.float32 for p in params)
            or any(p.requires_grad for name, p in model.named_parameters() if 'lora_' not in name)
            or any(c.lora_dropout != 0 or c.r != 8 for c in model.peft_config.values())):
        raise ValueError('exact rank8 FP32 LoRA-only training required')
    optimizer = torch.optim.AdamW(params, lr=2e-5, weight_decay=0.)
    if optimizer.state:
        raise ValueError('fresh optimizer unexpectedly has state')
    if resume is not None:
        restore_optimizer(optimizer, resume, 'cuda:0', step)
    model.train()
    model.gradient_checkpointing_enable(gradient_checkpointing_kwargs={'use_reentrant': False})
    initial = [p.detach().cpu().clone() for p in params]
    loaded_sha = s.sha(loaded / 'adapter_model.safetensors')
    for index in range(step, 8):
        order = list(range(27))
        random.Random(s.TRAIN_SEED + index).shuffle(order)
        metric = update(model, optimizer, [episodes[i] for i in order], 'cuda:0', deadline)
        delta = math.sqrt(sum(float((p.detach().cpu() - v).square().sum()) for p, v in zip(params, initial)))
        if not math.isfinite(delta) or delta <= 0:
            raise ValueError('no finite adapter change')
        metric.update(step=index + 1, episode_order=[episodes[i]['episode_id'] for i in order],
                      delta_l2_from_this_load=delta, loaded_adapter_sha256=loaded_sha)
        previous = s.sha(output / f'checkpoint-{index:04d}/state.json') if index else None
        path = old.save_checkpoint(model, optimizer, output, dict(identity=identity, corpus_sha256=corpus,
            epoch=index + 1, cursor=0, step=index + 1, metric=metric, previous_state_sha256=previous,
            optimizer_origin='fresh at new campaign0; persisted across full passes',
            elapsed_training_seconds=spent + time.monotonic() - started))
        states.append(checkpoint_state(path, identity, corpus))
        print({'step': index + 1, 'weighted_ce': metric['weighted_ce'], 'target_tokens': metric['target_tokens'],
               'gradient_norm': metric['gradient_norm'], 'checkpoint': str(path)}, flush=True)
    path = output / 'checkpoint-0008'
    selected = dict(rule='fixed final8; no validation selection', checkpoint=str(path), step=8,
        adapter_sha256=s.sha(path / 'adapter_model.safetensors'), config_sha256=s.sha(path / 'adapter_config.json'),
        state_sha256=s.sha(path / 'state.json'))
    if not (output / 'SELECTION.json').exists():
        s.write(output / 'SELECTION.json', selected)
    elif s.read(output / 'SELECTION.json') != selected:
        raise ValueError('fixed selection differs')
    result = dict(identity=identity, complete=True, selected=selected, optimizer_steps=8,
        episode_exposures=sum(t['metric']['episodes'] for t in states),
        root_turn_exposures=sum(t['metric']['root_turns'] for t in states),
        target_token_exposures=sum(t['metric']['target_tokens'] for t in states),
        starting_adapter_sha256=s.CONTROL_SHA, fresh_optimizer=True, child_loaded=False, child_updated=False,
        files_sha256=states[-1]['files_sha256'], cumulative_training_seconds=spent + time.monotonic() - started,
        peak_memory_allocated=torch.cuda.max_memory_allocated(), versions={k: importlib.metadata.version(k) for k in ('torch', 'transformers', 'peft')})
    if (result['episode_exposures'], result['root_turn_exposures'], result['target_token_exposures']) != (216, 912, 122048):
        raise ValueError('full-corpus exposures differ')
    s.write(output / 'RESULT.json', result)
    return result


def run(output, resume=None):
    started = time.monotonic()
    timings = [s.read(p) for p in output.glob('INVOCATION-*.json')] if output.exists() else []
    spent = sum(v['elapsed_seconds'] for v in timings)
    opened = {p.stem.removeprefix('INVOCATION_OPEN-') for p in output.glob('INVOCATION_OPEN-*.json')}
    closed = {p.stem.removeprefix('INVOCATION-') for p in output.glob('INVOCATION-*.json')}
    if opened != closed:
        raise ValueError('abrupt invocation has unknown spent time; automatic resume cannot reset cap')
    if resume is not None:
        saved = s.read(resume / 'state.json')['elapsed_training_seconds']
        spent = max(spent, saved)
    invocation = uuid.uuid4().hex
    try:
        return _run(output, resume, spent, started, invocation)
    finally:
        if (output / ('INVOCATION_OPEN-' + invocation + '.json')).exists():
            s.write(output / ('INVOCATION-' + invocation + '.json'),
                    dict(elapsed_seconds=time.monotonic() - started, prior_seconds=spent,
                         resume=str(resume) if resume else None, ended_epoch=time.time()))


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('command', choices=('verify', 'run'))
    parser.add_argument('--output', type=Path, default=s.ROOT / 'outputs/attempt-001/training')
    parser.add_argument('--resume', type=Path)
    args = parser.parse_args()
    try:
        print({'identity': verify()[0]['identity'], 'gpu_calls': 0} if args.command == 'verify' else run(args.output, args.resume))
    except BaseException as error:
        if args.command == 'run' and args.output.exists():
            s.write(args.output / ('FAILURE-' + uuid.uuid4().hex + '.json'), dict(type=type(error).__name__, message=str(error), traceback=traceback.format_exc()))
        raise
