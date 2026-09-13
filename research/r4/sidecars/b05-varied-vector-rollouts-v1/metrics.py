"""Retain all64 samples and16 G4 groups; frozen held labels never score training calls."""
import diagnostics
import study as s
with s.aliases({'study':s,'interface':s.interface},s.ROOT):previous=s.load('varied_vector_original_metrics',s.PRIOR/'metrics.py')
grade=previous.grade;aggregate=previous.aggregate;costs=previous.costs


def summarize(output,qualified):
    plan=s.read(s.INPUTS);tasks={r['root_id']:r for r in plan['tasks']};gold={r['root_id']:set(r['gold_ids']) for r in s.read(s.HOST)['rows'] if r['split']=='train'}
    records={p.stem:s.read(p) for p in (output/'calls').glob('*.json')};starts={p.stem:s.read(p) for p in (output/'starts').glob('*.json')}
    expected={s.call_id(c) for c in plan['calls']};assert set(records)<=expected and set(starts)<=expected
    start_only=set(starts)-set(records)
    for key in start_only:records[key]={**starts[key],'transport_valid':False,'usage':{},'status':'start_only_provider_unknown'}
    rows=[]
    for call in plan['calls']:
        key=s.call_id(call);record=records.get(key,{});order=tasks[call['root_id']]['public_order'];row=grade(call,record,order,gold[call['root_id']])
        row['native_spans']=diagnostics.native_spans(record,order) if row['semantic_valid'] else {'qualified':False,'reason':'full output invalid or unavailable','no_repair':True}
        rows.append(row)
    groups=[]
    for root,task in tasks.items():
        selected=sorted([r for r in rows if r['root_id']==root],key=lambda r:r['repeat']);assert [r['repeat'] for r in selected]==[0,1,2,3]
        groups.append({'root_id':root,'width':task['width'],'history_depth':task['history_depth'],'summary':aggregate(selected),
            'contrast':diagnostics.group_contrast(selected,task['public_order'],gold[root]),'all_native_spans_qualified':all(r['native_spans']['qualified'] for r in selected)})
    available=sum(r['available'] for r in rows)
    return dict(schema='b05-varied-vector-G4-rollouts64-result-v1',complete=bool(qualified and available==64 and not start_only),runtime_qualified=qualified,
        planned=64,available=available,unknown=64-available,context_units=16,G=4,summary=aggregate(rows),rows=rows,groups=groups,
        full_valid_G4_groups=sum(r['contrast']['full_G4_valid'] for r in groups),native_spans_qualified=sum(r['native_spans']['qualified'] for r in rows),
        exclusive_boolean_token_rows=sum(r['native_spans'].get('exclusive_boolean_token_feasible',False) for r in rows),
        cost=costs(list(records.values()),64),start_only=sorted(start_only),unattempted=sorted(expected-set(records)),
        held_calls_executed=0,no_optimizer_or_adapter=True,all_groups_retained=True,no_invalid_output_repair=True,unknown_is_not_wrong=True)
