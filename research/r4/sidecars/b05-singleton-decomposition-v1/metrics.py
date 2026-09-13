"""Complete-stage scalar union, fixed denominators, matched comparisons and physical costs."""
import collections
import interface
import study as s
vector_interface=s.load('singleton_existing_vector_interface',s.PRIOR/'interface.py')
with s.aliases({'study':s,'interface':vector_interface},s.PRIOR):prior=s.load('singleton_existing_vector_metrics',s.PRIOR/'metrics.py')
costs=prior.costs
ARMS=('list','vector','singleton')


def semantic(row,order,gold):
    row.update(exact=False,strict_exact=False,balanced_accuracy=None,precision=None,recall=None,candidate_accuracy=None,f1=None,jaccard=None)
    if not row['semantic_valid']:return row
    pred=set(row['ids']);known=set(order);tp=len(pred&gold);fp=len(pred-gold);fn=len(gold-pred);tn=len(known-gold-pred)
    recalls=([tp/len(gold)] if gold else [])+([tn/len(known-gold)] if known-gold else [])
    row.update(exact=pred==gold,strict_exact=pred==gold and row['strict_valid'],tp=tp,fp=fp,fn=fn,tn=tn,
        balanced_accuracy=sum(recalls)/len(recalls),candidate_accuracy=(tp+tn)/len(order),precision=tp/(tp+fp) if tp+fp else None,
        recall=tp/(tp+fn) if tp+fn else None,f1=2*tp/(2*tp+fp+fn) if 2*tp+fp+fn else 1.,jaccard=tp/(tp+fp+fn) if tp+fp+fn else 1.)
    return row


def aggregate(rows):
    value=prior.aggregate(rows);valid=[r for r in rows if r['semantic_valid']];c=value['confusion']
    value.update(correct=sum(r['exact'] for r in rows),wrong=sum(r['available'] and not r['exact'] for r in rows),
        task_exact_lower_bound=sum(r['exact'] for r in rows),task_exact_upper_bound=sum(r['exact'] or not r['available'] for r in rows),
        candidate_accuracy_valid_sets=(c['tp']+c['tn'])/sum(c.values()) if sum(c.values()) else None,
        valid_set_candidate_denominator=sum(c.values()),mean_f1_valid_sets=sum(r['f1'] for r in valid)/len(valid) if valid else None,
        mean_jaccard_valid_sets=sum(r['jaccard'] for r in valid)/len(valid) if valid else None,
        sorting_only=sum(r['semantic_valid'] and not r['strict_valid'] for r in rows),
        invalid_candidate_count=sum(len(r.get('invalid_candidates',[])) for r in rows),unknown_candidate_count=sum(len(r.get('unknown_candidates',[])) for r in rows))
    return value


def summarize(output,qualified):
    plan=s.read(s.INPUTS);gold={r['root_id']:set(r['gold_ids']) for r in s.read(s.HOST)['rows']}
    records={p.stem:s.read(p) for p in (output/'calls').glob('*.json')};starts={p.stem:s.read(p) for p in (output/'starts').glob('*.json')}
    expected={s.call_id(c) for c in plan['calls']};assert set(records)<=expected and set(starts)<=expected
    start_only=set(starts)-set(records)
    for key in start_only:records[key]={**starts[key],'transport_valid':False,'usage':{},'status':'start_only_provider_unknown'}
    rows=[];baselines=[]
    for task in plan['tasks']:
        root=task['root_id'];order=task['public_order'];truth=gold[root]
        for name,ids in [('all_true',order),('all_false',[])]:
            baselines.append(semantic(dict(root_id=root,width=task['width'],arm=name,available=True,semantic_valid=True,strict_valid=True,ids=ids),order,truth))
        for repeat in (0,1):
            for arm in ARMS:
                calls=[c for c in plan['calls'] if (c['root_id'],c['repeat'],c['arm'])==(root,repeat,arm)]
                call_ids=[s.call_id(c) for c in calls];values=[records.get(k,{}) for k in call_ids]
                row=dict(root_id=root,width=task['width'],repeat=repeat,seed=202609430000+2*task['case_index']+repeat,arm=arm,
                    call_ids=call_ids,available=False,semantic_valid=False,strict_valid=False,ids=None,unknown_candidates=[],invalid_candidates=[])
                if arm=='singleton':
                    row.update(interface.singleton_union(order,{c['candidate_index']:v for c,v in zip(calls,values)}))
                    observed=row['observed_decisions'];decisions=[(order[i] in truth,pred) for i,pred in observed.items()]
                    row['partial_candidate_confusion']={k:sum(condition(y,p) for y,p in decisions) for k,condition in {
                        'tp':lambda y,p:y and p,'fp':lambda y,p:not y and p,'fn':lambda y,p:y and not p,'tn':lambda y,p:not y and not p}.items()}
                    row['partial_candidate_denominator']=len(decisions)
                else:
                    assert len(calls)==1;row['available']=bool(values[0].get('transport_valid'))
                    if row['available']:
                        try:row.update(vector_interface.parse(values[0]['text'],arm,order),semantic_valid=True)
                        except (ValueError,AssertionError,TypeError,KeyError) as error:row['error']=f'{type(error).__name__}: {error}'
                row=semantic(row,order,truth);row['cost']=costs(values,len(calls));rows.append(row)
    arms={a:{**aggregate([r for r in rows if r['arm']==a]),'by_width':{str(w):aggregate([r for r in rows if r['arm']==a and r['width']==w]) for w in (6,12,20)},
        'cost':costs([records.get(s.call_id(c),{}) for c in plan['calls'] if c['arm']==a],sum(c['arm']==a for c in plan['calls']))} for a in ARMS}
    pairs={}
    for left,right in [('list','vector'),('list','singleton'),('vector','singleton')]:
        paired=[]
        for a in [r for r in rows if r['arm']==left]:
            b=next(r for r in rows if r['arm']==right and (r['root_id'],r['repeat'])==(a['root_id'],a['repeat']))
            matched=a['semantic_valid'] and b['semantic_valid'];known=a['available'] and b['available']
            paired.append(dict(root_id=a['root_id'],width=a['width'],repeat=a['repeat'],paired_known=known,matched_valid=matched,
                left_exact=a['exact'],right_exact=b['exact'],win=known and b['exact'] and not a['exact'],loss=known and a['exact'] and not b['exact'],
                changed_ids=sorted(set(a['ids'])^set(b['ids'])) if matched else None,BA_change=b['balanced_accuracy']-a['balanced_accuracy'] if matched else None))
        matchedroots={(p['root_id'],p['repeat']) for p in paired if p['matched_valid']}
        pairs[left+'_vs_'+right]=dict(rows=paired,wins=sum(p['win'] for p in paired),losses=sum(p['loss'] for p in paired),
            matched_valid=len(matchedroots),paired_known=sum(p['paired_known'] for p in paired),
            matched_valid_arms={arm:aggregate([r for r in rows if r['arm']==arm and (r['root_id'],r['repeat']) in matchedroots]) for arm in (left,right)})
    available=sum(bool(records.get(k,{}).get('transport_valid')) for k in expected)
    return dict(schema='b05-singleton-decomposition176-result-v1',complete=bool(qualified and available==176 and not start_only),runtime_qualified=qualified,
        planned=176,available=available,unknown=176-available,context_units=6,stage_seed_units=12,stage_arm_outputs=36,
        arms=arms,pairs=pairs,rows=rows,constant_baselines=baselines,cost=costs(list(records.values()),176),
        finish_counts=dict(collections.Counter(r.get('finish_reason','unknown') for r in records.values())),start_only=sorted(start_only),unattempted=sorted(expected-set(records)),
        singleton_partial_candidate_confusion={k:sum(r.get('partial_candidate_confusion',{}).get(k,0) for r in rows) for k in ('tp','fp','fn','tn')},
        singleton_partial_candidate_denominator=sum(r.get('partial_candidate_denominator',0) for r in rows),
        unknown_is_not_wrong=True,no_eligibility_repair=True,all_candidates_required_for_stage_semantics=True,
        singleton_partial_candidates_not_full_stage_score=True,strict_list_sorting_separate=True,token_costs_not_matched=True,not_learned_decomposition=True)
