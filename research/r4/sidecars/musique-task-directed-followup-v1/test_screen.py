import copy
import importlib.util
import json
from pathlib import Path


def module():
    path = Path(__file__).with_name('study.py')
    assert path.exists(), 'screen implementation absent'
    spec = importlib.util.spec_from_file_location('followup_study_fixture', path)
    m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m); return m


def test_shared_report_planning_prefix_and_labelblind_complete_partition():
    s = module()
    row = {'id': 'private-shape-id', 'question': 'Which river?', 'answer': 'HOST_ONLY_SECRET',
        'question_decomposition': [{'answer': 'SECRET_STEP'}],
        'paragraphs': [{'idx': i, 'title': str(i), 'paragraph_text': 'public facts ' + str(i), 'is_supporting': i == 1} for i in range(5)]}
    public = s.public_row(row)
    assert set(public) == {'question', 'paragraphs'}
    assert 'HOST_ONLY_SECRET' not in json.dumps(public) and 'is_supporting' not in json.dumps(public)
    halves = s.partition(public, 'opaque-fixture')
    assert sorted(p['idx'] for half in halves for p in half) == list(range(5))
    assert sorted(map(len, halves)) == [2, 3]
    report = ['ordinary left report', 'ordinary right report']; plan = '{"left":"a bridge?","right":"the river?"}'
    prefix = s.shared_parent(public, report, plan)
    stop = s.final_messages(public, report, plan, None)
    broad = s.final_messages(public, report, plan, ['additional left', 'additional right'])
    targeted = s.final_messages(public, report, plan, ['focused left', 'focused right'])
    assert stop[:-1] == broad[:-1] == targeted[:-1] == prefix
    assert s.roles() == ['report_left', 'report_right', 'plan', 'stop', 'broad_left', 'broad_right', 'broad', 'targeted_left', 'targeted_right', 'targeted', 'full_source']
    assert sum(s.output_cap(role) for role in s.roles()) == 7424
    assert 12 * len(s.roles()) == 132


def test_native_schema_final_score_and_known_budget_vs_unknown(tmp_path, monkeypatch):
    s = module()
    from transformers import AutoTokenizer
    tok = AutoTokenizer.from_pretrained(s.MODEL, local_files_only=True)
    request = s.request([{'role': 'user', 'content': 'Protocol fixture'}], 'stop', 17, 4, tok)
    text = '{"answer":"The Nile","support_idxs":[1,3]}'
    ids = tok.encode(text, add_special_tokens=False) + [151645]
    response = {'model': s.MODEL_ALIAS, 'request_id': 'fixture', 'choices': [{'token_ids': ids, 'finish_reason': 'stop'}],
        'usage': {'prompt_tokens': len(request['token_ids']), 'completion_tokens': len(ids)}}
    value = s.decode(request, response, tok)
    assert value['transport_valid'] and value['text'] == text
    score = s.score_final(value, {'answer': 'Nile', 'answer_aliases': [], 'support_idxs': [1,2]}, 4)
    assert score['available'] and score['answer_em'] == 1 and score['support_f1'] == .5
    bad = copy.deepcopy(response); bad['choices'][0]['finish_reason'] = 'unknown'
    assert not s.decode(request, bad, tok)['transport_valid']
    length = copy.deepcopy(response); length['choices'][0].update(token_ids=ids[:-3], finish_reason='length')
    length['usage']['completion_tokens'] = len(ids) - 3
    partial = s.decode(request, length, tok)
    score = s.score_final(partial, {'answer': 'Nile', 'answer_aliases': [], 'support_idxs': [1,2]}, 4)
    assert partial['transport_valid'] and score['available'] and score['answer_em'] == 0
    try:
        s.check_context([1] * 8192, 512)
    except ValueError:
        pass
    else:
        raise AssertionError('actual prefix plus requested output must be bounded')

    # Exercise one actual eleven-call graph and wire persistence with synthetic
    # responses. This is protocol/metrics evidence, never model evaluation data.
    with s.aliases({'study': s}, s.ROOT):
        collector = s.load('report_followup_fixture_collect', s.ROOT / 'collect.py')
        metrics = s.load('report_followup_fixture_metrics', s.ROOT / 'metrics.py')
        wrapper = s.load('report_followup_fixture_wrapper', s.ROOT / 'service_wrapper.py')
    class Wire:
        status = 200
        def __init__(self, raw): self.raw = raw
        def __enter__(self): return self
        def __exit__(self, *args): pass
        def read(self): return self.raw
    returned = []
    def native(request, timeout):
        body = json.loads(request.data)
        schema = body['sampling_params'].get('structured_outputs', {}).get('json', {})
        content = '{"left":"Which river?","right":"Where?"}' if list(schema.get('properties', {})) == ['left', 'right'] else text if schema else 'An ordinary report.'
        tokens = tok.encode(content, add_special_tokens=False) + [151645]
        returned.append(body)
        response = {'model': s.MODEL_ALIAS, 'request_id': 'SYNTHETIC-' + str(len(returned)),
            'choices': [{'token_ids': tokens, 'finish_reason': 'stop'}],
            'usage': {'prompt_tokens': len(body['token_ids']), 'completion_tokens': len(tokens),
                      'prompt_tokens_details': {'cached_tokens': 0}}}
        return Wire(json.dumps(response).encode())
    monkeypatch.setattr(collector, 'urlopen', native)
    monkeypatch.setenv('STRICT_RLM_CALIBRATION_API_KEY', 'SYNTHETIC-CPU-FIXTURE-NOT-A-SERVICE-KEY')
    s.official().metric_classes()
    import time
    c = collector.Collector('http://fixture.invalid', tmp_path / 'collector', time.time() + 60, tok)
    item = s.selected()[0]
    value = c.question(0, item)
    assert value['all_planned_roles_accounted'] and c.physical == len(returned) == 11
    summaries = metrics.summarize(tmp_path / 'collector', False)
    assert summaries['planned_physical_calls'] == 132 and summaries['planned_terminal_slots'] == 48
    assert summaries['physical_cost']['physical_started'] == 11
    assert all(a['available'] == 1 and a['unavailable'] == 11 and a['primary_accuracy'] is None for a in summaries['arms'].values())
    assert [summaries['arms'][a]['policy_cost']['physical_started'] for a in s.ARMS] == [4, 6, 6, 1]
    assert not summaries['promotion_screen_passed']
    assert metrics.costs([{'physical_started': True, 'usage': {}}], 1)['prompt_tokens_unknown_calls'] == 1

    # Run the prospective service config/environment seam with the actual base
    # builder, but do not execute main(), spawn a child, import GPU kernels or load weights.
    built = wrapper.build(tmp_path / 'service')
    runtime = built.study.base.runtime_study().service
    config = runtime.config(s.base_owner().study.binding()['checkpoint'], tmp_path / 'service', 'SYNTHETIC')
    assert config['vllm']['worker_extension_cls'] == 'report_worker.ReportWorker'
    assert config['vllm']['enforce_eager'] and not config['vllm']['enable_lora']
    env = built.adapt_environment({})
    assert env['REPORT_DISPATCH_RECEIPT'] == str(tmp_path / 'service/ACTUAL_DISPATCH.json')
    assert env['PYTHONPATH'].split(':')[0] == str(s.ROOT)

    # CPU sentinels exercise the exact instrumentation wrapper and refusal. A
    # CUDA-shaped fake is explicitly not a real dispatch or runtime qualification.
    from types import SimpleNamespace
    instrument = s.load('report_followup_fixture_instrument', s.ROOT / 'report_worker.py')
    source = tmp_path / 'fake-kernel.py'; source.write_text('# SYNTHETIC CPU fixture\n')
    calls = []
    def original(x): calls.append('original'); return x
    batch = SimpleNamespace(matmul_persistent=original, _batch_invariant_MODE=True, __file__=str(source))
    monkeypatch.setenv('VLLM_BATCH_INVARIANT', '1')
    fake = SimpleNamespace(device=SimpleNamespace(type='cuda'), dtype='SYNTHETIC', shape=(1, 2))
    receipt = tmp_path / 'SYNTHETIC_DISPATCH.json'
    instrument.install(batch, SimpleNamespace(VLLM_BATCH_INVARIANT=True), receipt)
    assert batch.matmul_persistent(fake) is fake and batch.matmul_persistent(fake) is fake
    assert calls == ['original', 'original'] and s.read(receipt)['original_function_returned']
    bad_batch = SimpleNamespace(matmul_persistent=original, _batch_invariant_MODE=False, __file__=str(source))
    instrument.install(bad_batch, SimpleNamespace(VLLM_BATCH_INVARIANT=True), tmp_path / 'REFUSED.json')
    try: bad_batch.matmul_persistent(fake)
    except RuntimeError: pass
    else: raise AssertionError('disabled worker mode must not attest')
    assert not (tmp_path / 'REFUSED.json').exists()
