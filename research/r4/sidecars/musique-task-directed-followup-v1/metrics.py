"""Fixed 12 paired questions and physical-versus-policy cost accounting."""
import collections

import study


def policy_roles(arm):
    if arm == 'full_source': return ['full_source']
    result = ['report_left', 'report_right', 'plan']
    if arm != 'stop': result += [arm + '_left', arm + '_right']
    return result + [arm]


def costs(calls, planned):
    value = {'planned_calls': planned, 'physical_started': sum(c.get('physical_started', False) for c in calls),
             'returned_transport_valid': sum(c.get('transport_valid', False) for c in calls),
             'not_started': planned - sum(c.get('physical_started', False) for c in calls),
             'sum_observed_call_seconds': sum(c.get('wall_seconds') or 0 for c in calls),
             'wall_sum_is_not_concurrent_elapsed': True, 'unknown_usage_is_not_zero': True}
    for field in ('prompt_tokens', 'completion_tokens'):
        usage = [(c.get('usage') or {}).get(field) for c in calls if c.get('physical_started')]
        value[field + '_observed_subtotal'] = sum(v for v in usage if type(v) is int)
        value[field + '_unknown_calls'] = sum(type(v) is not int for v in usage)
    cached = [((c.get('usage') or {}).get('prompt_tokens_details') or {}).get('cached_tokens')
              for c in calls if c.get('physical_started')]
    value.update(cached_prompt_tokens_observed_subtotal=sum(v for v in cached if type(v) is int),
                 cached_prompt_tokens_unknown_calls=sum(type(v) is not int for v in cached))
    return value


def paired(before, after):
    shared = [k for k in before if before[k]['available'] and after[k]['available']]
    return {'planned': len(before), 'both_available': len(shared), 'unavailable_pairs': len(before) - len(shared),
        'wins': sum(before[k]['answer_em'] == 0 and after[k]['answer_em'] == 1 for k in shared),
        'losses': sum(before[k]['answer_em'] == 1 and after[k]['answer_em'] == 0 for k in shared),
        'same_correct': sum(before[k]['answer_em'] == 1 and after[k]['answer_em'] == 1 for k in shared),
        'same_wrong': sum(before[k]['answer_em'] == 0 and after[k]['answer_em'] == 0 for k in shared),
        'answer_f1_delta_sum': sum(after[k]['answer_f1'] - before[k]['answer_f1'] for k in shared),
        'support_f1_delta_sum': sum(after[k]['support_f1'] - before[k]['support_f1'] for k in shared)}


def summarize(output, runtime_qualified):
    selected, schedule = study.selected(), study.schedule()
    gold = study.read(study.INPUTS / 'host/HOST_GOLD.json')
    expected = {r['call_id'] for r in schedule}
    calls = {p.stem: study.read(p) for p in (output / 'calls').glob('*.json')}
    starts = {p.stem for p in (output / 'starts').glob('*.json')}
    assert set(calls) <= expected and starts <= expected
    # Start-only costs remain unknown and do not become zero or model errors.
    for cid in starts - set(calls):
        calls[cid] = {**study.read(output / 'starts' / (cid + '.json')),
                      'status': 'start_only_provider_unknown', 'transport_valid': False, 'usage': {}}
    by_key = {(r['record_id'], r['role']): calls.get(r['call_id'], {}) for r in schedule}
    arms = {}
    for arm in study.ARMS:
        scores = {item['record_id']: study.score_final(by_key[item['record_id'], arm],
            gold[item['record_id']], item['paragraph_count']) for item in selected}
        for item in selected:
            native = by_key[item['record_id'], arm]
            scores[item['record_id']].update(final_native_status=native.get('status', 'unattempted'),
                final_finish_reason=native.get('finish_reason'), final_failure=native.get('failure'))
        known = [v for v in scores.values() if v['available']]
        correct = sum(v['answer_em'] for v in known)
        per_hop = {}
        for hop in (2, 3, 4):
            subset = [scores[i['record_id']] for i in selected if i['hop_count'] == hop]
            per_hop[str(hop)] = {'planned': 4, 'correct': sum(v['answer_em'] for v in subset if v['available']),
                                'available': sum(v['available'] for v in subset)}
        policy_calls = [by_key[item['record_id'], role] for item in selected for role in policy_roles(arm)]
        arms[arm] = {'planned': 12, 'available': len(known), 'correct': correct,
            'wrong': len(known) - correct, 'unavailable': 12 - len(known),
            'malformed_final_json': sum(not v['valid_json'] for v in known),
            'answer_f1_sum_available': sum(v['answer_f1'] for v in known),
            'support_f1_sum_available': sum(v['support_f1'] for v in known),
            'primary_accuracy': correct / 12 if runtime_qualified and len(known) == 12 else None,
            'per_hop': per_hop, 'scores': scores,
            'policy_cost': costs(policy_calls, 12 * len(policy_roles(arm)))}
    pairs = {a + '_to_targeted': paired(arms[a]['scores'], arms['targeted']['scores'])
             for a in ('stop', 'broad', 'full_source')}
    complete = runtime_qualified and len(calls) == 132 and all(a['available'] == 12 for a in arms.values())
    screen = complete and pairs['stop_to_targeted']['wins'] - pairs['stop_to_targeted']['losses'] >= 3
    screen = screen and pairs['broad_to_targeted']['wins'] - pairs['broad_to_targeted']['losses'] >= 2
    screen = screen and pairs['stop_to_targeted']['support_f1_delta_sum'] >= 0 and pairs['broad_to_targeted']['support_f1_delta_sum'] >= 0
    screen = screen and arms['stop']['correct'] >= 3
    return {'schema': 'musique-task-directed-followup-result-v1', 'runtime_qualified': runtime_qualified,
        'complete': complete, 'planned_physical_calls': 132, 'planned_terminal_slots': 48, 'unique_questions': 12,
        'arms': arms, 'paired': pairs, 'promotion_screen_passed': bool(screen),
        'screen_does_not_establish_novelty_or_learned_policy': True,
        'physical_cost': costs(list(calls.values()), 132),
        'status_counts': dict(collections.Counter(c.get('status') for c in calls.values())),
        'missing_receipt_ids': sorted(expected - set(calls)), 'start_only_ids': sorted(starts - {p.stem for p in (output / 'calls').glob('*.json')}),
        'raw_requests': len(list((output / 'native').glob('*-REQUEST.json'))),
        'raw_responses': len(list((output / 'native').glob('*-RESPONSE.json'))),
        'max_actual_prefix_plus_requested_output': max((c.get('actual_prefix_plus_output', 0) for c in calls.values()), default=0),
        'cost_boundary': 'Shared acquisition counted once physically and once per policy deployment; no charging the full-source reference for other arms. Four-question concurrency means summed call time is not elapsed time.',
        'mechanism_boundary': 'Fixed report-channel graph, not autonomous delegation or actual depth choice; no generated Python executed.'}
