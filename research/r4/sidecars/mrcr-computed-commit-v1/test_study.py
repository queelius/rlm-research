import pytest
import study


def test_byte_cap_uses_context_utf8_and_does_not_require_gold():
    assert hasattr(study, 'terminal_byte_cap'), 'public-only size policy absent'
    assert study.terminal_byte_cap(['abc', 'α' * 10]) == 1044


def test_prefix_and_restatement_are_counted_before_provider_dispatch():
    assert hasattr(study, 'CallBudget'), 'strict shared call accounting absent'
    budget = study.CallBudget()
    for _ in range(5):
        budget.reserve('prefix', 0)
    with pytest.raises(study.PrefixBudgetExceeded):
        budget.reserve('prefix', 1)
    budget.reserve('restatement', 0)
    with pytest.raises(ValueError):
        budget.reserve('restatement', 0)
    with pytest.raises(ValueError):
        study.CallBudget().reserve('restatement', 1)


def test_raw_official_score_does_not_hide_length_stopped_restatement():
    assert hasattr(study, 'score_pair'), 'paired score accounting absent'
    pair = {'candidate': 'abcTARGET', 'restatement': {'text': 'abcTARGET',
        'status': 'returned', 'valid_terminal': False, 'finish_reason': 'length'}}
    result = study.score_pair(pair, 'abcTARGET')
    assert result['commit']['raw_exact'] is True
    assert result['restatement']['raw_exact'] is True
    assert result['restatement']['strict_exact'] is False
    assert result['byte_fidelity'] is True


def test_missing_candidate_never_falls_back_to_native_terminal():
    assert hasattr(study, 'score_pair'), 'paired score accounting absent'
    result = study.score_pair(None, 'abcTARGET')
    assert result['status'] == 'non_submission'
    assert result['commit'] is None and result['restatement'] is None


def test_shared_cost_is_not_counted_twice_and_failed_usage_is_unknown():
    calls = [
        {'phase': 'prefix', 'status': 'returned', 'wire_request': {},
         'logical_input_tokens': 100, 'action_tokens': 20, 'started': 0, 'ended': 2},
        {'phase': 'restatement', 'status': 'returned', 'wire_request': {},
         'logical_input_tokens': 140, 'action_tokens': 12, 'started': 2, 'ended': 3}]
    result = study.cost_summary(calls)
    assert result['observed_shared_execution']['logical_prompt_tokens'] == 240
    assert result['commit_prefix_only']['logical_prompt_tokens'] == 100
    assert result['restatement_increment']['action_tokens'] == 12
    assert result['observed_shared_execution']['cached_prompt_tokens'] is None
    calls.append({'phase': 'prefix', 'status': 'error', 'wire_request': {}, 'started': 3, 'ended': 4})
    result = study.cost_summary(calls)
    assert result['usage_incomplete'] and result['physical_http_attempts'] == 3
    assert result['observed_shared_execution']['logical_prompt_tokens'] == 240


def test_system_contract_is_shared_and_does_not_rewrite_public_question_or_seed():
    original = study.read(study.ROOT / 'inputs/tasks.json')
    amended = study.system_contract_tasks(original)
    assert len(amended) == 6
    assert all(row['system_prompt'] == study.SYSTEM_CONTRACT for row in amended)
    assert 'overrides' in study.SYSTEM_CONTRACT and 'restatement' in study.SYSTEM_CONTRACT
    assert [{**row, 'system_prompt': None} for row in amended] == original
    assert all(row['system_prompt'] is None for row in original)


@pytest.mark.parametrize('prompt,canonical,finish,expected', [
    (8200, 10, None, 'input_budget_infeasible'),
    (1000, 2500, 'stop', 'canonical_copy_output_budget_exceeded'),
    (8100, 150, 'stop', 'canonical_copy_context_budget_exceeded'),
    (1000, 10, 'length', 'output_budget_stop'),
    (1000, 10, 'stop', 'semantic_copy_difference')])
def test_budget_failures_are_not_semantic_copy_failures(prompt, canonical, finish, expected):
    pair = {'candidate': 'committed', 'restatement': {'text': 'different',
        'finish_reason': finish, 'status': 'returned', 'valid_terminal': finish == 'stop'}}
    calls = [{'phase': 'restatement', 'generation_budget': {'prompt_tokens': prompt,
        'max_context_tokens': 8192, 'requested_output_tokens': 2048,
        'candidate_canonical_encoding_tokens': canonical}}]
    assert study.classify_restatement(pair, calls)['classification'] == expected
