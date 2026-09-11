"""Actual tiny PEFT Adam0→1→2 and saved-checkpoint no-double-step, CPU only."""
import torch
import pytest

import train as t

c = t.c


def test_actual_first_update_restore_and_second_generation(tmp_path):
    torch.set_num_threads(1)
    __import__('sys').modules.setdefault('campaign_train', t.broad)
    fixture = c.private('equality_tiny_fixture', c.OLD / 'test_training.py')
    model = fixture.tiny()
    base = {n: p.detach().clone() for n, p in model.named_parameters() if not p.requires_grad}
    original = tmp_path / 'original'
    model.save_pretrained(original, safe_serialization=True)
    policy = {'step': 0, 'path': str(original), 'adapter_sha256': c.file_hash(original / 'adapter_model.safetensors'),
        'config_sha256': c.file_hash(original / 'adapter_config.json'), 'optimizer_sha256': None, 'rng_sha256': None, 'state_sha256': None}
    recipe = c.read(t.a.BROAD / 'RECIPE.json')
    optimizer = t.trainer.make_optimizer(model, recipe)
    assert t.trainer.optimizer_step(optimizer) == 0
    first = c.generation_identity('CPU-fixture-not-research', 1, policy, 'fresh-first')
    rows = fixture.fresh_rows(model, policy['adapter_sha256'])
    child = fixture.fresh_rows(model, policy['adapter_sha256'])
    child[0]['turns'][0]['role_depth'] = 1
    with pytest.raises(ValueError, match='root'):
        t.trainer.update_generation(model, optimizer, child, tmp_path / 'invalid-child', recipe, first, {})
    result = t.trainer.update_generation(model, optimizer, rows, tmp_path / 'one', recipe, first, {'CPU-fixture': 'first'})
    assert result['optimizer_steps'] == t.trainer.optimizer_step(optimizer) == 1
    assert result['metrics']['child_loss_tokens'] == result['metrics']['observation_loss_tokens'] == 0
    policy = result['policy']
    before = {n: p.detach().clone() for n, p in model.named_parameters()}
    again = t.trainer.update_generation(model, optimizer, [], tmp_path / 'one', recipe, first, {'CPU-fixture': 'first'})
    assert again['recovered_checkpoint'] and t.trainer.optimizer_step(optimizer) == 1
    assert all(torch.equal(before[n], p) for n, p in model.named_parameters())
    from peft import PeftModel
    model = PeftModel.from_pretrained(fixture.tiny().unload(), policy['path'], is_trainable=True, autocast_adapter_dtype=True)
    assert all(torch.equal(before[n], p) for n, p in model.named_parameters())
    optimizer = t.trainer.make_optimizer(model, recipe)
    t.trainer.restore_optimizer(optimizer, policy, [n for n, p in model.named_parameters() if p.requires_grad])
    assert t.trainer.optimizer_step(optimizer) == 1
    second = c.generation_identity('CPU-fixture-not-research', 2, policy, 'fresh-second')
    result2 = t.trainer.update_generation(model, optimizer, fixture.fresh_rows(model, policy['adapter_sha256']),
        tmp_path / 'two', recipe, second, {'CPU-fixture': 'second'})
    assert result2['optimizer_steps'] == t.trainer.optimizer_step(optimizer) == 2
    assert result2['metrics']['trainable_parameter_delta_l2'] > 0
    assert all(torch.equal(base[n], p) for n, p in model.named_parameters() if not p.requires_grad)
