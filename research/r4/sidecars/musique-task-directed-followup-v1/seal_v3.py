"""Seal only the observed argv repair after actual start/claim/release regression."""
import os
from pathlib import Path
import subprocess
import sys
import time

import lifecycle_v3
import owner_v3
import study_v3 as study


def main():
    assert os.environ.get('CUDA_VISIBLE_DEVICES') == ''
    assert not study.READY.exists() and not study.ATTEMPT.exists()
    original = study.previous.verify()
    failed = study.ROOT / 'outputs/attempt-002'
    result, terminal = study.read(failed / 'RESULT.json'), study.read(failed / 'OWNER_TERMINAL.json')
    assert result['physical_cost']['physical_started'] == 0 and not terminal['released']
    old = study.base_owner().study.dependencies()
    old.SERVE = study.ROOT / 'service_wrapper_v2.py'; old.life.ALLOCATION_SERVICE = old.SERVE
    try:
        old.life.claim_service(failed / 'service/service')
    except ValueError as error:
        observed = str(error)
    else:
        raise AssertionError('actual sealed attempt did not reproduce expected failed boundary')
    assert observed == 'SERVER_START/config/launcher binding does not authenticate this owned service'
    assert not Path('/proc/577193').exists() and not Path('/proc/577315').exists()
    lifecycle_v3.install(old)
    assert old.life.claim_service(failed / 'service/service') is None
    assert not (failed / 'service/SERVICE_OWNER_V2.json').exists()
    command = [str(study.NATIVE), '-m', 'pytest', '-q', 'test_repair_v3.py']
    started = time.time()
    red = subprocess.run(command + ['-k', 'actual_start'], cwd=study.ROOT,
        env={**os.environ, 'REPORT_TEST_OWNER': 'owner_v2'}, capture_output=True, text=True, timeout=45)
    assert red.returncode == 1 and observed in red.stdout
    green = subprocess.run(command, cwd=study.ROOT, env={k: v for k, v in os.environ.items() if k != 'REPORT_TEST_OWNER'},
                           capture_output=True, text=True, timeout=45)
    assert green.returncode == 0, green.stdout + green.stderr
    module = owner_v3.implementation()
    assert module.study.ATTEMPT == study.ATTEMPT
    assert module.collect.study.schedule() == study.previous.schedule()
    evidence = {'schema': 'report-exact-engine-lifecycle-cpu-v3', 'python': sys.version,
        'CUDA_VISIBLE_DEVICES': '', 'GPU_calls': 0, 'model_queries': 0,
        'observed_attempt002_exception': observed,
        'saved_attempt002_repaired_claim_passed_binding_boundary_then_absent_PID': True,
        'failed_attempt_directory_unchanged': True,
        'red': {'argv': command + ['-k', 'actual_start'], 'REPORT_TEST_OWNER': 'owner_v2',
                'returncode': red.returncode, 'stdout': red.stdout, 'stderr': red.stderr},
        'green': {'argv': command, 'returncode': green.returncode, 'stdout': green.stdout, 'stderr': green.stderr},
        'elapsed_seconds': time.time() - started,
        'real_functions': ['start_service', 'observe_service', 'claim_service', 'release_service', 'stop_service'],
        'doubles': ['Popen', 'process observation/descendant scan', 'signal delivery', 'ports and HTTP readiness'],
        'live_GPU_cleanup_tested': False}
    study.write_x(study.ROOT / 'CPU_EVIDENCE_V3.json', evidence)
    closure = dict(original['closure_sha256'])
    paths = [study.ROOT / name for name in ('READY_V2.json', 'lifecycle_v3.py', 'study_v3.py',
        'owner_v3.py', 'test_repair_v3.py', 'seal_v3.py', 'PLAN_V3.md', 'REPAIR_V3.md', 'CPU_EVIDENCE_V3.json')]
    paths += [failed / name for name in ('OWNER_RUN.json', 'OWNER_TERMINAL.json', 'RESULT.json',
        'service/LAUNCHER_PROCESS.json', 'service/service/SERVER_START.json',
        'service/service/ACTUAL_DISPATCH.json', 'service/OWNED_PROCESSES/577193-1104196454.json')]
    cleanup = study.STORE / 'operations/2026-09-12-musique-attempt002-cleanup'
    paths += [cleanup / 'SIGTERM.json', cleanup / 'terminate_owned.py']
    for path in paths: closure[str(path)] = study.sha(path)
    value = {k: v for k, v in original.items() if k not in ('identity', 'created_epoch', 'closure_sha256')}
    value.update(schema='musique-task-directed-followup-ready-v3', created_epoch=time.time(),
        command=[str(study.NATIVE), str(study.ROOT / 'owner_v3.py'), 'run', '--outer-seconds', '1700'],
        output=str(study.ATTEMPT), source_V2_READY_sha256=study.sha(study.ROOT / 'READY_V2.json'),
        repair='exact V2 engine argv in authenticated claim/release; sanitized exception detail',
        failed_attempt002_zero_science_calls=True, failed_attempt002_original_release_false_preserved=True,
        main_cleanup_receipt_sha256=study.sha(cleanup / 'SIGTERM.json'),
        CPU_evidence_sha256=study.sha(study.ROOT / 'CPU_EVIDENCE_V3.json'), closure_sha256=closure)
    value['identity'] = study.digest(value)
    study.write_x(study.READY, value)
    assert study.verify() == value
    print({'READY_sha256': study.sha(study.READY), 'identity': value['identity'], 'pins': len(closure),
           'command': value['command'], 'test': green.stdout})


if __name__ == '__main__': main()
