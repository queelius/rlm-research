"""Reuse authenticated fixed inputs; qualify only the declared instruction delta and seal."""
import argparse
import os
from pathlib import Path
import subprocess
import time
import study

PREVIOUS_SHA='bcab05d001aa15845d72cee2f705c01cafcc5e1ba457e72b1884ad10244d1663'


def inputs():
    receipt=study.INPUTS/'INPUT_QUALIFICATION.json'
    if receipt.exists():
        value=study.read(receipt)
        for path,want in value['pins'].items():assert study.sha(path)==want,path
        return value
    assert study.sha(study.PREVIOUS/'CPU_READY.json')==PREVIOUS_SHA
    qualified=study.read(study.PREVIOUS/'inputs/INPUT_QUALIFICATION.json')
    for path,want in qualified['pins'].items():assert study.sha(path)==want,path
    manifest=study.read(study.PREVIOUS/'inputs/MANIFEST.json');cache=study.read(study.PREVIOUS/'inputs/host/BASELINE.json')
    assert len(manifest['selected'])==len(cache['scores'])==len(cache['direct_calls'])==12 and len(cache['acquisition_calls'])==36
    binding=study.read(study.FLEX/'outputs/attempt-001/BINDING.json');assert binding==study.base_owner().study.binding()
    assert study.digest(binding)==manifest['baseline_binding_sha256_canonical']
    from transformers import AutoTokenizer
    tok=AutoTokenizer.from_pretrained(study.MODEL,local_files_only=True)
    old={c['record_id']:c for c in cache['direct_calls']};checks=[];expected={}
    gold=study.read(study.SERVICE_ROOT/'inputs/host/HOST_GOLD.json')
    for index,item in enumerate(manifest['selected']):
        ident=item['record_id'];payload=study.read(item['source_payload_path']);assert study.sha(item['source_payload_path'])==item['source_payload_sha256']
        assert set(payload)=={'original_question','selected_ids','selection_error','evidence'} and len(payload['evidence'])==4
        call=old[ident];prompt=study.read(call['prompt_path']);body=study.read(call['request_path']);response=study.read(call['response_path'])
        assert prompt==study.baseline_messages(payload) and item['cached_final_seed']==study.seed(index,'concise')
        rebuilt=study.original.request(prompt,'relations',item['cached_final_seed'],item['paragraph_count'],tok);assert rebuilt==body
        decoded=study.decode(body,response,tok);assert decoded['transport_valid'] and decoded['text']==call['text']
        assert study.score_final(decoded,gold[ident],item['paragraph_count'])==cache['scores'][ident]
        new=study.request(study.final_messages(payload),'concise',item['cached_final_seed'],item['paragraph_count'],tok)
        assert {k:v for k,v in new.items() if k!='token_ids'}=={k:v for k,v in body.items() if k!='token_ids'}
        assert new['token_ids']!=body['token_ids'];expected[ident]=new
        checks.append({'record_id':ident,'source_payload_sha256':item['source_payload_sha256'],'same_base_and_seed_schema_sampling':True,
                       'only_final_instruction_added':True,'old_prefix_sha256_canonical':study.digest(body['token_ids']),
                       'new_prefix_sha256_canonical':study.digest(new['token_ids']),'expected_new_body_sha256_canonical':study.digest(new),
                       'cached_raw_decode_and_score_reproduced':True})
    study.write_x(study.INPUTS/'MANIFEST.json',manifest);study.write_x(study.INPUTS/'host/BASELINE.json',cache)
    study.write_x(study.INPUTS/'EXPECTED_REQUESTS.json',expected)
    pins={**qualified['pins'],str(study.PREVIOUS/'CPU_READY.json'):PREVIOUS_SHA,
          str(study.PREVIOUS/'inputs/INPUT_QUALIFICATION.json'):study.sha(study.PREVIOUS/'inputs/INPUT_QUALIFICATION.json')}
    pins.update({str(p):study.sha(p) for p in study.INPUTS.rglob('*.json')})
    value={'pins':pins,'checks':checks,'baseline_exact':True,'new_condition':'Only append one universal final-answer instruction; all native body fields except intentionally changed prompt token_ids equal cached direct.'}
    study.write_x(receipt,value);return value


def main():
    parser=argparse.ArgumentParser();parser.add_argument('--inputs-only',action='store_true');args=parser.parse_args()
    assert os.environ.get('CUDA_VISIBLE_DEVICES')=='';qualification=inputs()
    if args.inputs_only:return
    assert not study.READY.exists() and not study.ATTEMPT.exists()
    previous=study.read(study.PREVIOUS/'CPU_READY.json')
    for path,want in previous['closure_sha256'].items():assert study.sha(path)==want,path
    command=[str(study.NATIVE),'-m','pytest','-q','-p','no:cacheprovider','test_graph.py','--basetemp='+str(study.ROOT/'cpu-fixture-002')]
    result=subprocess.run(command,cwd=study.ROOT,capture_output=True,text=True,timeout=180)
    study.write_x(study.ROOT/'CPU_TESTS_V2.json',{'command':command,'returncode':result.returncode,'stdout':result.stdout,'stderr':result.stderr,'GPU_or_model_queries':0,
                  'scope':'All12 native request deltas; actual current owner→collector one-call HTTP fixtures; unchanged raw4, native decoding, wrong checkpoint rejection, known malformed schema vs unknown HTTP.'})
    assert result.returncode==0,result.stdout+result.stderr
    study.write_x(study.INPUTS/'SCHEDULE.json',study.schedule())
    paths=list(study.ROOT.glob('*.py'))+[study.ROOT/'RUNBOOK.md',study.ROOT/'CPU_TESTS_V2.json',study.PREVIOUS/'CPU_READY.json']
    paths+=list(study.INPUTS.rglob('*.json'))+list((study.ROOT/'cpu-fixture-002').rglob('*.json'))
    closure={**previous['closure_sha256'],**qualification['pins'],**{str(p):study.sha(p) for p in paths}}
    ready={'schema':'musique-direct-answer-contract-cpu-ready-v1','created_epoch':time.time(),'previous_READY_sha256':PREVIOUS_SHA,
           'schedule_sha256':study.digest(study.schedule()),'output':str(study.ATTEMPT),
           'command':[str(study.NATIVE),str(study.ROOT/'owner.py'),'run','--outer-seconds','950'],
           'all12_frozen_flexible_source_sets':True,'new_physical_calls':12,'new_finals':12,'cached_direct_finals':12,'paired_units':12,
           'graph':'Same frozen raw4 → direct final with universal answer-phrase instruction; cached original direct control.',
           'instruction':study.CONCISE_FINAL,'instruction_sha256_canonical':study.digest(study.CONCISE_FINAL),
           'caps':{'final_tokens':1024,'temperature':.5,'science_seconds':700,'owner_seconds':950,'external_seconds':1050,'question_workers':4,'context_plus_output':8192},
           'seeds':'unchanged202609230003+16i','model':str(study.MODEL),'model_alias':study.MODEL_ALIAS,'no_research_adapter':True,
           'natural_conditional_calls':{'direct':1,'concise':1},'natural_full_policy_calls':{'direct':4,'concise':4},
           'token_cost_matched':False,'cached_calls_not_rerun':True,'unknown':'Native failure unavailable; known malformed final JSON remains available with zero official score. No retry/fallback.',
           'gold_in_model_inputs':False,'new_GPU_or_model_queries_during_preparation':0,'optimizer_steps':0,
           'claim':'Adaptively proposed universal final-wording intervention on exposed12, not new evidence or demonstrated composition; no case-specific prompt or score rewriting.',
           'closure_sha256':closure,'launch_authority':'MAIN only'}
    ready['identity']=study.digest(ready);study.write_x(study.READY,ready);assert study.verify()==ready
    print({'READY_sha256':study.sha(study.READY),'identity':ready['identity'],'closure_files':len(closure),'tests':result.stdout})


if __name__=='__main__':main()
