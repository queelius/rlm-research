"""Freeze the existing exposed12 public records; no case or output selection."""
import argparse
import os
from pathlib import Path
import subprocess
import time
import study

SOURCE_READY_SHA='c799becad8d574d6785dbd4292e00b6bb27536175adb8b6b71f1df4c469dd1c1'


def inputs():
    source=study.SERVICE_ROOT/'inputs/MANIFEST.json'
    old=study.read(source)
    names=('record_id','hop_count','paragraph_count','public_path','public_sha256','partition_indices')
    values=[{k:r[k] for k in names} for r in old['selected']]
    assert len(values)==12
    for row in values:
        assert study.sha(row['public_path'])==row['public_sha256']
        public=study.read(row['public_path'])
        assert set(public)=={'question','paragraphs'}
        assert all(set(p)=={'idx','title','paragraph_text'} for p in public['paragraphs'])
        assert [[p['idx'] for p in h] for h in study.partition(public,row['record_id'])]==row['partition_indices']
    value={'selected':values,'source_manifest_sha256':study.sha(source),
           'all_original12_in_original_order':True,'previously_exposed_diagnostic':True,
           'gold_annotations_or_support_identifiers_in_public_manifest':False}
    path=study.INPUTS/'PUBLIC_MANIFEST.json'
    if path.exists():assert study.read(path)==value
    else:study.write_x(path,value)
    return value


def main():
    parser=argparse.ArgumentParser();parser.add_argument('--inputs-only',action='store_true');args=parser.parse_args()
    assert os.environ.get('CUDA_VISIBLE_DEVICES')==''
    inputs()
    if args.inputs_only:return
    assert not study.READY.exists() and not study.ATTEMPT.exists()
    old_ready_path=study.SERVICE_ROOT/'READY_V3.json'
    assert study.sha(old_ready_path)==SOURCE_READY_SHA
    old_ready=study.read(old_ready_path)
    for path,want in old_ready['closure_sha256'].items():assert study.sha(path)==want,path
    command=[str(study.NATIVE),'-m','pytest','-q','-p','no:cacheprovider','test_evidence.py','--basetemp='+str(study.ROOT/'cpu-fixture-001')]
    result=subprocess.run(command,cwd=study.ROOT,capture_output=True,text=True,timeout=180,
                          env={**os.environ,'PYTHONDONTWRITEBYTECODE':'1'})
    study.write_x(study.ROOT/'CPU_TESTS.json',{'command':command,'returncode':result.returncode,
                'stdout':result.stdout,'stderr':result.stderr,'model_queries':0,'GPU_used':False,
                'native_call_double':'Only urllib HTTP response; actual request, tokenizer, decode, call checkpoint, question graph and host scoring exercised.'})
    assert result.returncode==0,result.stdout+result.stderr
    import owner
    implementation=owner.implementation()
    assert implementation.study.ATTEMPT==study.ATTEMPT and implementation.collect is owner.collect
    # Reuse authenticated V3 service paths and exact engine claim, never launch.
    suite=study.base_owner().study.dependencies();implementation.lifecycle.install(suite)
    assert suite.SERVE==study.SERVICE_ROOT/'service_wrapper_v2.py'
    assert suite.life.REPORT_ENGINE_ENTRY==study.SERVICE_ROOT/'engine_entry_v2.py'
    from transformers import AutoTokenizer
    tok=AutoTokenizer.from_pretrained(study.MODEL,local_files_only=True)
    static=[]
    for index,item in enumerate(study.selected()):
        public=study.read(item['public_path']);halves=study.partition(public,item['record_id'])
        for side,label in enumerate(('left','right')):
            role='select_'+label
            body=study.request(study.selector_messages(public,halves[side]),role,study.seed(index,role),item['paragraph_count'],tok)
            static.append({'record_id':item['record_id'],'role':role,'body':body,'body_sha256':study.digest(body)})
    study.write_x(study.INPUTS/'STATIC_SELECTORS.json',static)
    study.write_x(study.INPUTS/'SCHEDULE.json',study.schedule())
    closure=dict(old_ready['closure_sha256'])
    paths=list(study.ROOT.glob('*.py'))+[study.ROOT/'RUNBOOK.md',study.ROOT/'CPU_TESTS.json',old_ready_path]
    paths+=list(study.INPUTS.glob('*.json'))+list((study.ROOT/'cpu-fixture-001').rglob('*.json'))
    closure.update({str(p):study.sha(p) for p in paths})
    ready={'schema':'musique-evidence-preservation-cpu-ready-v1','created_epoch':time.time(),
           'source_V3_READY_sha256':SOURCE_READY_SHA,'source_V3_READY_identity':old_ready['identity'],
           'schedule_sha256':study.digest(study.schedule()),'output':str(study.ATTEMPT),
           'command':[str(study.NATIVE),str(study.ROOT/'owner.py'),'run','--outer-seconds','950'],
           'questions':12,'final_slots':24,'physical_calls':72,'all_existing_contexts':True,
           'question_blind_original_halves':True,'exposed_diagnostic_panel':True,
           'graph':['select_left','select_right','summary_left_selected_only','summary_right_selected_only','paired_summary_final','paired_verbatim_final'],
           'role_seeds':'202609220000 +16*question_index +offset: select0/1, summaries2/3, bothfinals4',
           'caps':{'selector_output_tokens':128,'summary_output_tokens':512,'final_output_tokens':1024,
                   'science_seconds':700,'owner_seconds':950,'external_seconds':1050,'question_workers':4,'native_calls':72},
           'invalid_selector_policy':'Any invalid schema, duplicate/out-of-half ID yields recorded model error; both finals get identical empty-evidence/error packet, no replacement or cross-half fallback. All helper calls remain planned.',
           'summary_source_boundary':'Only validated selected exact original paragraph objects; no full half, selection prose, unselected source or gold.',
           'shared_acquisition':'Both finals reference the same four helper receipts; verbatim payload excludes summary content.',
           'natural_policy_calls_per_question':{'verbatim':3,'summary':5},'equal_natural_call_cost':False,'token_cost_matched':False,
           'metrics':['answer_em','answer_f1','support_em','support_f1','paired_answer_wins_losses','host_only_selected_gold_support_coverage','physical_and_natural_policy_costs'],
           'gold_in_model_prompts_or_collector_reads':False,'new_gpu_or_model_calls_in_preparation':0,'optimizer_steps':0,
           'claim':'Evidence representation mechanism only, not learned routing, recursion, novelty or confirmatory transfer.',
           'qualified_service':str(study.SERVICE_ROOT/'service_wrapper_v2.py'),'qualified_lifecycle':str(study.SERVICE_ROOT/'lifecycle_v3.py'),
           'closure_sha256':closure,'launch_authority':'MAIN only; no launch by preparation'}
    ready['identity']=study.digest(ready);study.write_x(study.READY,ready)
    assert study.verify()==ready
    print({'path':str(study.READY),'sha256':study.sha(study.READY),'identity':ready['identity'],'closure_files':len(closure),'tests':result.stdout})


if __name__=='__main__':main()
