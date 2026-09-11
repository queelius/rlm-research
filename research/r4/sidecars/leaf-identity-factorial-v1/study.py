"""Prospective prefix × numeric namespace × tag rule; private pinned collector."""
import hashlib
import importlib.util
import itertools
from collections import Counter, defaultdict
from copy import deepcopy
from pathlib import Path

ROOT = Path(__file__).resolve().parent
SIDE = ROOT.parent
PARENT = SIDE / 'leaf-identity-counter-v1'
PINS = {
    PARENT / 'study.py': 'e61c5cbae6484654855642e631332373c875dc5939ee2d1a849b896856475924',
    PARENT / 'driver.py': 'f3c7bf409323d1854abfdb30efb64ead13c7a9de0dd6aadb5c64c7083e645580',
    PARENT / 'owned.py': '8b3f18ec32748ba5189a61d64aea99c5ce087b15b53ae999e643c60e48261d29',
    PARENT / 'DATA.json': 'e105ebed28179fe7e78f815ec2a151b24fea172571c58b56edc727eff2fb4814',
    PARENT / 'SPEC.json': 'c6ab4f82525424b5aef77a21be1dc7fe46c333bf54575a48070b27a850a5565b',
}
for path, expected in PINS.items():
    if hashlib.sha256(path.read_bytes()).hexdigest() != expected:
        raise ValueError('frozen identity source changed: ' + str(path))
loader = importlib.util.spec_from_file_location('factorial_private_identity', PARENT / 'study.py')
counter = importlib.util.module_from_spec(loader)
loader.loader.exec_module(counter)
padding, anchor = counter.padding, counter.anchor
read, digest, file_hash = counter.read, counter.digest, counter.file_hash
serialize, write_once = counter.serialize, counter.write_once
INPUT_MARKER, ALIAS = counter.INPUT_MARKER, counter.ALIAS
MASTER = 981269001
SEEDS = [int(digest([ROOT.name, MASTER, 'sampling', i])[:8], 16) % 2147483647 for i in range(2)]
ARMS = ['meaningful_tag', 'ordinal_tag', 'constant_tag']
CONDITIONS = list(itertools.product(['q', 'p'], ['overlap', 'disjoint'], ARMS))


def affine_sequence(values):
    """Consecutive ranks have constant differences iff affine, including mod10000."""
    return len({(b - a) % 10000 for a, b in zip(values, values[1:])}) <= 1


def build_data(source):
    data = deepcopy(source)
    if len(data['contexts']) != 8 or any(len(c['records']) != 64 for c in data['contexts']):
        raise ValueError('requires exact eight frozen64 contexts')
    eligible = [v for v in range(1000, 10000) if not 1 <= v % 1000 <= 64]
    for c in data['contexts']:
        if sorted(r['id'] for r in c['records']) != [f'q{i:04d}' for i in range(1, 65)]:
            raise ValueError('original source rank bijection changed')
        values = sorted(eligible, key=lambda v: digest([ROOT.name, MASTER, 'disjoint-value', c['source_context_id'], v]))[:64]
        orders = [[values[int(c['records'][j]['id'][1:]) - 1] for j in order] for order in c['presentations']]
        if any(affine_sequence(v) for v in [values, *orders]):
            raise ValueError('affine ID map: stop preparation; no automatic alternate mapping')
        c['disjoint_values_by_rank'] = values
    data.update(master_seed=MASTER, sampling_seeds=SEEDS, source_path=str(PARENT / 'DATA.json'),
        source_sha256=PINS[PARENT / 'DATA.json'],
        assignment_rule='Original stable source ranks and presentation permutations unchanged; disjoint values selected in ascending SHA256(namespace,master,disjoint-value,source_context_id,value) order, assigned to stable ranks1..64; labels excluded',
        numeric_exclusions='Values1000..9999; last3 suffix001..064 excluded; exact affine/mod10000 rank or display mapping rejected',
        freshness='Exact exposed developmental eight contexts; only sampled seeds and source namespace are new')
    return data


def build_design(data):
    previous = read(PARENT / 'SPEC.json')['design']
    d = {k: deepcopy(previous[k]) for k in ['contract', 'labels', 'definitions', 'task_labels', 'task_definitions']}
    d.update(contexts=deepcopy(data['contexts']), model_alias=ALIAS, model_aliases={'old_sft': ALIAS},
        max_tokens=3072, max_concurrent_calls=4, call_timeout_seconds=120, wall_time_cap_seconds=1800,
        plan=[], coordinates=[], batches=[])
    for c in d['contexts']:
        for permutation, order in enumerate(c['presentations']):
            for repeat, seed in enumerate(SEEDS):
                group_index = c['index'] * 4 + permutation * 2 + repeat
                cycle = list(range(12)) if group_index < 12 or group_index >= 24 else list(reversed(range(12)))
                shift = group_index % 12
                for position, condition_index in enumerate(cycle[shift:] + cycle[:shift]):
                    prefix, namespace, arm = CONDITIONS[condition_index]
                    records = []
                    for i, j in enumerate(order):
                        r = c['records'][j]
                        rank = int(r['id'][1:])
                        number = rank if namespace == 'overlap' else c['disjoint_values_by_rank'][rank - 1]
                        records.append({**deepcopy(r), 'input_position': i + 1, 'source_rank': rank,
                                        'identity96_id': r['id'], 'id': f'{prefix}{number:04d}'})
                    row = {'dataset': c['dataset'], 'context_index': c['index'], 'source_context_id': c['source_context_id'],
                        'weight': 'old_sft', 'source_prefix': prefix, 'number_namespace': namespace, 'arm': arm,
                        'grammar': 'exact', 'seed': seed, 'repeat': repeat, 'size': 64, 'permutation': permutation,
                        'start': 0, 'condition_index': condition_index, 'cell_order': position,
                        'batch_id': len(d['batches']), 'dispatch_order': len(d['plan'])}
                    row['id'] = row['coordinate_id'] = digest([ROOT.name, row])
                    d['plan'].append(row)
                    d['coordinates'].append(deepcopy(row))
                    d['batches'].append({'questions': [r['question'] for r in records],
                        'gold': {'records': records, 'order': list(range(64)), 'arm': arm,
                            'source_prefix': prefix, 'number_namespace': namespace, 'labels': d['task_labels'][c['dataset']]}})
    return d


def expected_tags(records, arm, source_prefix):
    opposite = {'q': 'p', 'p': 'q'}[source_prefix]
    if arm == 'meaningful_tag':
        return [r['id'] for r in records]
    if arm == 'ordinal_tag':
        return [f'{opposite}{i:04d}' for i in range(1, len(records) + 1)]
    if arm == 'constant_tag':
        return [opposite + '0000'] * len(records)
    raise ValueError('unknown arm')


def make_request(design, row):
    body = anchor.make_request(design, {**row, 'arm': 'anonymous'})
    records = design['batches'][row['batch_id']]['gold']['records']
    prefix, rest = body['messages'][1]['content'].split('Return only', 1)
    rest = rest.split('\nAllowed labels:', 1)[1]
    opposite = {'q': 'p', 'p': 'q'}[row['source_prefix']]
    instruction = 'Return only a JSON array of objects in displayed input order, exactly one object per input record. Each object has exactly the keys tag then label. '
    instruction += {
        'meaningful_tag': "Set tag to the corresponding randomized source ID shown in the input and label to that record's label.",
        'ordinal_tag': f"Set tag to the displayed position counter {opposite}0001, {opposite}0002, through {opposite}0064, and label to the corresponding displayed record's label. These position tags are not source IDs.",
        'constant_tag': f'Set tag to the literal "{opposite}0000" in every object and label to the corresponding displayed record\'s label. This constant tag is not a source ID.',
    }[row['arm']]
    body['messages'][1]['content'] = prefix + instruction + '\nAllowed labels:' + rest
    items = [{'type': 'object', 'properties': {'tag': {'type': 'string', 'const': tag},
        'label': {'type': 'string', 'enum': design['task_labels'][row['dataset']]}},
        'required': ['tag', 'label'], 'additionalProperties': False}
        for tag in expected_tags(records, row['arm'], row['source_prefix'])]
    body['structured_outputs'] = {'json': {'type': 'array', 'prefixItems': items, 'items': False, 'minItems': 64, 'maxItems': 64}}
    return body


def score_labels(content, gold):
    tags = expected_tags(gold['records'], gold['arm'], gold['source_prefix'])
    adapted = {**gold, 'arm': 'meaningful_tag', 'records': [
        {**r, 'id': tag} for r, tag in zip(gold['records'], tags, strict=True)]}
    score = padding.score_labels(content, adapted)
    applicable = gold['arm'] == 'ordinal_tag' and gold['number_namespace'] == 'overlap'
    diagnostic = {'applicable': applicable, 'mapping_coverage': 0, 'correct': None,
        'reason': 'only_overlapping_ordinal_condition', 'primary_score_replaced': False}
    if applicable:
        by_number = {int(r['id'][1:]): r['gold_label'] for r in gold['records']}
        if set(by_number) != set(range(1, 65)) or len(gold['records']) != 64:
            raise ValueError('overlap diagnostic requires exact source numeric bijection')
        diagnostic.update(mapping_coverage=64, reason='invalid_output' if not score['schema_valid'] else 'available')
        if score['schema_valid']:
            diagnostic['correct'] = sum(p == by_number[i] for i, p in enumerate(score['predictions'], 1))
    score['numeric_source_diagnostic'] = diagnostic
    return score


def score_coordinate(design, coordinate, records):
    value = counter.score_coordinate(design, coordinate, records)
    value['class_count_l1'] = (sum(abs(v) for v in value['class_count_errors'].values())
                               if value['class_count_errors'] is not None else None)
    gold = design['batches'][coordinate['batch_id']]['gold']
    value['numeric_source_diagnostic'] = (records[0]['score']['numeric_source_diagnostic']
        if records and records[0].get('score') else {
            'applicable': gold['arm'] == 'ordinal_tag' and gold['number_namespace'] == 'overlap',
            'mapping_coverage': 64 if gold['arm'] == 'ordinal_tag' and gold['number_namespace'] == 'overlap' else 0,
            'correct': None, 'reason': 'unrun_or_infrastructure_null', 'primary_score_replaced': False})
    return value


def summarize(design, records):
    by_id = defaultdict(list)
    for r in records:
        by_id[r['coordinate']['id']].append(r)
    coordinates = [score_coordinate(design, c, by_id[c['id']]) for c in design['coordinates']]
    fields = ['dataset', 'source_prefix', 'number_namespace', 'arm']
    cells = []
    for key in sorted({tuple(c['coordinate'][f] for f in fields) for c in coordinates}):
        selected = [c for c in coordinates if tuple(c['coordinate'][f] for f in fields) == key]
        items = [i for c in selected for i in c['records'] if i['aligned']]
        l1 = [c['class_count_l1'] for c in selected if c['class_count_l1'] is not None]
        diagnostics = [c['numeric_source_diagnostic']['correct'] for c in selected if c['numeric_source_diagnostic']['correct'] is not None]
        cells.append({**dict(zip(fields, key)), 'planned_calls': len(selected),
            'recorded_calls': sum(c['complete'] for c in selected),
            'observable_calls': sum(c['strict_correct_assignments'] is not None for c in selected),
            'valid_calls': sum(c['fully_valid'] for c in selected),
            'infrastructure_errors': sum(c['infrastructure_errors'] for c in selected),
            'complete_batch_correct': sum(c['strict_full64_correct'] == 1 for c in selected),
            'planned_assignments': 64 * len(selected), 'aligned_assignments': len(items),
            'canonical_correct': sum(i['correct'] for i in items),
            'per_call_class_count_l1': l1, 'mean_per_call_class_count_l1': sum(l1) / len(l1) if l1 else None,
            'numeric_diagnostic_correct': sum(diagnostics) if diagnostics else None,
            'numeric_diagnostic_aligned_items': 64 * len(diagnostics),
            'position_accuracy': [{'position': p, 'aligned': sum(i['input_position'] == p for i in items),
                'correct': sum(i['input_position'] == p and i['correct'] for i in items)} for p in range(1, 65)],
            'confusion': [{'gold': g, 'prediction': p, 'count': n} for (g, p), n in sorted(Counter((i['gold'], i['prediction']) for i in items).items())],
            'usage': {k: sum(c['usage'][k] for c in selected) for k in ['logical_input_tokens', 'cached_input_tokens', 'uncached_input_tokens', 'completion_tokens']},
            'missing_usage': {k: sum(c['missing_usage'][k] for c in selected) for k in ['logical_input_tokens', 'cached_input_tokens', 'uncached_input_tokens', 'completion_tokens']},
            'length_stops': sum(c['length_stops'] for c in selected),
            'call_wall_seconds_sum': sum(c['call_wall_seconds_sum'] for c in selected)})
    groups = defaultdict(dict)
    for value in coordinates:
        c = value['coordinate']
        groups[c['dataset'], c['context_index'], c['permutation'], c['repeat'], c['source_prefix'], c['number_namespace']][c['arm']] = value
    pairs = []
    for key, arms in groups.items():
        for left, right in [('ordinal_tag', 'meaningful_tag'), ('constant_tag', 'ordinal_tag'), ('constant_tag', 'meaningful_tag')]:
            if left not in arms or right not in arms:
                continue
            a, b = arms[left], arms[right]
            observed = all(v['strict_correct_assignments'] is not None for v in [a, b])
            valid = a['fully_valid'] and b['fully_valid']
            pairs.append({**dict(zip(['dataset', 'context_index', 'permutation', 'repeat', 'source_prefix', 'number_namespace'], key)),
                'contrast': right + '_minus_' + left, 'both_observed': observed, 'jointly_valid': valid,
                'strict_difference': b['strict_correct_assignments'] - a['strict_correct_assignments'] if observed else None,
                'semantic_difference': b['semantic_correct_among_aligned'] - a['semantic_correct_among_aligned'] if valid else None,
                'item_gains': sum(not x['correct'] and y['correct'] for x, y in zip(a['records'], b['records'])) if valid else None,
                'item_losses': sum(x['correct'] and not y['correct'] for x, y in zip(a['records'], b['records'])) if valid else None})
    interactions = defaultdict(dict)
    for p in pairs:
        if p['contrast'] == 'meaningful_tag_minus_ordinal_tag':
            key = tuple(p[f] for f in ['dataset', 'context_index', 'permutation', 'repeat', 'source_prefix'])
            interactions[key][p['number_namespace']] = p
    interaction_rows = []
    for key, pair in interactions.items():
        if set(pair) == {'overlap', 'disjoint'}:
            row = dict(zip(['dataset', 'context_index', 'permutation', 'repeat', 'source_prefix'], key))
            for metric in ['strict_difference', 'semantic_difference']:
                a, b = pair['overlap'][metric], pair['disjoint'][metric]
                row['disjoint_minus_overlap_' + metric] = b - a if a is not None and b is not None else None
            interaction_rows.append(row)
    return {'coordinates': coordinates, 'cells': cells, 'paired_context_effects': pairs,
        'overlap_interactions': interaction_rows,
        'primary': 'Displayed-position meaningful-minus-ordinal in disjoint namespace, separately by task/prefix',
        'diagnostic': 'Numeric-source alignment only for overlapping ordinal outputs; never replaces primary; disjoint unavailable',
        'inference_unit': 'Four exposed contexts per task; permutations/seeds nested; one fixed child, no end-to-end RLM claim',
        'failure_caution': 'Invalid output gives strict failure and unavailable semantic alignment; infrastructure/unrun strict scores null',
        'compute_caution': 'Tag/token lengths and actual inference usage need not be equal'}


anchor.corr.fixed.make_request = make_request
anchor.corr.fixed.score_coordinate = score_coordinate
anchor.corr.fixed.leaf.score_labels = score_labels
anchor.corr.fixed.leaf.write_once = write_once
collect_calls = anchor.corr.fixed.collect_calls
