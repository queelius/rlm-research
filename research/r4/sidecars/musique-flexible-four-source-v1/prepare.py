"""Seal CPU-only source/input closure; no owner or GPU launch."""
import os
import subprocess
import time
import study

PRIOR_READY_SHA='d9e00faec0d54e12311e27f1952066c5677c52df309c546723dcf015ca5307f1'


def main():
    assert os.environ.get('CUDA_VISIBLE_DEVICES')==''
    assert not study.READY.exists() and not study.ATTEMPT.exists()
    prior_ready=study.PRIOR/'CPU_READY.json'; assert study.sha(prior_ready)==PRIOR_READY_SHA
    previous=study.read(prior_ready)
    for path,want in previous['closure_sha256'].items(): assert study.sha(path)==want,path
    assert study.read(study.INPUTS/'PUBLIC_MANIFEST.json')==study.read(study.PRIOR/'inputs/PUBLIC_MANIFEST.json')
    assert len(study.selected())==12 and len(study.schedule())==60
    for item in study.selected():
        public=study.read(item['public_path']); assert study.sha(item['public_path'])==item['public_sha256']
        assert set(public)=={'question','paragraphs'}
        assert all(set(p)=={'idx','title','paragraph_text'} for p in public['paragraphs'])
        halves=study.partition(public,item['record_id'])
        assert [[p['idx'] for p in half] for half in halves]==item['partition_indices']
        assert all(len(half)>=4 for half in halves)
    command=[str(study.NATIVE),'-m','pytest','-q','-p','no:cacheprovider','test_graph.py',
             '--basetemp='+str(study.ROOT/'cpu-fixture-001')]
    result=subprocess.run(command,cwd=study.ROOT,capture_output=True,text=True,timeout=180,
                          env={**os.environ,'PYTHONDONTWRITEBYTECODE':'1'})
    study.write_x(study.ROOT/'CPU_TESTS.json',{'command':command,'returncode':result.returncode,'stdout':result.stdout,'stderr':result.stderr,
                  'new_GPU_or_model_queries':0,'actual_entrypoint':'owner.implementation().collect.execute; only native urllib HTTP response is doubled',
                  'covered':['rank/order/exact4/duplicate/wrong-half/bool/schema','valid4+0 allocation','invalid shared selector affects both finals',
                             'invalid planner preserves fixed final','exact sorted original source binding','same final instruction/seed',
                             'physical5/natural3vs4','host gold unavailable during acquisition','current owner/collector/metrics modules and V3 service/engine paths']})
    assert result.returncode==0,result.stdout+result.stderr
    from transformers import AutoTokenizer
    tok=AutoTokenizer.from_pretrained(study.MODEL,local_files_only=True)
    static=[]
    for index,item in enumerate(study.selected()):
        public=study.read(item['public_path']); halves=study.partition(public,item['record_id'])
        for role,half in zip(study.roles()[:2],halves):
            body=study.request(study.selector_messages(public,half),role,study.seed(index,role),item['paragraph_count'],tok)
            static.append({'record_id':item['record_id'],'role':role,'body':body,'body_sha256':study.digest(body)})
    study.write_x(study.INPUTS/'STATIC_SELECTORS.json',static)
    study.write_x(study.INPUTS/'SCHEDULE.json',study.schedule())
    paths=list(study.ROOT.glob('*.py'))+[study.ROOT/'RUNBOOK.md',study.ROOT/'CPU_TESTS.json',prior_ready]
    paths+=list(study.INPUTS.glob('*.json'))+list((study.ROOT/'cpu-fixture-001').rglob('*.json'))
    closure={**previous['closure_sha256'],**{str(p):study.sha(p) for p in paths}}
    ready={'schema':'musique-flexible-four-source-cpu-ready-v1','created_epoch':time.time(),
           'prior_evidence_READY_sha256':PRIOR_READY_SHA,'prior_evidence_READY_identity':previous['identity'],
           'source_V3_READY_sha256':previous['source_V3_READY_sha256'],
           'schedule_sha256':study.digest(study.schedule()),'output':str(study.ATTEMPT),
           'command':[str(study.NATIVE),str(study.ROOT/'owner.py'),'run','--outer-seconds','950'],
           'questions':12,'final_slots':24,'physical_calls':60,'previously_exposed_diagnostic':True,'all_original_contexts_no_outcome_filter':True,
           'graph':['shared_ranked4_left','shared_ranked4_right','planner_choose4_from8','paired_fixed_first2_each','paired_flexible4'],
           'fresh_fixed2plus2_arm_required':True,'reuse_previous_fixed_score':False,
           'final_source_contract':'Exactly four original paragraphs sorted by original ID on valid rows; same payload schema/instruction/seed/cap, no arm label or planner text.',
           'seed':'202609230000+16*question_index+offset: selectors0/1,planner2,bothfinals3',
           'caps':{'selector_tokens':128,'planner_tokens':128,'final_tokens':1024,'temperature':.5,'science_seconds':700,
                   'owner_seconds':950,'external_seconds':1050,'question_workers':4,'native_calls':60,'context_plus_requested_output':8192},
           'natural_policy_calls_per_question':{'fixed':3,'flexible':4},'natural_policy_total_calls':{'fixed':36,'flexible':48},
           'final_paragraph_count_matched_on_valid_rows':4,'equal_natural_call_cost':False,'token_length_matched':False,
           'shared_selector_invalid':'Both finals identical empty evidence/error; planner receives empty candidate pool and returns empty list; no replacement/partial fallback.',
           'planner_invalid':'Only flexible final gets explicit empty evidence/error; fixed valid arm preserved; no fixed replacement for planner failure.',
           'unknown_policy':'Required native transport/deadline/context failures remain unknown, not zero; model schema/ID errors retain observed final score.',
           'host_only_diagnostics':['candidate_gold_coverage','selected_gold_coverage','half_allocation','relation_availability'],
           'primary_metrics':['answer_em','answer_f1','support_em','support_f1','paired_fixed_to_flexible'],
           'gold_available_to_routing':False,'new_GPU_or_model_calls_in_preparation':0,'optimizer_steps':0,
           'qualified_service':str(study.SERVICE_ROOT/'service_wrapper_v2.py'),'qualified_lifecycle':str(study.SERVICE_ROOT/'lifecycle_v3.py'),
           'claim':'Diagnostic fixed candidate allocation, not learned routing, recursion, novelty or confirmatory transfer.',
           'closure_sha256':closure,'launch_authority':'MAIN only'}
    ready['identity']=study.digest(ready); study.write_x(study.READY,ready)
    assert study.verify()==ready
    print({'READY_sha256':study.sha(study.READY),'identity':ready['identity'],'closure_files':len(closure),
           'static_selector_max_prefix_plus_output':max(len(x['body']['token_ids'])+128 for x in static),'tests':result.stdout})


if __name__=='__main__': main()
