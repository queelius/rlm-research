import importlib.util
import json
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent


def load():
    assert (ROOT / 'driver.py').exists(), 'sentiment preparation/scorer implementation absent'
    spec = importlib.util.spec_from_file_location('sentiment_test_driver', ROOT / 'driver.py')
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_group_selection_is_label_blind_and_retains_duplicate_indexes():
    m = load()
    rows = [{'idx': 7, 'sentence': ' A  GREAT movie ', 'label': 1},
            {'idx': 9, 'sentence': 'a great MOVIE', 'label': 0},
            {'idx': 11, 'sentence': 'bad', 'label': 0}]
    selected, report = m.select_groups(rows, 2)
    flipped, _ = m.select_groups([{**r, 'label': 1-r['label']} for r in rows], 2)
    assert [r['group_id'] for r in selected] == [r['group_id'] for r in flipped]
    assert [r['group_id'] for r in selected] == sorted(r['group_id'] for r in selected)
    duplicate = next(r for r in selected if r['source_indexes'] == [7, 9])
    assert duplicate['sentence'] == ' A  GREAT movie '
    assert duplicate['source_row_indexes'] == [0, 1]
    assert report['duplicate_rows'] == 1 and report['conflicting_label_groups'] == 1


def test_primary_scorer_never_repairs_or_accepts_trec_labels():
    m = load()
    assert m.score_labels('["negative", "positive"]', ['negative', 'positive'])['strict_correct'] == 2
    for content in ['["Negative","positive"]', '["entity","positive"]',
                    '["negative"]', '```json\n["negative","positive"]\n```']:
        assert not m.score_labels(content, ['negative', 'positive'])['schema_valid']
    score = m.score_labels('["entity","positive"]', ['negative', 'positive'])
    assert score['trec_label_leakage'] == 1 and score['strict_correct'] == 1
    assert m.score_labels('["negative"]', ['negative', 'positive'])['strict_correct'] == 0


def test_requests_use_sentiment_only_and_schema_exact_cardinality():
    m = load()
    records = [{'sentence': f'review{i}', 'gold': 'positive', 'group_id': str(i)} for i in range(256)]
    d = m.layout(records)
    assert len(d['plan']) == 120 and len(d['coordinates']) == 24
    assert sorted({len(b['questions']) for b in d['batches']}) == [4, 5, 64]
    row = next(r for r in d['plan'] if r['cell'] == 'schema64')
    req = m.make_request(d, row)
    assert req['structured_outputs']['json'] == {'type': 'array', 'items': {'type': 'string', 'enum': ['negative', 'positive']}, 'minItems': 64, 'maxItems': 64}
    assert 'human being' not in json.dumps(req)
    assert 'sentiment' in req['messages'][1]['content']
    assert 'structured_outputs' not in m.make_request(d, d['plan'][0])


def test_provenance_hash_rejects_changed_input(tmp_path):
    m = load()
    path = tmp_path / 'input.json'
    path.write_text('{}')
    hashes = {str(path): m.file_hash(path)}
    m.verify_hashes(hashes)
    path.write_text('{"changed":true}')
    with pytest.raises(ValueError, match='changed'):
        m.verify_hashes(hashes)


def test_reused_collector_retains_wire_schema_alias_ids_and_strict_failures(tmp_path):
    import asyncio
    import httpx
    m = load()
    records = [{'sentence': f'review{i}', 'gold': 'positive', 'group_id': str(i)} for i in range(256)]
    d = m.layout(records)
    d['model_alias'] = 'bound-sentiment-test'
    # Restrict fake collection to one complete 64 natural/schema coordinate each.
    d['coordinates'] = [c for c in d['coordinates'] if c['context_id'].endswith('00') and c['seed'] == 739019 and c['cell'] != 'natural5']
    keep = {c['id'] for c in d['coordinates']}
    d['plan'] = [r for r in d['plan'] if r['coordinate_id'] in keep]
    spec = {'design': d, 'request_sha256': {r['id']: m.digest(m.make_request(d, r)) for r in d['plan']}}
    bodies = [m.make_request(d, r) for r in d['plan']]
    assert {k: v for k, v in bodies[1].items() if k != 'structured_outputs'} == bodies[0]
    def handler(request):
        body = json.loads(request.content)
        content = json.dumps(['positive']*64) if 'structured_outputs' in body else '["entity"]'
        return httpx.Response(200, json={'model': 'bound-sentiment-test', 'prompt_token_ids': [101, 202],
            'choices': [{'message': {'content': content}, 'finish_reason': 'stop', 'token_ids': [303]}],
            'usage': {'prompt_tokens': 2, 'completion_tokens': 1}})
    for directory in ['calls', 'coordinates']:
        (tmp_path/directory).mkdir()
    m.fixed.make_request = m.make_request
    m.fixed.score_coordinate = m.score_coordinate
    m.fixed.leaf.score_labels = m.score_labels
    async def go():
        async with httpx.AsyncClient(transport=httpx.MockTransport(handler)) as client:
            return await m.fixed.collect_calls(client, 'http://fake/v1', spec, tmp_path)
    calls, reason = asyncio.run(go())
    assert reason is None and len(calls) == 2
    assert all(c['capture']['prompt_token_ids'] for c in calls)
    assert {m.score_coordinate(d, c, calls)['strict_reward'] for c in d['coordinates']} == {0, 1}
    assert len(list((tmp_path/'calls').glob('*.json'))) == 2


def test_template_budget_extracts_actual_ids_from_new_tokenizer_mapping():
    from collections import UserDict
    m = load()
    assert hasattr(m, 'template_ids'), 'explicit template token extraction absent'
    class Tokenizer:
        def apply_chat_template(self, *args, **kwargs):
            return UserDict({'input_ids': [101, 202, 303], 'attention_mask': [1, 1, 1]})
    assert m.template_ids(Tokenizer(), {'messages': [], 'tools': []}) == [101, 202, 303]
