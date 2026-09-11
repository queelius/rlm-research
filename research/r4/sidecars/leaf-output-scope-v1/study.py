"""Only the declared input/output scope changes; use qualified leaf helpers."""
from __future__ import annotations

import hashlib
import importlib.util
import json
from collections import Counter, defaultdict
from copy import deepcopy
from pathlib import Path

ROOT = Path(__file__).resolve().parent
UPSTREAM = ROOT.parent / 'leaf-correspondence-controls-v1'
SOURCE = UPSTREAM / 'SPEC-ROTATION.runtime-order-v2.json'
SOURCE_SHA = 'e08813e94cb2bf054437749b1ca86640edcc59b942840165062bd1207786d04d'
HELPER_SHA = '6fa2846b144f863cea79f2c82ee9e6d07d00104aba4f01dc8d95ec51fd1a49c8'
SEEDS = [981261601, 981261602]
ARMS = ('all64', 'full16', 'local16')
TARGET_MARKER = '\nRequested record IDs (in output order):\n'
INPUT_MARKER = '\nVisible input records:\n'
INSTRUCTION = ('Classify only the requested record IDs, in the listed order. '
    'Return only a JSON array of labels, exactly one for each requested ID; '
    'do not output IDs or labels for other records. Allowed labels: \n')
USAGE_KEYS = ('logical_input_tokens', 'cached_input_tokens', 'uncached_input_tokens', 'completion_tokens')


def read(path):
    return json.loads(Path(path).read_text())


def file_hash(path):
    with Path(path).open('rb') as stream:
        return hashlib.file_digest(stream, 'sha256').hexdigest()


if file_hash(UPSTREAM / 'driver.py') != HELPER_SHA or file_hash(SOURCE) != SOURCE_SHA:
    raise ValueError('qualified correspondence source changed')
loader = importlib.util.spec_from_file_location('scope_private_correspondence', UPSTREAM / 'driver.py')
corr = importlib.util.module_from_spec(loader)
loader.loader.exec_module(corr)
digest, write_once = corr.digest, corr.write_once


def design():
    original = read(SOURCE)['design']
    contexts = deepcopy(original['contexts'])
    records = [record for context in contexts for record in context['records']]
    if (len(contexts) != 4 or any(len(context['records']) != 64 for context in contexts)
            or [r['record_index'] for r in records] != list(range(1, 257))
            or len({r['question_group_sha256'] for r in records}) != 256):
        raise ValueError('source context/group/order changed')
    plan, batches = [], []
    for repeat, seed in enumerate(SEEDS):
        for context in contexts:
            treatments = [('all64', 0)] + [(arm, offset) for offset in (0, 16, 32, 48)
                                           for arm in ('full16', 'local16')]
            shift = (context['index'] + repeat * 4) % 9
            for arm, offset in treatments[shift:] + treatments[:shift]:
                target = list(range(64)) if arm == 'all64' else list(range(offset, offset + 16))
                visible = target if arm == 'local16' else list(range(64))
                row = {'arm': arm, 'offset': offset, 'context_index': context['index'],
                    'seed': seed, 'repeat': repeat, 'target_positions': target,
                    'visible_positions': visible, 'batch_id': len(batches), 'dispatch_order': len(plan)}
                row['id'] = digest([ROOT.name, context['index'], seed, arm, offset])
                row['coordinate_id'] = row['id']
                plan.append(row)
                batches.append({'questions': [context['records'][i]['question'] for i in visible],
                    'gold': {'arm': 'anonymous', 'order': list(range(len(target))),
                             'records': [deepcopy(context['records'][i]) for i in target]}})
    return {'comparison': 'output_scope', 'contexts': contexts, 'plan': plan,
        'coordinates': deepcopy(plan), 'batches': batches, 'model_alias': corr.PLACEHOLDER,
        'contract': deepcopy(original['contract']), 'labels': deepcopy(original['labels']),
        'definitions': original['definitions'], 'max_tokens': 1024, 'max_concurrent_calls': 4,
        'call_timeout_seconds': 60, 'wall_time_cap_seconds': 1200,
        'dispatch_order': 'cyclic nine-treatment order shifted by context_index+4*repeat'}


def make_request(value, row):
    records = value['contexts'][row['context_index']]['records']
    body = corr.leaf.make_request(value, {**row, 'arm': 'both'}, value['model_alias'])
    visible = [{'id': records[i]['id'], 'question': records[i]['question']}
               for i in row['visible_positions']]
    targets = [records[i]['id'] for i in row['target_positions']]
    body['messages'][1]['content'] = (INSTRUCTION + ', '.join(value['labels']) + '.\n\n'
        + value['definitions'] + TARGET_MARKER + json.dumps(targets) + INPUT_MARKER + json.dumps(visible))
    body['structured_outputs']['json']['minItems'] = len(targets)
    body['structured_outputs']['json']['maxItems'] = len(targets)
    return body


def score_coordinate(value, coordinate, records):
    selected = [r for r in records if r['coordinate']['id'] == coordinate['id']]
    if len(selected) > 1:
        raise ValueError('duplicate call checkpoint')
    record = selected[0] if selected else None
    score = record.get('score') if record else None
    sources = value['batches'][coordinate['batch_id']]['gold']['records']
    items = []
    if score is not None:
        for index, (source, position) in enumerate(zip(sources, coordinate['target_positions'], strict=True)):
            items.append({**source, 'source_position': position + 1, 'quartile': position // 16,
                'visible_input_position': coordinate['visible_positions'].index(position) + 1,
                'output_position': score['output_positions'][index],
                'prediction': score['predictions'][index],
                'aligned': score['aligned_records'] == len(sources),
                'canonical_correct': score['predictions'][index] == source['gold_label']})
    raw = (record or {}).get('raw_response') or {}
    usage = (record or {}).get('usage') or corr.leaf.usage_metrics(raw.get('usage') or {})
    ids = raw.get('prompt_token_ids')
    expected = value.get('rendered_prompts', {}).get(coordinate['id'], {})
    decoded = corr.tokenizer().decode(ids, skip_special_tokens=False) if isinstance(ids, list) else None
    complete = (decoded is not None and record is not None
                and all(message['content'] in decoded for message in record['request']['messages'])
                and len(ids) == raw.get('usage', {}).get('prompt_tokens'))
    available = score is not None and score['schema_valid']
    return {'coordinate': coordinate, 'model_completed': score is not None,
        'schema_valid': available, 'aligned_records': score['aligned_records'] if score else 0,
        'canonical_correct': score['strict_correct'] if score else 0, 'record_results': items,
        'usage': usage, 'model_called': bool(record and record.get('model_called')),
        'call_wall_seconds': record['ended'] - record['started'] if record else None,
        'counts': count_endpoint(items, available, score is not None, sources),
        'physical_prompt': {'captured': isinstance(ids, list),
            'full_system_and_user_input_verified': complete,
            'token_ids_sha256': digest(ids) if isinstance(ids, list) else None,
            'expected_cpu_token_ids_sha256': expected.get('token_ids_sha256'),
            'exact_cpu_template_match': digest(ids) == expected.get('token_ids_sha256') if isinstance(ids, list) else None},
        'error': record.get('error') if record else None,
        'finish_reason': record.get('finish_reason') if record else None}


def count_endpoint(items, available, observed, sources):
    counts = {}
    for label in ('human being', 'numeric value'):
        gold = sum(r['gold_label'] == label for r in sources)
        predicted = sum(r['prediction'] == label for r in items) if available else None
        counts[label] = {'gold_count': gold, 'predicted_count': predicted,
            'strict': int(predicted == gold) if available else 0 if observed else None,
            'false_positives': sum(r['prediction'] == label and r['gold_label'] != label for r in items) if available else None,
            'false_negatives': sum(r['prediction'] != label and r['gold_label'] == label for r in items) if available else None}
    return counts


def summarize(value, records):
    coordinates = [score_coordinate(value, row, records) for row in value['coordinates']]
    arms, context_counts = [], []
    item_maps = {arm: {} for arm in ARMS}
    for arm in ARMS:
        rows = [row for row in coordinates if row['coordinate']['arm'] == arm]
        items = [item for row in rows for item in row['record_results']]
        aligned = [item for item in items if item['aligned']]
        for row in rows:
            for item in row['record_results']:
                key = (row['coordinate']['context_index'], row['coordinate']['repeat'], item['source_position'])
                if key in item_maps[arm]:
                    raise ValueError('original position assigned twice for one arm/context/seed')
                item_maps[arm][key] = item
        arms.append({'arm': arm, 'planned_calls': len(rows),
            'dispatched_calls': sum(row['model_called'] for row in rows),
            'model_completed_calls': sum(row['model_completed'] for row in rows),
            'schema_valid_calls': sum(row['schema_valid'] for row in rows),
            'planned_assignments': sum(len(row['coordinate']['target_positions']) for row in rows),
            'aligned_assignments': len(aligned), 'canonical_correct': sum(r['canonical_correct'] for r in aligned),
            'accuracy_among_aligned': sum(r['canonical_correct'] for r in aligned) / len(aligned) if aligned else None,
            'original_position_quartiles': [{'quartile': q, 'original_first': q * 16 + 1,
                'aligned': sum(r['quartile'] == q for r in aligned),
                'correct': sum(r['quartile'] == q and r['canonical_correct'] for r in aligned)} for q in range(4)],
            'usage': {key: sum(row['usage'].get(key) or 0 for row in rows) for key in USAGE_KEYS},
            'missing_usage_calls': {key: sum(row['model_called'] and row['usage'].get(key) is None for row in rows) for key in USAGE_KEYS},
            'request_wall_seconds_sum': sum(row['call_wall_seconds'] or 0 for row in rows),
            'truncated_calls': sum(row['finish_reason'] == 'length' for row in rows),
            'physical_cpu_prompt_matches': sum(row['physical_prompt']['exact_cpu_template_match'] is True for row in rows),
            'full_physical_input_verified_calls': sum(row['physical_prompt']['full_system_and_user_input_verified'] for row in rows),
            'error_calls': sum(row['error'] is not None for row in rows)})
        for context in value['contexts']:
            for repeat in range(2):
                chosen = [r for r in rows if r['coordinate']['context_index'] == context['index'] and r['coordinate']['repeat'] == repeat]
                predictions = [item for row in chosen for item in row['record_results']]
                available = bool(chosen) and all(row['schema_valid'] for row in chosen) and len(predictions) == 64
                observed = bool(chosen) and all(row['model_completed'] for row in chosen)
                quarters = []
                for quarter in range(4):
                    subset = [r for r in chosen if quarter * 16 in r['coordinate']['target_positions']]
                    quarter_items = [r for r in predictions if r['quartile'] == quarter]
                    good = bool(subset) and all(r['schema_valid'] for r in subset) and len(quarter_items) == 16
                    seen = bool(subset) and all(r['model_completed'] for r in subset)
                    quarters.append({'quartile': quarter,
                        'counts': count_endpoint(quarter_items, good, seen, context['records'][quarter * 16:(quarter + 1) * 16])})
                context_counts.append({'arm': arm, 'context_index': context['index'], 'repeat': repeat,
                    'seed': SEEDS[repeat], 'aggregate_available': available,
                    'counts': count_endpoint(predictions, available, observed, context['records']),
                    'target16_counts': quarters})
    paired = []
    for left, right in [('all64', 'full16'), ('full16', 'local16')]:
        common = sorted(set(item_maps[left]) & set(item_maps[right]))
        common = [key for key in common if item_maps[left][key]['aligned'] and item_maps[right][key]['aligned']]
        paired_rows = [{'context_index': key[0], 'repeat': key[1], 'source_position': key[2],
            'question_group_sha256': item_maps[left][key]['question_group_sha256'],
            'left_correct': item_maps[left][key]['canonical_correct'],
            'right_correct': item_maps[right][key]['canonical_correct']} for key in common]
        paired.append({'left': left, 'right': right, 'common_aligned_assignments': len(common),
            'right_minus_left_correct': sum(r['right_correct'] - r['left_correct'] for r in paired_rows),
            'right_only_correct': sum(r['right_correct'] and not r['left_correct'] for r in paired_rows),
            'left_only_correct': sum(r['left_correct'] and not r['right_correct'] for r in paired_rows),
            'records': paired_rows})
    return {'schema': 'leaf-output-scope-analysis-v1', 'arms': arms, 'context_counts': context_counts,
        'paired_contrasts': paired, 'coordinates': coordinates,
        'caution': 'Four reused validation contexts/256 question groups; seeds are repeated measurements. '
            'all64→full16 changes output selection burden as well as length; full16→local16 removes only non-target input. '
            'All repeated full-prefix calls remain charged. Correct target counts can conceal cancelling errors. '
            'Malformed arrays are unaligned, infrastructure/unrun null; no majority vote, repair or attention-mechanism proof.'}


# Only privately loaded module globals are adapted; frozen helper files are untouched.
corr.make_request = make_request
corr.fixed.make_request = make_request
corr.fixed.score_coordinate = score_coordinate
collect_calls = corr.collect_calls
