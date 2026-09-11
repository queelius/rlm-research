"""Frozen outcome-independent coordinates and treatment prompts."""
import hashlib
import json

MASTER = 981334001


def digest(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(',', ':')).encode()).hexdigest()


def plan_for(contexts):
    rows = []
    for ci, context in enumerate(contexts):
        for fi, family in enumerate(('single_user', 'union')):
            block = digest([MASTER, context['id'], family])
            treatments = [(source, reducer) for source in ('native_c32', 'dataset_oracle')
                          for reducer in (False, True)]
            treatments.sort(key=lambda treatment: digest([block, treatment]))
            for order, (source, reducer) in enumerate(treatments):
                row = dict(context_id=context['id'], context_window_id=98133000 + ci,
                           stratum=context['stratum'], helper_partition=context['helper_partition'],
                           family=family, pair_id=block, map_source=source, reducer=reducer,
                           arm='typed', treatment_order=order, seed=981334201 + ci * 2 + fi,
                           temperature=.5, client_path='train')
                row['id'] = digest(row)
                rows.append(row)
    return rows


def prompt(base, row):
    source = ('one actual frozen native c32 child acquisition; labels may disagree with dataset'
              if row['map_source'] == 'native_c32' else
              'PRIVILEGED ORACLE TREATMENT: frozen dataset labels supplied by the host')
    text = base + '\n\nSupplied-map diagnostic treatment: labels.json is a JSON object mapping every public record ID to its category. Source: ' + source + '. Select the requested records using their public user metadata in records.json. You may use the supplied map and ordinary Python. Submit your own final Answer: N.'
    if row['reducer']:
        text += '\nA pure helper is available: from count_labels import count_labels. count_labels(labels, requested_ids, target) returns the integer number of exact target labels among the unique requested IDs. It requires a category-label dictionary, a list of covered unique IDs, and an exact category string; invalid inputs raise ValueError. It has no user metadata or query access. Choose requested_ids yourself, execute the reduction, and submit your own final answer.'
    return text
