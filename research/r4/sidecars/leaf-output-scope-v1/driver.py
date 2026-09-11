"""Freeze, explicitly bind and run the72-call proxy; never owns a GPU/service."""
from __future__ import annotations

import argparse
import asyncio
import datetime
import json
import os
import subprocess
import sys
import time
from copy import deepcopy
from pathlib import Path

import httpx

import study

ROOT = study.ROOT


def bind_identity(unbound, descriptor):
    study.corr.validate_endpoint(descriptor)
    result = deepcopy(unbound)
    alias = descriptor['model_alias']
    result['design']['model_alias'] = alias
    for key, body in result['requests'].items():
        body['model'] = alias
        if {**body, 'model': unbound['design']['model_alias']} != unbound['requests'][key]:
            raise ValueError('binding changed a non-model request field')
    result['request_sha256'] = {key: study.digest(body) for key, body in result['requests'].items()}
    return result


def verify(spec):
    if study.digest({k: v for k, v in spec.items() if k != 'spec_id'}) != spec['spec_id']:
        raise ValueError('spec identity changed')
    for path, expected in spec['source_file_sha256'].items():
        if study.file_hash(path) != expected:
            raise ValueError('frozen source/input changed: ' + path)
    value = deepcopy(spec['design'])
    value['model_alias'] = study.corr.PLACEHOLDER
    prompts = value.pop('rendered_prompts')
    if value != study.design() or prompts != spec['cpu_qualification']['rendered_prompts']:
        raise ValueError('source questions/targets/order or CPU prompt evidence changed')
    for row in spec['design']['plan']:
        body = study.make_request(spec['design'], row)
        if body != spec['requests'][row['id']] or study.digest(body) != spec['request_sha256'][row['id']]:
            raise ValueError('actual request differs from frozen body')
    if 'endpoint_binding' in spec:
        binding = spec['endpoint_binding']
        if (study.file_hash(binding['descriptor_path']) != binding['descriptor_sha256']
                or study.file_hash(binding['unbound_spec_path']) != binding['unbound_spec_sha256']):
            raise ValueError('bound endpoint or original spec changed')
        original = study.read(binding['unbound_spec_path'])
        verify(original)
        descriptor = study.read(binding['descriptor_path'])
        expected = bind_identity(original, descriptor)
        expected['endpoint_binding'] = binding
        expected.pop('spec_id', None)
        expected['spec_id'] = study.digest(expected)
        if expected != spec or binding['descriptor'] != descriptor:
            raise ValueError('binding exceeds the authenticated explicit model substitution')
    elif spec['design']['model_alias'] != study.corr.PLACEHOLDER:
        raise ValueError('unbound spec has an unverified model alias')


def bind(endpoint_path, output):
    original_path = ROOT / 'SPEC.json'
    original = study.read(original_path)
    verify(original)
    descriptor = study.read(endpoint_path)
    result = bind_identity(original, descriptor)
    result['endpoint_binding'] = {'descriptor_path': str(endpoint_path.resolve()),
        'descriptor_sha256': study.file_hash(endpoint_path), 'descriptor': descriptor,
        'unbound_spec_path': str(original_path), 'unbound_spec_sha256': study.file_hash(original_path),
        'live_contact_during_binding': False}
    result.pop('spec_id')
    result['spec_id'] = study.digest(result)
    verify(result)
    output.parent.mkdir(parents=True, exist_ok=True)
    study.write_once(output, result)
    output.chmod(0o444)
    print(json.dumps({'bound_spec': str(output), 'sha256': study.file_hash(output), 'model_calls': 0}))


def prepare():
    if (ROOT / 'SPEC.json').exists() or (ROOT / 'READY.json').exists():
        raise ValueError('preparation already sealed; no overwrite')
    source = study.read(study.SOURCE)
    for path, expected in source['source_file_sha256'].items():
        if study.file_hash(path) != expected:
            raise ValueError('upstream frozen provenance changed: ' + path)
    # Build the same sorted JSON object ordering that bind/run will reload.
    value = json.loads(json.dumps(study.design(), sort_keys=True))
    qualified = study.corr.qualify({'comparison': 'output_scope', 'design': value})
    if qualified['requests_validated'] != 72 or qualified['distinct_schemas_compiled'] != 2:
        raise ValueError('unexpected request/schema qualification shape')
    value['rendered_prompts'] = qualified['rendered_prompts']
    requests = {row['id']: study.make_request(value, row) for row in value['plan']}
    # The file contains every complete unbound body, not just a body-builder hash.
    study.write_once(ROOT / 'REQUESTS.unbound.json', requests)
    study.write_once(ROOT / 'CPU_QUALIFICATION.json', qualified)
    result = subprocess.run([sys.executable, '-m', 'pytest', '-q', str(ROOT / 'test_study.py')],
        capture_output=True, text=True, timeout=90,
        env={**os.environ, 'CUDA_VISIBLE_DEVICES': '', 'PYTHONDONTWRITEBYTECODE': '1'})
    study.write_once(ROOT / 'CPU_TESTS.json', {'returncode': result.returncode,
        'stdout': result.stdout, 'stderr': result.stderr, 'model_calls': 0})
    if result.returncode:
        raise ValueError('focused CPU tests failed: ' + result.stdout + result.stderr)
    paths = [*ROOT.glob('*.py'), *ROOT.glob('*.md'), ROOT / 'REQUESTS.unbound.json',
             ROOT / 'CPU_QUALIFICATION.json', ROOT / 'CPU_TESTS.json', study.SOURCE,
             study.UPSTREAM / 'driver.py']
    sources = {**source['source_file_sha256'], **{str(path): study.file_hash(path) for path in paths}}
    spec = {'schema': 'leaf-output-scope-v1', 'created_utc': datetime.datetime.now(datetime.timezone.utc).isoformat(),
        'design': value, 'requests': requests,
        'request_sha256': {key: study.digest(body) for key, body in requests.items()},
        'cpu_qualification': qualified, 'source_file_sha256': sources, 'weights': source['weights'],
        'provenance': {**source['provenance'],
            'source_rotation_spec_path': str(study.SOURCE), 'source_rotation_spec_sha256': study.SOURCE_SHA,
            'seeds': study.SEEDS, 'seed_provenance': 'Parent-assigned fresh namespace; differs from frozen predecessor seeds981261401/402. No claim of an exhaustive global namespace scan.',
            'source_test_entries_accessed_by_this_preparation': False,
            'new_group_selection': False, 'inspected_validation_not_untouched': True},
        'protocol': {'route': '/v1/chat/completions', 'kind': 'qualified reconstructed native first-leaf-response proxy, not TrainClient or recursive replay',
            'tools_executed': False, 'extra_logprobs_requested': False, 'retries': 0,
            'physical_prompt_check': 'actual provider token IDs versus frozen CPU template token-ID hash'},
        'analysis': {'primary': 'whole-array validity and aligned canonical correctness by original-position quartile and matched original ID',
            'secondary': 'HUM/NUM target16 and reassembled64 counts, with explicit false-positive/negative cancellation diagnostics',
            'cost': 'all72 calls, including four repeated full prefixes in full16; unknown fields counted explicitly',
            'limitation': 'all64→full16 changes selection burden; full16→local16 removes only non-target visible records. Four inspected validation contexts, not a generic attention-mechanism result.'},
        'checkpoint_policy': 'atomic per-call/full raw trace and per-coordinate scores; no overwrite, retry or resume'}
    spec['spec_id'] = study.digest(spec)
    study.write_once(ROOT / 'SPEC.json', spec)
    verify(study.read(ROOT / 'SPEC.json'))
    for path in [*paths, ROOT / 'SPEC.json']:
        if path.is_relative_to(ROOT):
            path.chmod(0o444)
    ready = {'status': 'READY_AUTHENTICATED_OLD_ENDPOINT_REQUIRED', 'spec_id': spec['spec_id'],
        'spec_sha256': study.file_hash(ROOT / 'SPEC.json'), 'requests': 72, 'schema_count': 2,
        'max_input_tokens': qualified['max_input_tokens'], 'max_output_tokens': 1024,
        'contexts': 4, 'unique_question_groups': 256, 'focused_tests': 9,
        'model_calls_during_preparation': 0, 'gpu_or_service_authority': False,
        'entrypoint': str(ROOT / 'driver.py'), 'runbook': str(ROOT / 'RUNBOOK.md')}
    study.write_once(ROOT / 'READY.json', ready)
    (ROOT / 'READY.json').chmod(0o444)
    print(json.dumps(ready), flush=True)


async def run(bound_path, output):
    spec = study.read(bound_path)
    verify(spec)
    if 'endpoint_binding' not in spec:
        raise ValueError('run requires a freshly bound authenticated old-child descriptor')
    endpoint = spec['endpoint_binding']['descriptor']
    url = f"http://{endpoint['host']}:{endpoint['port']}/v1"
    key = os.environ[endpoint['api_key_env']]
    output.mkdir(parents=True, exist_ok=False)
    (output / 'calls').mkdir()
    (output / 'coordinates').mkdir()
    study.write_once(output / 'SPEC.json', spec)
    study.write_once(output / 'ENDPOINT.json', endpoint)
    started, deadline = time.time(), time.monotonic() + spec['design']['wall_time_cap_seconds']
    study.write_once(output / 'ATTEMPT.json', {'started': started, 'bound_spec_sha256': study.file_hash(bound_path),
        'model_alias': endpoint['model_alias'], 'adapter_sha256': study.corr.SELECTED_SHA})
    records, reason = [], None
    try:
        async with asyncio.timeout(max(.001, deadline - time.monotonic())):
            async with httpx.AsyncClient(headers={'Authorization': 'Bearer ' + key},
                    timeout=spec['design']['call_timeout_seconds'], trust_env=False) as client:
                version = await client.get(url.removesuffix('/v1') + '/version')
                version.raise_for_status()
                study.write_once(output / 'VERSION_PREFLIGHT.json', version.json())
                if version.json().get('version') != '0.28.0':
                    raise ValueError('live server differs from qualified vLLM0.28.0')
                response = await client.get(url + '/models')
                response.raise_for_status()
                study.write_once(output / 'MODELS_PREFLIGHT.json', response.json())
                study.corr.validate_live_models(endpoint, response.json())
                records, reason = await study.collect_calls(client, url, spec, output, deadline)
    except TimeoutError:
        reason = 'wall_time_cap'
    except Exception as error:
        reason = 'preflight_or_runtime_error:' + type(error).__name__
        study.write_once(output / 'ERROR.json', {'type': type(error).__name__, 'message': str(error)[:1200]})
    finally:
        records = [study.read(path) for path in sorted((output / 'calls').glob('*.json'))]
        study.write_once(output / 'analysis.json', study.summarize(spec['design'], records))
        seen = {record['coordinate']['id'] for record in records}
        study.write_once(output / 'STATUS.json', {'planned': 72, 'recorded': len(records), 'stop_reason': reason,
            'wall_seconds': time.time() - started, 'unrun': [r['id'] for r in spec['design']['plan'] if r['id'] not in seen]})
    return 0 if reason is None and len(records) == 72 else 2


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('command', choices=['prepare', 'verify', 'bind', 'run'])
    parser.add_argument('--endpoint-descriptor', type=Path)
    parser.add_argument('--spec-path', type=Path, default=ROOT / 'SPEC.json')
    parser.add_argument('--output-dir', type=Path, default=ROOT / 'outputs/attempt-001')
    args = parser.parse_args()
    if args.command == 'prepare':
        prepare()
    elif args.command == 'verify':
        verify(study.read(args.spec_path))
        print(json.dumps({'verified': str(args.spec_path), 'sha256': study.file_hash(args.spec_path)}))
    elif args.command == 'bind':
        if args.endpoint_descriptor is None or args.spec_path == ROOT / 'SPEC.json':
            parser.error('bind requires --endpoint-descriptor and a NEW --spec-path')
        bind(args.endpoint_descriptor.resolve(), args.spec_path.resolve())
    else:
        raise SystemExit(asyncio.run(run(args.spec_path.resolve(), args.output_dir.resolve())))


if __name__ == '__main__':
    main()
