"""Publish READY last, only after real native/trainer qualification completed."""
import json
from pathlib import Path

import common as a

c = a.c


def main():
    if (a.ROOT / 'READY.json').exists():
        raise ValueError('already sealed')
    amendment = a.verify_amendment()
    prepared = c.read(a.ROOT / 'PREPARED.json')
    qualification = c.read(a.ROOT / 'CPU_QUALIFICATION.json')
    for name in ['focused_tests', 'tiny_actual_peft', 'actual_trainer_preflight']:
        if qualification[name]['returncode'] != 0:
            raise ValueError('required CPU qualification incomplete')
    identity = json.loads(qualification['actual_trainer_preflight']['stdout'])
    if (identity['native_replay']['selected'] != 15 or identity['generation']['round'] != 1
            or identity['generation']['previous_policy'] != c.original_policy()):
        raise ValueError('not exact original-root first update')
    source = dict(c.read(a.BROAD / 'READY.json')['source_sha256'])
    source.update(amendment['source_sha256'])
    artifacts = {str(p): c.file_hash(p) for p in a.ROOT.rglob('*')
        if p.is_file() and p.suffix in ['.json', '.md', '.py']}
    c.authenticate(source)
    c.authenticate(artifacts)
    if (a.ROOT / 'outputs/attempt-001').exists():
        raise ValueError('output already used')
    ready = {'status': 'CPU_READY_BROAD16_EQUALITY_CONTINUATION',
        'amendment_id': amendment['amendment_id'], 'amendment_sha256': c.file_hash(a.ROOT / 'AMENDMENT.json'),
        'source_sha256': source, 'artifact_sha256': artifacts, 'input_sha256': amendment['input_sha256'],
        'argv': [str(c.NATIVE_PYTHON), str(a.ROOT / 'driver.py'), 'run', '--output', str(a.ROOT / 'outputs/attempt-001')],
        'verify_argv': [str(c.NATIVE_PYTHON), str(a.ROOT / 'driver.py'), 'verify'],
        'budget': {'remaining_work_seconds': a.WORK_SECONDS, 'inclusive_exception_seconds': a.INCLUSIVE_SECONDS,
            'outer_seconds': a.OUTER_SECONDS, 'parent_signal_cleanup_seconds': 120,
            'prior_elapsed_seconds': a.PRIOR_SECONDS, 'original_total_work_seconds': 18000},
        'prepared': prepared, 'first_update_episodes': 15, 'inherited_optimizer_steps': 0,
        'first_root_sha256': c.original_policy()['adapter_sha256'], 'fixed_child_sha256': c.CHILD_SHA,
        'rerolled_episodes': 0, 'validation0_replayed': False, 'newly_admitted_episodes': 0,
        'parent_environment': 'Inherit exclusive actual MIG UUID/LD/API key; no hardcoded CUDA=0',
        'gpu_calls': 0, 'model_calls': 0, 'parent_acceptance_required': True}
    c.write_once(a.ROOT / 'READY.json', ready)
    print(json.dumps({'ready_sha256': c.file_hash(a.ROOT / 'READY.json'),
        'amendment_sha256': ready['amendment_sha256'], 'sources': len(source), 'artifacts': len(artifacts),
        'inputs': len(amendment['input_sha256'])}, sort_keys=True), flush=True)


if __name__ == '__main__':
    main()
