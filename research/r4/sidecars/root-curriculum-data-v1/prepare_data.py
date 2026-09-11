"""CPU-only candidate compositions; no model, training, or orchestration code."""
import hashlib
import importlib.util
import json
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parent
SIDE = ROOT.parent
SEED = 981267100
PINS = {
    'trec-leaf-sft-v1/source/data.py': 'b5aa353e2173c3fd48ecc36ce0596c9c3328767a7d82c8d22c57b4e0a32f0b8f',
    'trec-leaf-split-provenance-v1/INVENTORY.json': '5ad3bc2e9d2e440500a918b3ed7d41d163a29dceaf26cc31b41c2f488ffd660b',
    'root-only-credit-v1/inputs/PUBLIC.json': 'f833898ac2014abc3661e8a870e55185f52e41a2c4c6cf6bb7224cd78187248c',
    'root-rlvr-campaign-v1/inputs/TRANSFER_PUBLIC.json': '5d2ea9736ff6247656080a5ec234dbfe17141f8da2274c192e26ae52e703b14c',
    'root-rlvr-independent-seed-v1/inputs/TRANSFER_PUBLIC.json': '5d2ea9736ff6247656080a5ec234dbfe17141f8da2274c192e26ae52e703b14c',
    'leaf-composition-transfer-v1/prepared-v1/DATA.json': '1ea4640da5a8e3e305bee7f79d5abeecb02507d6bcc33d709d1c7209fd47bfc2',
    'leaf-sentiment-transfer-v1/DATA.json': 'e3b929cab3e16296e6b92efceddca0a7a84fbec3455c569ec0e66c91cf30e9b8',
    'leaf-correspondence-anchor-transfer-v1/DATA.json': '0f37d7e4820e77f6057577cad3afa103957b3a99e8449fa7c03e53a19f4c4739',
    'leaf-indexed-grammar-transfer-v1/DATA.json': 'ca5a895f361d8a590078e36393c6edf900e86a6da7b17382440366581642e17f',
}


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def digest(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(',', ':')).encode()).hexdigest()


def read(path):
    return json.loads(Path(path).read_text())


def order(rows, purpose):
    return sorted(rows, key=lambda r: digest([ROOT.name, SEED, purpose, r['group_id']]))


def build():
    sources = {str(SIDE / p): h for p, h in PINS.items()}
    for p, h in sources.items():
        assert sha(p) == h, p
    spec = importlib.util.spec_from_file_location('pinned_trec_source', SIDE / 'trec-leaf-sft-v1/source/data.py')
    source = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(source)
    partitions = source.load_partitions()
    inv = read(SIDE / 'trec-leaf-split-provenance-v1/INVENTORY.json')
    sources.update(inv['source_file_sha256'])
    split_path = SIDE / 'trec-leaf-split-provenance-v1/PROPOSED_SPLIT.json'
    sources[str(split_path)] = source.SPLIT_SHA
    prior_sets = {f'legacy-context-{k}': set(v['question_group_sha256']) for k, v in inv['old_contexts'].items()}
    for rel in list(PINS)[2:6]:
        prior_sets[rel] = {g for c in read(SIDE / rel)['contexts'] for g in c['group_ids']}
    forbidden = set().union(*prior_sets.values())
    pools = {name: order([r for r in rows if r['group_id'] not in forbidden], name)
             for name, rows in partitions.items()}
    pool_counts = {k: len(v) for k, v in pools.items()}
    sst = read(SIDE / 'leaf-sentiment-transfer-v1/DATA.json')
    prior_sst = {r['group_id'] for r in sst['selected']}
    for rel in ('leaf-correspondence-anchor-transfer-v1/DATA.json', 'leaf-indexed-grammar-transfer-v1/DATA.json'):
        for c in read(SIDE / rel)['contexts']:
            if c['dataset'] == 'sst2':
                prior_sst.update(r['group_id'] for r in c['records'])
    sst_rows = sst['dedup']['all_groups_in_selection_order']
    pools['sst'] = order([{**r, 'question': r['sentence']} for r in sst_rows if r['group_id'] not in prior_sst], 'sst')
    pool_counts['sst'] = len(pools['sst'])
    for item in sst['acquisition']['artifacts']:
        assert sha(item['path']) == item['sha256']
        sources[item['path']] = item['sha256']
    public, host, metadata = {'contexts': [], 'tasks': []}, {}, []
    labels = list(source.LABELS.values())
    training_labels = ['human being', 'numeric value', 'entity', 'location']

    def take(pool, split, size, number):
        assert len(pools[pool]) >= size * number, (pool, split, len(pools[pool]))
        for i in range(number):
            records, pools[pool] = pools[pool][:size], pools[pool][size:]
            cid = f'{split}-{size:03d}-{i:02d}'
            assert all('\n' not in r['question'] and '\r' not in r['question'] for r in records)
            text = ''.join(f"Date: 2000-01-{j % 28 + 1:02d} || User: {j % 8} || Instance: {r['question']}\n" for j, r in enumerate(records))
            text_sha = hashlib.sha256(text.encode()).hexdigest()
            # The only model-facing fields are text and task question; ids/splits stay host-side.
            public['contexts'].append({'id': cid, 'text': text})
            metadata.append({'id': cid, 'split': split, 'dataset': 'sst2' if pool == 'sst' else 'trec',
                             'source_partition': pool, 'size': size, 'within_size_index': i,
                             'group_ids': [r['group_id'] for r in records], 'context_sha256': text_sha})
            target_labels = ['negative', 'positive'] if pool == 'sst' else labels
            counts = dict(Counter(r['gold'] for r in records))
            for label in target_labels:
                tid = cid + ':' + label.replace(' ', '_')
                if pool == 'sst':
                    question = ("Classify each movie-review sentence by overall sentiment: positive means favorable and negative means unfavorable. "
                                f"How many records in the entire context have '{label}' sentiment? Return only 'Answer: X', replacing X with the exact integer count.")
                else:
                    template = next(t['question'] for t in read(SIDE / 'root-only-credit-v1/inputs/PUBLIC.json')['tasks'] if t['label'] == 'human being')
                    question = template.replace("'human being'", repr(label))
                public['tasks'].append({'id': tid, 'context_id': cid, 'question': question})
                host[tid] = {'answer_integer': counts.get(label, 0), 'answer': repr([counts.get(label, 0)]),
                             'target_label': label, 'context_id': cid}
            host[cid] = {'records': records, 'class_counts': {label: counts.get(label, 0) for label in target_labels}}

    for size in (16, 32, 64):
        take('train', 'training', size, 8)
    take('train', 'validation', 32, 4)
    take('train', 'validation', 64, 4)
    take('train', 'transfer-composition', 64, 6)
    take('train', 'transfer-size', 128, 4)
    take('train', 'transfer-size', 256, 2)
    take('validation', 'transfer-leaf-validation-exposed', 32, 8)
    take('test', 'transfer-leaf-test-exposed', 32, 3)
    take('sst', 'transfer-sst', 32, 3)
    schedule = []
    train = [c for c in metadata if c['split'] == 'training']
    for update in range(16):
        visit, i = divmod(update, 8)
        contexts = [c for c in train if c['within_size_index'] == i]
        schedule.append({'candidate_update': update + 1, 'tasks': [
            c['id'] + ':' + training_labels[(i + visit + j) % 4].replace(' ', '_')
            for j, c in enumerate(contexts)]})
    group_sets = {c['id']: set(c['group_ids']) for c in metadata}
    all_ids = [g for c in metadata for g in c['group_ids']]
    assert len(all_ids) == len(set(all_ids))
    assert len({c['context_sha256'] for c in metadata}) == len(metadata)
    assert not set(all_ids) & forbidden
    assert not {g for c in metadata if c['dataset'] == 'sst2' for g in c['group_ids']} & prior_sst
    audit = {'candidate_data_seed': SEED, 'context_counts': dict(Counter(c['split'] for c in metadata)),
             'record_counts': {s: sum(c['size'] for c in metadata if c['split'] == s) for s in {c['split'] for c in metadata}},
             'eligible_source_pools_after_exclusions': pool_counts, 'unused_pool_counts': {k: len(v) for k,v in pools.items()},
             'unique_groups': len(set(all_ids)), 'duplicate_context_hashes': 0, 'cross_context_group_overlap': 0,
             'known_prior_root_and_composition_union': len(forbidden), 'prior_root_exclusion_counts': {k: len(v) for k,v in prior_sets.items()},
             'prior_sst_exposed_groups': len(prior_sst), 'sst_source_dedup': {k:v for k,v in sst['dedup'].items() if k != 'all_groups_in_selection_order'},
             'known_prior_root_overlap': {k: len(set(all_ids) & v) for k,v in prior_sets.items()},
             'leaf_partition_overlap': {s: len(set(all_ids) & {r['group_id'] for r in rows}) for s,rows in partitions.items()},
             'oolong_pool_overlap': len(set(all_ids) & set(inv['overlap']['trec_train__oolong_validated_pool']['normalized_group_sha256'])),
             'root_history_scope': 'Named manifests and audited legacy contexts only; entire historical exposure/paraphrase/pretraining unknown',
             'sst_acquisition': sst['acquisition'], 'trec_licenses': inv['licenses'],
             'raw_trec_statistics': inv['statistics'], 'source_sha256': sources,
             'runtime_allowlist': ['contexts[].text', 'tasks[].question'],
             'not_frozen': ['root/child identity', 'optimizer and sampling hyperparameters', 'rollout seeds', 'validation/checkpoint selection', 'runtime rendering/tools', 'GPU caps and launch'],
             'gpu_calls': 0, 'model_outcomes_used_for_data_allocation': False}
    return {'PUBLIC.json': public, 'HOST_GOLD.json': host,
            'GROUPS.json': metadata, 'CANDIDATE_SCHEDULE.json': schedule, 'PROVENANCE.json': audit}


if __name__ == '__main__':
    outputs = build()
    for name, value in outputs.items():
        with (ROOT / name).open('x') as stream:
            json.dump(value, stream, indent=2, sort_keys=True, allow_nan=False)
            stream.write('\n')
    print(json.dumps({k:v for k,v in outputs['PROVENANCE.json'].items() if k in ('context_counts','record_counts','eligible_source_pools_after_exclusions','unused_pool_counts','unique_groups','prior_sst_exposed_groups')}))
