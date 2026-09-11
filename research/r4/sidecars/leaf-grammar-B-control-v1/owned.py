"""Parent-accepted B80 wrapper around the unchanged qualified single-service lifecycle."""
import argparse
import importlib.util
import json
import os
import signal
import sys
import time
from pathlib import Path

import driver as d

ROOT = Path(__file__).resolve().parent
ALIAS = 'strict-rlm-qwen3-4b-leaf-B-final-v1'
FROZEN_WRAPPER = ROOT.parent / 'leaf-indexed-grammar-transfer-v1/owned.py'
FROZEN_WRAPPER_SHA = 'd2eae2e0443d0ebd338649a5e420329af9240ec0ad1f5f544696a18eab4fd31f'


def load_lifecycle():
    if d.file_hash(FROZEN_WRAPPER) != FROZEN_WRAPPER_SHA:
        raise ValueError('qualified wrapper helper changed')
    spec = importlib.util.spec_from_file_location('B_private_owned_lifecycle', FROZEN_WRAPPER)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def service_binding(weights, weights_path):
    model = weights['models']['Bfinal']
    return {'schema': 'B-fixed-final-single-adapter-binding-v1',
        'models': {ALIAS: {'path': model['path'], 'adapter_sha256': model['model_sha256'],
                          'config_sha256': model['config_sha256']}},
        'role_map': {'root': ALIAS, 'children': [ALIAS]},
        'selection_path': str(weights_path), 'selection_sha256': d.file_hash(weights_path),
        'selection_semantics': 'B fixed-final epoch2/step204, not validation-selected',
        'descriptor_filename_semantics': {'endpoint-original.json': 'Bfinal single alias; no original-weight claim'},
        'post_training_test_consulted_for_binding': False}


def execute(directory, suite, weights, weights_path=ROOT / 'WEIGHTS.json'):
    started = time.time()
    directory.mkdir(parents=True, exist_ok=False)
    deadline = started + 1680
    output = ROOT / 'outputs/attempt-001'
    suite.c.write_once(directory / 'WRAPPER_ATTEMPT.json', {'started_epoch': started,
        'overall_deadline_epoch': started + 1800, 'work_deadline_epoch': deadline,
        'cleanup_reserve_seconds': 120, 'collector_output': str(output),
        'weights_sha256': d.file_hash(weights_path)})
    try:
        suite.start_service(directory, service_binding(weights, weights_path), deadline)
        bound = directory / 'B-BOUND.json'
        suite.command(directory, 'B-bind', [suite.PYTHON, str(ROOT / 'driver.py'), 'bind',
            '--endpoint-descriptor', str(directory / 'service/endpoint-original.json'),
            '--spec-path', str(bound)], 120, deadline)
        suite.command(directory, 'B-run', [suite.PYTHON, str(ROOT / 'driver.py'), 'run',
            '--spec-path', str(bound), '--output-dir', str(output),
            '--overall-start-epoch', str(started)], 930, deadline)
    except BaseException as error:
        suite.c.write_once(directory / 'ERROR.json', {'type': type(error).__name__,
            'message': str(error), 'epoch': time.time()})
        raise
    finally:
        try:
            suite.release_service(directory)
        finally:
            elapsed = time.time() - started
            suite.c.write_once(directory / 'FINISH.json', {'elapsed_seconds': elapsed,
                'overall1800_exceeded': elapsed > 1800,
                'owned_release_marker': str(directory / 'SERVICE_STOPPED.json'),
                'owned_release_completed': (directory / 'SERVICE_STOPPED.json').exists(),
                'collector_status_path': str(output / 'STATUS.json')})


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--operation-root', type=Path)
    parser.add_argument('--directory', type=Path)
    parser.add_argument('--verify', action='store_true')
    args = parser.parse_args()
    d.verify(d.read(ROOT / 'SPEC.json'))
    frozen = load_lifecycle()
    suite = frozen.load_suite()
    if args.verify:
        print(json.dumps({'sources_verified': True, 'gpu_calls': 0, 'single_alias': ALIAS}), flush=True)
        return
    if args.operation_root is None or args.directory is None:
        parser.error('explicit accepted operation root and unused owned directory required')
    operation, directory = args.operation_root.resolve(), args.directory.resolve()
    if not directory.is_relative_to(operation):
        raise ValueError('owned directory must belong to accepted operation')
    op = frozen.load('B_private_acceptance', frozen.COORDINATOR)
    op.ROOT = operation
    plan = op.read(operation / 'PLAN.json')
    op.validate_acceptance(op.read(operation / 'ACCEPTANCE.json'), plan)
    required = {str(ROOT / n) for n in ['owned.py', 'READY.json', 'WEIGHTS.json', 'SPEC.json']}
    if not required <= set(plan['acceptance_source_paths']):
        raise ValueError('parent acceptance omits B weights/source/readiness')
    actual_argv = [sys.executable, str(Path(__file__).resolve()), *sys.argv[1:]]
    if not any(job['argv'] == actual_argv for job in plan['jobs']):
        raise ValueError('exact owned command not accepted')
    for key, value in plan['required_inherited_environment'].items():
        if os.environ.get(key) != value:
            raise ValueError('wrong inherited environment: ' + key)
    for path, sha in d.read(ROOT / 'READY.json')['source_sha256'].items():
        if d.file_hash(path) != sha:
            raise ValueError('ready source changed: ' + path)
    weights = d.read(ROOT / 'WEIGHTS.json')
    if weights != d.authenticate_weights():
        raise ValueError('fixed-final B checkpoint changed')

    def interrupted(sig, frame):
        raise KeyboardInterrupt(f'owned B signal{sig}; release authenticated service')
    signal.signal(signal.SIGTERM, interrupted)
    signal.signal(signal.SIGINT, interrupted)
    execute(directory, suite, weights)


if __name__ == '__main__':
    main()
