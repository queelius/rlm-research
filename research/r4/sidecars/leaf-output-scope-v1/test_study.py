"""Focused invariants; existing data and the real collector, fake network only."""
import asyncio
import importlib.util
import json
from collections import Counter
from copy import deepcopy
from pathlib import Path

import httpx
import pytest

ROOT = Path(__file__).resolve().parent


def module():
    assert (ROOT / 'study.py').exists(), 'output-scope implementation absent'
    spec = importlib.util.spec_from_file_location('output_scope_test', ROOT / 'study.py')
    result = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(result)
    return result


def test_exact_frozen_contexts_are_partitioned_once_per_arm_seed():
    d = module()
    design = d.design()
    assert Counter(row['arm'] for row in design['plan']) == {'all64': 8, 'full16': 32, 'local16': 32}
    assert len({row['id'] for row in design['plan']}) == 72
    original = json.loads(d.SOURCE.read_text())['design']['contexts']
    assert design['contexts'] == original
    records = [record for context in design['contexts'] for record in context['records']]
    assert [r['record_index'] for r in records] == list(range(1, 257))
    assert len({r['question_group_sha256'] for r in records}) == 256
    for arm in ('all64', 'full16', 'local16'):
        for seed in (981261601, 981261602):
            selected = [row for row in design['plan'] if row['arm'] == arm and row['seed'] == seed]
            for context_index in range(4):
                positions = [p for row in selected if row['context_index'] == context_index for p in row['target_positions']]
                assert sorted(positions) == list(range(64))


def test_only_target_ids_or_visible_non_targets_differ_between_paired_payloads():
    d = module()
    design = d.design()
    rows = [row for row in design['plan'] if row['context_index'] == 0 and row['seed'] == 981261601]
    full = d.make_request(design, next(row for row in rows if row['arm'] == 'all64'))
    complete_records = full['messages'][1]['content'].split(d.INPUT_MARKER)[1]
    for offset in (0, 16, 32, 48):
        a = d.make_request(design, next(row for row in rows if row['arm'] == 'full16' and row['offset'] == offset))
        b = d.make_request(design, next(row for row in rows if row['arm'] == 'local16' and row['offset'] == offset))
        prefix_a, records_a = a['messages'][1]['content'].split(d.INPUT_MARKER)
        prefix_b, records_b = b['messages'][1]['content'].split(d.INPUT_MARKER)
        assert records_a == complete_records and prefix_a == prefix_b
        assert json.loads(records_b) == json.loads(complete_records)[offset:offset + 16]
        wanted = [f'q{i:04d}' for i in range(offset + 1, offset + 17)]
        assert json.loads(prefix_a.split(d.TARGET_MARKER)[1]) == wanted
        assert a['structured_outputs'] == b['structured_outputs']
        for body in (a, b, full):
            assert body['messages'][0] == design['contract']['system_message']
            assert body['tools'] == design['contract']['tools']
            assert body['max_tokens'] == 1024 and body['temperature'] == .5
            assert body['return_token_ids'] is True and 'logprobs' not in body
            assert design['definitions'] in body['messages'][1]['content']
            assert body['structured_outputs']['json']['items']['enum'] == design['labels']
            n = 64 if body == full else 16
            assert body['structured_outputs']['json']['minItems'] == n
            assert body['structured_outputs']['json']['maxItems'] == n


def test_gold_changes_do_not_affect_requests_and_json_freeze_keeps_physical_order():
    d = module()
    design = d.design()
    altered = deepcopy(design)
    for cx in altered['contexts']:
        for record in cx['records']:
            record['gold_label'] = 'HOST_GOLD_SENTINEL'
            record['coarse'] = 'HOST_GOLD_SENTINEL'
    for batch in altered['batches']:
        for record in batch['gold']['records']:
            record['gold_label'] = 'HOST_GOLD_SENTINEL'
    frozen = json.loads(json.dumps(design, sort_keys=True))
    for row in design['plan']:
        a, b, c = (d.make_request(value, row) for value in (design, altered, frozen))
        assert a == b == c
        assert json.dumps(a['tools']) == json.dumps(c['tools'])
        assert 'HOST_GOLD_SENTINEL' not in json.dumps(b) and 'gold_label' not in json.dumps(b)


def test_alignment_uses_declared_original_positions_not_output_position():
    d = module()
    design = d.design()
    row = next(r for r in design['plan'] if r['arm'] == 'local16' and r['offset'] == 48)
    batch = design['batches'][row['batch_id']]
    gold = [r['gold_label'] for r in batch['gold']['records']]
    score = d.corr.score_response(json.dumps(gold), batch['gold'])
    record = {'coordinate': row, 'score': score, 'started': 1, 'ended': 2,
              'model_called': True, 'request': d.make_request(design, row), 'usage': {}}
    result = d.score_coordinate(design, row, [record])
    assert result['schema_valid'] and result['aligned_records'] == 16
    assert [r['source_position'] for r in result['record_results']] == list(range(49, 65))
    assert [r['output_position'] for r in result['record_results']] == list(range(1, 17))
    assert all(r['quartile'] == 3 and r['canonical_correct'] for r in result['record_results'])
    record['score'] = d.corr.score_response(json.dumps(gold[:-1]), batch['gold'])
    result = d.score_coordinate(design, row, [record])
    assert not result['schema_valid'] and result['aligned_records'] == 0
    assert all(r['prediction'] is None for r in result['record_results'])


def test_full16_cost_keeps_four_full_prefixes_and_reassembles_original_quartiles():
    d = module()
    value = d.design()
    calls = []
    rows = [r for r in value['plan'] if r['arm'] == 'full16' and r['context_index'] == 0 and r['repeat'] == 0]
    for row in rows:
        scoring = value['batches'][row['batch_id']]['gold']
        score = d.corr.score_response(json.dumps([r['gold_label'] for r in scoring['records']]), scoring)
        calls.append({'coordinate': row, 'score': score, 'started': 1, 'ended': 2,
            'model_called': True, 'request': d.make_request(value, row),
            'usage': {'logical_input_tokens': 100, 'cached_input_tokens': 20,
                      'uncached_input_tokens': 80, 'completion_tokens': 10}})
    result = d.summarize(value, calls)
    cell = next(r for r in result['arms'] if r['arm'] == 'full16')
    assert cell['usage']['logical_input_tokens'] == 400
    assert cell['usage']['completion_tokens'] == 40
    assert cell['aligned_assignments'] == cell['canonical_correct'] == 64
    assert [r['aligned'] for r in cell['original_position_quartiles']] == [16, 16, 16, 16]
    group = next(r for r in result['context_counts'] if r['arm'] == 'full16' and r['context_index'] == 0 and r['repeat'] == 0)
    assert group['aggregate_available']
    assert all(c['strict'] == 1 for c in group['counts'].values())
    assert result['paired_contrasts'][0]['common_aligned_assignments'] == 0


def test_correct_count_can_hide_two_semantic_errors():
    d = module()
    sources = [{'gold_label': 'human being'}, {'gold_label': 'numeric value'}]
    items = [{'gold_label': 'human being', 'prediction': 'numeric value'},
             {'gold_label': 'numeric value', 'prediction': 'human being'}]
    count = d.count_endpoint(items, True, True, sources)
    assert count['human being']['strict'] == 1
    assert count['human being']['false_positives'] == count['human being']['false_negatives'] == 1


def test_real_inherited_collector_preserves_request_and_physical_ids(tmp_path):
    d = module()
    from transformers import AutoTokenizer
    hf = AutoTokenizer.from_pretrained(str(d.corr.BASE), local_files_only=True, trust_remote_code=False)
    value = d.design()
    value['plan'] = value['plan'][:3]
    value['coordinates'] = value['coordinates'][:3]
    value['rendered_prompts'] = {}
    for row in value['plan']:
        body = d.make_request(value, row)
        ids = hf.apply_chat_template(body['messages'], tools=body['tools'], add_generation_prompt=True, tokenize=True, return_dict=False)
        value['rendered_prompts'][row['id']] = {'token_ids_sha256': d.digest(ids), 'tokens': len(ids)}
    spec = {'design': value, 'request_sha256': {r['id']: d.digest(d.make_request(value, r)) for r in value['plan']}}
    (tmp_path / 'calls').mkdir()
    (tmp_path / 'coordinates').mkdir()
    seen = []
    def reply(request):
        body = json.loads(request.content)
        seen.append(body)
        ids = hf.apply_chat_template(body['messages'], tools=body['tools'], add_generation_prompt=True, tokenize=True, return_dict=False)
        n = body['structured_outputs']['json']['minItems']
        return httpx.Response(200, json={'model': body['model'], 'prompt_token_ids': ids,
            'choices': [{'finish_reason': 'stop', 'message': {'content': json.dumps(['entity'] * n)}, 'token_ids': [11, 12]}],
            'usage': {'prompt_tokens': len(ids), 'completion_tokens': 2,
                      'prompt_tokens_details': {'cached_tokens': 0}}})
    async def execute():
        async with httpx.AsyncClient(transport=httpx.MockTransport(reply)) as client:
            return await d.collect_calls(client, 'http://cpu-fixture/v1', spec, tmp_path)
    records, reason = asyncio.run(execute())
    assert reason is None and len(records) == len(seen) == 3
    assert [r['score']['records'] for r in records] == [64, 16, 16]
    assert all(r['score']['schema_valid'] and r['capture']['tools_executed'] is False for r in records)
    coords = [d.score_coordinate(value, row, records) for row in value['coordinates']]
    assert all(r['physical_prompt']['exact_cpu_template_match'] is True for r in coords)
    assert all(r['physical_prompt']['full_system_and_user_input_verified'] for r in coords)


def test_wrong_adapter_alias_is_null_but_observed_cost_is_not_lost(tmp_path):
    d = module()
    value = d.design()
    value['plan'] = value['plan'][:1]
    value['coordinates'] = value['coordinates'][:1]
    spec = {'design': value, 'request_sha256': {r['id']: d.digest(d.make_request(value, r)) for r in value['plan']}}
    (tmp_path / 'calls').mkdir()
    (tmp_path / 'coordinates').mkdir()
    def reply(request):
        return httpx.Response(200, json={'model': 'wrong', 'choices': [],
            'usage': {'prompt_tokens': 99, 'completion_tokens': 11, 'prompt_tokens_details': {'cached_tokens': 7}}})
    async def execute():
        async with httpx.AsyncClient(transport=httpx.MockTransport(reply)) as client:
            return await d.collect_calls(client, 'http://cpu-fixture/v1', spec, tmp_path)
    records, reason = asyncio.run(execute())
    assert reason == 'request_error' and len(records) == 1
    row = d.score_coordinate(value, value['plan'][0], records)
    assert row['model_completed'] is False and row['counts']['human being']['strict'] is None
    assert row['usage']['logical_input_tokens'] == 99 and row['usage']['uncached_input_tokens'] == 92
    assert row['usage']['completion_tokens'] == 11


def test_binding_changes_only_explicit_model_alias_and_rejects_new_weights():
    assert (ROOT / 'driver.py').exists(), 'scope binding implementation absent'
    spec = importlib.util.spec_from_file_location('scope_binding_test', ROOT / 'driver.py')
    runner = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(runner)
    d = runner.study
    design = d.design()
    unbound = {'design': design, 'requests': {r['id']: d.make_request(design, r) for r in design['plan']}}
    endpoint = d.read(d.corr.HISTORICAL_SELECTED)
    endpoint['model_alias'] = 'explicit-old-weight-test-alias'
    bound = runner.bind_identity(unbound, endpoint)
    for key, body in bound['requests'].items():
        assert body['model'] == 'explicit-old-weight-test-alias'
        assert {**body, 'model': d.corr.PLACEHOLDER} == unbound['requests'][key]
    bad = deepcopy(endpoint)
    bad['adapter']['model_sha256'] = 'new-training-checkpoint'
    with pytest.raises(ValueError, match='old selected'):
        runner.bind_identity(unbound, bad)
