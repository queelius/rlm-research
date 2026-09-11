"""CPU boundary regressions; generated root programs are never run here."""
import importlib.util
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent


def module(name):
    path = ROOT / (name + '.py')
    assert path.exists(), f'{name} implementation missing'
    spec = importlib.util.spec_from_file_location(name, path)
    value = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(value)
    return value


def test_reducer_counts_values_and_rejects_duplicate_or_missing_ids():
    count = module('count_labels').count_labels
    labels = {'a': 'numeric value', 'b': 'human being', 'c': 'numeric value'}
    assert count(labels, ['a', 'b'], 'numeric value') == 1
    assert count(labels, [], 'human being') == 0
    for ids in (['a', 'a'], ['absent']):
        with pytest.raises(ValueError):
            count(labels, ids, 'numeric value')
    with pytest.raises(ValueError):
        count({'a': 'NUM'}, ['a'], 'numeric value')


def test_native_final_availability_distinguishes_failed_tool_from_empty_final():
    score = module('metrics').score
    assert score({'ok': False, 'stop_condition': 'error', 'root_reply': ''}, True, 2)['reward'] is None
    assert score({'ok': True, 'is_completed': True, 'root_reply': ''}, True, 2)['reward'] == 0
    assert score({'ok': True, 'is_completed': True, 'root_reply': 'Answer: 2'}, True, 2)['reward'] == 1
    assert score({'ok': True, 'is_completed': False, 'root_reply': 'Answer: 2'}, True, 2)['reward'] is None
    assert score({'ok': True, 'is_completed': True, 'root_reply': 'Answer: 2.0'}, True, 2)['reward'] == 0


def test_map_validation_never_repairs_labels_or_missing_records():
    validate = module('metrics').validate_map
    assert validate('{"a":"human being"}', ['a']) == {'a': 'human being'}
    for text in ('{"a":"HUM"}', '{}', '{"a":"human being","b":"entity"}', '{"a":"entity","a":"human being"}'):
        with pytest.raises(ValueError):
            validate(text, ['a'])


def test_evidence_separates_scalar_agreement_from_executed_reduction():
    evidence = module('metrics').evidence
    trace = {'root_reply': 'Answer: 1', 'nodes': [
        {'message': {'role': 'assistant', 'tool_calls': [{'function': {'name': 'ipython', 'arguments': '{"code":"print(1)"}'}}]}},
        {'message': {'role': 'tool', 'content': '1'}}]}
    out = evidence(trace, {'a': 'human being', 'b': 'numeric value'}, ['a'], 'human being')
    assert out['supplied_map_count'] == 1
    assert out['final_map_consistent'] is True
    assert out['matching_integer_tool_observation'] is True
    assert out['actual_map_consistent_reduction'] is None


def test_plan_pairs_all_four_treatments_without_label_based_selection():
    plan = module('protocol').plan_for
    contexts = [{'id': 'x', 'stratum': 'new_root_train', 'helper_partition': 'train'}]
    rows = plan(contexts)
    assert len(rows) == 8
    for family in ('single_user', 'union'):
        block = [r for r in rows if r['family'] == family]
        assert len({r['seed'] for r in block}) == 1
        assert {(r['map_source'], r['reducer']) for r in block} == {
            ('native_c32', False), ('native_c32', True), ('dataset_oracle', False), ('dataset_oracle', True)}


def test_native_flat_tool_calls_preserve_code_and_dictionary_iteration_risk():
    evidence = module('metrics').evidence
    trace = {'root_reply': 'Answer: 0', 'nodes': [{'index': 3, 'message': {
        'role': 'assistant', 'tool_calls': [{'type': 'function', 'name': 'ipython',
        'arguments': '{"code":"labels = dict(zip(ids, labels))\\nprint(0)"}'}]}}]}
    result = evidence(trace, {'a': 'human being'}, ['a'], 'human being')
    assert result['programs'][0]['valid_python'] is True
    assert result['programs'][0]['bare_variable_zip_value_risk'] is True
    assert result['actual_map_consistent_reduction'] is None


def test_usage_audit_does_not_coerce_missing_cached_tokens_to_zero():
    usage = module('metrics').usage
    records = [{'depth': 0, 'response': {'usage': {'prompt_tokens': 10, 'completion_tokens': 3, 'cached_input_tokens': None}}},
               {'depth': 1, 'response': {'usage': {'prompt_tokens': 20, 'completion_tokens': 4, 'cached_input_tokens': 8}}}]
    result = usage(records)
    assert result['prompt_tokens']['sum_known'] == 30
    assert result['cached_input_tokens']['known_calls'] == 1
    assert result['cached_input_tokens']['sum_all'] is None
    assert result['child_requests'] == 1
