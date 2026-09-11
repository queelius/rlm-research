"""One-time CPU verification and immutable exploratory-spec/READY publication."""
import datetime
import hashlib
import importlib.metadata
import json
import os
import subprocess
import sys
from pathlib import Path

import driver
import overlay
import study

ROOT = study.ROOT


def seal():
    if (ROOT / 'SPEC.json').exists() or (ROOT / 'READY.json').exists():
        raise ValueError('this preparation is already sealed; use an additive future version')
    now = datetime.datetime.now(datetime.timezone.utc).isoformat()
    public = study.read(ROOT / 'inputs/PUBLIC.json')
    tasks = study.read(ROOT / 'inputs/tasks-system-contract-v2.json')
    if tasks != study.system_contract_tasks(study.read(ROOT / 'inputs/tasks.json')):
        raise ValueError('common prompt amendment changed any original task content')
    for row in public['cases']:
        if study.file_hash(ROOT / 'inputs/contexts' / (row['document_sha256'] + '.txt')) != row['document_sha256']:
            raise ValueError('public document changed')
    if len(tasks) != 6 or [row['seed'] for row in public['cases']] != list(range(981269100, 981269106)):
        raise ValueError('frozen six-document/seed plan changed')
    _, converted = study.native_helpers()
    proof = converted.verify_conversion()
    if proof['tensor_count'] != 504 or not proof['all_values_shapes_dtypes_and_bytes_equal']:
        raise ValueError('exact original adapter conversion proof failed')
    env = {**os.environ, 'CUDA_VISIBLE_DEVICES': '', 'PYTHONDONTWRITEBYTECODE': '1'}
    tests = [str(ROOT / name) for name in ('test_transport.py', 'test_pair.py', 'test_study.py')]
    result = subprocess.run([sys.executable, '-m', 'pytest', '-q', *tests],
                            capture_output=True, text=True, timeout=90, env=env)
    test_result = {'command': [sys.executable, '-m', 'pytest', '-q', *tests],
        'returncode': result.returncode, 'stdout': result.stdout, 'stderr': result.stderr,
        'gpu_calls': 0, 'created_utc': now}
    study.write_once(ROOT / 'qualification/UNIT_TESTS.json', test_result)
    if result.returncode:
        raise ValueError('focused tests failed: ' + result.stdout + result.stderr)
    native = study.read(ROOT / 'qualification/native-final-attempt-001/RESULT.json')
    repl = study.read(ROOT / 'qualification/repl-green-final-001/RESULT.json')
    if repl['exit_code'] or len(json.loads(repl['stdout'])['cases']) != 11:
        raise ValueError('real REPL qualification failed')
    expected_overlay = {'engine_sha256': hashlib.sha256(overlay.patched_engine(overlay.NANO_ENGINE.read_text()).encode()).hexdigest(),
                        'module_sha256': study.file_hash(ROOT / 'submission.py')}
    if (native['physical_provider_calls'] != 6 or native['shared_prefix_calls'] != 5
            or not native['prefix_and_restatement_byte_fidelity'] or native['gpu_calls'] != 0
            or any(native['executed_overlay'][key] != value for key, value in expected_overlay.items())):
        raise ValueError('final native proof is not the current executed overlay')
    git_blobs = {'src__rlm__tools__base.py': '295d6ff790498982f8eb6b987f0fc4a47682fe54',
        'src__rlm__tools__ipython.py': 'cc7ff13a57cb2e8e33f8aa5fd754c563b3b13213',
        'src__rlm__tools__registry.py': '1f1a47e3a1b05b5e74aae05896630f9039514dff'}
    acquired = []
    for name, expected in git_blobs.items():
        path = ROOT / 'inputs/upstream' / name
        data = path.read_bytes()
        actual = hashlib.sha1(b'blob ' + str(len(data)).encode() + b'\0' + data).hexdigest()
        if actual != expected:
            raise ValueError('acquired source differs from pinned official Git blob: ' + name)
        acquired.append({'path': str(path), 'sha256': study.file_hash(path), 'git_blob_sha1': actual,
            'url': 'https://raw.githubusercontent.com/PrimeIntellect-ai/nano-rlm/4ef3438d55fdd39b18d34035833c73e13b006733/' + name.replace('__', '/')})
    study.write_once(ROOT / 'inputs/ACQUISITION.json', {
        'created_utc': now, 'nano_revision': '4ef3438d55fdd39b18d34035833c73e13b006733',
        'retrieved_utc_date': '2026-09-09', 'license': 'MIT', 'files': acquired,
        'mrcr': {'source_repository': 'https://github.com/google-deepmind/eval_hub',
            'revision': '67b7fd29b2205ee0a3226e0d3e5d74140a253b42',
            'download_base': 'https://storage.googleapis.com/mrcr_v2',
            'cache_manifest': '/project/alex_phd/research-cache/datasets/mrcr_v2/manifest.json',
            'repository_license': 'Apache-2.0',
            'dataset_specific_license': 'No separate license statement established by this bounded cached-source inspection.',
            'data_role': 'same six previously used short-context development documents; no heldout/novelty claim'},
        'pre_system_amendment': {'original_tasks_preserved': True,
            'source_directory': str(ROOT / 'inputs/pre-system-contract-v1'),
            'source_copy_method': 'Reconstructed exactly by reversing the recorded task-system-only patch before further changes; hashes first sealed now.',
            'no_gpu_outcomes_used': True}})
    if driver.image_identity() != study.IMAGE_SHA:
        raise ValueError('qualified rootless image changed')
    versions = {}
    for name in ('openai', 'httpx', 'transformers', 'torch', 'verifiers', 'renderers'):
        try:
            versions[name] = importlib.metadata.version(name)
        except importlib.metadata.PackageNotFoundError:
            versions[name] = 'editable source identity pinned in source_sha256'
    spec = {'schema': 'mrcr-computed-commit-six-exploratory-v1', 'created_utc': now,
        'question': 'Does exact computed-string commitment avoid distortion/cost caused by one native final restatement?',
        'data_plan': public, 'data_split': 'six already-used MRCR short development documents; evaluation only',
        'environment': driver.environment_config(),
        'sampling': {'temperature': 0.0, 'top_p': 1.0, 'top_k': -1, 'min_p': 0.0,
                     'max_tokens': 2048, 'native_renderer': {'name': 'qwen3', 'enable_thinking': True}},
        'budget': {'prefix_calls_including_children': 5, 'restatement_calls': 1,
            'maximum_native_calls': 36, 'episode_seconds': 200, 'global_seconds': 1200,
            'cleanup_may_add_grace': True, 'retries_both_sdk_hops_and_episode': 0,
            'terminal_utf8_bytes': public['terminal_byte_cap']},
        'pair': {'one_actual_shared_prefix': True, 'candidate_persisted_before_final': True,
            'candidate_requires_successful_cell_and_one_plain_str': True, 'no_gold_or_stdout_repair': True,
            'primary': 'candidate-to-final byte fidelity plus paired official raw similarity and raw/strict byte-exact correctness',
            'secondary': 'non-submission, invalid/oversize/exception submissions, final budget/tool/truncation/transport outcomes',
            'metrics_preserved_under_budget_failure': True,
            'canonical_candidate_tokenization': 'diagnostic only, not native action evidence or minimum possible encoding proof'},
        'endpoint_binding': {'allowed_alias': converted.ALIAS, 'original_prime_sha256': converted.ORIGINAL_SHA,
            'converted_adapter_sha256': converted.CONVERTED_SHA, 'config_sha256': converted.CONFIG_SHA,
            'conversion_manifest_sha256': converted.MANIFEST_SHA, 'role_binding_sha256': converted.BOUND_SHA,
            'fresh_504_tensor_cpu_proof_before_calls': True, 'actual_descriptor_and_live_models_required': True,
            'live_memory_attestation': False},
        'runtime': {'image': study.IMAGE, 'image_sha256': study.IMAGE_SHA,
            'executed_overlay': expected_overlay, 'python': sys.version, 'executable': sys.executable,
            'package_versions': versions, 'generated_code_host_execution': False,
            'filesystem_boundary': 'one authenticated read-only /context.txt; host gold absent',
            'network_boundary': 'inherited host networking, not a network sandbox'},
        'qualification_sha256': {str(path): study.file_hash(path) for path in
                                sorted((ROOT / 'qualification').rglob('*.json'))},
        'source_sha256': driver.sources(),
        'checkpoint_policy': 'immutable per-coordinate native traces/pair/candidate/score; no automatic retry or resume',
        'review': 'Parent read driver, overlay, submission, study, plugin and design; required common system suffix and budget classification included.'}
    spec['spec_id'] = study.digest(spec)
    study.write_once(ROOT / 'SPEC.json', spec)
    driver.verify()
    for path in [ROOT / 'SPEC.json', *ROOT.glob('*.py'), *ROOT.glob('*.md'),
                 *ROOT.joinpath('inputs').rglob('*')]:
        if path.is_file():
            path.chmod(0o400 if path.name == 'HOST_GOLD.json' else 0o444)
    ready = {'status': 'READY_PARENT_ENDPOINT_REQUIRED', 'spec_id': spec['spec_id'],
        'spec_sha256': study.file_hash(ROOT / 'SPEC.json'), 'created_utc': now,
        'focused_tests': 17, 'real_repl_cases': 11, 'real_native_full_budget_calls': 6,
        'gpu_or_model_calls_during_preparation': 0, 'parent_owns_gpu_and_service': True,
        'entrypoint': str(ROOT / 'driver.py'), 'runbook': str(ROOT / 'RUNBOOK.md'),
        'default_new_output': str(ROOT / 'outputs/attempt-001'),
        'required_launch_argument': '--endpoint ACTUAL_ASSIGNED_ORIGINAL_ENDPOINT_JSON'}
    study.write_once(ROOT / 'READY.json', ready)
    (ROOT / 'READY.json').chmod(0o444)
    print(json.dumps(ready), flush=True)


if __name__ == '__main__':
    seal()
