"""Post-hoc counterfactual: ignore ordering only, never infer missing eligibility."""
import json
from pathlib import Path
import analyze

study, interface = analyze.modules()
expected = {study.call_id(call): call for call in study.calls()}
roots = {root['root_id']: root for root in study.active_roots()}
source = study.read(study.ATTEMPT / 'RESULT.json')
resolved = {}
rows = []
for cid, call in expected.items():
    record = study.read(study.ATTEMPT / 'calls' / (cid+'.json'))
    child = roots[call['root_id']]['safe_children'][call['child_index']]
    obj = json.loads(record['text'])
    assert set(obj) == {'eligible_ids'}
    ids = obj['eligible_ids']
    assert len(ids) == len(set(ids)) and all(isinstance(i, str) for i in ids)
    known = {row['implementation_id'] for row in child['stage']['tables']['implementations']}
    assert set(ids) <= known
    grade = interface.grade(record['text'], child)
    canonical = interface.grade(json.dumps({'eligible_ids': sorted(ids)}), child)
    assert canonical['status'] == 'valid_claim'
    target = {row['implementation_id'] for row in interface.reference().solve_child_reference(child)['rows']}
    rows.append(dict(call_id=cid, strict_valid=grade['status']=='valid_claim', sorted=ids==sorted(ids),
        unordered_set_exact=set(ids)==target, true_positive=len(set(ids)&target),
        false_positive=len(set(ids)-target), false_negative=len(target-set(ids))))
    resolved[cid] = interface.lookup(ids, child)
api = study.source.b05()
combos = []
for call in study.source.calls():
    if call['kind'] != 'recombined_synthesis':
        continue
    deps = [next(cid for cid,c in expected.items() if c['root_id']==call['root_id'] and c['child_index']==i and c['alternative']==a)
            for i,a in enumerate(call['alternatives'])]
    root = roots[call['root_id']]['safe_root']
    answer = api.combine_reports(root, [resolved[cid] for cid in deps])
    grade = api.grade_root_response(json.dumps(answer), root)
    combos.append(dict(call_id=study.call_id(call), status=grade['status']))
result = dict(schema='b05-posthoc-order-only-diagnostic-v1', strict_primary_unchanged=True,
    no_new_model_calls=True, no_eligibility_filter_or_missing_ID_repair=True,
    invalid_due_only_to_order=sum(not row['strict_valid'] for row in rows),
    unordered_exact=sum(row['unordered_set_exact'] for row in rows),
    posthoc_host_correct=sum(row['status']=='correct' for row in combos), host_coordinates=len(combos),
    rows=rows, combinations=combos, source_result_sha256=study.sha(study.ATTEMPT/'RESULT.json'),
    analysis_sha256=study.sha(Path(__file__)))
study.write_x(Path(__file__).with_name('ORDER_DIAGNOSTIC.json'), result)
print(json.dumps({k:v for k,v in result.items() if k not in ('rows','combinations')}))
