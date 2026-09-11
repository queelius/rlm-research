"""Final CPU verification and one-time READY publication; never starts inference."""
from copy import deepcopy
from pathlib import Path

import driver
import owned

s = driver.s
ROOT = s.ROOT


def main():
    if (ROOT / 'READY.json').exists():
        raise ValueError('READY already published; no mutation')
    spec = s.read(ROOT / 'SPEC.json')
    driver.verify(spec)
    if driver.weights() != s.read(ROOT / 'WEIGHTS.json'):
        raise ValueError('original selected-child closure changed')
    owned.load_suite()
    previous = s.read(s.PARENT / 'SPEC.json')
    compared = 0
    for row in spec['design']['plan']:
        if row['source_prefix'] != 'q' or row['number_namespace'] != 'overlap':
            continue
        old = next(r for r in previous['design']['plan'] if all(r[k] == row[k]
            for k in ['context_index', 'permutation', 'repeat', 'arm']))
        a, b = deepcopy(spec['requests'][row['id']]), deepcopy(previous['requests'][old['id']])
        a.pop('seed')
        b.pop('seed')
        if s.serialize(a) != s.serialize(b):
            raise ValueError('overlap/q request differs from original beyond fresh seed')
        compared += 1
    if compared != 96 or (ROOT / 'owned/attempt-001').exists() or (ROOT / 'outputs/attempt-001').exists():
        raise ValueError('crosswalk incomplete or launch paths already used')
    s.write_once(ROOT / 'FINAL_CPU_VERIFY.json', {'immutable_spec_verified': True,
        'old_child_binding_verified': True, 'pinned_lifecycle_verified': True,
        'original_overlap_q_serialized_equal_except_seed': compared,
        'source_count_before_final_report': len(spec['source_sha256']),
        'model_calls': 0, 'gpu_calls': 0})
    sources = dict(spec['source_sha256'])
    sources.update({str(p): s.file_hash(p) for p in ROOT.iterdir()
        if p.is_file() and p.suffix in ['.py', '.md', '.json']})
    s.anchor.sst.verify_hashes(sources)
    ready = {'status': 'CPU_READY_PARENT_ACCEPTANCE_REQUIRED', 'source_sha256': sources,
        'spec_path': str(ROOT / 'SPEC.json'), 'spec_sha256': s.file_hash(ROOT / 'SPEC.json'),
        'spec_id': spec['spec_id'], 'weights_path': str(ROOT / 'WEIGHTS.json'),
        'weights_sha256': s.file_hash(ROOT / 'WEIGHTS.json'),
        'argv': [owned.PYTHON, str(ROOT / 'owned.py'), '--directory', str(ROOT / 'owned/attempt-001')],
        'budget': spec['budget'], 'sampling_seeds': s.SEEDS, 'master': s.MASTER,
        'model_sha256': spec['weight']['models']['old_sft']['model_sha256'],
        'qualification': s.read(ROOT / 'PREPARED.json'),
        'parent_environment': 'Inherit exact parent-assigned MIG UUID/LD/API-key environment; never hardcode CUDA=0',
        'report': str(ROOT / 'IMPLEMENTATION_REPORT.md'),
        'gpu_calls': 0, 'model_calls': 0, 'acceptance_granted': False}
    # Publication is the final write: sources and inputs cannot be edited afterward.
    s.write_once(ROOT / 'READY.json', ready)
    print(s.serialize({'ready_sha256': s.file_hash(ROOT / 'READY.json'),
                       'source_files': len(sources), 'spec_id': spec['spec_id']}), flush=True)


if __name__ == '__main__':
    main()
