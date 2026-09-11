"""One-time CPU amendment/export qualification; READY is published separately last."""
import json
import os
import subprocess
import sys
from pathlib import Path

import native as n

a, c = n.a, n.c


def command(argv, cap=180):
    result = subprocess.run(argv, capture_output=True, text=True, timeout=cap,
        env={**os.environ, 'CUDA_VISIBLE_DEVICES': '', 'PYTHONDONTWRITEBYTECODE': '1'})
    if result.returncode:
        raise ValueError(json.dumps({'argv': argv, 'exit': result.returncode,
            'stdout': result.stdout[-6000:], 'stderr': result.stderr[-3000:]}))
    return {'argv': argv, 'returncode': result.returncode, 'stdout': result.stdout, 'stderr': result.stderr}


def main():
    if (a.ROOT / 'AMENDMENT.json').exists():
        raise ValueError('amendment already frozen')
    a.verify_prior()
    c.verify_campaign()
    recipe = c.read(a.BROAD / 'RECIPE.json')
    c.write_once(a.ROOT / 'RECIPE.json', {'unchanged_training_recipe': recipe,
        'actual_training_recipe_path': str(a.BROAD / 'RECIPE.json'),
        'actual_training_recipe_sha256': c.file_hash(a.BROAD / 'RECIPE.json'),
        'cumulative_total_work_seconds': 18000, 'prior_elapsed_seconds': a.PRIOR_SECONDS,
        'remaining_work_seconds': a.WORK_SECONDS, 'inclusive_exception_seconds': a.INCLUSIVE_SECONDS,
        'outer_seconds': a.OUTER_SECONDS, 'parent_signal_cleanup_seconds': 120,
        'primary_checkpoint': 'fixed-final16; no selection change', 'first_update': 'saved native round1, original857a, emptyAdam'})
    source = {str(p): c.file_hash(p) for p in a.ROOT.iterdir() if p.suffix in ['.py', '.md', '.json']}
    source.update({str(a.BROAD / 'READY.json'): a.BROAD_READY_SHA,
        str(c.CONT / 'native_amendment.py'): c.PINS[c.CONT / 'native_amendment.py']})
    decision = a.ROOT.parent.parent / 'operations/2026-09-09-continuous-allocation/BROAD16_EQUALITY_CONTINUATION_DECISION.md'
    source[str(decision)] = c.file_hash(decision)
    inputs = {str(a.STOP): a.STOP_SHA}
    # Pin raw stage bytes once. No tensors are repeatedly hashed per call.
    for directory in [a.PRIOR_RUN / 'round-01/collection', a.PRIOR_RUN / 'validation-00']:
        for path in directory.rglob('*.json'):
            inputs[str(path)] = c.file_hash(path)
    gen_path = a.PRIOR_RUN / 'round-01/GENERATION.json'
    inputs[str(gen_path)] = c.file_hash(gen_path)
    amendment = {'schema': 'broad16-exact-child-equality-exclusion-v1', 'source_sha256': source,
        'input_sha256': inputs, 'prior_stop_path': str(a.STOP), 'prior_optimizer_steps': 0,
        'remaining_work_seconds': a.WORK_SECONDS, 'inclusive_exception_seconds': a.INCLUSIVE_SECONDS,
        'root_rejections_admitted': False, 'newly_admitted_episodes': 0,
        'rule': 'exact8192 prompt+at-least1-output child400; old>8192 rule unchanged; all three affected episodes remain excluded'}
    amendment['amendment_id'] = c.digest(amendment)
    c.write_once(a.ROOT / 'AMENDMENT.json', amendment)
    attempt = a.PRIOR_RUN / 'round-01/collection/rollout'
    before, _, original = n.old.impl.rebuild_export(attempt)
    manifest = n.export(attempt, a.ROOT / 'prepared-round01')
    rows = c.read(a.ROOT / 'prepared-round01/EPISODES.json')
    group = c.read(a.ROOT / 'prepared-round01/GROUP.json')
    assert [{k: v for k, v in r.items() if k != 'admission_metadata'} for r in rows] == before
    excluded = {r['episode_id'] for r in before if r['reward'] is None}
    assert len(excluded) == 3 and excluded == {r['episode_id'] for r in rows if r['reward'] is None}
    assert all(not r['turns'] for r in rows if r['episode_id'] in excluded)
    assert manifest['recovered_episodes_newly_admitted'] == 0
    assert len(group['episodes']) == 15
    assert all(x['proof']['graph_nodes_removed'] == 0 for x in manifest['reclassified_exclusions'])
    recomputed = c.pilot_math().recompute_group(rows)
    for key in ['dataset_id', 'role_binding', 'generation', 'credit_policy']:
        recomputed[key] = group[key]
    recomputed['group_id'] = c.digest({k: v for k, v in recomputed.items() if k != 'group_id'})
    assert recomputed == group
    old_validation = n.authenticate_export(a.PRIOR_RUN / 'validation-00/export')
    c.write_once(a.ROOT / 'EXPORT_PROOF.json', {'original_planned': original['planned'],
        'original_recorded': original['recorded'], 'original_admitted': original['admitted_outcomes'],
        'original_strict_successes': original['strict_successes'], 'old_fields_exactly_equal': True,
        'old_fields_by_episode_sha256': {r['episode_id']: c.digest(r) for r in before},
        'excluded_episodes': sorted(excluded), 'newly_admitted_episodes': 0, 'graph_nodes_removed': 0,
        'mixed_group_episodes': len(group['episodes']), 'group_id': group['group_id'],
        'validation0_authentication': old_validation, 'failed_call_proofs': manifest['reclassified_exclusions']})
    tests = command([str(c.NATIVE_PYTHON), '-m', 'pytest', '-q', '-p', 'no:cacheprovider',
        str(a.ROOT / 'test_continuation.py'), str(a.ROOT / 'test_reuse.py')])
    toy = command([str(c.TRAIN_PYTHON), '-m', 'pytest', '-q', '-p', 'no:cacheprovider', str(a.ROOT / 'test_toy_update.py')])
    # Actual15-episode trainer authentication, including the routed native replay,
    # original grouped advantage reconstruction and exact root/base/child identities.
    preflight = command([str(c.TRAIN_PYTHON), str(a.ROOT / 'train.py'), '--preflight',
        '--group', str(a.ROOT / 'prepared-round01/GROUP.json'), '--generation', str(gen_path)], cap=300)
    identity = json.loads(preflight['stdout'])
    assert identity['native_replay']['selected'] == 15
    assert identity['generation']['previous_policy']['step'] == 0
    assert identity['generation']['previous_policy']['optimizer_sha256'] is None
    c.write_once(a.ROOT / 'CPU_QUALIFICATION.json', {'focused_tests': tests, 'tiny_actual_peft': toy,
        'actual_trainer_preflight': preflight, 'prior_red': 'Three desired tests failed before implementation; actual equality fixtures continue to assert old-rule rejection',
        'gpu_calls': 0, 'model_calls': 0, 'saved24_reused': True, 'validation0_replayed': False})
    c.write_once(a.ROOT / 'PREPARED.json', {'status': 'CPU_QUALIFIED_PARENT_READY_PENDING',
        'amendment_sha256': c.file_hash(a.ROOT / 'AMENDMENT.json'),
        'prepared_manifest_sha256': c.file_hash(a.ROOT / 'prepared-round01/MANIFEST.json'),
        'prepared_group_sha256': c.file_hash(a.ROOT / 'prepared-round01/GROUP.json'),
        'mixed_episodes': 15, 'remaining_work_seconds': a.WORK_SECONDS, 'gpu_calls': 0})
    print(json.dumps(c.read(a.ROOT / 'PREPARED.json'), sort_keys=True), flush=True)


if __name__ == '__main__':
    main()
