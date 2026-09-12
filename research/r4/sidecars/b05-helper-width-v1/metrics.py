"""Union unmodified claimed IDs; report known invalid and unavailable separately."""
from pathlib import Path
import interface
import study
with study.aliases({'runner_study':study},study.SOURCE):
    inherited=study.load('width_original_costs',study.SOURCE/'runner_metrics.py')
costs=inherited.costs

def stage_group(calls,records):
    first=calls[0];k=first['helpers']
    assert len(calls)==k and sorted(c['part'] for c in calls)==list(range(k))
    rows=[records.get(study.call_id(c),{}) for c in calls]
    available=all(r.get('transport_valid',False) for r in rows)
    valid=available and all(r.get('child_grade',{}).get('status')=='valid_claim' for r in rows)
    target=set(study.gold()[first['root_id']])
    value=dict(root_id=first['root_id'],width=first['width'],helpers=k,repeat=first['alternative'],
        call_ids=[study.call_id(c) for c in calls],available=available,strict_claim_valid=valid,
        invalid_claim=available and not valid,ids=None,exact=None,true_positive=None,
        false_positive=None,false_negative=None,precision=None,recall=None,gold_count=len(target),
        physical_cost=costs(rows,k))
    if valid:
        ids=set().union(*(set(r['child_grade']['parsed']['eligible_ids']) for r in rows))
        tp=len(ids&target)
        value.update(ids=sorted(ids),exact=ids==target,true_positive=tp,false_positive=len(ids-target),
            false_negative=len(target-ids),precision=tp/len(ids) if ids else None,
            recall=tp/len(target) if target else None)
    return value

def aggregate(groups):
    valid=[g for g in groups if g['strict_claim_valid']]
    tp=sum(g['true_positive'] for g in valid)
    fp=sum(g['false_positive'] for g in valid);fn=sum(g['false_negative'] for g in valid)
    return dict(planned=len(groups),available=sum(g['available'] for g in groups),
        unavailable=sum(not g['available'] for g in groups),strict_valid=len(valid),
        invalid_claim=sum(g['invalid_claim'] for g in groups),exact=sum(g['exact'] is True for g in groups),
        exact_denominator='planned; unknown and invalid counts remain separately visible',
        true_positive_valid_only=tp,false_positive_valid_only=fp,false_negative_valid_only=fn,
        micro_precision_valid_only=tp/(tp+fp) if tp+fp else None,
        micro_recall_valid_only=tp/(tp+fn) if tp+fn else None)

def summarize(output,runtime_qualified):
    output=Path(output);plan=study.calls();expected={study.call_id(c):c for c in plan}
    records={p.stem:study.read(p) for p in (output/'calls').glob('*.json')}
    starts={p.stem for p in (output/'starts').glob('*.json')}
    assert set(records)<=set(expected) and starts<=set(expected)
    start_only=starts-set(records)
    for ident in start_only:
        records[ident]={**study.read(output/'starts'/f'{ident}.json'),
            'status':'start_only_provider_unknown','transport_valid':False,'usage':{}}
    for ident,r in records.items():
        c=expected[ident]
        assert all(r[key]==value for key,value in c.items())
        if r.get('transport_valid'):
            assert r['child_grade']==interface.grade(r['text'],study.child(c))
    groups=[]
    for root in study.active_roots():
        for k in (1,2,4):
            for repeat in range(2):
                subset=[c for c in plan if c['root_id']==root['root_id'] and c['helpers']==k and c['alternative']==repeat]
                groups.append(stage_group(subset,records))
    arms={}
    for k in (1,2,4):
        selected=[g for g in groups if g['helpers']==k]
        calls=[c for c in plan if c['helpers']==k]
        arms[str(k)]={**aggregate(selected),'by_width':{str(n):aggregate([g for g in selected if g['width']==n]) for n in (6,12,20)},
                      'cost':costs([records.get(study.call_id(c),{}) for c in calls],len(calls))}
    paired={}
    for k in (2,4):
        pairs=[(next(g for g in groups if g['root_id']==r['root_id'] and g['repeat']==rep and g['helpers']==1),
                next(g for g in groups if g['root_id']==r['root_id'] and g['repeat']==rep and g['helpers']==k))
               for r in study.active_roots() for rep in range(2)]
        available=[(a,b) for a,b in pairs if a['available'] and b['available']]
        valid=[(a,b) for a,b in pairs if a['strict_claim_valid'] and b['strict_claim_valid']]
        paired[str(k)]={'planned':18,'both_available':len(available),'both_strict_valid':len(valid),
            'exact_wins_among_available_invalid_is_known_failure':sum(a['exact'] is not True and b['exact'] is True for a,b in available),
            'exact_losses_among_available_invalid_is_known_failure':sum(a['exact'] is True and b['exact'] is not True for a,b in available),
            'exact_wins_among_both_strict_valid':sum(not a['exact'] and b['exact'] for a,b in valid),
            'exact_losses_among_both_strict_valid':sum(a['exact'] and not b['exact'] for a,b in valid),
            'changed_ID_sets_among_both_strict_valid':sum(a['ids']!=b['ids'] for a,b in valid)}
    complete=bool(runtime_qualified and set(records)==set(expected) and not start_only and
                  all(r.get('transport_valid') for r in records.values()))
    return dict(schema='b05-width-stage-union-v1',complete=complete,runtime_qualified=runtime_qualified,
        planned_physical=126,planned_stage_policies=54,independent_stage_cases=9,repeats_per_case=2,
        root_model_calls=0,arms=arms,paired_vs_flat=paired,stage_groups=groups,
        physical_cost=costs(list(records.values()),126),start_only_ids=sorted(start_only),
        unattempted_ids=sorted(set(expected)-set(records)),call_statuses={k:v.get('status') for k,v in records.items()},
        raw_requests=len(list((output/'native').glob('*-REQUEST.json'))),
        raw_responses=len(list((output/'native').glob('*-RESPONSE.json'))),
        fixed_not_learned_fanout=True,no_eligibility_repair=True,
        limitations=['three stage cases per width; repeated decodes not independent cases',
          'stock guaranteed-feasible generator; not arbitrary database distribution',
          'no root synthesis or learned depth policy; IDs-only local predicate extraction'])
