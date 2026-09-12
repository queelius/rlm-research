"""CPU-only source/input seal after two focused actual-seam fixtures."""
import importlib.metadata
import os
import subprocess
import sys
import time

import study


def main():
    assert os.environ.get('CUDA_VISIBLE_DEVICES') == ''
    assert not study.ATTEMPT.exists() and not (study.ROOT / 'READY.json').exists()
    assert len(study.selected()) == 12 and len(study.schedule()) == 132
    base_ready = study.base_owner().study.verify()
    # Pin the genuine runtime implementation prospectively, including the paths
    # missing from the inherited reference's original source closure.
    site = study.NATIVE.parent.parent / 'lib/python3.12/site-packages'
    runtime = [site / 'vllm' / p for p in ('envs.py', 'env_override.py', 'v1/engine/utils.py',
        'v1/executor/uniproc_executor.py', 'v1/worker/gpu_worker.py', 'v1/worker/worker_base.py',
        'model_executor/layers/batch_invariant.py', 'model_executor/layers/linear.py', 'utils/jit_monitor.py')]
    runtime += [study.STORE.parent.parent / 'research-cache/repos/prime-rl/src/prime_rl/inference/vllm/worker/filesystem.py']
    argv = [str(study.NATIVE), '-m', 'pytest', '-q', 'test_screen.py']
    started = time.time()
    test = subprocess.run(argv, cwd=study.ROOT, capture_output=True, text=True, timeout=90)
    assert test.returncode == 0, test.stdout + test.stderr
    evidence = {'argv': argv, 'returncode': test.returncode, 'stdout': test.stdout, 'stderr': test.stderr,
        'elapsed_seconds': time.time() - started, 'python': sys.version,
        'versions': {name: importlib.metadata.version(name) for name in ('torch', 'vllm', 'transformers', 'tokenizers', 'pytest')},
        'CUDA_VISIBLE_DEVICES': '', 'model_queries': 0, 'GPU_launches': 0,
        'actual_11_call_graph_with_synthetic_responses': True,
        'actual_tokenizer_schema_official_scoring_and_missingness': True,
        'actual_native_launcher_configuration_but_no_process_execution': True,
        'CPU_instrumentation_fixture_is_not_real_dispatch_qualification': True}
    study.write_x(study.ROOT / 'CPU_EVIDENCE.json', evidence)
    closure = dict(base_ready['closure_sha256'])
    paths = list(study.ROOT.glob('*.py')) + [study.ROOT / n for n in ('PLAN.md', 'QUESTION.md', 'RUNBOOK.md', 'CPU_EVIDENCE.json')]
    paths += [p for p in study.INPUTS.rglob('*') if p.is_file()]
    paths += runtime + [study.BASE / 'READY_V2.json', study.ARCHIVE,
        study.STORE / 'ideas/2026-09-12-task-directed-report-followup.md',
        study.PRIOR / 'musique_study.py', study.PRIOR / 'scoring.py', study.PRIOR / 'inputs/MANIFEST.json',
        study.PRIOR / 'inputs/host/HOST_GOLD.json']
    paths += [study.REPO / 'metrics' / n for n in ('answer.py', 'support.py', 'metric.py', '__init__.py')]
    for path in paths:
        assert path.is_file(), str(path)
        closure[str(path)] = study.sha(path)
    ready = {'schema': 'musique-task-directed-followup-ready-v1', 'created_epoch': time.time(),
        'GPU_launch_authority': 'MAIN only', 'command': [str(study.NATIVE), str(study.ROOT / 'owner.py'), 'run', '--outer-seconds', '1700'],
        'output': str(study.ATTEMPT), 'owner_seconds': 1700, 'science_seconds': 1320, 'external_seconds': 1800,
        'selected_questions': 12, 'hops': {'2': 4, '3': 4, '4': 4}, 'physical_calls': 132,
        'terminal_slots': 48, 'policy_calls_per_question': {'stop': 4, 'broad': 6, 'targeted': 6, 'full_source': 1},
        'temperature': .5, 'ordinary_report_max_tokens': 512, 'planner_max_tokens': 256, 'final_max_tokens': 1024,
        'max_actual_prefix_plus_requested_output': 8192, 'max_concurrent_question_workers': 4,
        'frozen_static_max_prefix_plus_output': max(i['static_max_prefix_plus_output'] for i in study.selected()),
        'optimizer_steps': 0, 'model_path': str(study.MODEL), 'adapter': None,
        'source_base_READY_V2_sha256': study.sha(study.BASE / 'READY_V2.json'),
        'runtime_qualification': 'actual first original CUDA matmul dispatch plus flag/mode/source/PID/environment/binding/release; no optional warning gate',
        'schedule_sha256': study.digest(study.schedule()), 'manifest_sha256': study.sha(study.INPUTS / 'MANIFEST.json'),
        'CPU_evidence_sha256': study.sha(study.ROOT / 'CPU_EVIDENCE.json'), 'closure_sha256': closure}
    ready['identity'] = study.digest(ready)
    study.write_x(study.ROOT / 'READY.json', ready)
    assert study.verify() == ready
    print({'READY_sha256': study.sha(study.ROOT / 'READY.json'), 'identity': ready['identity'],
           'pins': len(closure), 'test': test.stdout, 'command': ready['command']})


if __name__ == '__main__': main()
