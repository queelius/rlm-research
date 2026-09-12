"""Additive narrowly observed registry repair; no GPU execution."""
import os
from pathlib import Path
import subprocess
import sys
import time

import study_v2 as study
import owner_v2


def main():
    assert os.environ.get('CUDA_VISIBLE_DEVICES') == ''
    assert not study.READY.exists() and not study.ATTEMPT.exists()
    original = study.base.verify()
    failed = study.ROOT / 'outputs/attempt-001'
    terminal = study.read(failed / 'OWNER_TERMINAL.json')
    result = study.read(failed / 'RESULT.json')
    assert terminal['released'] and not terminal['complete']
    assert result['physical_cost']['physical_started'] == 0
    command = [str(study.NATIVE), '-m', 'pytest', '-q', 'test_repair_v2.py']
    started = time.time()
    test = subprocess.run(command, cwd=study.ROOT, capture_output=True, text=True, timeout=90)
    assert test.returncode == 0, test.stdout + test.stderr
    module = owner_v2.implementation()
    assert module.study.ATTEMPT == study.ATTEMPT
    assert module.collect.study.schedule() == study.base.schedule()
    evidence = {'argv': command, 'returncode': test.returncode, 'stdout': test.stdout, 'stderr': test.stderr,
        'elapsed_seconds': time.time() - started, 'python': sys.version, 'CUDA_VISIBLE_DEVICES': '',
        'actual_prime_server_argument_boundary_executed': True,
        'only_terminal_GPU_serving_coroutine_stubbed': True, 'GPU_calls': 0, 'model_queries': 0,
        'before_actual_worker_class': 'prime_rl.inference.vllm.worker.filesystem.FileSystemWeightUpdateWorker',
        'after_actual_worker_class': 'report_worker.ReportWorker'}
    study.write_x(study.ROOT / 'CPU_EVIDENCE_V2.json', evidence)
    closure = dict(original['closure_sha256'])
    paths = [study.ROOT / name for name in ('READY.json', 'engine_entry_v2.py', 'service_wrapper_v2.py',
        'study_v2.py', 'owner_v2.py', 'test_repair_v2.py', 'seal_v2.py', 'REPAIR_V2.md', 'CPU_EVIDENCE_V2.json')]
    paths += [failed / name for name in ('OWNER_TERMINAL.json', 'RESULT.json', 'RUNTIME.json',
        'service/service/inference.log', 'service/service/ENGINE_ENV_ATTESTATION.json', 'service/SERVICE_STOPPED.json')]
    prime = Path('/project/alex_phd/research-cache/repos/prime-rl/src/prime_rl')
    paths += [prime / name for name in ('inference/vllm/server.py', 'inference/server.py',
                                      'entrypoints/inference.py', 'utils/process.py')]
    for path in paths: closure[str(path)] = study.sha(path)
    value = {k: v for k, v in original.items() if k not in ('identity', 'created_epoch', 'closure_sha256')}
    value.update(schema='musique-task-directed-followup-ready-v2', created_epoch=time.time(),
        command=[str(study.NATIVE), str(study.ROOT / 'owner_v2.py'), 'run', '--outer-seconds', '1700'],
        output=str(study.ATTEMPT), source_V1_READY_sha256=study.sha(study.ROOT / 'READY.json'),
        repair='actual Prime filesystem registry, prospective dispatch checked after science',
        failed_attempt001_zero_science_calls=True, CPU_evidence_sha256=study.sha(study.ROOT / 'CPU_EVIDENCE_V2.json'),
        closure_sha256=closure)
    value['identity'] = study.digest(value)
    study.write_x(study.READY, value)
    assert study.verify() == value
    print({'READY_sha256': study.sha(study.READY), 'identity': value['identity'], 'pins': len(closure),
           'command': value['command'], 'test': test.stdout})


if __name__ == '__main__': main()
