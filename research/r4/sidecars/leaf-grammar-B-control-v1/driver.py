"""B-only80 companion: immutable parent requests, private frozen collector, no service ownership."""
from __future__ import annotations

import argparse
import asyncio
import hashlib
import importlib.util
import json
import os
import subprocess
import sys
import time
from copy import deepcopy
from pathlib import Path

import httpx

ROOT = Path(__file__).resolve().parent
PARENT = ROOT.parent / 'leaf-indexed-grammar-transfer-v1'
B_CHECKPOINT = ROOT.parent / 'leaf-mixed-size-sft-v1/B/outputs/attempt-001/checkpoint-0204'
B_SHA = '59ad854293142161f6b5e613dd5d1e3630fed600637106d5eae2cbcd764e9200'
PINNED = {
    PARENT / 'study.py': '861fae26e0b5bc6855b80c20a459cd1526e4bfd49b4e83fb3a380abb4a161487',
    PARENT / 'driver.py': '17d46458875e2fdbb3f03d951ef6659ae54165cb3d420b5f4678886eb1857f67',
    PARENT / 'SPEC.json': 'c9bdead579cc6da8ae5910835f6c4742f2f1ed0121c42afcd397be1bc99e7f3b',
    PARENT / 'DATA.json': 'ca5a895f361d8a590078e36393c6edf900e86a6da7b17382440366581642e17f',
}


def load(name, path):
    if hashlib.sha256(path.read_bytes()).hexdigest() != PINNED[path]:
        raise ValueError('frozen parent source changed: ' + str(path))
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


g = load('B_private_grammar_study', PARENT / 'study.py')
prior_study = sys.modules.get('study')
try:
    sys.modules['study'] = g
    up = load('B_private_grammar_driver', PARENT / 'driver.py')
finally:
    if prior_study is None:
        sys.modules.pop('study', None)
    else:
        sys.modules['study'] = prior_study
read, digest, file_hash, serialize, write_once = g.read, g.digest, g.file_hash, g.serialize, g.write_once
g.WEIGHTS = ['Bfinal']


def assert_only_model(original, changed):
    expected = deepcopy(original)
    expected['model'] = changed['model']
    if serialize(expected) != serialize(changed):
        raise ValueError('non-model request field or serialization changed')


def build_design():
    for path, sha in PINNED.items():
        if file_hash(path) != sha:
            raise ValueError('frozen parent changed: ' + str(path))
    parent = read(PARENT / 'SPEC.json')
    design = deepcopy(parent['design'])
    key = lambda r: (r['context_index'], r['arm'], r['grammar'], r['repeat'], r['seed'])
    indexed = {key(r): r for r in design['plan'] if r['weight'] == 'indexed_final'}
    rows, crosswalk, templates, prompts = [], {}, {}, {}
    for original in design['plan']:
        if original['weight'] != 'old_sft':
            continue
        other = indexed[key(original)]
        old_body = parent['requests'][original['id']]
        assert_only_model(old_body, parent['requests'][other['id']])
        if design['rendered_prompts'][original['id']] != design['rendered_prompts'][other['id']]:
            raise ValueError('parent weights have different physical inputs')
        row = deepcopy(original)
        row['id'] = row['coordinate_id'] = digest([ROOT.name, original['id']])
        row['weight'] = 'Bfinal'
        row['dispatch_order'] = len(rows)
        rows.append(row)
        crosswalk[row['id']] = {'old_sft': original['id'], 'indexed_final': other['id'],
            'parent_dispatch_order': original['dispatch_order'],
            'request_without_model_sha256': digest({k: v for k, v in old_body.items() if k != 'model'}),
            'parent_spec_sha256': PINNED[PARENT / 'SPEC.json']}
        templates[row['id']] = deepcopy(old_body)
        templates[row['id']]['model'] = '__B_FINAL_ALIAS__'
        prompts[row['id']] = deepcopy(design['rendered_prompts'][original['id']])
    design['plan'] = design['coordinates'] = rows
    design['model_aliases'] = {'Bfinal': '__B_FINAL_ALIAS__'}
    design['wall_time_cap_seconds'] = 900
    design['request_templates'] = templates
    design['rendered_prompts'] = prompts
    if len(rows) != 80 or len(crosswalk) != 80:
        raise ValueError('requires exact eighty parent coordinates')
    return design, crosswalk


def make_request(design, row):
    body = deepcopy(design['request_templates'][row['id']])
    body['model'] = design['model_aliases'][row['weight']]
    return body


# Only this process-private imported collector instance is configured.
g.anchor.corr.fixed.make_request = make_request


def check_model_sha(value):
    if value != B_SHA:
        raise ValueError('requires exact Bfinal59ad854 model')


def authenticate_weights():
    state = read(B_CHECKPOINT / 'state.json')
    model = {'path': str(B_CHECKPOINT),
        'model_sha256': state['files_sha256']['adapter_model.safetensors'],
        'config_sha256': state['files_sha256']['adapter_config.json']}
    check_model_sha(model['model_sha256'])
    sources = {}
    g.anchor.sst.authenticate_weight('B', {'adapter': model, 'base_model': up.BASE}, sources)
    return {'models': {'Bfinal': model}, 'base_model': up.BASE, 'source_sha256': sources,
        'selection_semantics': 'fixed final epoch2/step204, not validation-selected',
        'outcome_metric_used_to_select_weights': False, 'gpu_calls': 0}


def verify(spec):
    if digest({k: v for k, v in spec.items() if k != 'spec_id'}) != spec['spec_id']:
        raise ValueError('spec identity changed')
    g.anchor.sst.verify_hashes(spec['source_sha256'])
    expected, crosswalk = build_design()
    if 'endpoint_binding' in spec:
        binding = spec['endpoint_binding']
        item = binding['endpoint']
        if file_hash(item['path']) != item['sha256'] or read(item['path']) != item['descriptor']:
            raise ValueError('actual descriptor changed')
        if binding['weights_sha256'] != file_hash(ROOT / 'WEIGHTS.json'):
            raise ValueError('weights closure changed')
        weights = read(ROOT / 'WEIGHTS.json')
        if weights != authenticate_weights():
            raise ValueError('fixed-final B identity changed')
        up.validate_descriptor('Bfinal', item['descriptor'], weights)
        expected['model_aliases']['Bfinal'] = item['descriptor']['model_alias']
    if expected != spec['design'] or crosswalk != spec['crosswalk']:
        raise ValueError('frozen parent crosswalk/design changed')
    for row in expected['plan']:
        body = make_request(expected, row)
        if serialize(body) != serialize(spec['requests'][row['id']]) or digest(body) != spec['request_sha256'][row['id']]:
            raise ValueError('request changed')


def prepare():
    if (ROOT / 'SPEC.json').exists():
        raise ValueError('already frozen')
    design, crosswalk = build_design()
    requests = {r['id']: make_request(design, r) for r in design['plan']}
    qualification = up.qualify(design, requests)
    if qualification['rendered_prompts'] != design['rendered_prompts']:
        raise ValueError('native B prompts differ from parent physical prompts')
    from transformers import AutoTokenizer
    tokenizer = AutoTokenizer.from_pretrained(up.BASE['path'], local_files_only=True, trust_remote_code=False)
    ids = {key: up.typed_prompt_ids(tokenizer, body) for key, body in requests.items()}
    if any(digest(value) != qualification['rendered_prompts'][key]['typed_token_ids_sha256'] for key, value in ids.items()):
        raise ValueError('full prompt-ID artifact mismatch')
    write_once(ROOT / 'PROMPT_IDS.json', ids)
    write_once(ROOT / 'CPU_QUALIFICATION.json', qualification)
    tests = subprocess.run([sys.executable, '-m', 'pytest', '-q', '-p', 'no:cacheprovider', str(ROOT / 'test_control.py')],
        capture_output=True, text=True, timeout=90,
        env={**os.environ, 'CUDA_VISIBLE_DEVICES': '', 'PYTHONDONTWRITEBYTECODE': '1'})
    write_once(ROOT / 'CPU_TESTS.json', {'returncode': tests.returncode, 'stdout': tests.stdout,
        'stderr': tests.stderr, 'prior_red': 'All five desired tests failed: B-only companion is not implemented; pytest105.',
        'gpu_calls': 0, 'fake_http_calls': 5})
    if tests.returncode:
        raise ValueError(tests.stdout[-3000:])
    weights = authenticate_weights()
    write_once(ROOT / 'WEIGHTS.json', weights)
    sources = dict(read(PARENT / 'SPEC.json')['source_sha256'])
    sources.update({str(p): h for p, h in PINNED.items()})
    sources.update(weights['source_sha256'])
    import owned
    lifecycle = owned.load_lifecycle()
    sources.update({str(p): h for p, h in lifecycle.PINNED.items()})
    sources[str(owned.FROZEN_WRAPPER)] = owned.FROZEN_WRAPPER_SHA
    sources.update({str(p): file_hash(p) for p in [*ROOT.glob('*.py'), *ROOT.glob('*.md'), *ROOT.glob('*.json')]})
    spec = {'schema': ROOT.name, 'design': design, 'crosswalk': crosswalk, 'requests': requests,
        'request_sha256': {k: digest(v) for k, v in requests.items()}, 'source_sha256': sources,
        'data_reference': {'path': str(PARENT / 'DATA.json'), 'sha256': PINNED[PARENT / 'DATA.json']},
        'budget': {'calls': 80, 'collection_seconds': 900, 'overall_seconds': 1800,
            'workers': 4, 'request_timeout_seconds': 120, 'output_cap': 3072},
        'order_rule': 'Parent old-weight subsequence, relative counterbalanced order preserved; later service stage',
        'selection': 'B fixed final epoch2/step204; no outcome-based checkpoint choice'}
    spec['spec_id'] = digest(spec)
    write_once(ROOT / 'SPEC.json', spec)
    verify(spec)
    write_once(ROOT / 'PREPARED.json', {'status': 'CPU_PREPARED_NOT_LAUNCH_AUTHORITY',
        'spec_sha256': file_hash(ROOT / 'SPEC.json'), 'spec_id': spec['spec_id'],
        'calls': 80, 'parent_request_crosswalks': 160, 'native_prompt_matches': 80,
        'weights_sha256': file_hash(ROOT / 'WEIGHTS.json'), 'gpu_calls': 0})
    print(serialize(read(ROOT / 'PREPARED.json')), flush=True)


def bind(endpoint_path, destination):
    spec = read(ROOT / 'SPEC.json')
    verify(spec)
    endpoint = read(endpoint_path)
    up.validate_descriptor('Bfinal', endpoint, read(ROOT / 'WEIGHTS.json'))
    spec['design']['model_aliases']['Bfinal'] = endpoint['model_alias']
    spec['requests'] = {r['id']: make_request(spec['design'], r) for r in spec['design']['plan']}
    spec['request_sha256'] = {k: digest(v) for k, v in spec['requests'].items()}
    spec['endpoint_binding'] = {'endpoint': {'path': str(endpoint_path), 'sha256': file_hash(endpoint_path),
        'descriptor': endpoint}, 'weights_sha256': file_hash(ROOT / 'WEIGHTS.json'), 'contacted_at_binding': False}
    spec.pop('spec_id')
    spec['spec_id'] = digest(spec)
    verify(spec)
    write_once(destination, spec)
    print(serialize({'bound': str(destination), 'sha256': file_hash(destination), 'gpu_calls': 0}), flush=True)


def collection_budget(launch, now):
    remaining = launch + 1800 - now
    if remaining <= 0:
        raise TimeoutError('overall deadline expired')
    return min(900, remaining)


async def run(spec_path, output, overall_start_epoch=None):
    entry = time.time()
    launch = entry if overall_start_epoch is None else overall_start_epoch
    if launch > entry + 1:
        raise ValueError('future overall launch time')
    spec = read(spec_path)
    verify(spec)
    endpoint = spec['endpoint_binding']['endpoint']['descriptor']
    if output.parent != ROOT / 'outputs':
        raise ValueError('owned sidecar output directory required')
    output.mkdir(parents=True, exist_ok=False)
    write_once(output / 'SPEC.json', spec)
    write_once(output / 'ATTEMPT.json', {'entered_epoch': entry, 'overall_started_epoch': launch,
        'overall_deadline_epoch': launch + 1800, 'source_spec_sha256': file_hash(spec_path),
        'weights_sha256': file_hash(ROOT / 'WEIGHTS.json'), 'gpu_process_owned': False})
    url = f"http://{endpoint['host']}:{endpoint['port']}/v1"
    reason, collection_started = None, None
    try:
        collection_budget(launch, time.time())
        async with asyncio.timeout(max(.001, launch + 1800 - time.time())):
            async with httpx.AsyncClient(headers={'Authorization': 'Bearer ' + os.environ[endpoint['api_key_env']]},
                    trust_env=False, timeout=120, event_hooks={'request': [up.wire_hook(spec, output)]}) as client:
                response = await client.get(url.removesuffix('/v1') + '/version')
                response.raise_for_status()
                write_once(output / 'VERSION_PREFLIGHT.json', response.json())
                if response.json().get('version') != '0.28.0':
                    raise ValueError('unqualified live vLLM version')
                response = await client.get(url + '/models')
                response.raise_for_status()
                up.validate_live_models({'Bfinal': endpoint}, response.json())
                write_once(output / 'MODELS_PREFLIGHT.json', response.json())
                collection_started = time.time()
                _, reason = await g.collect_calls(client, url, spec, output,
                    time.monotonic() + collection_budget(launch, collection_started))
    except TimeoutError:
        reason = 'overall_wall_time_cap'
    except Exception as error:
        reason = 'preflight_or_runtime_error:' + type(error).__name__
        write_once(output / 'ERROR.json', {'type': type(error).__name__, 'message': str(error)[:1200]})
    finally:
        records = [read(p) for p in sorted((output / 'calls').glob('*.json'))]
        analysis = g.summarize(spec['design'], records)
        analysis['inference_caution'] = ('Bfinal-only later service stage; compare against parent IDs, '
            'not contemporaneous three-weight interleaving. Component readout, not RLM evidence.')
        write_once(output / 'analysis.json', analysis)
        physical = [p for c in analysis['coordinates'] for p in c['physical_prompts']]
        if any(p['typed_template_equal'] is not True or p['reported_usage_length_equal'] is not True for p in physical):
            reason = reason or 'physical_prompt_identity_unverified'
        seen = {r['coordinate']['id'] for r in records}
        write_once(output / 'STATUS.json', {'planned': 80, 'recorded': len(records), 'stop_reason': reason,
            'actual_typed_prompt_matches': sum(p['typed_template_equal'] is True for p in physical),
            'collection_seconds': time.time() - collection_started if collection_started is not None else None,
            'driver_wall_seconds': time.time() - entry, 'overall_elapsed_seconds': time.time() - launch,
            'unrun': [r['id'] for r in spec['design']['plan'] if r['id'] not in seen]})
    return 0 if reason is None and len(records) == 80 else 2


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('command', choices=['prepare', 'verify', 'bind', 'run'])
    parser.add_argument('--spec-path', type=Path, default=ROOT / 'SPEC.json')
    parser.add_argument('--endpoint-descriptor', type=Path)
    parser.add_argument('--output-dir', type=Path, default=ROOT / 'outputs/attempt-001')
    parser.add_argument('--overall-start-epoch', type=float)
    args = parser.parse_args()
    if args.command == 'prepare':
        prepare()
    elif args.command == 'verify':
        verify(read(args.spec_path))
        print('verified', flush=True)
    elif args.command == 'bind':
        if not args.endpoint_descriptor or args.spec_path == ROOT / 'SPEC.json':
            parser.error('actual endpoint and new bound spec required')
        bind(args.endpoint_descriptor.resolve(), args.spec_path.resolve())
    else:
        raise SystemExit(asyncio.run(run(args.spec_path.resolve(), args.output_dir.resolve(), args.overall_start_epoch)))


if __name__ == '__main__':
    main()
