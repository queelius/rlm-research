"""The original four-step loop; only current-action row weighting and identity differ."""
import argparse
import functools
import math
import time
from pathlib import Path

import study as s

with s.aliases({'study': s.prior()}):
    impl = s.load('rowmean_original_training_loop', s.PRIOR / 'train.py', s.PINS[s.PRIOR / 'train.py'])
original_verify = impl.verify


def contribution(loss, count, batch_rows):
    if count <= 0 or batch_rows <= 0:
        raise ValueError('zero supervised row or batch')
    coefficient = loss.new_tensor(1. / (batch_rows * count))
    return loss * coefficient, float(coefficient.detach())


def update(model, optimizer, rows, device, deadline=None):
    import torch
    params = [p for p in model.parameters() if p.requires_grad]
    counts = [sum(v != -100 for v in row['labels'][1:]) for row in rows]
    if not rows or min(counts) <= 0:
        raise ValueError('zero supervised row or batch')
    denominator = sum(counts)
    optimizer.zero_grad(set_to_none=True)
    ledger, total_ce, objective = [], 0., 0.
    for row, expected_count in zip(rows, counts):
        if deadline is not None and time.monotonic() > deadline:
            raise TimeoutError('600s accumulated training cap')
        batch = {key: value.to(device) for key, value in impl.data.collate([row], 0).items()}
        result = model(input_ids=batch['input_ids'], attention_mask=batch['attention_mask'], use_cache=False)
        loss, count = impl.old.loss_sum(result.logits, batch['labels'])
        if count != expected_count or not torch.isfinite(loss):
            raise ValueError('nonfinite loss or changed shifted-target count')
        weighted, coefficient = contribution(loss, count, len(rows))
        weighted.backward()
        raw, value = float(loss.detach()), float(weighted.detach())
        total_ce += raw
        objective += value
        ledger.append({'id': row['id'], 'kind': row['kind'], 'target_tokens': count,
                       'ce_sum': raw, 'coefficient_fp32': coefficient, 'weighted_ce': value,
                       'row_mass_actual': coefficient * count, 'nominal_row_mass': 1. / len(rows),
                       'token_objective_coefficient': 1. / denominator})
    norm = torch.nn.utils.clip_grad_norm_(params, 1.)
    if not torch.isfinite(norm) or not math.isfinite(objective):
        raise ValueError('nonfinite gradient/objective')
    if deadline is not None and time.monotonic() > deadline:
        raise TimeoutError('training cap before update')
    optimizer.step()
    return {'nll': objective, 'loss_normalization': 'equal_row_mean_of_action_token_mean_CE',
            'token_nll': total_ce / denominator, 'target_tokens': denominator,
            'gradient_norm': float(norm), 'row_losses': ledger,
            'row_mass_sum': sum(r['row_mass_actual'] for r in ledger),
            'nominal_row_mass_sum': sum(r['nominal_row_mass'] for r in ledger),
            'weighted_ce_sum': objective}


@functools.lru_cache(maxsize=1)
def verify():
    ready = s.verify()
    recipe, rows, original_identity = original_verify()
    if original_identity != s.PRIOR_IDENTITY:
        raise ValueError('original SFT identity changed')
    return recipe, rows, ready['identity']


impl.update = update
impl.verify = verify

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('command', choices=('verify', 'run'))
    parser.add_argument('--output', type=Path, default=s.ROOT / 'outputs/attempt-001/training')
    args = parser.parse_args()
    print({'verified': verify()[2], 'gpu_calls': 0} if args.command == 'verify' else impl.run(args.output))
