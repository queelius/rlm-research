import asyncio
import importlib
import json
from collections import Counter
from copy import deepcopy
from pathlib import Path
from types import SimpleNamespace

import httpx
import pytest

ROOT = Path(__file__).resolve().parent


def module():
    assert (ROOT / 'driver.py').exists(), 'B-only companion is not implemented'
    return importlib.import_module('driver')


def test_exact_eighty_crosswalk_and_only_model_changes():
    d = module()
    design, crosswalk = d.build_design()
    parent = d.read(d.PARENT / 'SPEC.json')
    assert len(design['plan']) == len(crosswalk) == 80
    assert Counter((r['arm'], r['grammar']) for r in design['plan']) == {
        (a, g): 20 for a in ('anonymous', 'indexed') for g in ('free', 'exact')}
    assert [r['dispatch_order'] for r in design['plan']] == list(range(80))
    for row in design['plan']:
        body = d.make_request(design, row)
        item = crosswalk[row['id']]
        for key in ('old_sft', 'indexed_final'):
            original = parent['requests'][item[key]]
            expected = deepcopy(original)
            expected['model'] = body['model']
            assert d.serialize(body) == d.serialize(expected)
            assert design['rendered_prompts'][row['id']] == parent['design']['rendered_prompts'][item[key]]
    bad = deepcopy(body)
    bad['max_tokens'] = 1
    with pytest.raises(ValueError, match='non-model'):
        d.assert_only_model(body, bad)


def test_strict_invalid_and_infrastructure_are_not_semantic_negatives():
    d = module()
    gold = {'records': [{'id': 'q0001', 'gold_label': 'positive'}], 'order': [0],
            'arm': 'indexed', 'labels': ['negative', 'positive']}
    assert d.g.score_labels('{"q0001":"positive"}', gold)['strict_correct'] == 1
    for text in ('{}', '{"q0001":"positive"', '{"q0001":"positive","q0001":"negative"}'):
        score = d.g.score_labels(text, gold)
        assert not score['schema_valid'] and score['aligned_records'] == 0
        assert score['predictions'] == [None]
    design, _ = d.build_design()
    summary = d.g.summarize(design, [])
    assert all(c['strict_full64_correct'] is None for c in summary['coordinates'])
    assert all(c['accuracy_among_aligned'] is None for c in summary['cells'])


def test_real_fake_http_collector_preserves_wire_alias_and_usage(tmp_path):
    d = module()
    design, _ = d.build_design()
    rows = design['plan'][:4]
    design['plan'] = design['coordinates'] = rows
    design['model_aliases']['Bfinal'] = 'fake-B'
    bodies = {r['id']: d.make_request(design, r) for r in rows}
    spec = {'design': design, 'requests': bodies,
            'request_sha256': {k: d.digest(v) for k, v in bodies.items()}}

    async def provider(request):
        body = json.loads(request.content)
        row = next(r for r in rows if bodies[r['id']] == body)
        records = design['batches'][row['batch_id']]['gold']['records']
        content = json.dumps([r['gold_label'] for r in records] if row['arm'] == 'anonymous'
                             else {r['id']: r['gold_label'] for r in records})
        return httpx.Response(200, json={'id': row['id'], 'model': body['model'], 'prompt_token_ids': [1],
            'choices': [{'message': {'content': content}, 'finish_reason': 'stop', 'token_ids': [2]}],
            'usage': {'prompt_tokens': 1, 'completion_tokens': 1}})

    async def go():
        async with httpx.AsyncClient(transport=httpx.MockTransport(provider),
                event_hooks={'request': [d.up.wire_hook(spec, tmp_path)]}) as client:
            return await d.g.collect_calls(client, 'http://fake/v1', spec, tmp_path)
    records, reason = asyncio.run(go())
    assert reason is None and len(records) == 4
    assert all(r['request']['model'] == 'fake-B' and r['score']['strict_correct'] == 64 for r in records)
    assert sum('structured_outputs' in r['request'] for r in records) == 2
    assert len(list((tmp_path / 'wire').glob('*.json'))) == 4
    assert all(not r['capture']['tools_executed'] for r in records)


def test_owned_single_alias_release_on_failed_collection(tmp_path):
    module()
    assert (ROOT / 'owned.py').exists(), 'owned B wrapper is not implemented'
    o = importlib.import_module('owned')
    weights_path = tmp_path / 'WEIGHTS.json'
    weights_path.write_text('{}')
    weights = {'models': {'Bfinal': {'path': '/frozen/checkpoint-0204',
                'model_sha256': 'model', 'config_sha256': 'config'}}}
    binding = o.service_binding(weights, weights_path)
    assert list(binding['models']) == [o.ALIAS]
    assert binding['role_map'] == {'root': o.ALIAS, 'children': [o.ALIAS]}
    events = []
    def command(directory, name, argv, cap, deadline):
        events.append((name, cap))
        if name == 'B-run':
            raise RuntimeError('provider failure')
    suite = SimpleNamespace(PYTHON='python', c=SimpleNamespace(write_once=lambda p, v: None),
        start_service=lambda *a: events.append(('start', None)), command=command,
        release_service=lambda *a: events.append(('release', None)))
    with pytest.raises(RuntimeError, match='provider failure'):
        o.execute(tmp_path / 'owned', suite, weights, weights_path)
    assert events == [('start', None), ('B-bind', 120), ('B-run', 930), ('release', None)]


def test_deadline_and_wrong_weight_are_rejected():
    d = module()
    assert d.collection_budget(1000, 1001) == 900
    assert d.collection_budget(1000, 2500) == 300
    with pytest.raises(TimeoutError):
        d.collection_budget(1000, 2800)
    with pytest.raises(ValueError, match='Bfinal'):
        d.check_model_sha('not-the-fixed-B-model')


def test_provider_error_is_captured_as_infrastructure_null(tmp_path):
    d = module()
    design, _ = d.build_design()
    row = design['plan'][0]
    design['plan'] = [row]
    body = d.make_request(design, row)
    spec = {'design': design, 'requests': {row['id']: body},
            'request_sha256': {row['id']: d.digest(body)}}
    count = 0
    async def provider(request):
        nonlocal count
        count += 1
        return httpx.Response(400, json={'error': {'message': 'fake provider failure'}})
    async def go():
        async with httpx.AsyncClient(transport=httpx.MockTransport(provider),
                event_hooks={'request': [d.up.wire_hook(spec, tmp_path)]}) as client:
            return await d.g.collect_calls(client, 'http://fake/v1', spec, tmp_path)
    records, reason = asyncio.run(go())
    assert count == len(records) == 1 and reason is not None
    score = d.g.score_coordinate(design, row, records)
    assert score['strict_full64_correct'] is None and score['aligned_records'] == 0
    assert len(list((tmp_path / 'calls').glob('*.json'))) == 1
