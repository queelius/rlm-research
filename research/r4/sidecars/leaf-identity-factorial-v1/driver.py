"""CPU freeze/verify and parent-only384 collection; no launch during preparation."""
import argparse
import ast
import asyncio
import importlib.util
import json
import os
import subprocess
import sys
import time
from collections import Counter, defaultdict
from copy import deepcopy
from pathlib import Path

import httpx
import study as s

ROOT = s.ROOT
path = s.padding.GRAMMAR / 'driver.py'
if s.file_hash(path) != s.padding.PINS[path]:
    raise ValueError('frozen native helper changed')
loader = importlib.util.spec_from_file_location('factorial_private_native_http', path)
qualified_http = importlib.util.module_from_spec(loader)
loader.loader.exec_module(qualified_http)
BASE, wire_hook = qualified_http.BASE, qualified_http.wire_hook

# Reuse only the authenticated run function. Its collector, wire/version/model
# preflight, null handling and raw capture are unchanged. Explicit count/cap edits.
_source = (s.PARENT / 'driver.py').read_text()
_run = next(n for n in ast.parse(_source).body if isinstance(n, ast.AsyncFunctionDef) and n.name == 'run')
_run_source = ast.get_source_segment(_source, _run)
RUN_EDITS = [('96', '384', 3), ('launch + 1200', 'launch + 2400', 1),
             ('launch + 1080', 'launch + 2280', 2), ('min(600,', 'min(1800,', 1)]
for before, after, count in RUN_EDITS:
    if _run_source.count(before) != count:
        raise ValueError('collector adapter occurrence changed: ' + before)
    _run_source = _run_source.replace(before, after)
RUN_ADAPTED_SHA256 = __import__('hashlib').sha256(_run_source.encode()).hexdigest()
exec(compile(_run_source, str(s.PARENT / 'driver.py') + ':factorial-run-adapter', 'exec'), globals())


def weights():
    old = {'path': str(s.anchor.corr.ADAPTER), 'model_sha256': s.anchor.corr.SELECTED_SHA,
           'config_sha256': s.anchor.corr.CONFIG_SHA}
    sources = {}
    s.anchor.sst.authenticate_weight('old_sft', {'adapter': old, 'base_model': BASE}, sources)
    return {'models': {'old_sft': old}, 'base_model': BASE, 'source_sha256': sources,
        'selection': 'Existing validation-selected c32de only; no new outcome-based selection'}


def qualify(design, requests):
    from transformers import AutoTokenizer
    tokenizer = AutoTokenizer.from_pretrained(BASE['path'], local_files_only=True, trust_remote_code=False)
    # Parent qualifier expects one context/arm/seed; expand its temporary grouping
    # key only, without changing real requests, coordinates or display ordering.
    grouping = deepcopy(design)
    for row in grouping['plan']:
        row['context_index'] = ((row['context_index'] * 2 + row['permutation']) * 2
            + int(row['source_prefix'] == 'p')) * 2 + int(row['number_namespace'] == 'disjoint')
    result = qualified_http.qualify(grouping, requests)
    full_ids = {key: qualified_http.typed_prompt_ids(tokenizer, body) for key, body in requests.items()}
    if any(s.digest(ids) != result['rendered_prompts'][key]['typed_token_ids_sha256'] for key, ids in full_ids.items()):
        raise ValueError('full typed token identity mismatch')
    triples = defaultdict(list)
    tag_ids, cell_lengths = {}, defaultdict(list)
    for row in design['plan']:
        key = tuple(row[f] for f in ['context_index', 'permutation', 'repeat', 'source_prefix', 'number_namespace'])
        body = requests[row['id']]
        triples[key].append(body)
        gold = design['batches'][row['batch_id']]['gold']
        for tag in [r['id'] for r in gold['records']] + s.expected_tags(gold['records'], row['arm'], row['source_prefix']):
            tag_ids[tag] = tokenizer.encode(tag, add_special_tokens=False)
        cell_lengths['/'.join(row[f] for f in ['dataset', 'source_prefix', 'number_namespace', 'arm'])].append(len(full_ids[row['id']]))
    for bodies in triples.values():
        if len(bodies) != 3 or len({b['messages'][1]['content'].split(s.INPUT_MARKER)[1] for b in bodies}) != 1:
            raise ValueError('within-triple physical input differs')
        if not all(b['messages'][0] == bodies[0]['messages'][0] and b['tools'] == bodies[0]['tools'] for b in bodies):
            raise ValueError('within-triple system/tools differ')
    if any(len(tokenizer.encode(prefix, add_special_tokens=False)) != 1 for prefix in ['q', 'p']):
        raise ValueError('q/p standalone prefix qualification changed')
    result.update(paired_id_bearing_input_groups=len(triples), full_prompt_ids_sha256=s.digest(full_ids),
        tag_token_ids=tag_ids, tag_token_length_histogram=dict(Counter(len(v) for v in tag_ids.values())),
        condition_prompt_tokens={k: {'min': min(v), 'max': max(v), 'sum': sum(v), 'calls': len(v)} for k, v in cell_lengths.items()},
        length_caution='Actual IDs qualified; realized compute not assumed equal across representations/namespaces',
        max_prompt_plus_output=result['max_prompt_tokens'] + 3072)
    return result, full_ids


def verify(spec):
    if s.digest({k: v for k, v in spec.items() if k != 'spec_id'}) != spec['spec_id']:
        raise ValueError('spec identity changed')
    s.anchor.sst.verify_hashes(spec['source_sha256'])
    data = s.read(ROOT / 'DATA.json')
    if data != s.build_data(s.read(s.PARENT / 'DATA.json')):
        raise ValueError('frozen source-rank/permutation/value assignment changed')
    expected = s.build_design(data)
    expected['rendered_prompts'] = s.read(ROOT / 'CPU_QUALIFICATION.json')['rendered_prompts']
    if expected != spec['design'] or len(expected['plan']) != 384:
        raise ValueError('fixed384 design changed')
    for row in expected['plan']:
        body = s.make_request(expected, row)
        if s.serialize(body) != s.serialize(spec['requests'][row['id']]) or s.digest(body) != spec['request_sha256'][row['id']]:
            raise ValueError('fixed request changed')


def seed_audit():
    argv = ['rg', '--files', str(s.SIDE), '-g', '*SPEC*.json', '-g', '*READY*.json',
        '-g', '*RECIPE*.json', '-g', '*CAMPAIGN*.json', '-g', '*SEED*.json',
        '-g', '!**/outputs/**', '-g', '!**/leaf-identity-factorial-v1/**']
    inventory = subprocess.run(argv, capture_output=True, text=True, check=True, timeout=30)
    paths = sorted(set(inventory.stdout.splitlines()))
    pattern = r'\b(' + '|'.join(str(seed) for seed in [s.MASTER, *s.SEEDS]) + r')\b'
    audit = subprocess.run(['rg', '-n', pattern, *paths], capture_output=True, text=True, timeout=60)
    if audit.returncode != 1 or audit.stdout:
        raise ValueError('sampling seed collision/audit failure: ' + audit.stdout[:1000])
    return {'master': s.MASTER, 'sampling_seeds': s.SEEDS, 'inventory_argv': argv,
        'paths_sha256': {p: s.file_hash(p) for p in paths}, 'regex': pattern,
        'exit_code': audit.returncode, 'matches': audit.stdout, 'stderr': audit.stderr,
        'scope': 'Named sidecar SPEC/READY/RECIPE/CAMPAIGN/SEED JSON files excluding outputs and this sidecar; not a global all-history proof; master intentionally exists in approved proposal/decision'}


def prepare():
    if (ROOT / 'SPEC.json').exists():
        raise ValueError('already frozen')
    audit = seed_audit()
    data = s.build_data(s.read(s.PARENT / 'DATA.json'))
    design = s.build_design(data)
    requests = {r['id']: s.make_request(design, r) for r in design['plan']}
    qualified, ids = qualify(design, requests)
    design['rendered_prompts'] = qualified['rendered_prompts']
    tests = subprocess.run([sys.executable, '-m', 'pytest', '-q', '-p', 'no:cacheprovider', str(ROOT / 'test_study.py')],
        capture_output=True, text=True, timeout=90,
        env={**os.environ, 'CUDA_VISIBLE_DEVICES': '', 'PYTHONDONTWRITEBYTECODE': '1'})
    if tests.returncode:
        raise ValueError(tests.stdout[-4000:] + tests.stderr[-1000:])
    weight = weights()
    schemas = {s.digest(body['structured_outputs']['json']): body['structured_outputs']['json'] for body in requests.values()}
    dispatch = [{**row, 'request_sha256': s.digest(requests[row['id']]),
        'schema_sha256': s.digest(requests[row['id']]['structured_outputs']['json']),
        'typed_prompt_ids_sha256': s.digest(ids[row['id']])} for row in design['plan']]
    import owned
    for name, value in [('DATA.json', data), ('CPU_QUALIFICATION.json', qualified), ('PROMPT_IDS.json', ids),
        ('SCHEMAS.json', schemas), ('DISPATCH.json', dispatch), ('WEIGHTS.json', weight), ('SEED_AUDIT.json', audit),
        ('SOURCE_ADAPTERS.json', {'run_source_path': str(s.PARENT / 'driver.py'), 'run_edits': RUN_EDITS,
            'run_adapted_sha256': RUN_ADAPTED_SHA256, 'owned_source_path': str(owned.SOURCE_PATH),
            'owned_edits': owned.EDITS, 'owned_adapted_sha256': owned.ADAPTED_SHA256,
            'boundary': 'Private count/cap/namespace adapters only; frozen sources unchanged'}),
        ('CPU_TESTS.json', {'returncode': tests.returncode, 'stdout': tests.stdout, 'stderr': tests.stderr,
            'prior_red': 'Six desired tests failed because study.py absent; pytest-123, six failures exit1 before implementation',
            'gpu_calls': 0, 'network_model_calls': 0, 'fake_http_calls': 12})]:
        s.write_once(ROOT / name, value)
    sources = dict(s.read(s.PARENT / 'SPEC.json')['source_sha256'])
    sources.update({str(p): h for p, h in s.PINS.items()})
    sources.update(weight['source_sha256'])
    sources.update({str(p): h for p, h in owned.PINNED.items()})
    for p in [s.SIDE.parent / 'ideas/2026-09-09-identity-factorial-design.md',
              s.SIDE.parent / 'operations/2026-09-09-continuous-allocation/IDENTITY_FACTORIAL_DECISION.md']:
        sources[str(p)] = s.file_hash(p)
    sources.update({str(p): s.file_hash(p) for p in [*ROOT.glob('*.py'), *ROOT.glob('*.md'), *ROOT.glob('*.json')]})
    spec = {'schema': ROOT.name, 'design': design, 'requests': requests,
        'request_sha256': {k: s.digest(v) for k, v in requests.items()}, 'source_sha256': sources, 'weight': weight,
        'budget': {'calls': 384, 'collection_seconds': 1800, 'owned_seconds': 2400, 'parent_seconds': 2430,
            'cleanup_reserve_seconds': 120, 'workers': 4, 'request_timeout_seconds': 120, 'output_cap': 3072, 'retries': 0},
        'frozen_before_inference': True,
        'question': 'Meaningful versus ordinal under disjoint numeric namespace; overlap interaction and q/p prefix swap',
        'primary_alignment': 'displayed position', 'numeric_diagnostic': 'overlap ordinal only; disjoint unavailable; never rescues primary'}
    spec['spec_id'] = s.digest(spec)
    s.write_once(ROOT / 'SPEC.json', spec)
    verify(spec)
    owned.load_suite()
    s.write_once(ROOT / 'PREPARED.json', {'status': 'CPU_FROZEN_PARENT_LAUNCH_REQUIRED',
        'spec_sha256': s.file_hash(ROOT / 'SPEC.json'), 'spec_id': spec['spec_id'], 'calls': 384,
        'sampling_seeds': s.SEEDS, 'schemas_compiled': qualified['schemas_compiled'],
        'max_prompt_tokens': qualified['max_prompt_tokens'], 'max_prompt_plus_output': qualified['max_prompt_plus_output'],
        'gpu_calls': 0, 'network_model_calls': 0})
    print(s.serialize(s.read(ROOT / 'PREPARED.json')), flush=True)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('command', choices=['prepare', 'verify', 'run'])
    parser.add_argument('--endpoint', type=Path)
    parser.add_argument('--output-dir', type=Path, default=ROOT / 'outputs/attempt-001')
    parser.add_argument('--overall-start-epoch', type=float)
    args = parser.parse_args()
    if args.command == 'prepare':
        prepare()
    elif args.command == 'verify':
        verify(s.read(ROOT / 'SPEC.json'))
        print('verified', flush=True)
    else:
        if not args.endpoint:
            parser.error('actual endpoint required')
        raise SystemExit(asyncio.run(run(args.endpoint.resolve(), args.output_dir.resolve(), args.overall_start_epoch)))


if __name__ == '__main__':
    main()
