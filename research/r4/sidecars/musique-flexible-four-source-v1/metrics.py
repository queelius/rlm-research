"""Host-only exact/support outcomes, candidate coverage, allocation and honest costs."""
from collections import Counter
import study

with study.aliases({'study':study},study.ROOT): original=study.load('flex_original_metrics',study.SERVICE_ROOT/'metrics.py')
costs=original.costs; paired=original.paired


def policy_roles(arm): return ['select_left','select_right']+(['plan'] if arm=='flexible' else [])+[arm]


def summarize(output,runtime_qualified):
    selected=study.selected(); schedule=study.schedule(); expected={r['call_id'] for r in schedule}
    gold=study.read(study.SERVICE_ROOT/'inputs/host/HOST_GOLD.json')
    calls={p.stem:study.read(p) for p in (output/'calls').glob('*.json')}
    starts={p.stem for p in (output/'starts').glob('*.json')}; assert set(calls)<=expected and starts<=expected
    for cid in starts-set(calls): calls[cid]={**study.read(output/'starts'/(cid+'.json')),'status':'start_only_provider_unknown','transport_valid':False,'usage':{}}
    lookup={(r['record_id'],r['role']):calls.get(r['call_id'],{}) for r in schedule}
    questions={p.stem:study.read(p) for p in (output/'questions').glob('*.json')}; arms={}
    for arm in study.ARMS:
        scores={}
        for item in selected:
            ident=item['record_id']; call=lookup[ident,arm]
            score=study.score_final(call,gold[ident],item['paragraph_count'])
            if not all(lookup[ident,r].get('transport_valid',False) for r in policy_roles(arm)):
                score={'available':False,'answer_em':None,'answer_f1':None,'support_em':None,'support_f1':None,'valid_json':False,'observed_final_score_diagnostic_only':score}
            scores[ident]={**score,'native_status':call.get('status','unattempted')}
        known=[v for v in scores.values() if v['available']]
        arms[arm]={'planned':12,'available':len(known),'correct':sum(v['answer_em'] for v in known),'unavailable':12-len(known),
                   **{field+'_sum_available':sum(v[field] for v in known) for field in ('answer_f1','support_em','support_f1')},
                   'malformed_final_json':sum(not v['valid_json'] for v in known),
                   'primary_accuracy':sum(v['answer_em'] for v in known)/12 if runtime_qualified and len(known)==12 else None,
                   'scores':scores,'natural_policy_cost':costs([lookup[i['record_id'],r] for i in selected for r in policy_roles(arm)],12*len(policy_roles(arm)))}
    coverage={}
    for ident,q in questions.items():
        truth=set(gold[ident]['support_idxs']); pool={p['paragraph']['idx'] for p in study.candidates(q['selections'])}
        coverage[ident]={'gold_support_ids_HOST_ONLY':sorted(truth),'candidate_ids':sorted(pool),
                         'candidate_gold_recall':len(pool&truth)/len(truth),'all_gold_in_candidate_pool':truth<=pool,
                         'fixed2_per_half_gold_coverage_feasible':all(len(set(h)&truth)<=2 for h in q['partition_indices']),
                         'arms':{a:{'selected_ids':ids,'count':len(ids),'all_gold_selected':truth<=set(ids),
                                    'gold_recall':len(set(ids)&truth)/len(truth),
                                    'half_allocation':[len(set(ids)&set(h)) for h in q['partition_indices']]}
                                 for a,ids in q['branch_selected_ids'].items()},
                         'diagnostic_not_faithfulness':True}
    complete=runtime_qualified and len(calls)==60 and len(questions)==12 and all(a['available']==12 for a in arms.values())
    return {'schema':'musique-flexible-four-source-result-v1','complete':complete,'runtime_qualified':runtime_qualified,
            'planned_physical_calls':60,'planned_terminal_slots':24,'unique_questions':12,'arms':arms,
            'paired_fixed_to_flexible':paired(arms['fixed']['scores'],arms['flexible']['scores']),
            'physical_cost':costs(list(calls.values()),60),'host_gold_coverage':coverage,
            'selector_model_errors':sum(v['model_error'] for q in questions.values() for v in q['selections']),
            'planner_model_errors':sum(q['planner']['model_error'] for q in questions.values()),
            'status_counts':dict(Counter(v.get('status') for v in calls.values())),
            'missing_receipt_ids':sorted(expected-set(calls)),
            'raw_requests':len(list((output/'native').glob('*-REQUEST.json'))),'raw_responses':len(list((output/'native').glob('*-RESPONSE.json'))),
            'max_actual_prefix_plus_output':max((v.get('actual_prefix_plus_output',0) for v in calls.values()),default=0),
            'cost_boundary':'Physical60 shared calls. Natural fixed36/flexible48 (3 vs4/question). Four final paragraphs on valid rows; token lengths and natural call cost are not matched.',
            'claim_boundary':'All12 exposed contexts; fixed fresh2+2 versus model-selected flexible4, not gold allocation, learned routing, recursion or a novelty/confirmatory claim.'}
