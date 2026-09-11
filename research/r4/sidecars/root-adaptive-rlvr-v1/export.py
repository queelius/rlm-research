"""Stage-once native admission; no outcomes repaired and no operator likelihoods."""
from collections import Counter
from pathlib import Path

import native as n
import study as s

CREDIT = 'Native depth0 current-action suffix only; all prior/root/child/tool tokens masked.'


def outcome(episode, gold):
    traces = episode.get('traces') or []
    trace = traces[0] if len(traces) == 1 else {}
    completed = bool(trace.get('is_completed'))
    reply = trace.get('root_reply')
    calls = [call for t in traces for call in t.get('calls', [])]
    strict = s.endpoint_reward(reply, gold, completed, True)
    reason = None
    if any(call.get('error') for call in calls):
        reason = 'provider_failure'
    elif episode.get('ok') is False or episode.get('errors') or trace.get('errors') or not trace.get('ok'):
        reason = 'setup_runtime_or_trace_failure'
    elif not completed or not isinstance(reply, str):
        reason = 'incomplete_or_unobservable'
    elif not calls:
        reason = 'no_native_provider_call'
    return {'reply': reply, 'execution_completed': completed,
            'terminal_observable': strict is not None, 'strict_endpoint_reward': strict,
            'reward': strict if reason is None else None, 'null_reason': reason,
            'completed_empty': completed and reply == '', 'model_calls': len(calls),
            'provider_failed_calls': sum(bool(call.get('error')) for call in calls),
            'length_finished_calls': sum(call.get('finish_reason') == 'length' for call in calls)}


def mixed_group(rows, generation, binding, dataset_id):
    if generation is None:
        return None
    if any(r.get('qualification_only') or r.get('generation_id') != generation['generation_id'] for r in rows):
        raise ValueError('qualification or stale generation cannot supply likelihood')
    generic = n.stack().native.e.capture.recursive.exporter.trainer_module()
    try:
        group = generic.training_group(rows)
    except ValueError as error:
        if str(error) != 'no fresh within-prompt mixed reward group':
            raise
        return None
    group.update(dataset_id=dataset_id, role_binding=binding, generation=generation, credit_policy=CREDIT)
    group['group_id'] = s.digest({k: v for k, v in group.items() if k != 'group_id'})
    return group


def rebuild(attempt):
    from collect import verify_spec
    attempt = Path(attempt)
    spec = verify_spec(attempt / 'SPEC.json')
    status = s.read(attempt / 'STATUS.json')
    plans = {r['id']: r for r in spec['plan']}
    records = {p.stem: (p, s.read(p)) for p in sorted((attempt / 'rows').glob('*.json'))}
    if set(records) != set(plans) or status['recorded'] != len(plans) or status['stop_reason'] is not None:
        raise ValueError('incomplete/capped stage; no partial-round update')
    provenance = {'source_attempt': str(attempt.resolve()), 'source_spec_sha256': s.sha(attempt / 'SPEC.json'),
                  'status_sha256': s.sha(attempt / 'STATUS.json'),
                  'source_record_sha256': {k: s.sha(v[0]) for k, v in records.items()},
                  'generation': spec['generation'], 'role_binding': spec['binding'],
                  'coordinate_plan_sha256': s.digest(spec['plan'])}
    dataset_id = s.digest(provenance)
    public, host = s.data()
    public = {v['id']: v for v in public}
    rows, failures = [], []
    for identifier, (path, record) in records.items():
        coordinate = plans[identifier]
        if record['coordinate'] != coordinate:
            raise ValueError('stale/changed raw coordinate')
        row = {'episode_id': identifier, 'task_id': coordinate['task_name'], 'split': coordinate['split'],
               'sample_seed': coordinate['seed'], 'temperature': .5, 'dataset_id': dataset_id,
               'generation_id': spec['generation']['generation_id'] if spec['generation'] else None,
               'qualification_only': False, 'trace_trainable': False, 'turns': [], 'all_role_evidence': [],
               'reward': None, 'invalid_reason': None, 'coordinate': coordinate,
               'wall_seconds': record['ended_epoch'] - record['started_epoch']}
        if record.get('episode_path') is None:
            row.update(strict_reward=None, execution_completed=False, terminal_observable=False,
                       invalid_reason=record.get('error') or record.get('censored') or 'raw_episode_unavailable')
        else:
            raw_path = Path(record['episode_path'])
            if raw_path != attempt / 'episodes' / (identifier + '.json'):
                raise ValueError('episode path outside its immutable coordinate')
            s.check(raw_path, record['episode_sha256'])
            episode = s.read(raw_path)
            observed = outcome(episode, host[coordinate['context_id']]['answers'][coordinate['family']])
            row.update(observed, strict_reward=observed['strict_endpoint_reward'],
                       terminal_correct=observed['strict_endpoint_reward'] == 1,
                       terminal_schema_valid=bool(__import__('re').fullmatch(r'Answer: ([0-9]+)', (observed['reply'] or '').strip())),
                       invalid_reason=observed['null_reason'])
            row['provenance'] = {'source_record_sha256': s.sha(path), 'raw_episode_sha256': record['episode_sha256'],
                                  'adapter': spec['descriptor']['adapter'], 'role_binding': spec['binding'],
                                  'base_model': spec['descriptor']['base_model'], 'rollout_logprobs_mode': 'processed_logprobs',
                                  'renderer': {'name': 'qwen3', 'enable_thinking': True}}
            if row['reward'] is not None:
                try:
                    roots, evidence = n.exact_turns(episode, attempt, spec['binding'])
                    if any(t['sampling']['seed'] != coordinate['seed'] for t in evidence):
                        raise ValueError('physical generation seed mismatch')
                    expected = s.read(s.ROOT / 'inputs/TASKS.json')[coordinate['task_name']]
                    if roots[0]['input_ids'][:roots[0]['prompt_length']] != expected['first_prompt_token_ids']:
                        raise ValueError('first native physical prefix differs from frozen task')
                    for turn in evidence:
                        typed = s.read(turn['typed_audit_path'])
                        if typed['coordinate'] != coordinate:
                            raise ValueError('typed host coordinate metadata differs')
                        if typed['decision']['apply']:
                            context = public[coordinate['context_id']]
                            decision = n.stack().interface.hooks.contract.match_request(
                                typed['decision']['request_text'], n.stack().interface.catalogs({context['id']: context})[str(coordinate['context_window_id'])])
                            if not decision['matched'] or decision['schema'] != typed['decision']['schema']:
                                raise ValueError('child schema not derived from exact public source records')
                    row.update(turns=roots, all_role_evidence=evidence, trace_trainable=True,
                               action_tokens=sum(len(t['old_logprobs']) for t in roots),
                               child_action_tokens=sum(len(t['old_logprobs']) for t in evidence if not t['credited']))
                except (ValueError, KeyError, TypeError, AttributeError) as error:
                    row.update(reward=None, invalid_reason='native_integrity: ' + str(error))
                    failures.append({'episode_id': identifier, 'reason': str(error)})
        rows.append(row)
    group = None if failures else mixed_group(rows, spec['generation'], spec['binding'], dataset_id)
    counts = Counter(str(row['invalid_reason']) for row in rows if row['invalid_reason'])
    manifest = {**provenance, 'dataset_id': dataset_id, 'planned': len(plans), 'recorded': len(rows),
                'complete': True, 'strict_successes': sum(r['reward'] == 1 for r in rows),
                'admitted_outcomes': sum(r['reward'] is not None for r in rows),
                'integrity_failures': failures, 'exclusion_reasons': dict(counts),
                'training_group_episodes': len(group['episodes']) if group else 0,
                'training_group_unavailable_reason': 'no fresh within-prompt mixed reward group' if spec['generation'] and group is None and not failures else None,
                'root_action_tokens': sum(r.get('action_tokens', 0) for r in rows),
                'child_evidence_action_tokens': sum(r.get('child_action_tokens', 0) for r in rows),
                'model_calls': sum(r.get('model_calls', 0) for r in rows),
                'endpoint_successes_including_excluded': sum(r.get('strict_reward') == 1 for r in rows)}
    return rows, group, manifest


def export_attempt(attempt, output):
    rows, group, manifest = rebuild(attempt)
    output = Path(output)
    output.mkdir(parents=True, exist_ok=False)
    s.write(output / 'EPISODES.json', rows)
    if group:
        s.write(output / 'GROUP.json', group)
    manifest['artifact_sha256'] = {p.name: s.sha(p) for p in output.iterdir()}
    s.write(output / 'MANIFEST.json', manifest)
    return manifest


def authenticate_export(output):
    output = Path(output)
    manifest = s.read(output / 'MANIFEST.json')
    for name, expected in manifest['artifact_sha256'].items():
        s.check(output / name, expected)
    rows, group, rebuilt = rebuild(Path(manifest['source_attempt']))
    if (rows != s.read(output / 'EPISODES.json') or rebuilt != {k: v for k, v in manifest.items() if k != 'artifact_sha256'}
            or (group is None) != (not (output / 'GROUP.json').exists())
            or group is not None and group != s.read(output / 'GROUP.json')):
        raise ValueError('export differs from immutable native evidence')
    if manifest['integrity_failures']:
        raise ValueError('native integrity failure; do not train')
    return {'manifest_sha256': s.sha(output / 'MANIFEST.json'),
            'group_sha256': s.sha(output / 'GROUP.json') if group else None,
            'replayed': len(rows), 'selected': len(group['episodes']) if group else 0}
