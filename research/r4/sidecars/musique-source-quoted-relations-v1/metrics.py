"""Host-only cached direct versus new relation-assisted scores; explicit incremental costs."""
from collections import Counter
import study

with study.aliases({'study':study},study.ROOT):original=study.load('relations_original_metrics',study.SERVICE_ROOT/'metrics.py')
costs=original.costs;paired=original.paired


def summarize(output,runtime_qualified):
    cache=study.read(study.INPUTS/'host/BASELINE.json');gold=study.read(study.SERVICE_ROOT/'inputs/host/HOST_GOLD.json')
    calls={p.stem:study.read(p) for p in (output/'calls').glob('*.json')};schedule=study.schedule();expected={r['call_id'] for r in schedule}
    starts={p.stem for p in (output/'starts').glob('*.json')};assert set(calls)<=expected and starts<=expected
    for cid in starts-set(calls):calls[cid]={**study.read(output/'starts'/(cid+'.json')),'status':'start_only_provider_unknown','transport_valid':False,'usage':{}}
    lookup={(r['record_id'],r['role']):calls.get(r['call_id'],{}) for r in schedule}
    new_scores={}
    for item in study.selected():
        ident=item['record_id'];final=lookup[ident,'relations'];score=study.score_final(final,gold[ident],item['paragraph_count'])
        if not lookup[ident,'extract'].get('transport_valid',False):
            score={'available':False,'answer_em':None,'answer_f1':None,'support_em':None,'support_f1':None,'valid_json':False,'observed_final_score_diagnostic_only':score}
        new_scores[ident]=score
    # Missing contexts remain unknown; cached all12 controls are never case-filtered.
    for ident in cache['scores']:
        new_scores.setdefault(ident,{'available':False,'answer_em':None,'answer_f1':None,'support_em':None,'support_f1':None,'valid_json':False})
    arms={}
    for arm,scores in (('direct',cache['scores']),('relations',new_scores)):
        known=[v for v in scores.values() if v['available']]
        arms[arm]={'planned':12,'available':len(known),'correct':sum(v['answer_em'] for v in known),'unavailable':12-len(known),
                   **{field+'_sum_available':sum(v[field] for v in known) for field in ('answer_f1','support_em','support_f1')},
                   'scores':scores,'primary_accuracy':sum(v['answer_em'] for v in known)/12 if len(known)==12 and (arm=='direct' or runtime_qualified) else None}
    questions={p.stem:study.read(p) for p in (output/'questions').glob('*.json')}
    complete=runtime_qualified and len(calls)==24 and len(questions)==12 and arms['relations']['available']==12
    return {'schema':'musique-source-quoted-relations-result-v1','complete':complete,'runtime_qualified':runtime_qualified,
            'planned_new_physical_calls':24,'planned_new_final_slots':12,'comparison_terminal_slots':24,'unique_questions':12,
            'arms':arms,'paired_direct_to_relations':paired(arms['direct']['scores'],arms['relations']['scores']),
            'new_physical_cost':costs(list(calls.values()),24),'cached_direct_final_cost':costs(cache['direct_calls'],12),
            'cached_acquisition_cost':costs(cache['acquisition_calls'],36),
            'natural_full_policy_cost':{'direct':costs(cache['acquisition_calls']+cache['direct_calls'],48),
                                        'relations':costs(cache['acquisition_calls']+list(calls.values()),60)},
            'extract_model_errors':sum(v['report']['model_error'] for v in questions.values()),
            'reports_with_verified_quote_substrings':sum(v['report']['quote_substrings_verified'] for v in questions.values()),
            'relation_truth_verified':False,'status_counts':dict(Counter(v.get('status') for v in calls.values())),
            'missing_receipt_ids':sorted(expected-set(calls)),
            'cost_boundary':'24 newly spent calls. Conditional finalization1 vs2; full natural policies4 vs5 (48 vs60), with cached acquisition charged but not rerun. Token cost not matched.',
            'claim_boundary':'All12 exposed fixed-source cases. Extra sequential extraction plus relation representation, not proof of truth/faithfulness, learned routing, recursion or novelty.'}
