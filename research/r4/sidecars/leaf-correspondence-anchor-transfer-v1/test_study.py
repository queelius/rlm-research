import importlib
import json
from collections import Counter
from copy import deepcopy
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent


def module():
    assert (ROOT / 'study.py').exists(), 'correspondence-anchor implementation absent'
    return importlib.import_module('study')


def test_exact600_asymmetric_allocation_and_source_group_exclusion():
    d = module()
    data = d.load_data()
    value = d.build_design(data)
    assert len(value['plan']) == 600
    assert Counter(r['size'] for r in value['plan']) == {5: 520, 64: 80}
    assert all(r['permutation'] == 0 for r in value['plan'] if r['size'] == 5)
    assert len({r['id'] for c in value['contexts'] for r in c['records']}) == 640
    assert data['sst_provenance']['new_old_group_intersection'] == 0
    assert data['sst_provenance']['new_groups'] == 256
    for co in value['coordinates']:
        calls = [r for r in value['plan'] if r['coordinate_id'] == co['id']]
        ids = [r['id'] for call in calls for r in value['batches'][call['batch_id']]['gold']['records']]
        assert len(ids) == len(set(ids)) == 64
    for context in value['contexts']:
        assert context['permutations'][0] != context['permutations'][1]
        assert sorted(context['permutations'][0]) == sorted(context['permutations'][1]) == list(range(64))


def test_payload_has_no_gold_and_common_inputs_and_preserves_property_order():
    d = module()
    value = d.build_design(d.load_data())
    row = next(r for r in value['plan'] if r['arm'] == 'indexed')
    index = d.make_request(value, row)
    plain = d.make_request(value, {**row, 'arm': 'anonymous'})
    assert index['messages'][0] == plain['messages'][0]
    assert index['tools'] == plain['tools']
    assert index['messages'][1]['content'].split(d.INPUT_MARKER)[1] == plain['messages'][1]['content'].split(d.INPUT_MARKER)[1]
    targets = value['batches'][row['batch_id']]['gold']['records']
    assert list(index['structured_outputs']['json']['properties']) == [r['id'] for r in targets]
    frozen = json.loads(d.serialize(index))
    assert list(frozen['structured_outputs']['json']['properties']) == [r['id'] for r in targets]
    altered = deepcopy(value)
    for batch in altered['batches']:
        for record in batch['gold']['records']:
            record['gold_label'] = 'HOST_GOLD_SENTINEL'
    assert d.make_request(altered, row) == index
    assert 'HOST_GOLD_SENTINEL' not in d.serialize(index) and 'gold_label' not in d.serialize(index)
    assert index['max_tokens'] == plain['max_tokens'] == 3072


def test_parser_rejects_duplicate_ids_missing_ids_wrong_cardinality_without_repair():
    d = module()
    records = [{'id': 'q0002', 'gold_label': 'negative'}, {'id': 'q0001', 'gold_label': 'positive'}]
    gold = {'records': records, 'order': [0, 1], 'arm': 'indexed', 'labels': ['negative', 'positive']}
    valid = d.score_labels('{"q0001":"positive","q0002":"negative"}', gold)
    assert valid['schema_valid'] and valid['strict_correct'] == 2
    assert valid['output_positions'] == [2, 1]
    for text in ['{"q0001":"positive"}', '{"q0001":"positive","q0001":"negative","q0002":"negative"}', '{"q0001":"positive","q0002":"entity"}']:
        assert not d.score_labels(text, gold)['schema_valid']
    assert not d.score_labels('["negative"]', {**gold, 'arm': 'anonymous'})['schema_valid']


def test_typed_rendering_does_not_mutate_request_and_matches_provider_tool_order():
    assert (ROOT / 'driver.py').exists(), 'driver qualification absent'
    driver = importlib.import_module('driver')
    from transformers import AutoTokenizer
    d = module()
    value = d.build_design(d.load_data())
    body = d.make_request(value, value['plan'][0])
    before = d.serialize(body)
    hf = AutoTokenizer.from_pretrained(str(d.corr.BASE), local_files_only=True, trust_remote_code=False)
    ids = driver.typed_prompt_ids(hf, body)
    rendered = hf.decode(ids, skip_special_tokens=False)
    tools = json.loads(rendered.split('<tools>\n')[1].split('\n</tools>')[0])
    assert list(tools) == ['type', 'function']
    assert list(tools['function']) == ['name', 'description', 'parameters']
    assert all(m['content'] in rendered for m in body['messages'])
    assert d.serialize(body) == before and 'tool_choice' not in body


def test_real_collector_fake_http_preserves_wire_order_and_scores_no_tool_execution(tmp_path):
    assert (ROOT / 'driver.py').exists(), 'driver wire capture absent'
    import asyncio
    import httpx
    driver = importlib.import_module('driver')
    d = module()
    value = d.build_design(d.load_data())
    chosen = value['coordinates'][:2]
    ids = {r['id'] for r in chosen}
    value['coordinates'] = chosen
    value['plan'] = [r for r in value['plan'] if r['coordinate_id'] in ids]
    bodies = {r['id']: d.make_request(value, r) for r in value['plan']}
    spec = {'design': value, 'requests': bodies, 'request_sha256': {k: d.digest(v) for k, v in bodies.items()}}

    async def provider(request):
        body = json.loads(request.content)
        rid = next(k for k, v in bodies.items() if v == body)
        row = next(r for r in value['plan'] if r['id'] == rid)
        gold = value['batches'][row['batch_id']]['gold']
        result = [r['gold_label'] for r in gold['records']] if row['arm'] == 'anonymous' else {r['id']: r['gold_label'] for r in gold['records']}
        return httpx.Response(200, json={'id': rid, 'model': body['model'], 'prompt_token_ids': [1],
            'choices': [{'message': {'content': json.dumps(result)}, 'finish_reason': 'stop', 'token_ids': [2]}],
            'usage': {'prompt_tokens': 1, 'completion_tokens': 1}})

    async def go():
        async with httpx.AsyncClient(transport=httpx.MockTransport(provider),
                event_hooks={'request': [driver.wire_hook(spec, tmp_path)]}) as client:
            return await d.collect_calls(client, 'http://fake/v1', spec, tmp_path)
    records, reason = asyncio.run(go())
    assert reason is None and len(records) == 2
    assert all(r['score']['schema_valid'] and r['score']['strict_correct'] == 64 for r in records)
    assert len(list((tmp_path / 'calls').glob('*.json'))) == 2
    assert len(list((tmp_path / 'wire').glob('*.json'))) == 2
    for row in records:
        wire = d.read(tmp_path / 'wire' / (row['coordinate']['id'] + '.json'))
        assert wire['body_utf8'] == d.serialize(row['request'])
        assert not row['capture']['tools_executed']
