"""Thin one-shot independent raw audit; reuse qualified native decoder/scorer, no inference."""
import importlib.util
import json
import os
from pathlib import Path
import time

ROOT=Path(__file__).resolve().parent;STORE=ROOT.parents[1]
SIDE=STORE/'sidecars/musique-direct-answer-contract-v1';OUT=SIDE/'outputs/attempt-001'
PRIOR=ROOT.parent/'musique-source-quoted-relations-independent-2026-09-12'
READY_SHA='a5e12d1f80f5b72ecaf169b250f1dcb97a5a57effd8866759c36c635b7b79b6e'


def load(name,path):
    spec=importlib.util.spec_from_file_location(name,path);v=importlib.util.module_from_spec(spec);spec.loader.exec_module(v);return v


m=load('answer_contract_native_core',PRIOR/'analyze.py');a=m.a;s=load('answer_contract_audit_study',SIDE/'study.py');m.s=s


def main():
    assert os.environ.get('CUDA_VISIBLE_DEVICES')=='' and not (ROOT/'REPORT.json').exists()
    terminal_present=(OUT/'OWNER_TERMINAL.json').exists()
    a.write_x(ROOT/'PENDING_CHECK.json',{'owner_terminal_present':terminal_present,'checked_epoch':time.time(),'check_count':1,'no_polling':True})
    if not terminal_present:print('PENDING');return
    assert a.sha(s.READY)==READY_SHA
    terminal=a.read(OUT/'OWNER_TERMINAL.json');owner=a.read(OUT/'RESULT.json');assert terminal['complete'] and terminal['released'] and terminal['runtime_qualified']
    assert terminal['result_sha256']==a.sha(OUT/'RESULT.json') and a.read(OUT/'OWNER_RUN.json')['ready_sha256']==READY_SHA
    assert a.read(OUT/'BINDING.json')==a.read(m.BASE/'BINDING.json')
    quoted_path=PRIOR/'outcome/REPORT.json';assert a.sha(quoted_path)=='e3b3f36902d8a7df48efd4498ead145a6137f9a1560974f1478436d915a4cdd1'
    quoted=a.read(quoted_path);cache=a.read(s.INPUTS/'host/BASELINE.json');expected=a.read(s.INPUTS/'EXPECTED_REQUESTS.json')
    from transformers import AutoTokenizer
    tok=AutoTokenizer.from_pretrained(s.MODEL,local_files_only=True)
    calls,issues=m.audit_calls(OUT,s.schedule(),tok,True)
    baseline,prior_issues=m.audit_calls(m.BASE,[v for v in s.original.original.schedule() if v['role']=='flexible'],tok,False);issues.extend(prior_issues)
    controls={v['record_id']:v for v in baseline};new={v['record_id']:v for v in calls}
    gold=a.read(s.SERVICE_ROOT/'inputs/host/HOST_GOLD.json');questions=[];mismatches=[]
    for item in s.selected():
        ident=item['record_id'];before=controls[ident];after=new[ident];frozen=a.read(item['source_payload_path'])
        assert a.sha(item['source_payload_path'])==item['source_payload_sha256']
        instruction_only=after['prompt']==[before['prompt'][0],{'role':'user','content':before['prompt'][1]['content']+' '+s.ANSWER_RULE}]
        payload_exact=m.payload(after['prompt'])[0]==m.payload(before['prompt'])[0]==frozen
        body=a.read(OUT/'native'/(after['call_id']+'-REQUEST.json'))
        if not instruction_only or not payload_exact or body!=expected[ident]:issues.append(ident+':declared_instruction_only_delta')
        outcomes={}
        for arm,c in (('direct',before),('concise',after)):
            score=a.score_text(c['decoded_text'],gold[ident],item['paragraph_count']) if c['authenticated'] else None
            outcomes[arm]={'outcome':'C' if score and score['answer_em'] else 'W' if score else 'U','score':score,
                           'decoded_final':c['decoded_text'],'completion_ids_sha256':c.get('completion_ids_sha256')}
            saved=owner['arms'][arm]['scores'][ident]
            for k in ('answer_em','answer_f1','support_em','support_f1'):
                if saved[k]!=(score[k] if score else None):mismatches.append([ident,arm,k])
        q=next(v for v in quoted['questions'] if v['record_id']==ident)
        questions.append({'record_id':ident,'question':frozen['original_question'],'selected_ids':frozen['selected_ids'],
                          'source_payload_path':item['source_payload_path'],'source_payload_sha256':item['source_payload_sha256'],
                          'instruction_only_prompt_delta_exact':instruction_only,'frozen_payload_exact':payload_exact,
                          'paired_final_seed_equal':before['native_seed']==after['native_seed']==item['cached_final_seed'],
                          'outcomes':outcomes,'quoted_arm_outcome':q['outcomes']['relations'],
                          'gold_HOST_ONLY':gold[ident]['answer'],'gold_support_HOST_ONLY':gold[ident]['support_idxs'],
                          'raw_source_paragraphs':frozen['evidence'],'calls':{'direct':before['paths'],'concise':after['paths']}})
    arms={}
    for arm in ('direct','concise'):
        values=[q['outcomes'][arm] for q in questions if q['outcomes'][arm]['outcome']!='U']
        arms[arm]={'planned':12,'available':len(values),'correct':sum(v['outcome']=='C' for v in values),
                   **{k+'_sum_available':sum(v['score'][k] for v in values) for k in ('answer_f1','support_em','support_f1')}}
    acquisition=quoted['cached_acquisition_calls']
    paths=[Path(__file__),PRIOR/'analyze.py',quoted_path,m.PRIOR,s.READY,s.INPUTS/'EXPECTED_REQUESTS.json',s.INPUTS/'MANIFEST.json',
           s.INPUTS/'host/BASELINE.json',s.INPUTS/'INPUT_QUALIFICATION.json',s.SERVICE_ROOT/'inputs/host/HOST_GOLD.json',*SIDE.glob('*.py')]
    paths+=list(OUT.glob('*.json'))+[p for folder in ('calls','starts','native','prompts','questions') for p in (OUT/folder).glob('*.json')]
    paths+=[Path(p) for c in baseline for p in c['paths'].values()]+[Path(v['source_payload_path']) for v in s.selected()]
    report={'schema':'musique-direct-answer-contract-independent-v1','arms':arms,'questions':questions,
            'new_authenticated_calls':sum(v['authenticated'] for v in calls),'new_exact_prefixes':sum(v['exact_prefix'] for v in calls),
            'baseline_authenticated_calls':sum(v['authenticated'] for v in baseline),'integrity_issues':issues,'owner_score_mismatches':mismatches,
            'paired_direct_to_concise':a.paired({q['record_id']:q['outcomes']['direct'] for q in questions},{q['record_id']:q['outcomes']['concise'] for q in questions}),
            'new_physical_cost':a.call_cost(calls),'cached_acquisition_cost':a.call_cost(acquisition),
            'natural_full_policy_cost':{'direct':a.call_cost(acquisition+baseline),'concise':a.call_cost(acquisition+calls)},
            'quoted_natural_policy_cost_context_only':quoted['natural_full_policy_cost']['relations'],
            'new_calls':calls,'baseline_calls':baseline,'owner_terminal':terminal,'source_sha256':{str(p):a.sha(p) for p in paths},
            'limits':'All12 exposed paired units. One universal instruction change, exact raw4 and old final seed/model/schema.12 new calls, natural4 vs4, not token matched. Prior quoted arm contextual comparison, no score rewrite or claim of novel information/composition.',
            'GPU_calls':0,'generated_code_executed':False}
    a.write_x(ROOT/'REPORT.json',report)
    print(json.dumps({'sha256':a.sha(ROOT/'REPORT.json'),'arms':arms,'pairs':report['paired_direct_to_concise'],'issues':issues,'score_mismatches':mismatches}))


if __name__=='__main__':main()
