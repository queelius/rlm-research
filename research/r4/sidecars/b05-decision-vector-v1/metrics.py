"""Full-set exact, strict interface validity, matched-valid BA and honest unknown costs."""
import interface
import study as s
with s.aliases({'runner_study':s},s.SOURCE):costs=s.load('vector_native_costs',s.SOURCE/'runner_metrics.py').costs


def grade(call,record,order,gold):
    row={**call,'call_id':s.call_id(call),'available':bool(record.get('transport_valid')),'semantic_valid':False,'strict_valid':False,
         'exact':False,'strict_exact':False,'balanced_accuracy':None,'precision':None,'recall':None,'ids':None,'vector':None}
    if not row['available']:return row
    try:
        parsed=interface.parse(record['text'],call['arm'],order);pred=set(parsed['ids']);known=set(order)
        tp=len(pred&gold);fp=len(pred-gold);fn=len(gold-pred);tn=len(known-gold-pred)
        recalls=([tp/len(gold)] if gold else [])+([tn/len(known-gold)] if known-gold else [])
        row.update(**parsed,semantic_valid=True,exact=pred==gold,strict_exact=pred==gold and parsed['strict_valid'],
            tp=tp,fp=fp,fn=fn,tn=tn,balanced_accuracy=sum(recalls)/len(recalls),precision=tp/len(pred) if pred else None,recall=tp/len(gold) if gold else None)
    except (ValueError,AssertionError,TypeError,KeyError) as error:row['error']=f'{type(error).__name__}: {error}'
    return row


def aggregate(rows):
    valid=[r for r in rows if r['semantic_valid']];counts={k:sum(r[k] for r in valid) for k in ('tp','fp','fn','tn')}
    tp,fp,fn=counts['tp'],counts['fp'],counts['fn']
    return dict(planned=len(rows),available=sum(r['available'] for r in rows),unknown=sum(not r['available'] for r in rows),
        unordered_exact=sum(r['exact'] for r in rows),exact_denominator_all_planned=len(rows),semantic_valid=len(valid),
        invalid_known=sum(r['available'] and not r['semantic_valid'] for r in rows),strict_valid=sum(r['strict_valid'] for r in rows),strict_exact=sum(r['strict_exact'] for r in rows),
        confusion=counts,BA_valid_set_mean=sum(r['balanced_accuracy'] for r in valid)/len(valid) if valid else None,BA_valid_set_denominator=len(valid),
        micro_precision_valid_sets=tp/(tp+fp) if tp+fp else None,micro_recall_valid_sets=tp/(tp+fn) if tp+fn else None)


def summarize(output,qualified):
    plan=s.read(s.INPUTS);tasks={r['root_id']:r for r in plan['tasks']};gold={r['root_id']:set(r['gold_ids']) for r in s.read(s.HOST)['rows']}
    records={p.stem:s.read(p) for p in (output/'calls').glob('*.json')};starts={p.stem:s.read(p) for p in (output/'starts').glob('*.json')}
    expected={s.call_id(c) for c in plan['calls']};assert set(records)<=expected and set(starts)<=expected
    start_only=set(starts)-set(records)
    for key in start_only:records[key]={**starts[key],'transport_valid':False,'usage':{},'status':'start_only_provider_unknown'}
    rows=[grade(c,records.get(s.call_id(c),{}),tasks[c['root_id']]['public_order'],gold[c['root_id']]) for c in plan['calls']]
    arms={a:{**aggregate([r for r in rows if r['arm']==a]),'cost':costs([records.get(r['call_id'],{}) for r in rows if r['arm']==a],24)} for a in ('list','vector')}
    pairs=[];matched=[]
    for left in [r for r in rows if r['arm']=='list']:
        right=next(r for r in rows if r['arm']=='vector' and (r['root_id'],r['repeat'])==(left['root_id'],left['repeat']))
        assert left['seed']==right['seed'];valid=left['semantic_valid'] and right['semantic_valid']
        if valid:matched.extend([left,right])
        pairs.append(dict(root_id=left['root_id'],repeat=left['repeat'],seed=left['seed'],paired_known=left['available'] and right['available'],matched_valid=valid,
            list_exact=left['exact'],vector_exact=right['exact'],BA_change=right['balanced_accuracy']-left['balanced_accuracy'] if valid else None))
    known=[p for p in pairs if p['paired_known']];available=sum(r['available'] for r in rows)
    return dict(schema='b05-normalized-list-vs-decision-vector48-result-v1',complete=bool(qualified and available==48 and not start_only),runtime_qualified=qualified,
        planned=48,available=available,unknown=48-available,context_units=12,paired_seed_units=24,arms=arms,pairs=pairs,rows=rows,
        vector_wins=sum(not p['list_exact'] and p['vector_exact'] for p in known),vector_losses=sum(p['list_exact'] and not p['vector_exact'] for p in known),
        matched_valid_arms={a:aggregate([r for r in matched if r['arm']==a]) for a in ('list','vector')},
        cost=costs(list(records.values()),48),start_only=sorted(start_only),unattempted=sorted(expected-set(records)),unknown_is_not_wrong=True,
        no_partial_credit_on_invalid=True,invalid_ids_remain_none=True,strict_list_sorting_separate=True,
        output_interface_and_lengths_differ=True,natural_model_calls_per_answer=1,token_costs_not_matched=True,not_learned_decomposition=True)
