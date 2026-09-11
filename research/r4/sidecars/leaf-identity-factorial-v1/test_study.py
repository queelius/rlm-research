"""Focused prospective namespace, scoring, request and owned-lifecycle checks."""
import asyncio
import importlib
import json
from collections import Counter, defaultdict
from copy import deepcopy
from pathlib import Path
from types import SimpleNamespace

import httpx
import pytest


def module():
    assert (Path(__file__).parent / 'study.py').exists(), 'approved factorial not implemented'
    return importlib.import_module('study')


def design():
    s = module()
    return s, s.build_design(s.build_data(s.read(s.PARENT / 'DATA.json')))


def test_disjoint_numbers_keep_source_identity_but_never_encode_ordinals():
    s = module()
    parent = s.read(s.PARENT / 'DATA.json')
    data = s.build_data(parent)
    changed = deepcopy(parent)
    for c in changed['contexts']:
        for r in c['records']:
            r['gold_label'] = 'UNUSED_HOST_GOLD'
    alternate = s.build_data(changed)
    for original, c, other in zip(parent['contexts'], data['contexts'], alternate['contexts']):
        assert c['records'] == original['records']
        assert c['presentations'] == original['presentations'] == other['presentations']
        assert c['disjoint_values_by_rank'] == other['disjoint_values_by_rank']
        values = c['disjoint_values_by_rank']
        assert len(values) == len(set(values)) == 64
        assert all(1000 <= v <= 9999 and not 1 <= v % 1000 <= 64 for v in values)
        assert not s.affine_sequence(values)
        for order in c['presentations']:
            displayed = [values[int(c['records'][j]['id'][1:]) - 1] for j in order]
            assert not s.affine_sequence(displayed)
    assert s.affine_sequence([1001 + i for i in range(64)])
    assert s.affine_sequence([(9991 + 17*i) % 10000 for i in range(64)])


def test_grid_is_complete_balanced_and_triples_share_actual_inputs():
    s, d = design()
    assert len(d['plan']) == len({r['id'] for r in d['plan']}) == 384
    counts = Counter((r['source_prefix'], r['number_namespace'], r['arm']) for r in d['plan'])
    assert len(counts) == 12 and set(counts.values()) == {32}
    by_rank = defaultdict(Counter)
    triples = defaultdict(list)
    for r in d['plan']:
        by_rank[r['cell_order']][r['condition_index']] += 1
        triples[r['context_index'], r['permutation'], r['repeat'], r['source_prefix'], r['number_namespace']].append(r)
    assert all(set(c.values()) <= {2, 3} and len(c) == 12 for c in by_rank.values())
    for rows in triples.values():
        bodies = [s.make_request(d, r) for r in rows]
        assert len(rows) == 3
        assert len({b['messages'][1]['content'].split(s.INPUT_MARKER)[1] for b in bodies}) == 1
        assert all(b['messages'][0] == bodies[0]['messages'][0] and b['tools'] == bodies[0]['tools'] for b in bodies)
    altered = deepcopy(d)
    for b in altered['batches']:
        for r in b['gold']['records']:
            r['gold_label'] = 'GOLD_MUST_NOT_ENTER_REQUEST'
    assert s.make_request(d, d['plan'][0]) == s.make_request(altered, altered['plan'][0])


def test_every_condition_preserves_original_permutation_and_prefix_swap_identity():
    s, d = design()
    original = s.read(s.PARENT / 'DATA.json')
    mappings = defaultdict(dict)
    for row in d['plan']:
        source = original['contexts'][row['context_index']]
        expected = [source['records'][j] for j in source['presentations'][row['permutation']]]
        actual = d['batches'][row['batch_id']]['gold']['records']
        assert [(r['group_id'], r['question']) for r in actual] == [(r['group_id'], r['question']) for r in expected]
        for old, new in zip(expected, actual):
            assert new['id'][0] == row['source_prefix']
            number = int(new['id'][1:])
            if row['number_namespace'] == 'overlap':
                assert number == int(old['id'][1:])
            else:
                assert number > 64 and not 1 <= number % 1000 <= 64
            key = (row['context_index'], row['number_namespace'], new['group_id'])
            previous = mappings[key].setdefault('value', number)
            assert number == previous


def test_tag_rules_prefix_swap_and_strict_failures():
    s, d = design()
    for row in d['plan'][:12]:
        gold = d['batches'][row['batch_id']]['gold']
        tags = s.expected_tags(gold['records'], row['arm'], row['source_prefix'])
        opposite = 'p' if row['source_prefix'] == 'q' else 'q'
        if row['arm'] == 'ordinal_tag':
            assert tags == [f'{opposite}{i:04d}' for i in range(1, 65)]
        elif row['arm'] == 'constant_tag':
            assert tags == [opposite + '0000'] * 64
        else:
            assert tags == [r['id'] for r in gold['records']]
        output = [{'tag': tag, 'label': r['gold_label']} for tag, r in zip(tags, gold['records'])]
        assert s.score_labels(json.dumps(output), gold)['strict_correct'] == 64
        output[0]['tag'] = 'wrong'
        score = s.score_labels(json.dumps(output), gold)
        assert not score['schema_valid'] and score['predictions'] == [None] * 64
        assert s.score_coordinate(d, row, [])['strict_correct_assignments'] is None


def test_numeric_source_alignment_is_diagnostic_not_primary_and_disjoint_is_null():
    s = module()
    records = [{'id': f'q{i:04d}', 'gold_label': 'positive' if i % 2 else 'negative'} for i in range(64, 0, -1)]
    gold = {'records': records, 'order': list(range(64)), 'arm': 'ordinal_tag',
            'labels': ['negative', 'positive'], 'source_prefix': 'q', 'number_namespace': 'overlap'}
    output = json.dumps([{'tag': f'p{i:04d}', 'label': 'positive' if i % 2 else 'negative'} for i in range(1, 65)])
    score = s.score_labels(output, gold)
    assert score['strict_correct'] == 0
    assert score['numeric_source_diagnostic']['correct'] == 64
    assert score['numeric_source_diagnostic']['mapping_coverage'] == 64
    disjoint = deepcopy(gold)
    disjoint['number_namespace'] = 'disjoint'
    for i, record in enumerate(disjoint['records']):
        record['id'] = f'q{2000 + i*7:04d}'
    score = s.score_labels(output, disjoint)
    assert score['strict_correct'] == 0
    assert score['numeric_source_diagnostic']['correct'] is None
    assert score['numeric_source_diagnostic']['mapping_coverage'] == 0
    invalid = s.score_labels(output[:-1], gold)
    assert invalid['numeric_source_diagnostic']['correct'] is None


def test_real_collector_retains_all_twelve_cells_and_separate_diagnostic(tmp_path):
    s, d = design()
    d['plan'] = d['coordinates'] = d['plan'][:12]
    requests = {r['id']: s.make_request(d, r) for r in d['plan']}
    spec = {'design': d, 'requests': requests, 'request_sha256': {k: s.digest(v) for k, v in requests.items()}}
    async def provider(request):
        body = json.loads(request.content)
        row = next(r for r in d['plan'] if requests[r['id']] == body)
        gold = d['batches'][row['batch_id']]['gold']
        tags = s.expected_tags(gold['records'], row['arm'], row['source_prefix'])
        content = json.dumps([{'tag': t, 'label': r['gold_label']} for t, r in zip(tags, gold['records'])])
        return httpx.Response(200, json={'model': s.ALIAS, 'prompt_token_ids': [1],
            'choices': [{'message': {'content': content}, 'finish_reason': 'stop', 'token_ids': [2]}],
            'usage': {'prompt_tokens': 1, 'completion_tokens': 1}})
    async def go():
        from driver import wire_hook
        async with httpx.AsyncClient(transport=httpx.MockTransport(provider),
                event_hooks={'request': [wire_hook(spec, tmp_path)]}) as client:
            return await s.collect_calls(client, 'http://fake/v1', spec, tmp_path)
    records, reason = asyncio.run(go())
    assert reason is None and len(records) == len(list((tmp_path / 'calls').glob('*.json'))) == 12
    assert all(r['score']['strict_correct'] == 64 and not r['capture']['tools_executed'] for r in records)
    assert len(list((tmp_path / 'wire').glob('*.json'))) == 12
    for path in (tmp_path / 'wire').glob('*.json'):
        wire = s.read(path)
        assert wire['body_utf8'] == s.serialize(requests[wire['coordinate_id']])
    result = s.summarize(d, records)
    assert len(result['cells']) == 12 and len(result['paired_context_effects']) == 12
    assert len(result['overlap_interactions']) == 2
    assert all(c['class_count_l1'] == 0 for c in result['coordinates'])


def test_owned_deadline_and_finally_release_on_startup_failure(tmp_path, monkeypatch):
    module()
    assert (Path(__file__).parent / 'owned.py').exists(), 'factorial owned wrapper missing'
    o = importlib.import_module('owned')
    assert o.work_deadline(1000) == 3280
    assert o.collection_command_cap(1000, 1001) == 1830
    with pytest.raises(TimeoutError):
        o.collection_command_cap(1000, 3280)
    monkeypatch.setattr(o, 'ROOT', tmp_path)
    (tmp_path / 'WEIGHTS.json').write_text('{}')
    events = []
    def fail(*args):
        raise RuntimeError('fixture startup failure')
    suite = SimpleNamespace(start_service=fail, release_service=lambda *args: events.append('release'))
    weights = {'models': {'old_sft': {'path': '/frozen/old', 'model_sha256': 'sha', 'config_sha256': 'config'}}}
    with pytest.raises(RuntimeError, match='fixture startup failure'):
        o.execute(tmp_path / 'owned', suite, weights, 1000)
    assert events == ['release']
