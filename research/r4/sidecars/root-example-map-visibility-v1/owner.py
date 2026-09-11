"""Additive MAIN-owned launcher; original visibility READY and source stay frozen."""
import argparse
import functools
import os
import signal
import subprocess
import sys
import time

import study as s
from protocol import digest

ATTEMPT = s.ROOT / 'outputs/attempt-001'
RUNTIME = s.ROOT.parent / 'runtime-an27-5780-v1'


def credential_preflight():
    credential = s.load('visibility_credential_preflight', RUNTIME / 'credential_preflight.py',
                        '2ff11844d7237f99d1d6080b2e599a1bacf34ad693e13acd98a41cddcaaa8110')
    return credential.require_provider_credential()


def runtime_preflight():
    import runtime_binding
    runtime_binding.adapt()


@functools.lru_cache(maxsize=1)
def dependencies():
    # Reuse the qualified absent-process handling and lifecycle install unchanged.
    original = s.source().plan.old.row
    with s.source().aliases({'study': original}):
        launcher = s.load('visibility_qualified_owned_dependencies', original.ROOT / 'launch.py',
                          '62d7d0049b5e3303f6e68247038290c7cde0d74e3394b4856fea0e3e138d6b46')
    suite = launcher.dependencies()
    previous = list(sys.path)
    sys.path.insert(0, str(RUNTIME))
    try:
        adapter = s.load('visibility_actual_service_lifecycle', RUNTIME / 'lifecycle_adapter.py',
                         '18a5f3cc5003f294422c170826ac1595bd379f9958d52b00b59339ea24927375')
    finally:
        sys.path[:] = previous
    adapter.install(suite)
    return suite


def verify():
    s.verify()
    ready = s.read(s.ROOT / 'OWNER_READY.json')
    if s.sha(s.ROOT / 'READY.json') != ready['scientific_ready_sha256']:
        raise ValueError('scientific READY changed')
    if digest({k: v for k, v in ready.items() if k != 'identity'}) != ready['identity']:
        raise ValueError('owner READY identity changed')
    for path, pin in ready['source_sha256'].items():
        if s.sha(path) != pin:
            raise ValueError('owner source changed: ' + path)
    return ready


def execute(output):
    credential = credential_preflight()  # Before output creation or service/process work.
    if output.resolve() != ATTEMPT.resolve():
        raise ValueError('only exact new outputs/attempt-001 is authorized')
    if output.exists():
        raise FileExistsError('attempt already exists; no overwrite or retry')
    gpu = os.environ.get('CUDA_VISIBLE_DEVICES', '')
    if not gpu or ',' in gpu:
        raise ValueError('MAIN must assign one GPU under its independently owned lock')
    started = time.time()
    work, owned = started + 1200, started + 1320
    ready = verify()
    runtime_preflight()
    suite = dependencies()
    output.mkdir(parents=True, exist_ok=False)
    stage = output / 'owned-service'
    stage.mkdir()
    s.write(output / 'OWNER_RUN.json', dict(owner_identity=ready['identity'], scientific_ready_sha256=ready['scientific_ready_sha256'],
            started_epoch=started, work_deadline_epoch=work, owned_deadline_epoch=owned,
            outer_seconds=1350, cleanup_seconds=120, gpu=gpu, **credential))
    def expired(_sig, _frame):
        raise TimeoutError('owned1320-second inclusive deadline or MAIN termination')
    previous = {sig: signal.signal(sig, expired) for sig in (signal.SIGINT, signal.SIGTERM, signal.SIGALRM)}
    signal.setitimer(signal.ITIMER_REAL, max(.001, owned - time.time()))
    error, release_error, terminal, released = None, None, None, False
    try:
        suite.start_service(stage, s.read(s.ROOT / 'inputs/BINDING.json'), min(work, time.time() + 180))
        argv = [str(s.NATIVE), str(s.ROOT / 'collect.py'), '--binding', str(stage / 'BINDING.json'),
                '--endpoint', str(stage / 'service/endpoint-original.json'), '--output', str(output / 'rollout'),
                '--deadline', str(work)]
        suite.command(stage, 'visibility-collect', argv, 1200, work)
        terminal = s.read(output / 'rollout/TERMINAL.json')
        if terminal['planned'] != 32 or terminal['recorded'] != 32:
            raise ValueError('collector did not retain full planned endpoint accounting')
    except BaseException as caught:
        error = dict(type=type(caught).__name__, message=str(caught))
    finally:
        try:
            suite.release_service(stage)
            released = True
        except BaseException as caught:
            release_error = dict(type=type(caught).__name__, message=str(caught))
        signal.setitimer(signal.ITIMER_REAL, 0)
        for sig, handler in previous.items():
            signal.signal(sig, handler)
    result = dict(complete=error is None and released, error=error, release_error=release_error,
                  released=released, collector_terminal=terminal, planned=32, acquisitions=0, reused_acquisitions=4,
                  work_deadline_epoch=work, owned_deadline_epoch=owned, elapsed_seconds=time.time() - started,
                  collector_output=str(output / 'rollout'), outer_seconds=1350,
                  missing_endpoint_reward=None, no_retry=True, main_owns_gpu_and_lock=True)
    s.write(output / 'OWNER_TERMINAL.json', result)
    return result


def seal():
    s.verify()
    scientific_sha = s.sha(s.ROOT / 'READY.json')
    command = [str(s.NATIVE), '-m', 'pytest', '-q', str(s.ROOT / 'test_owner.py')]
    result = subprocess.run(command, cwd=s.ROOT, capture_output=True, text=True, timeout=60,
                            env={**os.environ, 'CUDA_VISIBLE_DEVICES': '', 'PYTHONDONTWRITEBYTECODE': '1'})
    s.write(s.ROOT / 'OWNER_CPU_TESTS.json', dict(argv=command, returncode=result.returncode,
            stdout=result.stdout, stderr=result.stderr, gpu_calls=0, service_calls=0))
    if result.returncode:
        raise ValueError('owner focused tests failed; retained OWNER_CPU_TESTS')
    lifecycle = s.read(RUNTIME / 'LIFECYCLE_READY_V2.json')
    sources = dict(lifecycle['source_sha256'])
    for path in [s.ROOT / 'owner.py', s.ROOT / 'test_owner.py', s.ROOT / 'OWNER_CPU_TESTS.json',
                 s.ROOT / 'READY.json', RUNTIME / 'LIFECYCLE_READY_V2.json', RUNTIME / 'credential_preflight.py']:
        sources[str(path)] = s.sha(path)
    value = dict(status='CPU_READY_OWNED_SUCCESSOR_FOR_MAIN_ACCEPTANCE', source_sha256=sources,
                 scientific_ready_sha256=scientific_sha, original_science_sources_unchanged=True,
                 parent_outer_seconds=1350, owned_inclusive_seconds=1320, work_seconds=1200, cleanup_seconds=120,
                 service_readiness_cap_seconds=180, shared_clock='owner start through service startup plus32 endpoints;4 completed acquisitions reused, not newly paid',
                 argv=[str(s.NATIVE), str(s.ROOT / 'owner.py'), 'run', '--output', str(ATTEMPT)],
                 verify_argv=[str(s.NATIVE), str(s.ROOT / 'owner.py'), 'verify'],
                 output_nesting='owner at outputs/attempt-001; service at owned-service; visibility collector at rollout',
                 service_wrapper=str(RUNTIME / 'service_wrapper_v2.py'), credential_preflight_before_output=True,
                 credential_environment_variable='STRICT_RLM_CALIBRATION_API_KEY',
                 no_secret_argv_or_logging=True, gpu_calls=0, model_service_calls=0,
                 ownership='MAIN independently owns GPU+lock; qualified suite owns its exact service and collector children')
    value['identity'] = digest(value)
    s.write(s.ROOT / 'OWNER_READY.json', value)
    print(dict(owner_ready_sha256=s.sha(s.ROOT / 'OWNER_READY.json'), identity=value['identity']))


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('command', choices=('verify', 'seal', 'run'))
    parser.add_argument('--output', type=__import__('pathlib').Path, default=ATTEMPT)
    args = parser.parse_args()
    if args.command == 'seal':
        seal()
    elif args.command == 'verify':
        print(verify()['identity'])
    else:
        result = execute(args.output)
        print(result)
        raise SystemExit(0 if result['complete'] else 1)
