"""Independent native-input, allocation and raw-score audit; no model calls."""
import argparse
from collections import Counter
import importlib.util
import json
import os
from pathlib import Path

ROOT=Path(__file__).resolve().parent
SIDE=ROOT.parents[1]/'sidecars/musique-flexible-four-source-v1'
PRIOR=ROOT.parent/'musique-task-directed-followup-independent-2026-09-12/analyze.py'
READY_SHA='6324911d00c6b893ec6371a73bba89f5c1be206582fe74cbce8520127cd87cf2'


def load(name,path):
    spec=importlib.util.spec_from_file_location(name,path)
    value=importlib.util.module_from_spec(spec);spec.loader.exec_module(value);return value


s=load('flexible_audit_study',SIDE/'study.py')
assert s.sha(PRIOR)=='5b1072b8c5635cbbae0e0fed9b5ac2d749ecdc49292585278209ef25a6d5bce7'
a=load('flexible_independent_native_score',PRIOR)
ROLES=('select_left','select_right','plan','fixed','flexible')
POLICY={'fixed':('select_left','select_right','fixed'),'flexible':('select_left','select_right','plan','flexible')}


def parse_selection(call,paragraphs):
    value={'valid':False,'model_error':False,'ids':[],'error':'selection_transport_unavailable'}
    if not call['authenticated']:return value
    try:
        parsed=json.loads(call['decoded_text'],object_pairs_hook=a.strict_object)
        assert isinstance(parsed,dict) and set(parsed)=={'paragraph_ids'}
        ids=parsed['paragraph_ids'];allowed={p['idx'] for p in paragraphs}
        assert isinstance(ids,list) and len(ids)==4 and all(type(i) is int for i in ids)
        assert len(set(ids))==4 and set(ids)<=allowed
        value.update(valid=True,ids=ids,error=None)
    except (ValueError,TypeError,AssertionError,KeyError):value.update(model_error=True,error='invalid_selection_schema_or_ids')
    return value


def inspect_question(item,calls,attempt):
    ident=item['record_id'];public=a.read(item['public_path']);assert a.sha(item['public_path'])==item['public_sha256']
    gold=a.read(s.SERVICE_ROOT/'inputs/host/HOST_GOLD.json')[ident]
    originals={p['idx']:p for p in public['paragraphs']};halves=[[originals[i] for i in h] for h in item['partition_indices']]
    selected=[parse_selection(calls[r],h) for r,h in zip(ROLES[:2],halves)]
    shared_error=[{'stage':r,'error':v['error']} for r,v in zip(ROLES[:2],selected) if not v['valid']]
    candidates=[] if shared_error else [{'half':side,'rank':rank+1,'paragraph':originals[i]}
                 for side,v in zip(('left','right'),selected) for rank,i in enumerate(v['ids'])]
    planner=parse_selection(calls['plan'],[v['paragraph'] for v in candidates])
    if shared_error:planner.update(valid=False,model_error=False,ids=[],error='shared_selector_invalid')
    expected={r:{'original_question':public['question'],'paragraphs':h} for r,h in zip(ROLES[:2],halves)}
    expected['plan']={'original_question':public['question'],'candidates':candidates,'selection_error':shared_error or None}
    ids={};outcomes={};issues=[]
    for arm in POLICY:
        error=shared_error or ([{'stage':'plan','error':planner['error']}] if arm=='flexible' and not planner['valid'] else [])
        ids[arm]=[] if error else sorted(selected[0]['ids'][:2]+selected[1]['ids'][:2] if arm=='fixed' else planner['ids'])
        expected[arm]={'original_question':public['question'],'selected_ids':ids[arm],'selection_error':error or None,
                       'evidence':[originals[i] for i in ids[arm]]}
        known=all(calls[r]['authenticated'] for r in POLICY[arm])
        score=a.score_text(calls[arm]['decoded_text'],gold,item['paragraph_count']) if calls[arm]['authenticated'] else None
        outcomes[arm]={'outcome':'C' if known and score['answer_em'] else 'W' if known else 'U',
                       'score':score if known else None,'observed_final_score_diagnostic_only':None if known else score,
                       'decoded_final':calls[arm]['decoded_text'],'response_sha256':calls[arm].get('response_sha256')}
    checked=0
    for role,call in calls.items():
        prompt=call.get('prompt')
        if not prompt:continue
        checked+=1
        try:
            content,instruction=prompt[1]['content'].rsplit('\n\n',1)
            if json.loads(content,object_pairs_hook=a.strict_object)!=expected[role]:issues.append(role+'_payload')
            want=s.SELECT if role in ROLES[:2] else s.PLAN if role=='plan' else s.FINAL
            if len(prompt)!=2 or prompt[1]['role']!='user' or prompt[0]!={'role':'system','content':s.SYSTEM} or instruction!=want:
                issues.append(role+'_instruction_or_roles')
        except (ValueError,TypeError,KeyError,IndexError):issues.append(role+'_prompt_schema')
    receipt_path=attempt/'questions'/(ident+'.json')
    if receipt_path.exists():
        receipt=a.read(receipt_path)
        comparisons={'calls':{r:calls[r]['call_id'] for r in ROLES},'branch_selected_ids':ids,
                     'candidate_pool_sha256':a.digest(candidates),'branch_payload_sha256':{arm:a.digest(expected[arm]) for arm in POLICY},
                     'shared_selector_call_ids':[calls[r]['call_id'] for r in ROLES[:2]],
                     'shared_selector_return_sha256':a.digest({r:a.read(attempt/'calls'/(calls[r]['call_id']+'.json')) for r in ROLES[:2]})}
        issues.extend('receipt_'+key for key,want in comparisons.items() if receipt.get(key)!=want)
    truth=set(gold['support_idxs']);pool={v['paragraph']['idx'] for v in candidates}
    seeds=[calls[arm].get('native_seed') for arm in POLICY]
    facts=[{**v,'support_paragraph':originals[v['paragraph_support_idx']],
            'annotated_source_in_candidate_pool':v['paragraph_support_idx'] in pool,
            'annotated_source_selected':{arm:v['paragraph_support_idx'] in values for arm,values in ids.items()}}
           for v in gold['source_row']['question_decomposition']]
    return {'record_id':ident,'question':public['question'],'hop':item['hop_count'],'issues':issues,
            'evidence_bindings_exact':not issues and checked==5,'paired_final_seed_equal':seeds[0]==seeds[1] and seeds[0] is not None,
            'ranked_selectors':selected,'planner':planner,'candidate_ids':sorted(pool),'candidate_original_paragraphs':candidates,
            'selected_ids':ids,'selected_original_paragraphs':{arm:expected[arm]['evidence'] for arm in POLICY},
            'half_allocation':{arm:[len(set(values)&set(h)) for h in item['partition_indices']] for arm,values in ids.items()},
            'shared_selector_model_error':any(v['model_error'] for v in selected),'planner_model_error':planner['model_error'],
            'gold_support_ids_HOST_ONLY':sorted(truth),'candidate_gold_recall':len(pool&truth)/len(truth),'all_gold_in_candidate_pool':truth<=pool,
            'selected_gold_recall':{arm:len(set(values)&truth)/len(truth) for arm,values in ids.items()},
            'all_gold_selected':{arm:truth<=set(values) for arm,values in ids.items()},
            'fixed2plus2_coverage_feasible':all(len(set(h)&truth)<=2 for h in item['partition_indices']),
            'gold_answer_HOST_ONLY':gold['answer'],'component_fact_review_HOST_ONLY':facts,'outcomes':outcomes,
            'mechanism_review':'Inspect requested relations in these exact sources and finals; coverage changes alone do not establish faithful routing or combining.'}


def inspect_attempt(attempt,tokenizer):
    attempt=Path(attempt);calls=[];issues=[]
    for row in s.schedule():
        call=a.check_call(attempt,row,tokenizer);call['exact_prefix']=False
        if call['authenticated']:
            body=a.read(attempt/'native'/(row['call_id']+'-REQUEST.json'))
            rendered=tokenizer.apply_chat_template(call['prompt'],tokenize=True,add_generation_prompt=True,enable_thinking=False)
            ids=rendered['input_ids'] if hasattr(rendered,'keys') else rendered
            call['exact_prefix']=list(ids)==body['token_ids'];call['native_seed']=body['sampling_params']['seed']
            call['prefix_ids_sha256']=a.digest(body['token_ids'])
            if not call['exact_prefix']:issues.append(row['call_id']+':actual_prefix')
        if call['violations'] and call['status']=='returned_valid':issues.append({row['call_id']:call['violations']})
        calls.append(call)
    provider=[v['provider_request_id'] for v in calls if v['authenticated']]
    if len(provider)!=len(set(provider)):issues.append('duplicate_provider_request_ids')
    lookup={(v['record_id'],v['role']):v for v in calls}
    questions=[inspect_question(item,{r:lookup[item['record_id'],r] for r in ROLES},attempt) for item in s.selected()]
    issues.extend({q['record_id']:q['issues']} for q in questions if q['issues']);arms={}
    for arm,roles in POLICY.items():
        known=[q['outcomes'][arm] for q in questions if q['outcomes'][arm]['outcome']!='U']
        arms[arm]={'planned':12,'available':len(known),'correct':sum(v['outcome']=='C' for v in known),'unavailable':12-len(known),
                   **{k+'_sum_available':sum(v['score'][k] for v in known) for k in ('answer_f1','support_em','support_f1')},
                   'natural_cost':a.call_cost([lookup[i['record_id'],r] for i in s.selected() for r in roles]),
                   'all_gold_selected':sum(q['all_gold_selected'][arm] for q in questions)}
    return {'schema':'musique-flexible-four-source-independent-v1','questions_planned':12,'finals_planned':24,
            'authenticated_calls':sum(v['authenticated'] for v in calls),'exact_prefixes':sum(v['exact_prefix'] for v in calls),
            'integrity_issues':issues,'arms':arms,'physical_cost':a.call_cost(calls),
            'paired_fixed_to_flexible':a.paired({q['record_id']:q['outcomes']['fixed'] for q in questions},{q['record_id']:q['outcomes']['flexible'] for q in questions}),
            'candidate_pool_contains_all_gold':sum(q['all_gold_in_candidate_pool'] for q in questions),
            'flexible_allocation_counts':dict(Counter(str(q['half_allocation']['flexible']) for q in questions)),
            'questions':questions,'calls':calls,
            'limits':'All12 exposed paired contexts.60 physical calls versus natural36 fixed/48 flexible; four final paragraphs only on valid rows, no token-length matching. '
                     'Coverage is host-only diagnostic, not necessary/sufficient for faithful relations; actual routing is evaluated, not novel or learned routing.'}


def main():
    parser=argparse.ArgumentParser();parser.add_argument('--output',type=Path,default=ROOT/'outcome');args=parser.parse_args()
    assert os.environ.get('CUDA_VISIBLE_DEVICES')=='' and not args.output.exists()
    assert (s.ATTEMPT/'OWNER_TERMINAL.json').exists(),'terminal absent; no polling or partial headline'
    assert a.sha(s.READY)==READY_SHA
    ready=a.read(ROOT/'CPU_READY.json')
    for path,want in ready['input_sha256'].items():assert a.sha(path)==want,path
    terminal=a.read(s.ATTEMPT/'OWNER_TERMINAL.json');original=a.read(s.ATTEMPT/'RESULT.json')
    assert terminal['result_sha256']==a.sha(s.ATTEMPT/'RESULT.json')
    assert a.read(s.ATTEMPT/'OWNER_RUN.json')['ready_sha256']==READY_SHA
    from transformers import AutoTokenizer
    report=inspect_attempt(s.ATTEMPT,AutoTokenizer.from_pretrained(s.MODEL,local_files_only=True))
    report['owner_terminal']=terminal;mismatches=[]
    for q in report['questions']:
        for arm,value in q['outcomes'].items():
            saved=original['arms'][arm]['scores'][q['record_id']]
            for key in ('answer_em','answer_f1','support_em','support_f1'):
                expected=value['score'][key] if value['score'] is not None else None
                if saved[key]!=expected:mismatches.append([q['record_id'],arm,key,saved[key],expected])
    report['owner_score_mismatches']=mismatches
    paths=[p for folder in ('calls','starts','native','prompts','questions') for p in (s.ATTEMPT/folder).glob('*.json')]
    paths += [p for p in s.ATTEMPT.glob('*.json')]
    report['source_sha256']={**ready['input_sha256'],**{str(p):a.sha(p) for p in paths}}
    a.write_x(args.output/'REPORT.json',report);a.write_x(args.output/'MECHANISM_EVIDENCE.json',report['questions'])
    lines=['# Flexible source allocation: independent raw readout','',
           f"{report['authenticated_calls']}/60 authenticated native returns; {report['exact_prefixes']} exact prefix matches; "
           f"{len(report['integrity_issues'])} integrity issues; {len(mismatches)} owner-score mismatches.",'',
           '| Arm | Exact | Available /12 | All annotated supports selected | Natural calls |','|---|---:|---:|---:|---:|']
    for arm,v in report['arms'].items():lines.append(f"| {arm} | {v['correct']} | {v['available']} | {v['all_gold_selected']} | {v['natural_cost']['planned_boundaries']} |")
    lines += ['', 'Fixed→flexible paired outcomes: '+json.dumps(report['paired_fixed_to_flexible']),
              '',f"Candidate pool contains all annotated supports for {report['candidate_pool_contains_all_gold']}/12 contexts.",
              '',report['limits'],'','All12 exact source sets, candidate rankings, planner choices, component facts and raw finals are retained in MECHANISM_EVIDENCE.json for inert relation-level review.',
              '',f"REPORT SHA256: `{a.sha(args.output/'REPORT.json')}`. No GPU/model/generated-code execution."]
    a.write_x(args.output/'REPORT.md','\n'.join(lines))
    print(json.dumps({'path':str(args.output/'REPORT.json'),'sha256':a.sha(args.output/'REPORT.json'),'arms':report['arms'],'issues':report['integrity_issues']}))


if __name__=='__main__':main()
