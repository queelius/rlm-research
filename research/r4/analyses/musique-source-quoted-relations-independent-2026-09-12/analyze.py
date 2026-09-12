"""CPU-only native-input, quoted-report and raw-score audit; no generated-code execution."""
import argparse
import importlib.util
import json
import os
from pathlib import Path

ROOT=Path(__file__).resolve().parent
SIDE=ROOT.parents[1]/'sidecars/musique-source-quoted-relations-v1'
PRIOR=ROOT.parent/'musique-task-directed-followup-independent-2026-09-12/analyze.py'
READY_SHA='bcab05d001aa15845d72cee2f705c01cafcc5e1ba457e72b1884ad10244d1663'


def load(name,path):
    spec=importlib.util.spec_from_file_location(name,path)
    value=importlib.util.module_from_spec(spec);spec.loader.exec_module(value);return value


s=load('quoted_relations_audit_study',SIDE/'study.py')
assert s.sha(PRIOR)=='5b1072b8c5635cbbae0e0fed9b5ac2d749ecdc49292585278209ef25a6d5bce7'
a=load('quoted_relations_independent_native_score',PRIOR)
BASE=s.FLEX/'outputs/attempt-001'
ROLES=('extract','relations')


def parse_report(call,paragraphs):
    value={'valid':False,'model_error':False,'quote_substrings_verified':False,'relation_truth_verified':False,
           'data':{'relations':[],'missing_links':[]},'error':'extract_transport_unavailable'}
    if not call['authenticated']:return value
    try:
        data=json.loads(call['decoded_text'],object_pairs_hook=a.strict_object)
        assert isinstance(data,dict) and set(data)=={'relations','missing_links'}
        assert isinstance(data['relations'],list) and len(data['relations'])<=4
        assert isinstance(data['missing_links'],list) and len(data['missing_links'])<=4
        assert all(isinstance(v,str) and v.strip() for v in data['missing_links'])
        originals={p['idx']:p['paragraph_text'] for p in paragraphs}
        for row in data['relations']:
            assert isinstance(row,dict) and set(row)=={'subject','relation','object','paragraph_id','quote'}
            assert all(isinstance(row[k],str) and row[k].strip() for k in ('subject','relation','object','quote'))
            assert type(row['paragraph_id']) is int and row['paragraph_id'] in originals
            assert row['quote'] in originals[row['paragraph_id']]
        value.update(valid=True,quote_substrings_verified=True,data=data,error=None)
    except (ValueError,TypeError,AssertionError,KeyError):
        value.update(model_error=True,error='invalid_report_schema_or_quote')
    return value


def payload(prompt):
    raw,instruction=prompt[1]['content'].rsplit('\n\n',1)
    return json.loads(raw,object_pairs_hook=a.strict_object),instruction


def prompt_check(call,expected,instruction):
    if not call.get('prompt'):return None,None
    try:
        value,actual_instruction=payload(call['prompt']);prompt=call['prompt']
        return value==expected,(len(prompt)==2 and prompt[1]['role']=='user'
                and prompt[0]=={'role':'system','content':s.SYSTEM} and actual_instruction==instruction)
    except (ValueError,TypeError,KeyError,IndexError):return False,False


def inspect_question(item,calls,baseline,attempt):
    ident=item['record_id'];frozen=a.read(item['source_payload_path'])
    assert a.sha(item['source_payload_path'])==item['source_payload_sha256']
    assert len(frozen['evidence'])==4 and frozen['selected_ids']==sorted(p['idx'] for p in frozen['evidence'])
    gold=a.read(s.SERVICE_ROOT/'inputs/host/HOST_GOLD.json')[ident]
    value=parse_report(calls['extract'],frozen['evidence']);issues=[]
    augmented={**frozen,'relation_report':{**value['data'],'error':value['error'],
               'quote_substrings_verified':value['quote_substrings_verified'],'relation_truth_verified':False}}
    checks={}
    for label,call,expected,instruction in (
        ('extract',calls['extract'],{'original_question':frozen['original_question'],'paragraphs':frozen['evidence']},s.EXTRACT),
        ('final',calls['relations'],augmented,s.FINAL),('baseline',baseline,frozen,s.FINAL)):
        checks[label]=prompt_check(call,expected,instruction)
        if checks[label][0] is False:issues.append(label+'_source_payload')
        if checks[label][1] is False:issues.append(label+'_instruction_or_roles')
    seed_equal=calls['relations'].get('native_seed')==baseline.get('native_seed')==item['cached_final_seed']
    if calls['relations']['authenticated'] and not seed_equal:issues.append('paired_final_seed')
    if baseline['call_id']!=item['cached_direct_call_id']:issues.append('cached_direct_call_id')
    receipt_path=Path(attempt)/'questions'/(ident+'.json')
    if receipt_path.exists():
        receipt=a.read(receipt_path)
        expected={'record_id':ident,'source_payload_sha256':item['source_payload_sha256'],
                  'source_ids':frozen['selected_ids'],'extract_call_id':calls['extract']['call_id'],
                  'final_call_id':calls['relations']['call_id'],'paired_final_seed':item['cached_final_seed'],
                  'report':value,'raw_sources_preserved_even_report_invalid':True,'all_planned_roles_accounted':True}
        issues.extend('receipt_'+k for k,v in expected.items() if receipt.get(k)!=v)
    outcomes={}
    for arm,call,known in (('direct',baseline,baseline['authenticated']),
                          ('relations',calls['relations'],all(v['authenticated'] for v in calls.values()))):
        score=a.score_text(call['decoded_text'],gold,item['paragraph_count']) if call['authenticated'] else None
        answer=(score or {}).get('parsed',{}).get('answer');aliases=[gold['answer'],*gold.get('answer_aliases',[])]
        outcomes[arm]={'outcome':'C' if known and score['answer_em'] else 'W' if known else 'U',
            'score':score if known else None,'observed_final_score_diagnostic_only':None if known else score,
            'decoded_final':call['decoded_text'],'response_sha256':call.get('response_sha256'),
            'normalized_gold_substring_diagnostic_not_correctness':None if answer is None else any(
                a.normalize_answer(v) and a.normalize_answer(v) in a.normalize_answer(answer) for v in aliases)}
    ids=set(frozen['selected_ids']);originals={p['idx']:p for p in gold['source_row']['paragraphs']}
    facts=[{**v,'annotated_source_selected':v['paragraph_support_idx'] in ids,
            'support_paragraph':originals[v['paragraph_support_idx']]}
           for v in gold['source_row']['question_decomposition']]
    return {'record_id':ident,'question':frozen['original_question'],'issues':issues,
            'extract_source_payload_exact':checks['extract'][0], 'final_source_payload_exact':checks['final'][0],
            'baseline_source_payload_exact':checks['baseline'][0],'final_seed_matches_baseline':seed_equal,
            'source_payload_sha256':item['source_payload_sha256'],'selected_ids':frozen['selected_ids'],
            'selected_original_paragraphs':frozen['evidence'],'parsed_report':value,
            'raw_extractor_text':calls['extract']['decoded_text'],'extract_response_sha256':calls['extract'].get('response_sha256'),
            'accepted_relation_count':len(value['data']['relations']),'outcomes':outcomes,
            'gold_answer_HOST_ONLY':gold['answer'],'gold_support_ids_HOST_ONLY':gold['support_idxs'],
            'all_annotated_sources_selected':set(gold['support_idxs'])<=ids,'component_fact_review_HOST_ONLY':facts,
            'mechanism_adjudication':'PENDING inert entity/relation review. Exact quote and answer-string presence do not prove faithful composition; format and entity errors remain separate.'}


def audit_calls(attempt,schedule,tokenizer,current):
    calls=[];issues=[]
    for row in schedule:
        call=a.check_call(attempt,row,tokenizer);call['exact_prefix']=False
        if call['authenticated']:
            body=a.read(Path(attempt)/'native'/(row['call_id']+'-REQUEST.json'))
            rendered=tokenizer.apply_chat_template(call['prompt'],tokenize=True,add_generation_prompt=True,enable_thinking=False)
            ids=rendered['input_ids'] if hasattr(rendered,'keys') else rendered
            call['exact_prefix']=list(ids)==body['token_ids'];call['native_seed']=body['sampling_params']['seed']
            call['prefix_ids_sha256']=a.digest(body['token_ids'])
            response=a.read(Path(attempt)/'native'/(row['call_id']+'-RESPONSE.json'))
            call['completion_ids_sha256']=a.digest(response['choices'][0]['token_ids'])
            item=next(i for i in s.selected() if i['record_id']==row['record_id'])
            module=s if current else s.original
            expected=module.request(call['prompt'],row['role'],row['seed'],item['paragraph_count'],tokenizer)
            call['native_request_matches_frozen_source']=body==expected
            if not call['exact_prefix']:issues.append(row['call_id']+':actual_prefix')
            if body!=expected:issues.append(row['call_id']+':native_request_source_contract')
        if call['violations'] and call['status']=='returned_valid':issues.append({row['call_id']:call['violations']})
        calls.append(call)
    provider=[v['provider_request_id'] for v in calls if v['authenticated']]
    if len(provider)!=len(set(provider)):issues.append('duplicate_provider_request_ids')
    return calls,issues


def inspect_attempt(attempt,tokenizer):
    attempt=Path(attempt);calls,issues=audit_calls(attempt,s.schedule(),tokenizer,True)
    old_schedule=[v for v in s.original.schedule() if v['role'] in ('select_left','select_right','plan','flexible')]
    old,old_issues=audit_calls(BASE,old_schedule,tokenizer,False);issues.extend(old_issues)
    baseline=[v for v in old if v['role']=='flexible'];acquisition=[v for v in old if v['role']!='flexible']
    lookup={(v['record_id'],v['role']):v for v in calls};controls={v['record_id']:v for v in baseline}
    questions=[inspect_question(item,{r:lookup[item['record_id'],r] for r in ROLES},controls[item['record_id']],attempt) for item in s.selected()]
    issues.extend({q['record_id']:q['issues']} for q in questions if q['issues'])
    extra_receipts={p.stem for p in (attempt/'calls').glob('*.json')}-{v['call_id'] for v in s.schedule()}
    if extra_receipts:issues.append({'unplanned_call_receipts':sorted(extra_receipts)})
    arms={}
    for arm in ('direct','relations'):
        known=[q['outcomes'][arm] for q in questions if q['outcomes'][arm]['outcome']!='U']
        arms[arm]={'planned':12,'available':len(known),'correct':sum(v['outcome']=='C' for v in known),'unavailable':12-len(known),
                   **{k+'_sum_available':sum(v['score'][k] for v in known) for k in ('answer_f1','support_em','support_f1')}}
    return {'schema':'musique-source-quoted-relations-independent-v1','questions_planned':12,'new_calls_planned':24,
            'new_authenticated_calls':sum(v['authenticated'] for v in calls),'new_exact_prefixes':sum(v['exact_prefix'] for v in calls),
            'baseline_authenticated_calls':sum(v['authenticated'] for v in baseline),'baseline_exact_prefixes':sum(v['exact_prefix'] for v in baseline),
            'cached_acquisition_authenticated_calls':sum(v['authenticated'] for v in acquisition),
            'integrity_issues':issues,'arms':arms,'new_physical_cost':a.call_cost(calls),
            'cached_direct_final_cost':a.call_cost(baseline),'cached_acquisition_cost':a.call_cost(acquisition),
            'natural_full_policy_cost':{'direct':a.call_cost(acquisition+baseline),'relations':a.call_cost(acquisition+calls)},
            'paired_direct_to_relations':a.paired({q['record_id']:q['outcomes']['direct'] for q in questions},{q['record_id']:q['outcomes']['relations'] for q in questions}),
            'extract_model_errors':sum(q['parsed_report']['model_error'] for q in questions),
            'valid_reports':sum(q['parsed_report']['valid'] for q in questions),
            'nonempty_valid_reports':sum(q['parsed_report']['valid'] and q['accepted_relation_count']>0 for q in questions),
            'relation_truth_verified':False,'questions':questions,'new_calls':calls,'baseline_calls':baseline,'cached_acquisition_calls':acquisition,
            'limits':'All12 exposed paired contexts, no case selection.24 new physical calls; cached direct12 and acquisition36 separately charged. '
                     'Conditional finalization1 vs2, full natural policies4 vs5 (48 vs60). Same four sources and paired final seeds, not equal token/call cost. '
                     'Valid quote substrings are not relation truth; source coverage and answer substrings are diagnostic only. Unknown is not wrong. No novel or learned routing claim.'}


def main():
    parser=argparse.ArgumentParser();parser.add_argument('--output',type=Path,default=ROOT/'outcome');args=parser.parse_args()
    assert os.environ.get('CUDA_VISIBLE_DEVICES')=='' and not args.output.exists()
    assert (s.ATTEMPT/'OWNER_TERMINAL.json').exists(),'terminal absent; no polling or partial headline'
    assert a.sha(s.READY)==READY_SHA
    ready=a.read(ROOT/'CPU_READY.json')
    assert ready['identity']==a.digest({k:v for k,v in ready.items() if k!='identity'})
    for path,want in ready['input_sha256'].items():assert a.sha(path)==want,path
    terminal=a.read(s.ATTEMPT/'OWNER_TERMINAL.json');original=a.read(s.ATTEMPT/'RESULT.json')
    assert terminal['result_sha256']==a.sha(s.ATTEMPT/'RESULT.json')
    assert a.read(s.ATTEMPT/'OWNER_RUN.json')['ready_sha256']==READY_SHA
    assert a.read(s.ATTEMPT/'BINDING.json')==a.read(BASE/'BINDING.json')
    assert a.digest(a.read(s.ATTEMPT/'BINDING.json'))==a.read(s.INPUTS/'MANIFEST.json')['baseline_binding_sha256_canonical']
    from transformers import AutoTokenizer
    report=inspect_attempt(s.ATTEMPT,AutoTokenizer.from_pretrained(s.MODEL,local_files_only=True))
    report['owner_terminal']=terminal;report['model_binding_exact']=True;mismatches=[]
    for q in report['questions']:
        for arm,value in q['outcomes'].items():
            saved=original['arms'][arm]['scores'][q['record_id']]
            for key in ('answer_em','answer_f1','support_em','support_f1'):
                expected=value['score'][key] if value['score'] is not None else None
                if saved[key]!=expected:mismatches.append([q['record_id'],arm,key,saved[key],expected])
    report['owner_score_mismatches']=mismatches
    paths=[p for folder in ('calls','starts','native','prompts','questions') for p in (s.ATTEMPT/folder).glob('*.json')]
    paths+=list(s.ATTEMPT.glob('*.json'))
    report['source_sha256']={**ready['input_sha256'],**{str(p):a.sha(p) for p in paths}}
    a.write_x(args.output/'REPORT.json',report);a.write_x(args.output/'MECHANISM_EVIDENCE.json',report['questions'])
    lines=['# Source-quoted relations: independent native readout','',
           f"New native returns {report['new_authenticated_calls']}/24; exact new prefixes {report['new_exact_prefixes']}; "
           f"cached controls {report['baseline_authenticated_calls']}/12. Integrity issues {len(report['integrity_issues'])}; owner-score mismatches {len(mismatches)}.",'',
           '| Arm | Exact | Available /12 | Natural full calls |','|---|---:|---:|---:|']
    for arm,v in report['arms'].items():lines.append(f"| {arm} | {v['correct']} | {v['available']} | {report['natural_full_policy_cost'][arm]['planned_boundaries']} |")
    lines+=['','Direct→relations: '+json.dumps(report['paired_direct_to_relations']),'',report['limits'],'',
            'All12 original sources, raw reports/finals and host-only component facts are retained in MECHANISM_EVIDENCE.json. '
            'Entity joining versus answer-format changes require inert case adjudication; no automatic truth certification.',
            '',f"REPORT SHA256: `{a.sha(args.output/'REPORT.json')}`. No GPU/model/generated-code execution."]
    a.write_x(args.output/'REPORT.md','\n'.join(lines))
    print(json.dumps({'path':str(args.output/'REPORT.json'),'sha256':a.sha(args.output/'REPORT.json'),'arms':report['arms'],
                      'issues':report['integrity_issues'],'owner_score_mismatches':mismatches}))


if __name__=='__main__':main()
