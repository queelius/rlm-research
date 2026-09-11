"""Prepare/verify/run the six shared-prefix pairs; never starts an inference server."""
from __future__ import annotations

import argparse
import asyncio
import copy
import hashlib
import json
import os
import subprocess
import time
from pathlib import Path
from typing import Any

import mrcr_computed_commit_v1 as plugin
from study import ROOT, OLD, DIRECT, IMAGE, IMAGE_SHA, read, file_hash, digest, write_once
import study


def environment_config():
    source = read(OLD / 'outputs/attempt-001/SPEC.json')['environment']
    config = copy.deepcopy(source)
    config['taskset'] = {'id': ROOT.name, 'tasks_file': str(ROOT / 'inputs/tasks-system-contract-v2.json')}
    config['agent']['harness']['id'] = ROOT.name
    config['agent']['max_turns'] = 6
    config['timeout']['episode'] = 200
    config['agent']['timeout']['rollout'] = 170
    config['agent']['timeout']['setup'] = 90
    return config


def prepare():
    public = study.prepare_inputs()
    tasks = [study.old.MRCRData(idx=row['index'], name=row['task_name'],
        prompt=study.task_prompt(row, public['terminal_byte_cap']), row_id=row['row_id'],
        document_sha256=row['document_sha256'], arm='shared_computation').model_dump(mode='json')
        for row in public['cases']]
    write_once(ROOT / 'inputs/tasks.json', tasks)
    print(json.dumps({'cases': len(tasks), 'terminal_byte_cap': public['terminal_byte_cap'],
                      'context_utf8_bytes': public['context_utf8_bytes'], 'gold_in_task_data': False}))


def prepare_system_contract():
    original = read(ROOT / 'inputs/tasks.json')
    write_once(ROOT / 'inputs/tasks-system-contract-v2.json', study.system_contract_tasks(original))
    print(json.dumps({'task_count': len(original), 'original_task_sha256': file_hash(ROOT / 'inputs/tasks.json'),
        'amendment': 'explicit existing TaskData.system_prompt suffix; same question/context/seed and both branches'}))


def sources():
    import renderers
    import verifiers.v1 as vf
    import overlay
    paths = [*ROOT.glob('*.py'), ROOT / 'bin/docker', *ROOT.glob('*.md'),
        *ROOT.joinpath('inputs').rglob('*'),
        overlay.NANO_ENGINE,
        Path('/project/alex_phd/research-cache/2026-09-08-literature/recursive-example.6xBrmx/src__rlm__client.py'),
        Path('/project/alex_phd/research-cache/2026-09-08-literature/recursive-example.6xBrmx/src__rlm__semantic.py'),
        Path('/project/alex_phd/research-cache/datasets/mrcr_v2/manifest.json'),
        Path('/project/alex_phd/research-cache/datasets/mrcr_v2/mrcr_v2p1_2needle_in_(4096,8192)_dynamic_fewshot_text_style_fast.csv'),
        Path('/project/alex_phd/research-cache/repos/eval_hub/eval_hub/mrcr_v2/run_evaluation.py'),
        Path('/project/alex_phd/research-cache/repos/eval_hub/eval_hub/mrcr_v2/README.md'),
        Path('/project/alex_phd/research-cache/repos/eval_hub/LICENSE'),
        OLD / 'source/mrcr_rootless_document_baseline_v2.py', OLD / 'source/boundary.py',
        DIRECT / 'driver.py', DIRECT / 'driver_converted.py', DIRECT / 'CONVERSION_PROOF.json', DIRECT / 'SPEC.json',
        ROOT.parent / 'rootless-runtime-feasibility-v1/bin/docker',
        ROOT.parent / 'rootless-runtime-feasibility-v1/bin/crun-isolated',
        ROOT.parent / 'rootless-runtime-feasibility-v1/config/containers.conf',
        ROOT.parent / 'rootless-runtime-feasibility-v1/config/registries.conf']
    paths += list(Path(vf.__file__).parent.rglob('*.py')) + list(Path(renderers.__file__).parent.rglob('*.py'))
    paths += [Path(study.old.OLD / 'source/mrcr_context_sketch' / name) for name in
              ('__init__.py', 'data.py', 'canonical.py', 'provenance.py', 'scoring.py', 'sketch.py')]
    return {str(p): file_hash(p) for p in sorted(set(paths)) if p.is_file()}


def image_identity():
    docker = ROOT.parent / 'rootless-runtime-feasibility-v1/bin/docker'
    result = subprocess.run([str(docker), 'image', 'inspect', IMAGE, '--format', '{{.Id}}'],
        check=True, text=True, capture_output=True, timeout=30)
    return result.stdout.strip().removeprefix('sha256:')


def verify():
    spec = read(ROOT / 'SPEC.json')
    if digest({k: v for k, v in spec.items() if k != 'spec_id'}) != spec['spec_id']:
        raise ValueError('spec changed')
    for path, expected in spec['source_sha256'].items():
        if file_hash(path) != expected:
            raise ValueError('source/input changed: ' + path)
    if image_identity() != IMAGE_SHA:
        raise ValueError('runtime image identity changed')
    return spec


async def authenticate(endpoint_path):
    native, converted = study.native_helpers()
    proof = converted.verify_conversion()
    endpoint = read(endpoint_path)
    if endpoint.get('status', '').startswith('planned'):
        raise ValueError('actual endpoint descriptor required')
    converted.validate_converted_binding(endpoint, read(DIRECT / 'SPEC.json')['original_identity'])
    if file_hash(Path(endpoint['base_model']['path']) / 'local-research-manifest.json') != endpoint['base_model']['manifest_sha256']:
        raise ValueError('base manifest changed')
    if not os.environ.get(endpoint['api_key_env']):
        raise ValueError('assigned endpoint API-key environment variable missing')
    client = native.make_client(endpoint)
    client.client.max_retries = 0
    try:
        advertised = await asyncio.wait_for(client.client.get('/models', cast_to=dict[str, Any]), 15)
        card = {row['id']: row for row in advertised['data']}.get(endpoint['model_alias'], {})
        if Path(card.get('root', '')).resolve() != Path(endpoint['adapter']['path']).resolve() or card.get('parent') != endpoint['base_model']['path']:
            raise ValueError('live alias/root/parent does not match exact original adapter')
        observed_limit = card.get('max_model_len')
        if observed_limit is not None and (type(observed_limit) is not int or observed_limit <= 0):
            raise ValueError('invalid advertised model context limit')
    finally:
        await client.client.close()
    endpoint = {**endpoint, 'observed_max_model_len': observed_limit}
    return endpoint, {'endpoint': endpoint, 'endpoint_file_sha256': file_hash(endpoint_path),
        'conversion_proof_sha256': digest(proof), 'advertised': advertised,
        'scope': 'Disk tensor identity + actual launch descriptor and live alias/root/parent; no live-memory attestation.'}


def context(endpoint, case):
    from renderers import Qwen3RendererConfig
    from verifiers.v1.clients import ModelContext
    from verifiers.v1.configs.client import TrainClientConfig
    from verifiers.v1.types import SamplingConfig
    return ModelContext(model=endpoint['model_alias'], client=TrainClientConfig(
        base_url=endpoint['url'], api_key_var=endpoint['api_key_env'],
        renderer=Qwen3RendererConfig(enable_thinking=True), renderer_model_name=endpoint['base_model']['path']),
        sampling=SamplingConfig.model_validate({'temperature': 0.0, 'top_p': 1.0, 'seed': case['seed'],
        'max_tokens': 2048, 'extra_body': {'top_k': -1, 'min_p': 0.0, 'return_token_ids': True, 'cache_salt': '0'}}))


async def run_case(environment, task, endpoint, case, output, timeout):
    from verifiers.v1.env import RunSlot
    os.environ['MRCR_SUBMIT_CONTEXT'] = str(ROOT / 'inputs/contexts' / (case['document_sha256'] + '.txt'))
    slot = RunSlot(task)
    started = time.time()
    with study.native_capture(output / 'wire', endpoint['model_alias'], endpoint.get('observed_max_model_len')) as calls:
        try:
            episode = await asyncio.wait_for(environment.run_slot(slot, context(endpoint, case)), timeout)
            raw = episode.to_record()
        except BaseException as error:
            raw = {'ok': False, 'errors': [{'type': type(error).__name__, 'message': str(error)}],
                   'traces': [trace.to_record() for trace in slot.traces]}
    captures = [plugin.CAPTURES.pop(trace['id']) for trace in raw.get('traces', []) if trace.get('id') in plugin.CAPTURES]
    if len(captures) > 1:
        raise ValueError('multiple independent root capture artifacts')
    captured = captures[0] if captures else None
    pair = captured['pair'] if captured else None
    if pair is not None:
        accepted = [row for row in captured['submissions'] if row['accepted']]
        if len(accepted) != 1 or accepted[0] != pair['submission']:
            raise ValueError('pair not bound to exactly one successful cell submission')
        candidate = pair['candidate'].encode('utf-8')
        if hashlib.sha256(candidate).hexdigest() != pair['candidate_sha256']:
            raise ValueError('candidate bytes changed')
        finals = [row for row in calls if row['phase'] == 'restatement']
        if len(finals) != 1:
            raise ValueError('accepted pair lacks exactly one restatement attempt')
        if pair['restatement'].get('request_messages') != finals[0]['request']['messages']:
            raise ValueError('restatement report/actual request mismatch')
    row = {'case': case, 'episode': raw, 'captured': captured, 'calls': calls,
           'accounting': study.cost_summary(calls),
           'started': started, 'ended': time.time()}
    write_once(output / 'EPISODE.json', row)
    return row


async def run(endpoint_path, output):
    from verifiers.v1.envs.single_agent import SingleAgentEnv, SingleAgentEnvConfig
    spec = verify()
    endpoint, binding = await authenticate(endpoint_path)
    if output.parent != ROOT / 'outputs':
        raise ValueError('run output must be owned by this sidecar')
    output.mkdir(parents=True, exist_ok=False)
    write_once(output / 'BINDING.json', binding)
    write_once(output / 'SPEC.json', spec)
    os.environ['PATH'] = str(ROOT / 'bin') + os.pathsep + os.environ.get('PATH', '')
    os.environ.setdefault('VERIFIERS_CACHE_DIR', '/project/alex_phd/cache/verifiers-prime')
    environment = SingleAgentEnv(SingleAgentEnvConfig.model_validate(spec['environment']))
    tasks = {task.data.name: task for task in environment.taskset}
    public, gold = read(ROOT / 'inputs/PUBLIC.json'), read(ROOT / 'inputs/HOST_GOLD.json')
    results, started = [], time.monotonic()
    async with environment.serving():
        for case in public['cases']:
            remaining = 1200 - (time.monotonic() - started)
            if remaining <= 0:
                break
            row = await run_case(environment, tasks[case['task_name']], endpoint, case,
                                 output / f"case-{case['index']}", min(200, remaining))
            pair = (row.get('captured') or {}).get('pair')
            scored = {'case': case, **study.score_pair(pair, gold[case['row_id']]),
                'restatement_outcome': study.classify_restatement(pair, row['calls']),
                'accounting': row['accounting'],
                'submission_outcomes': [item['reason'] for item in (row.get('captured') or {}).get('submissions', [])],
                'native_finish_reasons': [call.get('finish_reason') for call in row['calls']],
                'native_errors': [{key: call.get(key) for key in ('phase', 'error_type', 'error')}
                                  for call in row['calls'] if call['status'] == 'error']}
            write_once(output / f"case-{case['index']}" / 'SCORE.json', scored)
            results.append(scored)
    write_once(output / 'RESULT.json', {'schema': 'computed-commit-six-v1', 'spec_id': spec['spec_id'],
        'planned': 6, 'completed_coordinates': len(results), 'results': results,
        'wall_seconds': time.monotonic() - started, 'gpu_service_started_by_driver': False})


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('command', choices=['prepare', 'prepare-system-contract', 'verify', 'run'])
    parser.add_argument('--endpoint', type=Path)
    parser.add_argument('--output', type=Path, default=ROOT / 'outputs/attempt-001')
    args = parser.parse_args()
    if args.command == 'prepare':
        prepare()
    elif args.command == 'prepare-system-contract':
        prepare_system_contract()
    elif args.command == 'verify':
        print(json.dumps({'verified': verify()['spec_id']}))
    else:
        if args.endpoint is None:
            parser.error('--endpoint is required for run')
        asyncio.run(run(args.endpoint.resolve(), args.output.resolve()))


if __name__ == '__main__':
    main()
