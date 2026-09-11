"""CPU preparation and parent-launched600-call collection; no GPU/service ownership."""
from __future__ import annotations

import argparse
import asyncio
import hashlib
import importlib.metadata
import json
import os
import subprocess
import sys
import time
from copy import deepcopy
from pathlib import Path

import httpx
import study as s

ROOT = s.ROOT


def typed_prompt_ids(tokenizer, body):
    from vllm.entrypoints.openai.chat_completion.protocol import ChatCompletionRequest
    # Pydantic inserts tool_choice=auto into its input: never pass the frozen object.
    parsed = ChatCompletionRequest.model_validate(deepcopy(body))
    return tokenizer.apply_chat_template(body['messages'], tools=[t.model_dump() for t in parsed.tools],
        add_generation_prompt=True, tokenize=True, return_dict=False)


def wire_hook(spec, output):
    by_hash = {h: key for key, h in spec['request_sha256'].items()}
    if len(by_hash) != len(spec['request_sha256']):
        raise ValueError('duplicate physical request coordinate')

    async def capture(request):
        if request.method != 'POST' or not request.url.path.endswith('/chat/completions'):
            return
        decoded = json.loads(request.content)
        key = by_hash[s.digest(decoded)]
        expected = s.serialize(spec['requests'][key]).encode()
        if request.content != expected:
            raise ValueError('actual serialized request differs from frozen field ordering')
        s.write_once(output / 'wire' / (key + '.json'), {'coordinate_id': key,
            'method': request.method, 'route': request.url.path, 'body_utf8': request.content.decode(),
            'body_sha256': hashlib.sha256(request.content).hexdigest(), 'credentials_recorded': False})
    return capture


def qualify(value, requests):
    from transformers import AutoTokenizer
    import xgrammar as xgr
    hf = AutoTokenizer.from_pretrained(str(s.corr.BASE), local_files_only=True, trust_remote_code=False)
    compiler = xgr.GrammarCompiler(xgr.TokenizerInfo.from_huggingface(hf), max_threads=1)
    seen, prompts = set(), {}
    for key, body in requests.items():
        before = s.serialize(body)
        ids = typed_prompt_ids(hf, body)
        raw = hf.apply_chat_template(body['messages'], tools=body['tools'],
            add_generation_prompt=True, tokenize=True, return_dict=False)
        if not isinstance(ids, list) or not ids or any(type(i) is not int for i in ids):
            raise ValueError('non-flat typed physical prompt')
        if len(ids) + body['max_tokens'] > 8192:
            raise ValueError('typed prompt plus common cap exceeds8192')
        schema = body['structured_outputs']['json']
        schema_key = s.serialize(schema)
        if schema_key not in seen:
            compiler.compile_json_schema(schema_key)
            seen.add(schema_key)
        if s.serialize(body) != before:
            raise ValueError('qualification mutated physical request')
        prompts[key] = {'tokens': len(ids), 'typed_token_ids_sha256': s.digest(ids),
            'raw_dict_token_ids_sha256': s.digest(raw), 'physical_source': 'vLLM typed tool.model_dump() then pinned HF chat template'}
    return {'requests': len(prompts), 'schemas_compiled': len(seen), 'rendered_prompts': prompts,
        'max_prompt_tokens': max(p['tokens'] for p in prompts.values()),
        'versions': {k: importlib.metadata.version(k) for k in ['vllm', 'transformers', 'tokenizers', 'httpx', 'xgrammar', 'pyarrow']},
        'model_calls': 0, 'gpu_calls': 0}


def verify(spec):
    if s.digest({k: v for k, v in spec.items() if k != 'spec_id'}) != spec['spec_id']:
        raise ValueError('outer spec identity changed')
    for path, expected in spec['source_sha256'].items():
        if s.file_hash(path) != expected:
            raise ValueError('source/data identity changed: ' + path)
    expected = s.build_design(s.read(ROOT / 'DATA.json'))
    expected['rendered_prompts'] = spec['cpu_qualification']['rendered_prompts']
    if 'endpoint_binding' in spec:
        binding = spec['endpoint_binding']
        if s.file_hash(binding['path']) != binding['sha256'] or s.read(binding['path']) != binding['descriptor']:
            raise ValueError('endpoint descriptor changed')
        s.corr.validate_endpoint(binding['descriptor'])
        expected['model_alias'] = binding['descriptor']['model_alias']
    if expected != spec['design']:
        raise ValueError('frozen data/order/coordinate design changed')
    if len(spec['requests']) != 600:
        raise ValueError('requires600 exact requests')
    for row in expected['plan']:
        body = s.make_request(expected, row)
        if (s.serialize(body) != s.serialize(spec['requests'][row['id']])
                or s.digest(body) != spec['request_sha256'][row['id']]):
            raise ValueError('frozen body or field ordering changed')


def prepare():
    if (ROOT / 'SPEC.json').exists() or (ROOT / 'READY.json').exists():
        raise ValueError('already frozen; additive attempt only')
    seeds = subprocess.run(['rg', '-n', r'\b(910883|910901|910907)\b', str(s.SIDE),
        '-g', '*SPEC*.json', '-g', '*READY*.json', '-g', '*RECIPE*.json', '-g', '*PLAN*.json',
        '-g', '!**/leaf-correspondence-anchor-transfer-v1/**', '-g', '!**/outputs/**',
        '-g', '!**/inputs/**', '-g', '!**/exports/**'], capture_output=True, text=True, timeout=30)
    if seeds.returncode != 1 or seeds.stdout:
        raise ValueError('existing ready seed namespace collision or unavailable audit: ' + seeds.stdout[:1200])
    s.write_once(ROOT / 'SEED_AUDIT.json', {'args': seeds.args, 'exit_code': seeds.returncode, 'matches': seeds.stdout,
        'sampling': s.SEEDS, 'permutation_master': s.PERMUTATION_MASTER,
        'scope': 'Existing non-output sidecar specs/ready/recipes/plans; not exhaustive every prior token/log. Dossier N1 prospectively assigned sampling seeds.'})
    data = s.load_data()
    s.write_once(ROOT / 'DATA.json', data)
    value = s.build_design(data)
    requests = {r['id']: s.make_request(value, r) for r in value['plan']}
    qualified = qualify(value, requests)
    value['rendered_prompts'] = qualified['rendered_prompts']
    s.write_once(ROOT / 'CPU_QUALIFICATION.json', qualified)
    s.write_once(ROOT / 'REQUESTS.json', requests)
    tests = subprocess.run([sys.executable, '-m', 'pytest', '-q', '-p', 'no:cacheprovider', str(ROOT / 'test_study.py')],
        capture_output=True, text=True, timeout=90, env={**os.environ, 'CUDA_VISIBLE_DEVICES': '', 'PYTHONDONTWRITEBYTECODE': '1'})
    s.write_once(ROOT / 'CPU_TESTS.json', {'returncode': tests.returncode, 'stdout': tests.stdout, 'stderr': tests.stderr,
        'gpu_calls': 0, 'real_model_calls': 0, 'fake_provider_calls': 2})
    if tests.returncode:
        raise ValueError('focused tests failed: ' + tests.stdout[-2000:])
    upstream = s.read(s.SIDE / 'leaf-correspondence-controls-v1/SPEC-REPRESENTATION.runtime-order-v2.json')
    sources = dict(upstream['source_file_sha256'])
    sources.update(s.read(s.SST.parent / 'SPEC.json')['source_sha256'])
    trec_manifest = s.read(s.TREC_DATA.parent / 'MANIFEST.json')
    sources.update(trec_manifest['source_sha256'])
    trec_inventory = s.read(s.SIDE / 'trec-leaf-split-provenance-v1/INVENTORY.json')
    for path, sha in trec_inventory['source_file_sha256'].items():
        if '/trec-leaf-splits.' in path or path.endswith('/trec_hf_metadata.json'):
            sources[path] = sha
    import vllm
    vllm_root = Path(vllm.__file__).parent
    paths = [*ROOT.glob('*.py'), *ROOT.glob('*.md'), ROOT / 'DATA.json', ROOT / 'SEED_AUDIT.json',
        ROOT / 'REQUESTS.json', ROOT / 'CPU_QUALIFICATION.json', ROOT / 'CPU_TESTS.json', s.CORR, s.SST,
        s.TREC_DATA, s.TREC_DATA.parent / 'MANIFEST.json',
        s.SIDE.parents[0] / 'analyses/cross-experiment-synthesis-2026-09-09/NEXT_EXPERIMENTS.md',
        vllm_root / 'renderers/online_renderer.py', vllm_root / 'entrypoints/openai/chat_completion/protocol.py',
        vllm_root / 'entrypoints/openai/engine/protocol.py']
    sources.update({str(p): s.file_hash(p) for p in paths})
    spec = {'schema': ROOT.name, 'design': value, 'requests': requests,
        'request_sha256': {k: s.digest(v) for k, v in requests.items()}, 'cpu_qualification': qualified,
        'source_sha256': sources, 'weights': upstream['weights'], 'data_provenance': data,
        'primary': 'TREC context-paired indexed−anonymous64 canonical correctness, validity separate; source groups/repeats nested',
        'budget': {'calls': 600, 'hard_seconds': 1800, 'per_call_output_tokens': 3072, 'workers': 4},
        'checkpoint_policy': 'exclusive immutable per-call/wire/coordinate outputs; no retry/repair/resume or weight update'}
    spec['spec_id'] = s.digest(spec)
    s.write_once(ROOT / 'SPEC.json', spec)
    verify(s.read(ROOT / 'SPEC.json'))
    s.write_once(ROOT / 'READY.json', {'status': 'READY_ACTUAL_OLD_ENDPOINT_REQUIRED', 'driver': str(Path(__file__).resolve()),
        'driver_sha256': s.file_hash(__file__), 'spec': str(ROOT / 'SPEC.json'), 'spec_id': spec['spec_id'],
        'spec_sha256': s.file_hash(ROOT / 'SPEC.json'), 'output': str(ROOT / 'outputs/attempt-001'),
        'calls': 600, 'hard_seconds': 1800, 'focused_tests': 5, 'schemas_compiled': qualified['schemas_compiled'],
        'max_prompt_tokens': qualified['max_prompt_tokens'], 'adapter_sha256': s.corr.SELECTED_SHA,
        'cpu_model_calls': 0, 'gpu_authority': False})
    print(json.dumps(s.read(ROOT / 'READY.json')), flush=True)


def bind(endpoint_path, destination):
    spec = s.read(ROOT / 'SPEC.json')
    verify(spec)
    endpoint = s.read(endpoint_path)
    s.corr.validate_endpoint(endpoint)
    spec['design']['model_alias'] = endpoint['model_alias']
    for body in spec['requests'].values():
        body['model'] = endpoint['model_alias']
    spec['request_sha256'] = {k: s.digest(v) for k, v in spec['requests'].items()}
    spec['endpoint_binding'] = {'path': str(endpoint_path), 'sha256': s.file_hash(endpoint_path),
        'descriptor': endpoint, 'contacted_at_binding': False}
    spec.pop('spec_id')
    spec['spec_id'] = s.digest(spec)
    verify(spec)
    s.write_once(destination, spec)
    print(json.dumps({'bound': str(destination), 'sha256': s.file_hash(destination), 'model_calls': 0}), flush=True)


async def run(spec_path, output):
    spec = s.read(spec_path)
    verify(spec)
    endpoint = spec['endpoint_binding']['descriptor']
    if output.parent != ROOT / 'outputs':
        raise ValueError('owned sidecar output required')
    output.mkdir(parents=True, exist_ok=False)
    s.write_once(output / 'SPEC.json', spec)
    s.write_once(output / 'ATTEMPT.json', {'started_epoch': time.time(), 'spec_sha256': s.file_hash(spec_path),
        'model_alias': endpoint['model_alias'], 'adapter_sha256': s.corr.SELECTED_SHA,
        'client_gpu_visible': os.environ.get('CUDA_VISIBLE_DEVICES'), 'service_owned_by_parent': True})
    url = f"http://{endpoint['host']}:{endpoint['port']}/v1"
    started, deadline = time.time(), time.monotonic() + 1800
    records, reason = [], None
    try:
        async with asyncio.timeout(1800):
            async with httpx.AsyncClient(headers={'Authorization': 'Bearer ' + os.environ[endpoint['api_key_env']]},
                    trust_env=False, timeout=120, event_hooks={'request': [wire_hook(spec, output)]}) as client:
                response = await client.get(url.removesuffix('/v1') + '/version')
                response.raise_for_status()
                s.write_once(output / 'VERSION_PREFLIGHT.json', response.json())
                if response.json().get('version') != '0.28.0':
                    raise ValueError('unqualified live vLLM version')
                response = await client.get(url + '/models')
                response.raise_for_status()
                s.corr.validate_live_models(endpoint, response.json())
                s.write_once(output / 'MODELS_PREFLIGHT.json', response.json())
                records, reason = await s.collect_calls(client, url, spec, output, deadline)
    except TimeoutError:
        reason = 'wall_time_cap'
    except Exception as error:
        reason = 'preflight_or_runtime_error:' + type(error).__name__
        s.write_once(output / 'ERROR.json', {'type': type(error).__name__, 'message': str(error)[:1200]})
    finally:
        records = [s.read(p) for p in sorted((output / 'calls').glob('*.json'))]
        analysis = s.summarize(spec['design'], records)
        s.write_once(output / 'analysis.json', analysis)
        physical = [p for r in analysis['coordinates'] for p in r['physical_prompts']]
        if any(p['typed_template_equal'] is not True or p['reported_usage_length_equal'] is not True for p in physical):
            reason = reason or 'physical_prompt_identity_unverified'
        seen = {r['coordinate']['id'] for r in records}
        s.write_once(output / 'STATUS.json', {'planned': 600, 'recorded': len(records), 'stop_reason': reason,
            'typed_physical_prompt_matches': sum(p['typed_template_equal'] is True for p in physical),
            'wall_seconds': time.time() - started,
            'unrun': [r['id'] for r in spec['design']['plan'] if r['id'] not in seen]})
    return 0 if reason is None and len(records) == 600 else 2


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('command', choices=['prepare', 'verify', 'bind', 'run'])
    parser.add_argument('--endpoint-descriptor', type=Path)
    parser.add_argument('--spec-path', type=Path, default=ROOT / 'SPEC.json')
    parser.add_argument('--output-dir', type=Path, default=ROOT / 'outputs/attempt-001')
    args = parser.parse_args()
    if args.command == 'prepare':
        prepare()
    elif args.command == 'verify':
        verify(s.read(args.spec_path))
    elif args.command == 'bind':
        if args.endpoint_descriptor is None or args.spec_path == ROOT / 'SPEC.json':
            parser.error('actual endpoint descriptor and NEW bound spec required')
        bind(args.endpoint_descriptor.resolve(), args.spec_path.resolve())
    else:
        raise SystemExit(asyncio.run(run(args.spec_path.resolve(), args.output_dir.resolve())))


if __name__ == '__main__':
    main()
