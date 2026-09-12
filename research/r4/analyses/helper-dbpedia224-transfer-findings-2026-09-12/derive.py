"""Compact synthesis of the sealed DBpedia raw audit, with no raw article/call duplication."""
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent
STORE = ROOT.parents[1]
AUDIT = STORE / 'analyses/helper-dbpedia224-transfer-independent-2026-09-12'
EVAL = STORE / 'sidecars/helper-dbpedia224-transfer-eval-v1'
DATA = STORE / 'sidecars/helper-dbpedia224-transfer-data-v1'
ARMS = ('c32', 'rl_step8', 'sft_step8', 'rl_seed2_step8')


def read(path):
    return json.loads(Path(path).read_text())


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def digest(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(',', ':')).encode()).hexdigest()


def effects(before, after, gold):
    paired = sorted(set(before) & set(after) & set(gold))
    wins = [i for i in paired if before[i] != gold[i] and after[i] == gold[i]]
    losses = [i for i in paired if before[i] == gold[i] and after[i] != gold[i]]
    changes = [i for i in paired if before[i] != after[i]]
    return {'paired_available': len(paired), 'paired_unavailable': len(gold) - len(paired),
            'wins': len(wins), 'losses': len(losses), 'net': len(wins) - len(losses),
            'changed_labels': len(changes), 'wrong_to_different_wrong': len(changes) - len(wins) - len(losses),
            'changes': [{'id': i, 'gold': gold[i], 'before': before[i], 'after': after[i]} for i in changes]}


def derive():
    audit = read(AUDIT / 'RESULT.json')
    assert read(AUDIT / 'WATCH_TERMINAL.json')['status'] == 'COMPLETE'
    gold = read(DATA / 'inputs/HOST_GOLD.json')['labels']
    schedule = read(DATA / 'inputs/REQUESTS.json')
    assert len(gold) == 224 and len(schedule) == 56 and set(audit['arms']) == set(ARMS)
    arms, responses = {}, {}
    for arm in ARMS:
        value = audit['arms'][arm]; predictions = value['predictions']; directory = EVAL / 'outputs' / (arm + '-001')
        assert value['complete'] and set(predictions) == set(gold)
        assert value['inventory']['valid_calls'] == value['inventory']['expected_calls'] == 56
        assert value['metrics']['available_predictions'] == 224 and value['metrics']['unavailable_predictions'] == 0
        assert sum(predictions[i] == gold[i] for i in gold) == value['metrics']['correct']
        per_class = {label: {'planned': sum(x == label for x in gold.values()),
                            'available': sum(gold[i] == label for i in predictions),
                            'correct': sum(gold[i] == label and predictions[i] == label for i in predictions)}
                     for label in sorted(set(gold.values()))}
        assert all(v['planned'] == v['available'] == 16 and v['correct'] == value['per_class'][k]['correct'] for k, v in per_class.items())
        owner = read(directory / 'OWNER_TERMINAL.json')
        assert owner['complete'] and owner['released'] and owner['runtime_qualified'] and not owner['errors']
        assert owner['result_sha256'] == sha(directory / 'RESULT.json') == audit['provenance'][arm]['result_sha256']
        eligibility = read(directory / 'ELIGIBILITY.json')['arm_eligibility']
        binding = eligibility['binding']; child = binding['models'][binding['fixed_child']]
        request_inventory = []
        for call in value['calls']:
            saved = read(directory / 'calls' / (call['call_id'] + '.json'))
            assert sha(saved['raw_response_path']) == saved['raw_response_bytes_sha256']
            assert sha(saved['raw_request_path']) == saved['raw_request_bytes_sha256']
            request_inventory.append({'call_id': call['call_id'], 'model_alias': call['model'],
                'request_id': call['request_id'], 'request_body_sha256': call['request_body_sha256'],
                'response_object_sha256': call['raw_response_sha256'],
                'request_bytes_sha256': saved['raw_request_bytes_sha256'], 'response_bytes_sha256': saved['raw_response_bytes_sha256'],
                'completion_ids_sha256': digest(call['completion_ids'])})
        responses[arm] = request_inventory
        arms[arm] = {'correct': value['metrics']['correct'], 'available': 224, 'planned': 224,
            'accuracy': value['metrics']['correct'] / 224, 'valid_calls': 56, 'unavailable': 0,
            'per_class': per_class, 'cost': {**value['cost'], 'owner_seconds': owner['elapsed_seconds']},
            'model': child, 'model_alias': binding['fixed_child'], 'eligibility_sha256': sha(directory / 'ELIGIBILITY.json'),
            'runtime_sha256': sha(directory / 'RUNTIME.json'), 'engine_attestation_sha256': sha(directory / 'ENGINE_ATTESTATION.json'),
            'raw_audit_provenance': audit['provenance'][arm]}
    comparisons = {}
    for name, primary in audit['comparisons'].items():
        left, right = name.split('_vs_'); comparison = effects(audit['arms'][left]['predictions'], audit['arms'][right]['predictions'], gold)
        assert (comparison['wins'], comparison['losses'], comparison['changed_labels']) == (primary['wins'], primary['losses'], primary['category_disagreements'])
        groups = []
        for row in schedule:
            change = sum(audit['arms'][right]['predictions'][i] == gold[i] for i in row['ids']) - sum(audit['arms'][left]['predictions'][i] == gold[i] for i in row['ids'])
            groups.append(change)
        comparison.update(positive_B4_groups=sum(v > 0 for v in groups), negative_B4_groups=sum(v < 0 for v in groups),
            unchanged_score_B4_groups=sum(v == 0 for v in groups), planned_B4_groups=56,
            descriptive_interval_from_reviewed_audit=primary['descriptive_cluster_bootstrap_95_interval'])
        comparisons[name] = comparison
    same = sum(len({audit['arms'][arm]['predictions'][i] for arm in ARMS}) == 1 for i in gold)
    return {'schema': 'helper-dbpedia224-compact-findings-v1', 'status': 'completed_exploratory_cross_dataset_readout',
        'arms': arms, 'comparisons': comparisons, 'all_four_same_label': same, 'all_four_differing_records': 224 - same,
        'no_endpoint_or_seed_selection': True, 'response_provenance': responses,
        'source_sha256': {str(p): sha(p) for p in [AUDIT / 'RESULT.json', AUDIT / 'WATCH_TERMINAL.json',
            DATA / 'DATA_READY.json', DATA / 'inputs/HOST_GOLD.json', DATA / 'inputs/REQUESTS.json', EVAL / 'ENDPOINTS_FIXED.json', Path(__file__)]},
        'audit_scope': 'Counts and changed labels recomputed from previously raw-redecoded predictions; response byte hashes rechecked. Native decoder/trainer audit is reused, not independently rewritten.',
        'inherited_wording_correction': 'Audit baseline_reuse/training_costs prose mentions fresh512; actual DBpedia inventory is 56 B4 calls and 224 records per arm. No AG/DB pooling.',
        'interpretation': 'No meaningful DBpedia transfer gain: RL seed1 only changes one wrong label to another; seed2 fixes one OfficeHolder; SFT loses one Village. No broad learned semantic capability or RL superiority established.',
        'limits': ['Fourteen classes with sixteen items each; this is a balanced small panel, not natural class prevalence.',
                   '56 shared B4 groups, not 224 independent request units; descriptive bootstrap is not confirmation.',
                   'New local dataset/schema readout does not prove absence from pretraining.',
                   'No root, aggregation, delegation or recursion was tested.',
                   'Training costs are separate; no new training is charged to these endpoint calls.',
                   'Released-base comparison is separate and cannot support matched-cost claims because cache/LoRA service settings differ.']}


def markdown(result):
    lines = ['# DBpedia transfer: essentially unchanged', '',
        'All four fixed models returned 224/224 available labels in 56/56 valid four-record calls, with qualified runtime and clean release. No endpoint or seed was chosen from these outcomes.', '',
        '| Fixed model | Correct / 224 | Accuracy | Owner seconds |', '|---|---:|---:|---:|']
    for arm in ARMS:
        a = result['arms'][arm]; lines.append(f"| {arm} | {a['correct']} | {a['accuracy']:.2%} | {a['cost']['owner_seconds']:.2f} |")
    lines += ['', '| Before → after | Wins / losses | Labels changed | Wrong → different wrong |', '|---|---:|---:|---:|']
    for key, c in result['comparisons'].items():
        lines.append(f"| {key.replace('_vs_', ' → ')} | {c['wins']} / {c['losses']} | {c['changed_labels']} | {c['wrong_to_different_wrong']} |")
    lines += ['', f"All four agree on {result['all_four_same_label']}/224 labels. RL seed1's only c32-relative change remains wrong; seed2 corrects that OfficeHolder item. SFT introduces one Village error. These two items explain all variation; article text is not reproduced.", '',
              '| Gold class (16 each) | c32 | RL seed1 | SFT | RL seed2 |', '|---|---:|---:|---:|---:|']
    for label in result['arms']['c32']['per_class']:
        lines.append('| ' + label + ' | ' + ' | '.join(str(result['arms'][a]['per_class'][label]['correct']) for a in ARMS) + ' |')
    lines += ['', 'Every arm used 60,945 input tokens (36,832 cached); outputs were ' + ', '.join(f"{a}: {result['arms'][a]['cost']['completion_tokens_observed_subtotal']}" for a in ARMS) + '. All usage fields were available. Training cost is separate.', '',
        'Decision: do not promote AG-trained RL as broad helper capability transfer or meaningfully superior to SFT. DBpedia is almost invariant across these fixed endpoints. The released-base reference will distinguish recovery of pretrained skill from improvement beyond base; different cache/LoRA settings preclude a matched-cost interpretation.', '',
        'Scope: fourteen balanced classes, sixteen records each; uncertainty units are 56 shared B4 requests. Local holdout is not pretraining exclusion. No whole-RLM/delegation capability was measured. The source audit contains inherited fresh512 wording; the actual verified DBpedia denominator here is 224, and panels are not pooled.', '',
        'Reproduce with `CUDA_VISIBLE_DEVICES=\'\' PYTHONDONTWRITEBYTECODE=1 /project/alex_phd/envs/prime-rl-5990b1b/bin/python derive.py --check`. FINDINGS.json retains source/model/response hashes without raw articles or full native calls.', '']
    return '\n'.join(lines)


if __name__ == '__main__':
    import sys
    value = derive()
    if '--check' in sys.argv:
        assert value == read(ROOT / 'FINDINGS.json')
        assert markdown(value) == (ROOT / 'FINDINGS.md').read_text()
        print('Reproduced compact JSON and Markdown exactly')
    else:
        for name, text in [('FINDINGS.json', json.dumps(value, indent=2, sort_keys=True) + '\n'), ('FINDINGS.md', markdown(value))]:
            with (ROOT / name).open('x') as stream: stream.write(text)
        print({a: value['arms'][a]['correct'] for a in ARMS})
