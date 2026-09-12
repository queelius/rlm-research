"""Authenticate cached direct controls once, freeze all12 payloads, then CPU seal."""
import argparse
import os
from pathlib import Path
import subprocess
import time
import study

FLEX_READY_SHA='6324911d00c6b893ec6371a73bba89f5c1be206582fe74cbce8520127cd87cf2'
ANALYSIS=study.ROOT.parents[1]/'analyses/musique-flexible-four-source-independent-2026-09-12/outcome/REPORT.json'
ANALYSIS_SHA='3ff7230537b4ed3f17b35d9dcbaa896ead0cf22267785fa5aae07339a3f2c2b2'


def inputs():
    receipt=study.INPUTS/'INPUT_QUALIFICATION.json'
    if receipt.exists():
        value=study.read(receipt)
        for path,want in value['pins'].items():assert study.sha(path)==want,path
        return value
    old=study.FLEX/'outputs/attempt-001';ready=study.FLEX/'CPU_READY.json'
    assert study.sha(ready)==FLEX_READY_SHA and study.sha(ANALYSIS)==ANALYSIS_SHA
    analysis=study.read(ANALYSIS);assert analysis['authenticated_calls']==analysis['exact_prefixes']==60
    assert not analysis['integrity_issues'] and not analysis['owner_score_mismatches']
    terminal=study.read(old/'OWNER_TERMINAL.json');assert terminal['complete'] and terminal['released'] and terminal['runtime_qualified']
    result=study.read(old/'RESULT.json');assert terminal['result_sha256']==study.sha(old/'RESULT.json')
    assert study.read(old/'OWNER_RUN.json')['ready_sha256']==FLEX_READY_SHA
    binding=study.read(old/'BINDING.json');assert binding==study.base_owner().study.binding()
    from transformers import AutoTokenizer
    tok=AutoTokenizer.from_pretrained(study.MODEL,local_files_only=True)
    gold=study.read(study.SERVICE_ROOT/'inputs/host/HOST_GOLD.json');source=study.original.selected()
    schedule={(r['record_id'],r['role']):r for r in study.original.schedule()};selected=[];scores={};direct=[];acquisition=[];checks=[]
    pins={str(ready):FLEX_READY_SHA,str(ANALYSIS):ANALYSIS_SHA}
    for name in ('OWNER_TERMINAL.json','OWNER_RUN.json','RESULT.json','BINDING.json','ENGINE_ATTESTATION.json','RUNTIME.json'):
        pins[str(old/name)]=study.sha(old/name)
    for index,item in enumerate(source):
        ident=item['record_id'];row=schedule[ident,'flexible'];calls={}
        for role in ('select_left','select_right','plan','flexible'):
            call_path=old/'calls'/(schedule[ident,role]['call_id']+'.json')
            assert study.sha(call_path)==analysis['source_sha256'][str(call_path)]
            calls[role]=study.read(call_path);assert calls[role]['transport_valid'];pins[str(call_path)]=study.sha(call_path)
        c=calls['flexible'];prompt=study.read(c['prompt_path']);body=study.read(c['request_path']);response=study.read(c['response_path'])
        for key in ('prompt_path','request_path','response_path'):
            path=Path(c[key]);assert study.sha(path)==analysis['source_sha256'][str(path)];pins[str(path)]=study.sha(path)
        assert len(prompt)==2 and prompt[0]=={'role':'system','content':study.SYSTEM}
        text,instruction=prompt[1]['content'].rsplit('\n\n',1);assert instruction==study.FINAL
        payload=__import__('json').loads(text);assert set(payload)=={'original_question','selected_ids','selection_error','evidence'}
        public=study.read(item['public_path']);originals={p['idx']:p for p in public['paragraphs']}
        assert payload['original_question']==public['question'] and payload['selection_error'] is None
        ids=payload['selected_ids'];assert len(ids)==len(set(ids))==4 and ids==sorted(ids)
        assert payload['evidence']==[originals[i] for i in ids]
        assert row['seed']==study.seed(index,'relations')
        rebuilt=study.request(study.messages(payload,study.FINAL),'relations',row['seed'],item['paragraph_count'],tok)
        assert rebuilt==body,'cached direct native request differs from new unaugmented final'
        decoded=study.decode(body,response,tok);assert decoded['transport_valid'] and decoded['text']==c['text']
        score=study.score_final(decoded,gold[ident],item['paragraph_count'])
        assert all(score[k]==result['arms']['flexible']['scores'][ident][k] for k in ('available','answer_em','answer_f1','support_em','support_f1','valid_json'))
        path=study.INPUTS/'public'/(ident+'.json');study.write_x(path,payload)
        selected.append({'record_id':ident,'paragraph_count':item['paragraph_count'],'source_payload_path':str(path),'source_payload_sha256':study.sha(path),
                         'cached_direct_call_id':row['call_id'],'cached_final_seed':row['seed']})
        scores[ident]=score;direct.append(c);acquisition.extend(calls[r] for r in ('select_left','select_right','plan'))
        checks.append({'record_id':ident,'same_native_unaugmented_final_body':True,'raw_decode_and_score_reproduced':True,
                       'source_payload_sha256':study.sha(path),'cached_request_sha256':study.sha(c['request_path'])})
    assert len(selected)==12
    study.write_x(study.INPUTS/'MANIFEST.json',{'selected':selected,'all12_exposed_flexible_source_sets':True,
                  'baseline_binding_sha256_canonical':study.digest(binding),'gold_or_cached_answer_in_public_payloads':False})
    study.write_x(study.INPUTS/'host/BASELINE.json',{'scores':scores,'direct_calls':direct,'acquisition_calls':acquisition,'source_owner_terminal_sha256':study.sha(old/'OWNER_TERMINAL.json')})
    pins.update({str(p):study.sha(p) for p in study.INPUTS.rglob('*.json')})
    value={'pins':pins,'checks':checks,'cached_control_qualification':'Exact unaugmented native body including tokens/schema/seed/decoding, same model binding, raw decode and all12 scores reproduced on CPU.'}
    study.write_x(receipt,value);return value


def main():
    parser=argparse.ArgumentParser();parser.add_argument('--inputs-only',action='store_true');args=parser.parse_args()
    assert os.environ.get('CUDA_VISIBLE_DEVICES')=='';qualification=inputs()
    if args.inputs_only:return
    assert not study.READY.exists() and not study.ATTEMPT.exists()
    previous=study.read(study.FLEX/'CPU_READY.json')
    for path,want in previous['closure_sha256'].items():assert study.sha(path)==want,path
    command=[str(study.NATIVE),'-m','pytest','-q','-p','no:cacheprovider','test_graph.py','--basetemp='+str(study.ROOT/'cpu-fixture-001')]
    result=subprocess.run(command,cwd=study.ROOT,capture_output=True,text=True,timeout=180)
    study.write_x(study.ROOT/'CPU_TESTS.json',{'command':command,'returncode':result.returncode,'stdout':result.stdout,'stderr':result.stderr,'GPU_or_model_queries':0,
                  'scope':'Actual owner→collector native HTTP double; invalid report preserves raw4; wrong-person valid quote does not certify truth; paired seeds and costs.'})
    assert result.returncode==0,result.stdout+result.stderr
    study.write_x(study.INPUTS/'SCHEDULE.json',study.schedule())
    paths=list(study.ROOT.glob('*.py'))+[study.ROOT/'RUNBOOK.md',study.ROOT/'CPU_TESTS.json',study.FLEX/'CPU_READY.json']
    paths+=list(study.INPUTS.rglob('*.json'))+list((study.ROOT/'cpu-fixture-001').rglob('*.json'))
    closure={**previous['closure_sha256'],**qualification['pins'],**{str(p):study.sha(p) for p in paths}}
    ready={'schema':'musique-source-quoted-relations-cpu-ready-v1','created_epoch':time.time(),'baseline_READY_sha256':FLEX_READY_SHA,
           'baseline_analysis_sha256':ANALYSIS_SHA,'schedule_sha256':study.digest(study.schedule()),'output':str(study.ATTEMPT),
           'command':[str(study.NATIVE),str(study.ROOT/'owner.py'),'run','--outer-seconds','950'],
           'all12_frozen_flexible_source_sets':True,'new_physical_calls':24,'new_finals':12,'cached_direct_finals':12,'paired_units':12,
           'graph':'Exact frozen raw4 → quoted relation extractor → same raw4 plus report → unchanged final; cached direct control.',
           'caps':{'extract_tokens':512,'final_tokens':1024,'temperature':.5,'science_seconds':700,'owner_seconds':950,'external_seconds':1050,'question_workers':4,'context_plus_output':8192},
           'seeds':'extract202609240000+16i; final unchanged202609230000+16i+3',
           'natural_conditional_calls':{'direct':1,'relations':2},'natural_full_policy_calls':{'direct':4,'relations':5},
           'token_cost_matched':False,'cached_calls_not_rerun':True,'max_relations':4,'max_missing_links':4,
           'quote_validation':'Exact nonempty substring of cited selected paragraph_text; schema/source-ID only, never relation truth.',
           'invalid_report':'Retain raw report; final always keeps same raw4 plus explicit error/no accepted relations; no retry or hidden replacement.',
           'unknown':'Required native extraction/final failure stays unavailable; known schema/quote model errors retain observed final score.',
           'gold_in_model_inputs':False,'new_GPU_or_model_queries_during_preparation':0,'optimizer_steps':0,
           'claim':'Extra sequential relation extraction at fixed sources, not isolated compute-matched representation, learned routing, recursion or novelty.',
           'closure_sha256':closure,'launch_authority':'MAIN only'}
    ready['identity']=study.digest(ready);study.write_x(study.READY,ready);assert study.verify()==ready
    print({'READY_sha256':study.sha(study.READY),'identity':ready['identity'],'closure_files':len(closure),'tests':result.stdout})


if __name__=='__main__':main()
