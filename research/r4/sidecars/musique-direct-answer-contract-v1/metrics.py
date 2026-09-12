"""Frozen direct12 versus new concise12; all answer/support fields and unknowns retained."""
from collections import Counter
import study

with study.aliases({'study':study},study.ROOT):original=study.load('answer_contract_original_metrics',study.SERVICE_ROOT/'metrics.py')
costs=original.costs;paired=original.paired


def summarize(output,runtime_qualified):
    cache=study.read(study.INPUTS/'host/BASELINE.json');gold=study.read(study.SERVICE_ROOT/'inputs/host/HOST_GOLD.json')
    calls={p.stem:study.read(p) for p in (output/'calls').glob('*.json')};schedule=study.schedule();expected={r['call_id'] for r in schedule}
    starts={p.stem for p in (output/'starts').glob('*.json')};assert set(calls)<=expected and starts<=expected
    for cid in starts-set(calls):calls[cid]={**study.read(output/'starts'/(cid+'.json')),'status':'start_only_provider_unknown','transport_valid':False,'usage':{}}
    lookup={r['record_id']:calls.get(r['call_id'],{}) for r in schedule};new_scores={}
    for item in study.selected():
        ident=item['record_id'];native=lookup[ident]
        new_scores[ident]=study.score_final(native,gold[ident],item['paragraph_count'])
        new_scores[ident].update(final_native_status=native.get('status','unattempted'),final_finish_reason=native.get('finish_reason'),final_failure=native.get('failure'))
    for ident in cache['scores']:
        new_scores.setdefault(ident,{'available':False,'answer_em':None,'answer_f1':None,'support_em':None,'support_f1':None,'valid_json':False,'final_native_status':'unattempted'})
    arms={}
    for arm,scores in (('direct',cache['scores']),('concise',new_scores)):
        known=[v for v in scores.values() if v['available']]
        arms[arm]={'planned':12,'available':len(known),'correct':sum(v['answer_em'] for v in known),'unavailable':12-len(known),
                   'malformed_final_json':sum(not v['valid_json'] for v in known),
                   **{field+'_sum_available':sum(v[field] for v in known) for field in ('answer_f1','support_em','support_f1')},
                   'scores':scores,'primary_accuracy':sum(v['answer_em'] for v in known)/12 if len(known)==12 and (arm=='direct' or runtime_qualified) else None}
    complete=runtime_qualified and len(calls)==12 and len(list((output/'questions').glob('*.json')))==12 and arms['concise']['available']==12
    return {'schema':'musique-direct-answer-contract-result-v1','complete':complete,'runtime_qualified':runtime_qualified,
            'planned_new_physical_calls':12,'planned_new_final_slots':12,'comparison_terminal_slots':24,'unique_questions':12,
            'arms':arms,'paired_direct_to_concise':paired(arms['direct']['scores'],arms['concise']['scores']),
            'new_physical_cost':costs(list(calls.values()),12),'cached_direct_final_cost':costs(cache['direct_calls'],12),
            'cached_acquisition_cost':costs(cache['acquisition_calls'],36),
            'natural_full_policy_cost':{'direct':costs(cache['acquisition_calls']+cache['direct_calls'],48),
                                        'concise':costs(cache['acquisition_calls']+list(calls.values()),48)},
            'status_counts':dict(Counter(v.get('status') for v in calls.values())),'missing_receipt_ids':sorted(expected-set(calls)),
            'cost_boundary':'12 newly spent calls. Conditional finalization1 vs1; full natural policies4 vs4 (48 each), cached acquisition charged but not rerun. Token cost not matched.',
            'claim_boundary':'One universal answer-wording intervention adaptively proposed on exposed12 after observing answer-surface errors; not new information or demonstrated composition.'}
