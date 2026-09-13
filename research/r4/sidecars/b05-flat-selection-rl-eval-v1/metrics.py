"""Strict ID contract primary and unordered-known-unique semantics separately."""
import json
import study as s
with s.aliases({'runner_study':s},s.ROOT):costs=s.load('ba18_eval_costs',s.SOURCE/'runner_metrics.py').costs

def grade(c,r):
    result=dict(call_id=s.call_id(c),**c,available=bool(r.get('transport_valid')),strict_valid=False,semantic_valid=False,
        strict_exact=False,semantic_exact=False,ids=None,balanced_accuracy=None)
    if not result['available']:return result
    strict=s.b05().grade_child_response(r['text'],s.child(c));result['strict_valid']=strict['status']=='valid_claim'
    known=set(s.task(c)['known_ids']);gold=s.gold()[c['split'],c['root_id']]
    try:
        def pairs(items):
            out={}
            for k,v in items:
                assert k not in out;out[k]=v
            return out
        parsed=json.loads(r['text'],object_pairs_hook=pairs);assert set(parsed)=={'eligible_ids'}
        ids=parsed['eligible_ids'];assert isinstance(ids,list) and all(isinstance(x,str) for x in ids)
        assert len(ids)==len(set(ids)) and set(ids)<=known
        pred=set(ids);tp=len(pred&gold);fp=len(pred-gold);fn=len(gold-pred);tn=len(known-gold-pred)
        result.update(semantic_valid=True,ids=ids,semantic_exact=pred==gold,strict_exact=result['strict_valid'] and pred==gold,
            balanced_accuracy=s.train.reward(pred,gold,known),tp=tp,fp=fp,fn=fn,tn=tn,
            jaccard=tp/(tp+fp+fn) if tp+fp+fn else 1.,f1=2*tp/(2*tp+fp+fn) if 2*tp+fp+fn else 1.,
            precision=tp/len(pred) if pred else None,recall=tp/len(gold) if gold else None,
            all_ids_BA=s.train.reward(known,gold,known),empty_BA=s.train.reward(set(),gold,known))
    except (ValueError,TypeError,AssertionError,KeyError):pass
    return result

def summarize(output,qualified):
    records={p.stem:s.read(p) for p in (output/'calls').glob('*.json')};expected={s.call_id(c) for c in s.calls()}
    starts={p.stem:s.read(p) for p in (output/'starts').glob('*.json')}
    assert set(records)<=expected and set(starts)<=expected
    start_only=set(starts)-set(records)
    for key in start_only:records[key]={**starts[key], 'status':'start_only_provider_unknown','transport_valid':False,'usage':{}}
    rows=[grade(c,records.get(s.call_id(c),{})) for c in s.calls()];summary={};paired={}
    for split in ('train','held'):
        for arm in ('base','cp1'):
            items=[r for r in rows if r['split']==split and r['arm']==arm];sem=[r for r in items if r['semantic_valid']]
            summary[f'{split}/{arm}']=dict(planned=18,available=sum(r['available'] for r in items),
                unavailable=sum(not r['available'] for r in items),strict_valid=sum(r['strict_valid'] for r in items),
                strict_exact=sum(r['strict_exact'] for r in items),semantic_valid=len(sem),semantic_exact=sum(r['semantic_exact'] for r in items),
                balanced_accuracy_mean=sum(r['balanced_accuracy'] for r in sem)/len(sem) if sem else None,
                BA_available_denominator=len(sem),confusion={k:sum(r[k] for r in sem) for k in ('tp','fp','fn','tn')},
                cost=costs([records.get(r['call_id'],{}) for r in items],18))
        pairs=[]
        for a in [r for r in rows if r['split']==split and r['arm']=='base']:
            b=next(r for r in rows if r['split']==split and r['root_id']==a['root_id'] and r['repeat']==a['repeat'] and r['arm']=='cp1')
            pairs.append(dict(root_id=a['root_id'],repeat=a['repeat'],available=a['available'] and b['available'],
                strict_base=a['strict_exact'],strict_cp1=b['strict_exact'],semantic_base=a['semantic_exact'],semantic_cp1=b['semantic_exact'],
                both_semantic_valid=a['semantic_valid'] and b['semantic_valid'],BA_change=b['balanced_accuracy']-a['balanced_accuracy'] if a['semantic_valid'] and b['semantic_valid'] else None))
        paired[split]=dict(contexts=9,planned_pairs=18,available_pairs=sum(p['available'] for p in pairs),pairs=pairs)
    valid=sum(r['available'] for r in rows)
    return dict(schema='BA18-fixed-endpoint-native-readout-v1',complete=qualified and valid==72 and not start_only,
        runtime_qualified=qualified,planned72=72,available=valid,summary=summary,paired=paired,rows=rows,
        cost=costs(list(records.values()),72),start_only=sorted(start_only),unattempted=sorted(expected-set(records)),
        length_stops=sum(r.get('finish_reason')=='length' for r in records.values()),
        primary='strict ordered eligible-ID-set exact; unavailable is not wrong',
        semantic_secondary='unordered known unique IDs; BA over present classes',
        no_eligibility_repair=True,train_is_in_sample=True,held_context_units=9)
