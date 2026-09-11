"""Narrow grouped anchor control over frozen source data and qualified callbacks."""
from __future__ import annotations

import hashlib
import importlib.util
import json
import os
import unicodedata
from collections import Counter, defaultdict
from copy import deepcopy
from functools import lru_cache
from pathlib import Path

ROOT = Path(__file__).resolve().parent
SIDE = ROOT.parent
CORR = SIDE / 'leaf-correspondence-controls-v1/driver.py'
CORR_SHA = '6fa2846b144f863cea79f2c82ee9e6d07d00104aba4f01dc8d95ec51fd1a49c8'
SST = SIDE / 'leaf-sentiment-transfer-v1/driver.py'
SST_SHA = 'eb9509ed00a85cd942d959407deb8c80f495f7fec2426f477265af48e407cb63'
TREC_DATA = SIDE / 'leaf-composition-transfer-v1/prepared-v1/DATA.json'
TREC_SHA = '1ea4640da5a8e3e305bee7f79d5abeecb02507d6bcc33d709d1c7209fd47bfc2'
SEEDS = [910901, 910907]
PERMUTATION_MASTER = 910883
INPUT_MARKER = '\nInput records (ID to text, in input order):\n'


def file_hash(path):
    with Path(path).open('rb') as stream:
        return hashlib.file_digest(stream, 'sha256').hexdigest()


def load(name, path, expected):
    if file_hash(path) != expected:
        raise ValueError('qualified source changed: ' + str(path))
    loader = importlib.util.spec_from_file_location(name, path)
    result = importlib.util.module_from_spec(loader)
    loader.loader.exec_module(result)
    return result


corr = load('anchor_private_correspondence', CORR, CORR_SHA)
sst = load('anchor_private_sentiment', SST, SST_SHA)
digest = corr.digest


def read(path):
    return json.loads(Path(path).read_text())


def serialize(value):
    return json.dumps(value, ensure_ascii=False, separators=(',', ':'), allow_nan=False)


def write_once(path, value):
    """Preserve actual object/schema insertion order, with exclusive durable writes."""
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open('x') as stream:
        stream.write(serialize(value) + '\n')
        stream.flush()
        os.fsync(stream.fileno())


def normalized_hash(text):
    normalized = ' '.join(unicodedata.normalize('NFKC', text).casefold().split())
    return hashlib.sha256(normalized.encode()).hexdigest()


@lru_cache(maxsize=1)
def load_data():
    import pyarrow.parquet as pq
    if file_hash(TREC_DATA) != TREC_SHA:
        raise ValueError('six exposed TREC contexts changed')
    previous_spec = read(SST.parent / 'SPEC.json')
    sst.checked_identity(previous_spec)
    sst.verify_hashes(previous_spec['source_sha256'])
    previous = read(SST.parent / 'DATA.json')
    old = {r['group_id'] for c in previous['design']['contexts'] for r in c['records']}
    assert len(old) == 256
    assert old == {normalized_hash(r['sentence']) for c in previous['design']['contexts'] for r in c['records']}
    rows = pq.read_table(sst.CACHE / 'validation.parquet').to_pylist()
    _, dedup = sst.select_groups(rows)
    remaining = [r for r in dedup['all_groups_in_selection_order'] if r['group_id'] not in old]
    chosen = remaining[:256]
    assert len(chosen) == 256 and not old & {r['group_id'] for r in chosen}
    assert all(normalized_hash(r['sentence']) == r['group_id'] for r in chosen)
    contexts = []
    for c in read(TREC_DATA)['contexts']:
        records = [{'question': r['question'], 'group_id': r['group_id'], 'gold_label': r['gold'],
                    'source_line_1based': r['source_line_1based']} for r in c['records']]
        contexts.append({'dataset': 'trec', 'source_context_id': c['id'], 'records': records})
    assert len(contexts) == 6 and len({r['group_id'] for c in contexts for r in c['records']}) == 384
    for index in range(4):
        records = [{'question': r['sentence'], 'group_id': r['group_id'], 'gold_label': r['gold'],
                    'source_indexes': r['source_indexes'], 'source_row_indexes': r['source_row_indexes']}
                   for r in chosen[index * 64:(index + 1) * 64]]
        contexts.append({'dataset': 'sst2', 'source_context_id': f'fresh-sst2-{index:02d}', 'records': records})
    for index, c in enumerate(contexts):
        c['index'] = index
        for position, r in enumerate(c['records']):
            r['id'] = f'q{index * 64 + position + 1:04d}'
            r['source_position'] = position + 1
            r['question_group_sha256'] = r['group_id']
        c['permutations'] = [sorted(range(64), key=lambda j: digest([ROOT.name, PERMUTATION_MASTER,
            c['source_context_id'], permutation, c['records'][j]['group_id']])) for permutation in range(2)]
    trec_inventory = read(SIDE / 'trec-leaf-split-provenance-v1/INVENTORY.json')
    trec_acquisition_path = next(Path(p) for p in trec_inventory['source_file_sha256']
        if '/trec-leaf-splits.' in p and p.endswith('/PROVENANCE.json'))
    trec_acquisition = read(trec_acquisition_path)
    sst_acquisition = read(sst.CACHE / 'ACQUISITION.json')
    return {'contexts': contexts, 'sst_provenance': {'dataset': 'stanfordnlp/sst2',
        'revision': sst.REVISION, 'split': 'validation', 'rows': len(rows), 'all_groups': dedup['unique_groups'],
        'remaining_after_previous': len(remaining), 'new_groups': len(chosen), 'new_old_group_intersection': 0,
        'previous_groups': sorted(old), 'new_groups_sha256': digest([r['group_id'] for r in chosen]),
        'selection': 'first256 remaining normalized SHA256 groups in lexical hash order; no labels used',
        'normalization': 'NFKC, casefold, whitespace collapse', 'task_transfer_not_label_rename': True,
        'acquisition': {k: v for k, v in sst_acquisition.items() if k != 'artifacts'},
        'source_artifacts': [{k: v for k, v in a.items() if k != 'final_url'}
            for a in sst_acquisition['artifacts']]},
        'trec_provenance': {'exposed_context_path': str(TREC_DATA), 'sha256': TREC_SHA,
            'groups': 384, 'contexts': 6, 'fresh_context_group_claim': False,
            'licenses': trec_inventory['licenses'], 'source_test_file_sha256': '033f22c028c2bbba9ca682f68ffe204dc1aa6e1cf35dd6207f2d4ca67f0d0e8e',
            'acquisition_manifest': str(trec_acquisition_path),
            'acquisition_manifest_sha256': file_hash(trec_acquisition_path),
            'retrieved_utc_date': trec_acquisition['retrieved_utc_date'],
            'source_artifacts': [a for a in trec_acquisition['files']
                if Path(a['path']).name in ['TREC_10.label', 'trec_hf_loader.py']],
            'content_identity_note': trec_acquisition['content_identity_note']},
        'permutation_master': PERMUTATION_MASTER, 'sampling_seeds': SEEDS}


def build_design(data):
    contexts = deepcopy(data['contexts'])
    source = read(SIDE / 'leaf-correspondence-controls-v1/SPEC-REPRESENTATION.runtime-order-v2.json')['design']
    sentiment = read(SST.parent / 'DATA.json')['design']
    value = {'contexts': contexts, 'contract': source['contract'], 'model_alias': corr.PLACEHOLDER,
        'labels': source['labels'], 'definitions': source['definitions'],
        'task_definitions': {'trec': source['definitions'], 'sst2': sentiment['definitions'].removesuffix('Sentences:\n')},
        'task_labels': {'trec': source['labels'], 'sst2': sentiment['labels']},
        'max_tokens': 3072, 'max_concurrent_calls': 4, 'call_timeout_seconds': 120,
        'wall_time_cap_seconds': 1800, 'plan': [], 'coordinates': [], 'batches': []}
    for size in [64, 5]:
        for c in contexts:
            for permutation in ([0, 1] if size == 64 else [0]):
                ordered = [c['records'][i] for i in c['permutations'][permutation]]
                for repeat, seed in enumerate(SEEDS):
                    arms = ['anonymous', 'indexed'] if (c['index'] + permutation + repeat) % 2 == 0 else ['indexed', 'anonymous']
                    for arm in arms:
                        co = {'dataset': c['dataset'], 'context_index': c['index'], 'source_context_id': c['source_context_id'],
                            'size': size, 'permutation': permutation, 'repeat': repeat, 'seed': seed, 'arm': arm}
                        co['id'] = digest([ROOT.name, co])
                        value['coordinates'].append(co)
                        for start in range(0, 64, size):
                            subset = deepcopy(ordered[start:start + size])
                            bid = len(value['batches'])
                            value['batches'].append({'questions': [r['question'] for r in subset],
                                'gold': {'records': subset, 'order': list(range(len(subset))), 'arm': arm,
                                         'labels': value['task_labels'][c['dataset']]}})
                            row = {**co, 'coordinate_id': co['id'], 'batch_id': bid, 'start': start,
                                   'dispatch_order': len(value['plan'])}
                            row['id'] = digest([co['id'], start])
                            value['plan'].append(row)
    return value


def make_request(value, row):
    records = value['batches'][row['batch_id']]['gold']['records']
    labels = value['task_labels'][row['dataset']]
    body = corr.leaf.make_request(value, {**row, 'arm': 'both'}, value['model_alias'])
    prefix = ('Classify the answer type of each question.\n' if row['dataset'] == 'trec'
              else 'Classify the overall sentiment of each movie-review sentence.\n')
    instruction = ('Return only a JSON array of labels in input order, exactly one label per input ID.'
        if row['arm'] == 'anonymous' else 'Return only a JSON object mapping every input ID to its one label. Include each input ID exactly once, with no missing or extra IDs. Emit entries in input order.')
    body['messages'][1]['content'] = (prefix + instruction + '\nAllowed labels: ' + ', '.join(labels)
        + '.\n\n' + value['task_definitions'][row['dataset']] + INPUT_MARKER
        + json.dumps({r['id']: r['question'] for r in records}, ensure_ascii=False))
    label_schema = {'type': 'string', 'enum': labels}
    schema = ({'type': 'array', 'items': label_schema, 'minItems': len(records), 'maxItems': len(records)}
        if row['arm'] == 'anonymous' else {'type': 'object', 'properties': {r['id']: deepcopy(label_schema) for r in records},
            'required': [r['id'] for r in records], 'additionalProperties': False})
    body['structured_outputs'] = {'json': schema}
    return body


def score_labels(content, gold):
    score = corr.score_response(content, gold)
    score['noncanonical_labels'] = sum(p not in gold['labels'] for p in score['predictions']) if score['parse_status'] == 'aligned' else 0
    score['schema_valid'] = score['parse_status'] == 'aligned' and score['noncanonical_labels'] == 0
    return score


def score_coordinate(value, coordinate, records):
    planned = [r for r in value['plan'] if r['coordinate_id'] == coordinate['id']]
    items, physical = [], []
    for call in records:
        score = call.get('score')
        row = call['coordinate']
        for index, source in enumerate(value['batches'][row['batch_id']]['gold']['records']):
            items.append({'id': source['id'], 'group_id': source['group_id'], 'source_position': source['source_position'],
                'input_position': row['start'] + index + 1, 'gold': source['gold_label'],
                'prediction': score['predictions'][index] if score else None,
                'output_position': row['start'] + score['output_positions'][index] if score and score['output_positions'][index] else None,
                'aligned': bool(score and score['aligned_records']),
                'correct': bool(score and score['predictions'][index] == source['gold_label'])})
        raw = call.get('raw_response') or {}
        ids = raw.get('prompt_token_ids')
        expected = value.get('rendered_prompts', {}).get(row['id'], {})
        physical.append({'call_id': row['id'], 'captured': isinstance(ids, list),
            'physical_token_ids_sha256': digest(ids) if isinstance(ids, list) else None,
            'expected_typed_token_ids_sha256': expected.get('typed_token_ids_sha256'),
            'typed_template_equal': digest(ids) == expected.get('typed_token_ids_sha256') if isinstance(ids, list) and expected else None,
            'reported_usage_length_equal': len(ids) == raw.get('usage', {}).get('prompt_tokens') if isinstance(ids, list) else None})
    complete = len(records) == len(planned)
    failures = sum(r.get('score') is None for r in records)
    valid = complete and not failures and all(r['score']['schema_valid'] for r in records)
    usage = [r.get('usage') or corr.leaf.usage_metrics((r.get('raw_response') or {}).get('usage') or {}) for r in records]
    return {'coordinate': coordinate, 'planned_calls': len(planned), 'recorded_calls': len(records),
        'complete': complete, 'fully_valid': valid, 'infrastructure_errors': failures,
        'schema_valid_calls': sum(bool(r.get('score') and r['score']['schema_valid']) for r in records),
        'strict_full64_correct': int(valid and all(i['correct'] for i in items)) if complete and not failures else None,
        'canonical_correct': sum(r['correct'] for r in items), 'aligned_records': sum(r['aligned'] for r in items),
        'records': items, 'physical_prompts': physical,
        'usage': {k: sum(r.get(k) or 0 for r in usage) for k in ['logical_input_tokens', 'cached_input_tokens', 'uncached_input_tokens', 'completion_tokens']},
        'missing_usage': {k: sum(r.get(k) is None for r in usage) for k in ['logical_input_tokens', 'cached_input_tokens', 'uncached_input_tokens', 'completion_tokens']},
        'length_stops': sum(r.get('finish_reason') == 'length' for r in records)}


def summarize(value, records):
    coordinates = [score_coordinate(value, co, [r for r in records if r['coordinate']['coordinate_id'] == co['id']]) for co in value['coordinates']]
    cells, pairs = [], []
    grouped = defaultdict(dict)
    for r in coordinates:
        co = r['coordinate']
        grouped[co['dataset'], co['context_index'], co['size'], co['permutation'], co['repeat']][co['arm']] = r
    for key, arms in grouped.items():
        a, b = arms['anonymous'], arms['indexed']
        observed = all(r['complete'] and r['infrastructure_errors'] == 0 for r in [a, b])
        pairs.append({'dataset': key[0], 'context_index': key[1], 'size': key[2], 'permutation': key[3], 'repeat': key[4],
            'indexed_minus_anonymous_correct': b['canonical_correct'] - a['canonical_correct'] if observed else None,
            'jointly_valid': a['fully_valid'] and b['fully_valid'], 'both_observed': observed})
    for dataset in ['trec', 'sst2']:
        for size in [5, 64]:
            for arm in ['anonymous', 'indexed']:
                selected = [r for r in coordinates if r['coordinate']['dataset'] == dataset and r['coordinate']['size'] == size and r['coordinate']['arm'] == arm]
                items = [i for r in selected for i in r['records']]
                cells.append({'dataset': dataset, 'size': size, 'arm': arm, 'planned_coordinates': len(selected),
                    'completed_coordinates': sum(r['complete'] for r in selected), 'valid_full64_coordinates': sum(r['fully_valid'] for r in selected),
                    'planned_assignments': len(selected) * 64, 'canonical_correct': sum(r['correct'] for r in items),
                    'aligned_assignments': sum(r['aligned'] for r in items),
                    'output_quartiles': [{'quartile': q, 'aligned': sum(i['aligned'] and i['output_position'] is not None and (i['output_position'] - 1) // 16 == q for i in items),
                        'correct': sum(i['correct'] and i['output_position'] is not None and (i['output_position'] - 1) // 16 == q for i in items)} for q in range(4)],
                    'usage': {k: sum(r['usage'][k] for r in selected) for k in ['logical_input_tokens', 'cached_input_tokens', 'uncached_input_tokens', 'completion_tokens']},
                    'length_stops': sum(r['length_stops'] for r in selected)})
    return {'cells': cells, 'paired_context_coordinates': pairs, 'coordinates': coordinates,
        'unit_caution': 'Six TREC and four SST contexts; repeated seeds/permutations/source questions are nested, not independent calls. Different tasks reported separately.',
        'primary': 'context-paired indexed minus anonymous64 correctness, coverage separate; batch5 only permutation0'}


corr.fixed.make_request = make_request
corr.fixed.score_coordinate = score_coordinate
corr.fixed.leaf.score_labels = score_labels
corr.fixed.leaf.write_once = write_once
collect_calls = corr.fixed.collect_calls
