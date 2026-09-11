"""Frozen fresh join population, no-repair contracts, and model-visible evidence."""
import hashlib
import itertools
import json
import random

MASTER = 981391001
REPRESENTATIONS = ('direct', 'colocated', 'cross')
SYSTEM = ('You answer questions about purchase records. Each record states one purchase; '
          'record order has no temporal significance. Use the supplied evidence. '
          'Use of any advertised tool is optional. Return only the requested final answer.')
EXTRACTION_SYSTEM = ('You are a purchase-record extraction assistant. Return only the requested '
                     'complete JSON extraction. Do not write code, use tools, explain, or reason aloud.')


def serialize(value):
    return json.dumps(value, ensure_ascii=False, separators=(',', ':'), allow_nan=False)


def digest(value):
    return hashlib.sha256(serialize(value).encode()).hexdigest()


def oracle(records, products):
    """Trusted host diagnostic; never installed in a model runtime."""
    buyers = [{c for _, c, product in records if product == target} for target in products]
    return sorted(set.intersection(*buyers))


def worlds():
    result = []
    for wi in range(4):
        seed = 981391011 + wi
        rng = random.Random(seed)
        customers = [f'c{x:04}' for x in rng.sample(range(1000, 10000), 12)]
        ids = [f'r{x:05}' for x in rng.sample(range(10000, 100000), 48)]
        products = rng.sample(['K', 'L', 'M', 'N', 'P', 'R', 'S', 'T'], 4)
        records, colocated, cross = [], [[], [], []], [[], [], []]
        for ci, customer in enumerate(customers):
            pattern = [0, 1, 2, 3] if ci < 3 + 2 * wi else ([0, 2, 2, 3] if ci % 2 else [2, 1, 2, 3])
            for pi, product in enumerate(pattern):
                row = [ids[4 * ci + pi], customer, products[product]]
                records.append(row); colocated[ci // 4].append(row); cross[(ci + pi) % 3].append(row)
        rng.shuffle(records)
        for chunks in (colocated, cross):
            for chunk in chunks:
                rng.shuffle(chunk)
        result.append(dict(id=f'fresh-join-{wi}', index=wi, generator_seed=seed,
                           query_products=products[:2], products=products, customers=sorted(customers),
                           records=records, partitions=dict(colocated=colocated, cross=cross)))
    return result


def plan(population):
    conditions = list(itertools.product(REPRESENTATIONS, (False, True)))
    rng = random.Random(MASTER)
    rng.shuffle(conditions)
    blocks = list(range(8)); rng.shuffle(blocks)
    rows = []
    for block in blocks:
        world = population[block // 2]
        order = conditions[block % 6:] + conditions[:block % 6]
        if block >= 6:
            order = list(reversed(order))
        for position, (representation, python) in enumerate(order):
            row = dict(world_id=world['id'], world_index=world['index'], block=block,
                       repeat=block % 2, seed=981391101 + block, representation=representation,
                       python=python, pair_position=position, dispatch_order=len(rows))
            row['id'] = digest(['root-native-partition-join-v1', row]); rows.append(row)
    return rows


def extraction(raw, chunk):
    try:
        rows = json.loads(raw)
        valid = isinstance(rows, list) and all(isinstance(r, list) and len(r) == 3 and
                    all(isinstance(v, str) for v in r) for r in rows)
        if not valid:
            raise ValueError('not a list of string triples')
    except (ValueError, TypeError):
        return dict(rows=None, shape_valid=False, exact=False, available=False)
    exact = sorted(rows) == sorted(chunk)
    return dict(rows=rows, shape_valid=True, exact=exact, available=exact)


def score(content, gold, customers, available=True):
    value = dict(available=available, reward=None, valid=None, answer=None)
    if not available:
        return value
    try:
        answer = json.loads(content)
        valid = (isinstance(answer, list) and all(isinstance(x, str) and x in customers for x in answer)
                 and len(answer) == len(set(answer)) and answer == sorted(answer))
    except (ValueError, TypeError):
        answer, valid = None, False
    value.update(reward=int(valid and answer == gold), valid=valid, answer=answer if valid else None)
    return value


def query(world):
    a, b = world['query_products']
    return f'Find every customer who purchased both product {a} and product {b} anywhere in the evidence.'


def record_text(records):
    return '\n'.join(f'{r}: customer {c} purchased product {t}.' for r, c, t in records)


def acquisition_plan(population):
    rows = []
    for world in population:
        for partition in ('colocated', 'cross'):
            for chunk_index, chunk in enumerate(world['partitions'][partition]):
                row = dict(world_id=world['id'], partition=partition, chunk_index=chunk_index,
                           seed=981391201 + len(rows), records=chunk)
                row['id'] = digest(['join-extraction', row]); rows.append(row)
    return rows


def extraction_messages(world, chunk):
    text = (query(world) + '\nYou see only one of three chunks. Extract every purchase in this chunk '
            'as a JSON array of triples [record_id, customer_id, product]. Preserve all records and '
            'their IDs, including partial evidence and distractor products. Return only that JSON array.\n'
            'This chunk:\n' + record_text(chunk))
    return [dict(role='system', content=EXTRACTION_SYSTEM), dict(role='user', content=text)]


def evidence(world, representation, acquisitions):
    if representation == 'direct':
        return dict(available=True, text=record_text(world['records']),
                    files={'evidence.txt': record_text(world['records'])}, acquisition_ids=[])
    calls = [x for x in acquisitions if x['coordinate']['world_id'] == world['id'] and
             x['coordinate']['partition'] == representation]
    calls.sort(key=lambda x: x['coordinate']['chunk_index'])
    if len(calls) != 3 or not all(c.get('extraction', {}).get('available') for c in calls):
        return dict(available=False, reason='source extraction unavailable or not exact',
                    acquisition_ids=[x['coordinate']['id'] for x in calls])
    # Preserve actual raw bytes in each report file; no reserialization replaces them.
    files = {f'report-{i}.json': call['content'] for i, call in enumerate(calls)}
    text = '\n\n'.join(f'Partial report {i}:\n{files[f"report-{i}.json"]}' for i in range(3))
    return dict(available=True, text=text, files=files,
                acquisition_ids=[x['coordinate']['id'] for x in calls])


def prompt(world, package):
    return (query(world) + '\nCustomers: ' + ', '.join(world['customers']) +
            '\nA purchase triple has fields [record_id, customer_id, product], in that order. '
            'The supplied files duplicate the complete evidence shown below. '
            'File access is possible only through an advertised tool; tool use is optional. '
            'No additional facts are hidden in the files.\nFiles: ' + ', '.join(package['files']) +
            '\nEvidence:\n' + package['text'] +
            '\nReturn only a JSON array of distinct customer IDs in ascending order; use [] if none.')


def null_row(row, reason):
    return dict(coordinate=row, available=False, reward=None, valid=None, answer=None,
                operational_success=0, unavailable_reason=reason, completed=False)
