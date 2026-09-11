"""Actual error-family fixtures and no-reroll continuation boundaries."""
import importlib
import json
from copy import deepcopy
from pathlib import Path

import pytest


def module():
    assert (Path(__file__).parent / 'native.py').exists(), 'equality continuation not implemented'
    return importlib.import_module('native')


def failed_calls():
    n = module()
    attempt = n.a.PRIOR_RUN / 'round-01/collection/rollout'
    audits = {}
    for p in (attempt.with_name('rollout-routing') / 'role-audit').glob('*-result.json'):
        v = n.c.read(p)
        if v['status'] == 'error':
            audits[v['request_id']] = v
    binding = n.c.read(attempt / 'SPEC.json')['role_binding']
    result = []
    for p in (attempt / 'episodes').glob('*.json'):
        r = n.c.read(p)
        for t in r['episode']['traces']:
            for call in t['calls']:
                if call.get('error'):
                    result.append((call, audits[call['acp']['request_id']], binding, r['coordinate']['seed']))
    return result


def test_exact_actual_equality_family_and_unchanged_overlong_family():
    n = module()
    cases = failed_calls()
    assert len(cases) == 6
    equality = overlong = 0
    for call, audit, binding, seed in cases:
        length = len(audit['native_wire_request']['body']['token_ids'])
        if length == 8192:
            equality += 1
            with pytest.raises(ValueError, match='not the explicit decoder-context'):
                n.ORIGINAL_VERIFY(call, audit, binding, seed)
            proof = n.verify_failed_call(call, audit, binding, seed)
            assert proof['prompt_tokens'] == 8192 and proof['training_admission'] is False
        else:
            overlong += 1
            assert n.verify_failed_call(call, audit, binding, seed) == n.ORIGINAL_VERIFY(call, audit, binding, seed)
    assert equality == overlong == 3


def test_equality_rule_rejects_changed_role_sampling_tokens_or_completion():
    n = module()
    base = next(c for c in failed_calls() if len(c[1]['native_wire_request']['body']['token_ids']) == 8192)
    changes = ['root', 'alias', 'count', 'limit', 'other400', 'http500', 'seed', 'node', 'usage', 'completion', 'choices', 'link', 'role_hash']
    for mutation in changes:
        call, audit, binding, seed = deepcopy(base)
        if mutation == 'root': audit['depth'] = 0
        elif mutation == 'alias': audit['actual_alias'] = binding['role_map']['root']
        elif mutation == 'count': audit['native_wire_request']['body']['token_ids'].pop()
        elif mutation == 'limit': audit['native_wire_response']['body'] = audit['native_wire_response']['body'].replace('8192', '8193')
        elif mutation == 'other400': audit['native_wire_response']['body'] = json.dumps({'error': {'message': 'unrelated rejection', 'type': 'BadRequestError', 'code': 400}})
        elif mutation == 'http500': audit['native_wire_response']['http_status'] = 500
        elif mutation == 'seed': seed += 1
        elif mutation == 'node': call['node'] = 0
        elif mutation == 'usage': call['usage'] = {'completion_tokens': 0}
        elif mutation == 'completion': audit['native_response'] = {}
        elif mutation == 'choices': audit['native_wire_response']['body'] = json.dumps({'error': {}, 'choices': []})
        elif mutation == 'link': audit['request_id'] = 'different'
        elif mutation == 'role_hash': audit['role_map_sha256'] = 'different'
        with pytest.raises((ValueError, KeyError), match='.'):
            n.verify_failed_call(call, audit, binding, seed)


def test_saved_stage_map_starts_with_training_not_service_or_rollout(tmp_path):
    n = module()
    assert (Path(__file__).parent / 'driver.py').exists(), 'continuation driver missing'
    loader = importlib.util.spec_from_file_location('equality_test_driver', Path(__file__).parent / 'driver.py')
    d = importlib.util.module_from_spec(loader)
    loader.loader.exec_module(d)
    schedule = d.schedule()
    assert schedule[0] == ['training', 1]
    assert ['collection', 1] not in schedule and ['validation', 0] not in schedule
    assert [s[1] for s in schedule if s[0] == 'training'] == list(range(1, 17))
    assert [s[1] for s in schedule if s[0] == 'validation'] == [4, 8, 12, 16]
    envelope = d.run_envelope(1000, 'synthetic-no-GPU')
    assert envelope['deadline_epoch'] == 17829.460386276245
    assert envelope['inherited_optimizer_steps'] == 0
    assert envelope['prior_elapsed_seconds'] + envelope['new_work_cap_seconds'] == 18000
    assert d.dispatch_command([str(n.c.TRAIN_PYTHON), str(n.a.BROAD / 'campaign_train.py'), '--group', 'fake'])[1] == str(n.a.ROOT / 'train.py')
    with pytest.raises(ValueError):
        d.dispatch_command(['python', 'unknown.py'])
