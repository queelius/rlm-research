"""Host-only scoring and selected-gold coverage; never imported by the collector."""
import collections
import study

with study.aliases({'study':study},study.ROOT):
    original=study.load('evidence_original_metrics',study.SERVICE_ROOT/'metrics.py')
costs=original.costs
paired=original.paired


def policy_roles(arm):
    return ['select_left','select_right']+(['summary_left','summary_right'] if arm=='summary' else [])+[arm]


def summarize(output,runtime_qualified):
    selected=study.selected();schedule=study.schedule();expected={r['call_id'] for r in schedule}
    # This is the only experiment code that reads answer/support annotations.
    gold=study.read(study.SERVICE_ROOT/'inputs/host/HOST_GOLD.json')
    calls={p.stem:study.read(p) for p in (output/'calls').glob('*.json')}
    starts={p.stem for p in (output/'starts').glob('*.json')}
    assert set(calls)<=expected and starts<=expected
    for cid in starts-set(calls):calls[cid]={**study.read(output/'starts'/(cid+'.json')),'status':'start_only_provider_unknown','transport_valid':False,'usage':{}}
    by_key={(r['record_id'],r['role']):calls.get(r['call_id'],{}) for r in schedule}
    questions={p.stem:study.read(p) for p in (output/'questions').glob('*.json')}
    arms={}
    for arm in study.ARMS:
        scores={}
        for item in selected:
            ident=item['record_id'];value=by_key[ident,arm]
            score=study.score_final(value,gold[ident],item['paragraph_count'])
            dependencies=all(by_key[ident,role].get('transport_valid',False) for role in policy_roles(arm))
            if not dependencies:
                score={'available':False,'answer_em':None,'answer_f1':None,'support_em':None,'support_f1':None,'valid_json':False,
                       'observed_final_score_diagnostic_only':score}
            scores[ident]={**score,'native_status':value.get('status','unattempted'),
                           'helper_model_errors':[s['error'] for s in questions.get(ident,{}).get('selections',[]) if s['model_error']]}
        known=[r for r in scores.values() if r['available']]
        arms[arm]={'planned':12,'available':len(known),'correct':sum(r['answer_em'] for r in known),
                   'unavailable':12-len(known),'answer_f1_sum_available':sum(r['answer_f1'] for r in known),
                   'support_em_sum_available':sum(r['support_em'] for r in known),
                   'support_f1_sum_available':sum(r['support_f1'] for r in known),
                   'malformed_final_json':sum(not r['valid_json'] for r in known),
                   'primary_accuracy':sum(r['answer_em'] for r in known)/12 if runtime_qualified and len(known)==12 else None,
                   'scores':scores,'natural_policy_cost':costs([by_key[item['record_id'],role] for item in selected for role in policy_roles(arm)],12*len(policy_roles(arm)))}
    coverage={}
    for ident,question in questions.items():
        actual={i for s in question['selections'] for i in s['paragraph_ids']}
        presented=actual if all(s['valid'] for s in question['selections']) else set()
        truth=set(gold[ident]['support_idxs'])
        coverage[ident]={'selected_ids':sorted(actual),'presented_ids':sorted(presented),
                         'gold_support_ids_HOST_ONLY':sorted(truth),'selected_gold_support_recall':len(actual&truth)/len(truth),
                         'all_gold_support_selected':truth<=actual,'all_gold_support_presented':truth<=presented,
                         'diagnostic_not_proof_of_faithful_answer_use':True}
    complete=runtime_qualified and len(calls)==72 and len(questions)==12 and all(a['available']==12 for a in arms.values())
    return {'schema':'musique-evidence-preservation-result-v1','runtime_qualified':runtime_qualified,'complete':complete,
            'planned_physical_calls':72,'planned_terminal_slots':24,'unique_questions':12,
            'arms':arms,'paired':paired(arms['summary']['scores'],arms['verbatim']['scores']),
            'physical_cost':costs(list(calls.values()),72),'host_selected_gold_coverage':coverage,
            'selector_model_error_count':sum(s['model_error'] for q in questions.values() for s in q['selections']),
            'status_counts':dict(collections.Counter(c.get('status') for c in calls.values())),
            'missing_receipt_ids':sorted(expected-set(calls)),
            'raw_requests':len(list((output/'native').glob('*-REQUEST.json'))),'raw_responses':len(list((output/'native').glob('*-RESPONSE.json'))),
            'max_actual_prefix_plus_output':max((c.get('actual_prefix_plus_output',0) for c in calls.values()),default=0),
            'cost_boundary':'Physical72 shared calls. Natural deployment: verbatim3/question, summary5/question;36 versus60 calls. Not token-cost matched or equal-natural-call-cost.',
            'claim_boundary':'Exposed12-context evidence-representation screen; not learned routing, recursion, an invention claim, or confirmatory transfer.'}

