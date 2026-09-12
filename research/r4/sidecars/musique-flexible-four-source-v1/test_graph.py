import importlib.util
import json
from pathlib import Path
import time
import pytest

ROOT = Path(__file__).resolve().parent


def modules():
    assert (ROOT / 'study.py').exists(), 'flexible-four implementation absent'
    spec = importlib.util.spec_from_file_location('flex_fixture_study', ROOT / 'study.py')
    s = importlib.util.module_from_spec(spec); spec.loader.exec_module(s)
    with s.aliases({'study': s}, ROOT):
        c = s.load('flex_fixture_collect', ROOT / 'collect.py')
        m = s.load('flex_fixture_metrics', ROOT / 'metrics.py')
        with s.aliases({'collect': c, 'metrics': m}, ROOT): o = s.load('flex_fixture_owner', ROOT / 'owner.py')
    return s, c, m, o


def test_ranked_ids_require_exactly_four_unique_original_integers():
    s, _, _, _ = modules(); half = [{'idx': i, 'title': str(i), 'paragraph_text': 'Exact  source\n'} for i in range(5)]
    good = s.selection({'transport_valid': True, 'text': '{"paragraph_ids":[3,1,0,2]}'}, half)
    assert good['valid'] and good['paragraphs'] == [half[i] for i in (3,1,0,2)]
    for text in ('{"paragraph_ids":[1,2]}', '{"paragraph_ids":[0,1,2,99]}',
                 '{"paragraph_ids":[0,1,1,2]}', '{"paragraph_ids":[false,1,2,3]}',
                 '{"paragraph_ids":[0,1,2,3],"paragraph_ids":[1,2,3,4]}'):
        bad = s.selection({'transport_valid': True, 'text': text}, half)
        assert not bad['valid'] and bad['model_error'] and bad['paragraphs'] == []


@pytest.mark.parametrize('failure', ['none', 'shared_selector', 'planner'])
def test_current_owner_collector_entrypoint_uses_exact_five_call_graph(tmp_path, monkeypatch, failure):
    s, c, m, o = modules()
    from transformers import AutoTokenizer
    tok = AutoTokenizer.from_pretrained(s.MODEL, local_files_only=True)
    item = s.selected()[0]; public = s.read(item['public_path']); halves = s.partition(public, item['record_id'])
    ranked = [[p['idx'] for p in h[:4]][::-1] for h in halves]
    monkeypatch.setattr(s, 'selected', lambda: [item])
    seen = []
    class Wire:
        status = 200
        def __init__(self, raw): self.raw = raw
        def __enter__(self): return self
        def __exit__(self, *args): pass
        def read(self): return self.raw
    def native(request, timeout):
        body = json.loads(request.data); seen.append(body); offset = body['sampling_params']['seed'] - 202609230000
        if offset in (0, 1): text = json.dumps({'paragraph_ids': [999]*4 if failure == 'shared_selector' and offset == 0 else ranked[offset]})
        elif offset == 2: text = json.dumps({'paragraph_ids': [] if failure == 'shared_selector' else [999]*4 if failure == 'planner' else ranked[0]})
        else: text = '{"answer":"fixture answer","support_idxs":[]}'
        ids = tok.encode(text, add_special_tokens=False) + [151645]
        return Wire(json.dumps({'model': s.MODEL_ALIAS, 'request_id': 'CPU-'+str(len(seen)),
                    'choices': [{'token_ids': ids, 'finish_reason': 'stop'}],
                    'usage': {'prompt_tokens': len(body['token_ids']), 'completion_tokens': len(ids)}}).encode())
    monkeypatch.setattr(c.source, 'urlopen', native)
    monkeypatch.setenv('STRICT_RLM_CALIBRATION_API_KEY', 'SYNTHETIC-NOT-A-SERVICE-KEY')
    current = o.implementation()
    assert current.study is s and current.collect is c and current.metrics is m
    assert current.study.ATTEMPT == ROOT / 'outputs/attempt-001'
    old_read = s.read
    def blind(path):
        assert 'GOLD' not in str(path)
        return old_read(path)
    with monkeypatch.context() as scope:
        scope.setattr(s, 'read', blind)
        result = current.collect.execute('http://fixture.invalid', tmp_path, time.time()+90)
    assert result['physical_started'] == len(seen) == 5 and result['errors'] == []
    assert seen[-1]['sampling_params']['seed'] == seen[-2]['sampling_params']['seed'] == 202609230003
    prompts = {r['role']: s.read(tmp_path / 'prompts' / (r['call_id']+'.json')) for r in s.schedule()}
    payloads = {r: json.loads(p[1]['content'].rsplit('\n\n', 1)[0]) for r, p in prompts.items()}
    if failure == 'shared_selector':
        assert payloads['plan']['candidates'] == []
        assert payloads['fixed']['evidence'] == payloads['flexible']['evidence'] == []
        assert payloads['fixed']['selection_error'] == payloads['flexible']['selection_error']
    else:
        original = {p['idx']: p for h in halves for p in h}
        assert [v['paragraph'] for v in payloads['plan']['candidates']] == [original[i] for ids in ranked for i in ids]
        fixed = sorted(ranked[0][:2]+ranked[1][:2])
        assert payloads['fixed']['evidence'] == [original[i] for i in fixed]
        if failure == 'planner':
            assert payloads['flexible']['evidence'] == [] and payloads['flexible']['selection_error']
        else:
            assert payloads['flexible']['evidence'] == [original[i] for i in sorted(ranked[0])]
            assert len(payloads['fixed']['evidence']) == len(payloads['flexible']['evidence']) == 4
    assert prompts['fixed'][0] == prompts['flexible'][0]
    assert prompts['fixed'][1]['content'].endswith(s.FINAL) and prompts['flexible'][1]['content'].endswith(s.FINAL)
    scored = current.metrics.summarize(tmp_path, False)
    assert scored['physical_cost']['physical_started'] == 5
    assert scored['arms']['fixed']['natural_policy_cost']['physical_started'] == 3
    assert scored['arms']['flexible']['natural_policy_cost']['physical_started'] == 4
    assert scored['arms']['fixed']['available'] == scored['arms']['flexible']['available'] == 1
    suite = s.base_owner().study.dependencies(); current.lifecycle.install(suite)
    assert suite.SERVE == s.SERVICE_ROOT / 'service_wrapper_v2.py'
    assert suite.life.REPORT_ENGINE_ENTRY == s.SERVICE_ROOT / 'engine_entry_v2.py'
