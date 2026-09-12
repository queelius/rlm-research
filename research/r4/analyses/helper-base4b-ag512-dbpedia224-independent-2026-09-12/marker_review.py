"""Additive, CPU-only diagnosis; never changes the frozen owner qualification."""
import ast
import hashlib
import importlib.util
import json
import os
from pathlib import Path
from types import SimpleNamespace

ROOT = Path(__file__).resolve().parent
SIDE = ROOT.parents[1] / 'sidecars/helper-base4b-ag512-dbpedia224-eval-v1'
ATTEMPT = SIDE / 'outputs/attempt-002'
SITE = Path('/project/alex_phd/envs/prime-rl-5990b1b/lib/python3.12/site-packages')
VLLM = SITE / 'vllm'
OLD_LOG = SIDE.parent / 'root-qs6-fixed-helper-top20-batch-invariant-v1/outputs/attempt-003/service/service/inference.log'


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def read(path):
    return json.loads(Path(path).read_text())


def node(path, name, parent=None):
    tree = ast.parse(Path(path).read_text())
    body = tree.body if parent is None else next(n.body for n in tree.body if isinstance(n, ast.ClassDef) and n.name == parent)
    return next(n for n in body if isinstance(n, ast.FunctionDef) and n.name == name)


def compile_function(item, namespace):
    tree = ast.Module(body=[ast.ImportFrom(module='__future__', names=[ast.alias(name='annotations')], level=0), item], type_ignores=[])
    exec(compile(ast.fix_missing_locations(tree), '<actual-installed-source-extract>', 'exec'), namespace)
    return namespace[item.name]


def dispatch_fixture():
    """Execute the real dispatch/initialization bodies with CPU sentinels, not kernels."""
    env = SimpleNamespace(VLLM_BATCH_INVARIANT=True)
    events = []
    ns = {'envs': env, 'current_platform': SimpleNamespace(is_cuda_alike=lambda: True),
          'linear_batch_invariant': lambda *a: events.append('batch_invariant') or 'invariant',
          'dispatch_unquantized_gemm': lambda: lambda *a: events.append('ordinary') or 'ordinary'}
    fn = compile_function(node(VLLM / 'model_executor/layers/linear.py', 'apply', 'UnquantizedLinearMethod'), ns)
    assert fn(None, SimpleNamespace(weight='weight'), 'input') == 'invariant'
    env.VLLM_BATCH_INVARIANT = False
    assert fn(None, SimpleNamespace(weight='weight'), 'input') == 'ordinary'
    assert events == ['batch_invariant', 'ordinary']
    events.clear()
    fake_torch = SimpleNamespace(backends=SimpleNamespace(cuda=SimpleNamespace(matmul=SimpleNamespace()),
        cudnn=SimpleNamespace(conv=SimpleNamespace(), rnn=SimpleNamespace())))
    ns = {'envs': env, 'torch': fake_torch,
          'override_envs_for_invariance': lambda: events.append('override'),
          'enable_batch_invariant_mode': lambda: events.append('enable')}
    initialize = compile_function(node(VLLM / 'model_executor/layers/batch_invariant.py', 'init_batch_invariance'), ns)
    initialize(); assert events == []
    env.VLLM_BATCH_INVARIANT = True
    initialize(); assert events == ['override', 'enable']
    assert fake_torch.backends.cuda.matmul.fp32_precision == 'ieee'
    return {'actual_source_bodies_executed': ['UnquantizedLinearMethod.apply', 'init_batch_invariance'],
            'flag_on_and_off_branches_passed': True, 'GPU_executed': False,
            'scope': 'dispatch and initialization regression only; not retrospective device kernel telemetry'}


def execute():
    if os.environ.get('CUDA_VISIBLE_DEVICES') != '':
        raise ValueError('CPU hidden process required')
    fixture = dispatch_fixture()
    spec = importlib.util.spec_from_file_location('released_base_marker_review_source', ROOT / 'compare.py')
    comparison = importlib.util.module_from_spec(spec); spec.loader.exec_module(comparison)
    comparison.study.verify()
    start = comparison.owner.attest_start(ATTEMPT / 'service')
    terminal = read(ATTEMPT / 'OWNER_TERMINAL.json')
    original = read(ROOT / 'RESULT.json')
    assert terminal['complete'] is False and terminal['runtime_qualified'] is False
    assert terminal['errors'] == [{'message': 'actual batch-invariant kernel marker absent', 'stage': 'kernel_attestation', 'type': 'ValueError'}]
    assert terminal['attempted_calls'] == 184 and terminal['released'] is True
    stopped = read(ATTEMPT / 'service/SERVICE_STOPPED.json')
    assert stopped['all_owned_process_identities_exited'] and stopped['ports_free']
    log_path = ATTEMPT / 'service/service/inference.log'
    log = log_path.read_text()
    assert 'batch_invariant.py' not in log and 'matmul_persistent' not in log
    assert 'Enforce eager set, disabling torch.compile and CUDAGraphs' in log
    assert "'mode': <CompilationMode.NONE: 0>" in log
    previous = OLD_LOG.read_text()
    assert 'Dynamo detected a call' in previous and 'batch_invariant.py:141' in previous
    assert 'in matmul_persistent' in previous
    safe_lines = [line for line in log.splitlines() if 'api_key' not in line and
        ('Enforce eager set' in line or 'Inductor compilation was disabled' in line or
         'Kernel JIT monitor activated' in line)]
    kernel = node(VLLM / 'model_executor/layers/batch_invariant.py', 'matmul_persistent')
    assert not any(isinstance(n, ast.Name) and n.id in ('logger', 'print') for n in ast.walk(kernel))
    reviewed = [VLLM / p for p in ('envs.py', 'env_override.py', 'v1/engine/utils.py',
        'v1/executor/uniproc_executor.py', 'v1/worker/gpu_worker.py',
        'model_executor/layers/linear.py', 'model_executor/layers/batch_invariant.py', 'utils/jit_monitor.py')]
    accepted = read(SIDE / 'READY_V2.json')['closure_sha256']
    pins = {str(p): {'sha256': sha(p), 'mtime_ns': p.stat().st_mtime_ns,
                     'pinned_in_original_READY': str(p) in accepted} for p in reviewed}
    summary = {}
    for panel, value in original['panels'].items():
        assert value['inventory']['invalid_calls'] == 0
        assert value['inventory']['request_errors'] == 0
        assert value['inventory']['unattempted_calls'] == 0
        assert value['metrics']['unavailable_predictions'] == 0
        summary[panel] = {'correct': value['metrics']['correct'], 'available': value['metrics']['available_predictions'],
                          'planned': value['inventory']['expected_ids'], 'per_class': value['per_class'],
                          'cost': value['cost'], 'original_primary_accuracy': value['metrics']['primary_accuracy'],
                          'base_to_fixed_models': original['base_to_trained_comparisons'][panel]}
    provenance_files = [ROOT / 'RESULT.json', ROOT / 'WATCH_TERMINAL.json', SIDE / 'READY_V2.json',
        SIDE / 'owner.py', SIDE / 'service_base_batch_v2.py', OLD_LOG, log_path,
        ATTEMPT / 'OWNER_TERMINAL.json', ATTEMPT / 'RUNTIME.json', ATTEMPT / 'BINDING.json',
        ATTEMPT / 'service/service/ENGINE_ENV_ATTESTATION.json', ATTEMPT / 'service/service/SERVER_START.json',
        ATTEMPT / 'service/SERVICE_STOPPED.json', Path(__file__)]
    return {'schema': 'released-base-log-marker-diagnosis-v1', 'original_qualification_changed': False,
        'original_runtime_qualified': False, 'original_complete': False,
        'posthoc_evidence_class': 'source-and-preexec-environment-supported runtime; device-dispatch not directly recorded',
        'missing_log_marker_is_not_evidence_flag_off': True,
        'mandatory_kernel_log_exists_in_reviewed_matmul_function': False,
        'diagnosis': 'The old marker was a Dynamo lru_cache tracing warning. Eager execution disables that tracing path. A warmed Triton kernel also need not emit an inference JIT event; cache hit is plausible but not needed to explain the missing Dynamo warning.',
        'safe_actual_log_excerpts': safe_lines, 'preexec_attestation': start, 'CPU_fixture': fixture,
        'reviewed_source_receipts': pins,
        'source_limit': 'These installed vLLM files were inspected/hash-pinned after the run, not included in its original READY closure. Source-path reasoning and inherited preexec environment strongly support activation but do not replace missing in-worker dispatch telemetry.',
        'empirical_repeatability_limit': 'No no-LoRA eager batch-invariance equivalence experiment was run. The compiled LoRA probe does not establish bitwise invariance for this configuration.',
        'readout_scope': 'All 184 calls/736 labels are available and independently raw-redecoded. Present as an additive exploratory true-base reference with explicit logging-gate deviation; not the unchanged frozen primary.',
        'panels': summary, 'owner_elapsed_seconds': terminal['elapsed_seconds'],
        'future_gate': 'Before a new run, replace optional-warning qualification with explicit in-worker state and first real dispatch receipt, retaining preexec/binding/source/clean-release checks. Do not require another warning or claim a CPU sentinel is device evidence.',
        'provenance': {str(p): sha(p) for p in provenance_files}}


if __name__ == '__main__':
    value = execute()
    destination = ROOT / 'RUNTIME_MARKER_ADDENDUM.json'
    with destination.open('x') as stream:
        json.dump(value, stream, indent=2, sort_keys=True); stream.write('\n')
    print(json.dumps({'path': str(destination), 'sha256': sha(destination), 'CPU_fixture': value['CPU_fixture']}))
