"""CPU preparation and fixed first-response SST-2 transfer; no training or remote code."""
from __future__ import annotations

import argparse
import asyncio
import copy
import hashlib
import importlib.util
import json
import os
import platform
import time
import unicodedata
import urllib.request
from collections import Counter, defaultdict
from collections.abc import Mapping
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent
SIDECARS = ROOT.parent
BASE = Path('/project/alex_phd/research-cache/models/Qwen--Qwen3-4B-Instruct-2507--cdbee75f17c01a7cc42f958dc650907174af0554')
REVISION = '8d51e7e4887a4caaa95b3fbebbf53c0490b58bbb'
CACHE = Path('/project/alex_phd/research-cache/datasets') / ('stanfordnlp--sst2--' + REVISION)
FIXED_PATH = SIDECARS / 'fixed-leaf-composition-v1/driver.py'
FIXED_SHA = '9afd6c5d5219a6705c79839e99a87ca45e50c84fc7bdff197c97482f6cd8387a'
CONTRACT_PATH = SIDECARS / 'trec-leaf-contract-probe-v1/CONTRACT.json'
CONTRACT_SHA = 'cb50c6fddff7ea62a96936a7fcb58da84307248028adb420d7b1ab971a74bea7'
LABELS = ['negative', 'positive']
WEIGHTS = {
    'original': '857a7ce6907c759a8c1b478eb53029d3b700b81c3094d8edb3394e52def9fcb6',
    'old_sft': 'c32de1293c01bba5104eb1f123867649c71dd38e5194661ace4b17dcbbe66ba3',
}
MIXED_IDENTITIES = {'A': '8eb3268bbb336cfbe8fb5c9f9dc23cedbd10b4a6c24cd86ff87896a01726f865',
                    'B': '4db9de214de98539125047f22f5b4f8c52eb431dac235a1b31078caaa40e871b'}


def file_hash(path):
    with Path(path).open('rb') as stream:
        return hashlib.file_digest(stream, 'sha256').hexdigest()


def verify_hashes(hashes):
    for path, expected in hashes.items():
        if file_hash(path) != expected:
            raise ValueError(f'authenticated input changed: {path}')


verify_hashes({FIXED_PATH: FIXED_SHA, CONTRACT_PATH: CONTRACT_SHA})
loader = importlib.util.spec_from_file_location('sentiment_owned_fixed_collector', FIXED_PATH)
fixed = importlib.util.module_from_spec(loader)
loader.loader.exec_module(fixed)
leaf = fixed.leaf
digest = leaf.digest
write_once = leaf.write_once


def read(path):
    return json.loads(Path(path).read_text())


def checked_identity(obj):
    if obj['identity'] != digest({k: v for k, v in obj.items() if k != 'identity'}):
        raise ValueError('identity changed')


def select_groups(rows, count=256):
    groups = defaultdict(list)
    for index, row in enumerate(rows):
        normalized = ' '.join(unicodedata.normalize('NFKC', row['sentence']).casefold().split())
        group_id = hashlib.sha256(normalized.encode('utf-8')).hexdigest()
        groups[group_id].append({**row, 'source_row_index': index, 'normalized': normalized})
    if len(groups) < count:
        raise ValueError('not enough unique groups')
    ordered = []
    for group_id, items in sorted(groups.items()):
        first = items[0]
        if any(r['label'] not in (0, 1) for r in items):
            raise ValueError('not public labelled validation')
        ordered.append({'group_id': group_id, 'sentence': first['sentence'],
                        'normalized': first['normalized'], 'gold': LABELS[first['label']],
                        'source_indexes': [r['idx'] for r in items],
                        'source_row_indexes': [r['source_row_index'] for r in items],
                        'source_labels': [r['label'] for r in items]})
    report = {'source_rows': len(rows), 'unique_groups': len(groups),
              'duplicate_rows': len(rows)-len(groups),
              'conflicting_label_groups': sum(len(set(r['source_labels'])) > 1 for r in ordered),
              'selected_groups': count, 'all_groups_in_selection_order': ordered,
              'selection_uses_labels': False, 'normalization': 'NFKC, casefold, whitespace collapse'}
    return ordered[:count], report


def score_labels(content, gold):
    try:
        raw = json.loads(content) if isinstance(content, str) else None
    except ValueError:
        raw = None
    status = 'aligned'
    if not isinstance(raw, list) or any(not isinstance(x, str) for x in raw):
        status = 'invalid_json'
    elif len(raw) != len(gold):
        status = 'length_mismatch'
    predictions = raw if status == 'aligned' else [None]*len(gold)
    return {'parse_status': status, 'raw_array_length': len(raw) if isinstance(raw, list) else None,
            'schema_valid': status == 'aligned' and all(x in LABELS for x in predictions),
            'predictions': predictions, 'records': len(gold),
            'noncanonical_labels': sum(x not in LABELS for x in predictions) if status == 'aligned' else 0,
            'trec_label_leakage': sum(x in leaf.LABELS for x in raw) if isinstance(raw, list) else 0,
            'strict_correct': sum(a == b for a, b in zip(predictions, gold, strict=True))}


def layout(records):
    if len(records) != 256:
        raise ValueError('exactly256 selected records required')
    contract = read(CONTRACT_PATH)
    contract['baseline_user_prefix'] = (
        'Classify the overall sentiment of each movie-review sentence. Return only a JSON array '
        'of labels in the same order as the input sentences, with exactly one label per sentence. '
        'Use exactly these two labels: "negative", "positive". Do not call tools.\n')
    design = {'contract': contract, 'definitions':
              'negative: an unfavorable or critical overall opinion of the movie.\n'
              'positive: a favorable or approving overall opinion of the movie.\n'
              'Choose the overall sentiment, including when wording is mixed or ironic.\nSentences:\n',
              'labels': LABELS, 'max_tokens': 1024, 'max_concurrent_calls': 4,
              'wall_time_cap_seconds': 1200, 'call_timeout_seconds': 120,
              'contexts': [], 'batches': [], 'coordinates': [], 'plan': [],
              'model_alias': '__UNBOUND_WEIGHT__'}
    for cindex in range(4):
        context = {'id': f'sst2-validation-context-{cindex:02d}', 'records': records[cindex*64:(cindex+1)*64]}
        design['contexts'].append(context)
        for cell, size in [('natural5', 5), ('natural64', 64), ('schema64', 64)]:
            batch_ids = []
            for start in range(0, 64, size):
                subset = context['records'][start:start+size]
                bid = len(design['batches'])
                batch_ids.append(bid)
                design['batches'].append({'batch_id': bid, 'context_id': context['id'],
                    'questions': [r['sentence'] for r in subset], 'gold': [r['gold'] for r in subset],
                    'record_indices': list(range(start+1, start+len(subset)+1)),
                    'question_group_ids': [r['group_id'] for r in subset]})
            for repeat, seed in enumerate([739019, 739043]):
                cid = digest([context['id'], cell, seed])
                coordinate = {'id': cid, 'pair_id': digest([context['id'], seed]),
                              'context_id': context['id'], 'cell': cell, 'seed': seed, 'repeat': repeat}
                design['coordinates'].append(coordinate)
                for bindex, bid in enumerate(batch_ids):
                    design['plan'].append({**coordinate, 'id': digest([cid, bindex]),
                        'coordinate_id': cid, 'batch_id': bid, 'batch_index': bindex,
                        'dispatch_order': len(design['plan']), 'arm': cell})
    return design


def make_request(design, row):
    return leaf.make_request(design, {**row, 'arm': 'both' if row['cell'] == 'schema64' else 'definitions'}, design['model_alias'])


def score_coordinate(design, coordinate, records):
    selected = [r for r in records if r['coordinate']['coordinate_id'] == coordinate['id']]
    planned = [r for r in design['plan'] if r['coordinate_id'] == coordinate['id']]
    item_rows = []
    for call in selected:
        batch = design['batches'][call['coordinate']['batch_id']]
        score = call.get('score')
        predictions = score['predictions'] if score else [None]*len(batch['gold'])
        for index, group, gold, prediction in zip(batch['record_indices'], batch['question_group_ids'], batch['gold'], predictions, strict=True):
            item_rows.append({'position': index, 'group_id': group, 'gold': gold,
                              'prediction': prediction, 'correct': prediction == gold,
                              'aligned': bool(score and score['parse_status'] == 'aligned')})
    complete = len(selected) == len(planned)
    errors = sum(r.get('score') is None for r in selected)
    contract = complete and not errors and all(r['score']['schema_valid'] for r in selected)
    strict = int(contract and sum(r['correct'] for r in item_rows) == 64) if complete and not errors else None
    return {'coordinate': coordinate, 'complete': complete, 'infrastructure_errors': errors,
            'strict_reward': strict, 'full_array_coverage': contract,
            'canonical_correct': sum(r['correct'] for r in item_rows), 'planned_items': 64,
            'items': sorted(item_rows, key=lambda r: r['position']),
            'position_quartile_correct': [sum(r['correct'] for r in item_rows if q*16 < r['position'] <= (q+1)*16) for q in range(4)],
            'truncated_calls': sum(r.get('finish_reason') == 'length' for r in selected),
            'trec_label_leakage': sum((r.get('score') or {}).get('trec_label_leakage', 0) for r in selected),
            'usage': {k: sum(r.get('usage', {}).get(k) or 0 for r in selected) for k in ['logical_input_tokens', 'cached_input_tokens', 'completion_tokens']}}


def acquire():
    CACHE.mkdir(parents=True, exist_ok=True)
    urls = {
        'validation.parquet': f'https://huggingface.co/datasets/stanfordnlp/sst2/resolve/{REVISION}/data/validation-00000-of-00001.parquet',
        'README.md': f'https://huggingface.co/datasets/stanfordnlp/sst2/resolve/{REVISION}/README.md',
        'dataset-api.json': f'https://huggingface.co/api/datasets/stanfordnlp/sst2/revision/{REVISION}',
        'HF-datasets-APACHE-2.0.txt': 'https://raw.githubusercontent.com/huggingface/datasets/88896a7b28610ace95e444b94f9a4bc332cc1ee3/LICENSE',
        'Stanford-sentiment.html': 'https://nlp.stanford.edu/sentiment/index.html',
    }
    artifacts = []
    for name, url in urls.items():
        path = CACHE / name
        if path.exists():
            raise ValueError('acquisition destination already exists; inspect ownership, never overwrite')
        with urllib.request.urlopen(url, timeout=60) as response:
            data = response.read()
            final_url = response.url
        with path.open('xb') as stream:
            stream.write(data)
        artifacts.append({'path': str(path), 'url': url, 'final_url': final_url,
                          'retrieved_utc': datetime.now(timezone.utc).isoformat(),
                          'sha256': file_hash(path), 'bytes': len(data)})
    if read(CACHE / 'dataset-api.json')['sha'] != REVISION:
        raise ValueError('dataset revision mismatch')
    manifest = {'dataset': 'stanfordnlp/sst2', 'revision': REVISION, 'split': 'validation',
                'underlying_dataset_license': 'unknown (official card; not inferred from software)',
                'hf_loader_library_license': 'Apache-2.0', 'hf_loader_library_commit': '88896a7b28610ace95e444b94f9a4bc332cc1ee3',
                'remote_loader_executed': False, 'artifacts': artifacts}
    write_once(CACHE / 'ACQUISITION.json', manifest)
    print(json.dumps(manifest))


def template_ids(tokenizer, body):
    rendered = tokenizer.apply_chat_template(body['messages'], tools=body['tools'], tokenize=True, add_generation_prompt=True)
    ids = rendered['input_ids'] if isinstance(rendered, Mapping) else rendered
    if not isinstance(ids, list) or not ids or any(not isinstance(x, int) for x in ids):
        raise ValueError('expected flat native prompt token IDs')
    return ids


def prepare():
    import pyarrow
    import pyarrow.parquet as pq
    from transformers import AutoTokenizer
    acquisition = read(CACHE / 'ACQUISITION.json')
    verify_hashes({r['path']: r['sha256'] for r in acquisition['artifacts']})
    rows = pq.read_table(CACHE / 'validation.parquet').to_pylist()
    if len(rows) != 872:
        raise ValueError('validation split shape changed')
    selected, dedup = select_groups(rows)
    design = layout(selected)
    tokenizer = AutoTokenizer.from_pretrained(BASE, local_files_only=True, trust_remote_code=False)
    prompt_tokens = {}
    for row in design['plan']:
        body = make_request(design, row)
        ids = template_ids(tokenizer, body)
        if len(ids)+body['max_tokens'] > 8192:
            raise ValueError('prompt plus reserved output exceeds8192')
        prompt_tokens[row['id']] = {'hf_estimated_prompt_ids': ids, 'length': len(ids), 'reserved_total': len(ids)+1024}
    data = {'selected': selected, 'dedup': dedup, 'design': design, 'acquisition': acquisition,
            'versions': {'python': platform.python_version(), 'pyarrow': pyarrow.__version__},
            'prompt_token_estimates': prompt_tokens,
            'request_sha256': {r['id']: digest(make_request(design, r)) for r in design['plan']}}
    write_once(ROOT / 'DATA.json', data)
    sources = [Path(__file__), ROOT/'test_driver.py', ROOT/'DESIGN.md', ROOT/'DATA.json',
               FIXED_PATH, CONTRACT_PATH, SIDECARS/'trec-leaf-contract-probe-v1/driver.py', CACHE/'ACQUISITION.json']
    sources += [Path(r['path']) for r in acquisition['artifacts']]
    sources += [BASE/name for name in ['tokenizer.json', 'tokenizer_config.json', 'chat_template.jinja', 'local-research-manifest.json'] if (BASE/name).exists()]
    spec = {'schema': ROOT.name, 'data_path': str(ROOT/'DATA.json'),
            'source_sha256': {str(p): file_hash(p) for p in sources},
            'weight_conditions': ['original', 'old_sft', 'A', 'B'],
            'calls_per_weight': 120, 'total_calls': 480, 'max_reserved_tokens': max(r['reserved_total'] for r in prompt_tokens.values()),
            'model_calls_before_freeze': 0}
    spec['identity'] = digest(spec)
    write_once(ROOT/'SPEC.json', spec)
    print(json.dumps(spec))


def authenticate_weight(condition, endpoint, sources):
    adapter = Path(endpoint['adapter']['path'])
    for name, key in [('adapter_model.safetensors', 'model_sha256'), ('adapter_config.json', 'config_sha256')]:
        sources[str(adapter/name)] = endpoint['adapter'][key]
    base = endpoint['base_model']
    if base['path'] != str(BASE) or base['manifest_sha256'] != '19619b44b0bd30bf5debe0960e6dfd6acc5be8287c581727456aa5d17699c18f':
        raise ValueError('base identity mismatch')
    sources[str(BASE/'local-research-manifest.json')] = base['manifest_sha256']
    if condition in WEIGHTS:
        if endpoint['adapter']['model_sha256'] != WEIGHTS[condition]:
            raise ValueError('original/oldSFT weight identity mismatch')
        config_sha = {'original': 'e6828a7cbb97028a871958e71ba6b8a75ac4887c25008ac4dbf7366bd298fbc4',
                      'old_sft': 'ec773bc3b9de58af98a7c4dce9a40af795a4d05cd47284dbbfb27eac99b74174'}[condition]
        if endpoint['adapter']['config_sha256'] != config_sha:
            raise ValueError('original/oldSFT configuration identity mismatch')
        if condition == 'old_sft':
            selection_path = SIDECARS/'trec-leaf-sft-v1/outputs/attempt-001/SELECTION.json'
            sources[str(selection_path)] = '46025168d985242c4d237fb7691ea94aa6658b7b8647fdf2771c21c00b48f0ed'
            if adapter.resolve() != Path(read(selection_path)['selected']['checkpoint']).resolve():
                raise ValueError('oldSFT path differs from validation-only selection')
    else:
        arm = SIDECARS/'leaf-mixed-size-sft-v1'/condition
        manifest = read(arm/'MANIFEST.json')
        checked_identity(manifest)
        if manifest['identity'] != MIXED_IDENTITIES[condition]:
            raise ValueError('mixed curriculum manifest identity mismatch')
        result_path = arm/'outputs/attempt-001/RESULT.json'
        result = read(result_path)
        selection_path = result_path.with_name('SELECTION.json')
        selection = read(selection_path)
        expected_step = {'A': 206, 'B': 204}[condition]
        if result['identity'] != manifest['identity'] or result['selected'] != selection['selected'] or result['selected']['epoch'] != 2 or result['optimizer_steps'] != expected_step:
            raise ValueError('not authenticated fixed final epoch2 result')
        if selection['post_training_test_inspected'] is not False or selection['identity'] != manifest['identity']:
            raise ValueError('checkpoint selection provenance mismatch')
        if adapter.resolve() != Path(result['selected']['checkpoint']).resolve() or adapter.parent != result_path.parent or adapter.name != f'checkpoint-{expected_step:04d}':
            raise ValueError('endpoint does not bind exact final checkpoint')
        state_path = adapter/'state.json'
        state = read(state_path)
        if state['identity'] != manifest['identity'] or state['epoch'] != 2 or state['cursor'] != 0 or state['step'] != expected_step:
            raise ValueError('final checkpoint state mismatch')
        required = {'adapter_model.safetensors', 'adapter_config.json', 'optimizer.pt', 'rng_state.pt'}
        if not required <= state['files_sha256'].keys() or any(Path(n).name != n for n in state['files_sha256']):
            raise ValueError('checkpoint member inventory mismatch')
        if (state['files_sha256']['adapter_model.safetensors'] != endpoint['adapter']['model_sha256']
            or state['files_sha256']['adapter_config.json'] != endpoint['adapter']['config_sha256']):
            raise ValueError('endpoint/state weight hashes disagree')
        sources.update({str(adapter/name): sha for name, sha in state['files_sha256'].items()})
        sources[str(arm/'RECIPE.json')] = manifest['recipe_sha256']
        sources[str(arm/'data.json')] = manifest['data_sha256']
        sources.update(read(arm/'RECIPE.json')['source_hashes'])
        for path in [arm/'MANIFEST.json', result_path, selection_path, state_path]:
            sources[str(path)] = file_hash(path)
    verify_hashes(sources)


def bind(condition, endpoint_path, destination):
    frozen = read(ROOT/'SPEC.json')
    checked_identity(frozen)
    verify_hashes(frozen['source_sha256'])
    data = read(frozen['data_path'])
    endpoint = read(endpoint_path)
    sources = dict(frozen['source_sha256'])
    sources[str(ROOT/'SPEC.json')] = file_hash(ROOT/'SPEC.json')
    sources[str(endpoint_path.resolve())] = file_hash(endpoint_path)
    authenticate_weight(condition, endpoint, sources)
    design = copy.deepcopy(data['design'])
    design['model_alias'] = endpoint['model_alias']
    spec = {'schema': ROOT.name+'-bound', 'prepared_identity': frozen['identity'],
            'condition': condition, 'endpoint': endpoint, 'source_sha256': sources, 'design': design,
            'request_sha256': {r['id']: digest(make_request(design, r)) for r in design['plan']},
            'selection_from_transfer_outcomes': False}
    spec['identity'] = digest(spec)
    write_once(destination, spec)
    print(json.dumps({'bound': str(destination), 'identity': spec['identity']}))


async def run(spec_path, output):
    import httpx
    spec = read(spec_path)
    checked_identity(spec)
    verify_hashes(spec['source_sha256'])
    endpoint = spec['endpoint']
    authenticate_weight(spec['condition'], endpoint, dict(spec['source_sha256']))
    if endpoint['host'] != '127.0.0.1':
        raise ValueError('only explicit local research endpoint supported')
    url = f"http://{endpoint['host']}:{endpoint['port']}/v1"
    key = os.environ.get(endpoint.get('api_key_env', ''), 'local-only')
    output.mkdir(parents=True, exist_ok=False)
    (output/'calls').mkdir()
    (output/'coordinates').mkdir()
    write_once(output/'SPEC.json', spec)
    fixed.make_request = make_request
    fixed.score_coordinate = score_coordinate
    fixed.leaf.score_labels = score_labels
    async with httpx.AsyncClient(timeout=spec['design']['call_timeout_seconds'], headers={'Authorization': 'Bearer '+key}) as client:
        response = await client.get(url+'/models')
        response.raise_for_status()
        models = response.json()
        entries = [r for r in models.get('data', []) if r['id'] == endpoint['model_alias']]
        if len(entries) != 1 or entries[0].get('root') != endpoint['adapter']['path']:
            raise ValueError('runtime alias/root differs from bound adapter')
        write_once(output/'PREFLIGHT.json', {'models': models, 'time': time.time(), 'endpoint': endpoint,
            'python': platform.python_version(), 'httpx': httpx.__version__, 'request_spec_sha256': file_hash(spec_path)})
        records, reason = await fixed.collect_calls(client, url, spec, output)
    coordinates = [score_coordinate(spec['design'], c, records) for c in spec['design']['coordinates']]
    cells = []
    for cell in ['natural5', 'natural64', 'schema64']:
        selected = [c for c in coordinates if c['coordinate']['cell'] == cell]
        cells.append({'cell': cell, 'planned_coordinates': 8,
            'strict_successes': sum(c['strict_reward'] or 0 for c in selected),
            'observable_coordinates': sum(c['strict_reward'] is not None for c in selected),
            'array_coverage': sum(c['full_array_coverage'] for c in selected),
            'canonical_correct': sum(c['canonical_correct'] for c in selected), 'planned_items': 512,
            'quartile_correct': [sum(c['position_quartile_correct'][q] for c in selected) for q in range(4)],
            'trec_label_leakage': sum(c['trec_label_leakage'] for c in selected)})
    write_once(output/'SUMMARY.json', {'identity': spec['identity'], 'condition': spec['condition'],
        'calls': len(records), 'planned_calls': 120, 'stop_reason': reason, 'cells': cells,
        'coordinates': coordinates, 'actual_prompt_id_capture_calls': sum(r.get('capture', {}).get('prompt_token_ids', False) for r in records)})
    return int(bool(reason) or len(records) != 120)


def main():
    parser = argparse.ArgumentParser()
    subs = parser.add_subparsers(dest='command', required=True)
    subs.add_parser('acquire')
    subs.add_parser('prepare')
    b = subs.add_parser('bind')
    b.add_argument('--condition', choices=['original', 'old_sft', 'A', 'B'], required=True)
    b.add_argument('--endpoint', type=Path, required=True)
    b.add_argument('--output', type=Path, required=True)
    r = subs.add_parser('run')
    r.add_argument('--spec', type=Path, required=True)
    r.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    if args.command == 'acquire':
        acquire()
    elif args.command == 'prepare':
        prepare()
    elif args.command == 'bind':
        bind(args.condition, args.endpoint, args.output)
    else:
        raise SystemExit(asyncio.run(run(args.spec, args.output)))


if __name__ == '__main__':
    main()
