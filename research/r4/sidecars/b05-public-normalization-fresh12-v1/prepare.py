"""Freeze outcome-blind new public stages and prefixes before computing host labels."""
from datetime import datetime,timezone
import json
import subprocess
import owner
import study as s


def frozen(path,value):
    if path.exists():assert s.read(path)==value,'frozen public/host payload changed'
    else:s.write_x(path,value)


def main():
    assert not s.READY_RUN.exists() and s.sha(s.PRIOR/'CPU_READY.json')==s.PRIOR_SHA
    api=s.source.b05()
    ids_side=s.ROOT.parent/'b05-eligible-ids-interface-v1'
    with s.aliases({'study':s},ids_side):interface=s.load('fresh_normalization_identical_ID_contract',ids_side/'interface.py')
    oldpaths=[s.SOURCE/'inputs/PUBLIC.json',s.ROOT.parents[1]/'ideas/b05-helper-width-feasibility-2026-09-12/public/PUBLIC.json',s.TRAIN/'HELD_PUBLIC.json']
    oldroots=[r['safe_root'] for path in oldpaths for r in s.read(path)['roots']]
    usedroots={r['root_id'] for r in oldroots};usedids={i['implementation_id'] for r in oldroots for stage in r['stages'] for i in stage['tables']['implementations']}
    dimensions=[(1,6,0),(1,6,1),(1,12,2),(1,12,0),(1,20,1),(1,20,2),(3,6,0),(3,6,1),(3,6,2),(3,12,0),(3,12,1),(3,12,2)]
    tasks=[];calls=[];prompts={};requests={};audit=[];roots=[];children=[]
    for index,(history,width,stage_index) in enumerate(dimensions):
        generation_seed=202609360000+index
        root=api.generate(generation_seed,api.StructuralConfig(width,history,1,3,1,'chain','helper-width-local-v1'))
        assert root['root_id'] not in usedroots;usedroots.add(root['root_id'])
        allids={i['implementation_id'] for stage in root['stages'] for i in stage['tables']['implementations']}
        assert not usedids&allids;usedids|=allids
        child=api.extract_child(root,stage_index);children.append(child);roots.append(api.build_safe_root_record(root))
        raw=interface.render(api.render_child(child));view,_=s.normalize.public_view(raw);normal=s.normalize.normalized_view(view);normalized=s.normalize.render(raw)
        known=sorted(i['implementation_id'] for i in child['stage']['tables']['implementations'])
        assert len(s.tokenizer().encode(json.dumps({'eligible_ids':known}),add_special_tokens=False))+1<=384
        tasks.append(dict(root_id=root['root_id'],width=width,history_depth=history,check_revisions=1,generation_seed=generation_seed,selected_stage=stage_index,known_ids=known,raw_prompt=raw,raw_public_view=view,normalized_public_view=normal,normalized_prompt=normalized))
        for repeat in (0,1):
            seed=202609370000+2*index+repeat
            for arm in (('raw','normalized') if (index+repeat)%2==0 else ('normalized','raw')):
                call=dict(root_id=root['root_id'],width=width,history_depth=history,repeat=repeat,arm=arm,kind='selection',seed=seed,max_tokens=384)
                key=s.call_id(call);prompt=raw if arm=='raw' else normalized
                tokens=s.renderer().render_ids([{'role':'user','content':prompt}],add_generation_prompt=True)
                audit.append(dict(call_id=key,root_id=root['root_id'],arm=arm,history_depth=history,width=width,input_tokens=len(tokens),prefix_sha256=s.digest(tokens)))
                calls.append(call);prompts[key]=prompt
                if len(tokens)+384<=8192:requests[key]=s.request_body(prompt,seed,384)
    frozen(s.ROOT/'TOKEN_PREFLIGHT.json',{'rows':audit,'outcome_blind':True,'all_fixed_seeds_retained':True,'history3_varies_changes_only_check_revisions1':True})
    assert len(requests)==48,'Prospective token overflow: stop; no hard-example filtering or automatic shrinking'
    frozen(s.ROOT/'PUBLIC_ROOTS.json',{'roots':roots,'generation_seeds':[202609360000+i for i in range(12)],'no_prior_root_or_ID_overlap':True})
    # No reference solver or host labels have been accessed before this public freeze.
    frozen(s.INPUTS,{'schema':'b05-fresh12-raw-vs-public-normalized48-plan-v1','tasks':tasks,'calls':calls,'prompts':prompts,'requests':requests})
    host=[]
    for task,child in zip(tasks,children):
        answer=api.solve_child_reference(child);assert answer==api.solve_child_independent(child)
        host.append({'root_id':task['root_id'],'gold_ids':[r['implementation_id'] for r in answer['rows']]})
    frozen(s.HOST,{'rows':host,'labels_computed_after_public_freeze':True,'two_independent_solvers_agree':True});s.HOST.chmod(0o600)
    command=[str(s.NATIVE),'-m','pytest','-q','test_fresh.py','--basetemp=cpu-fixture-seal-002']
    result=subprocess.run(command,cwd=s.ROOT,capture_output=True,text=True)
    s.write_x(s.ROOT/'CPU_TESTS_V2.json',{'command':command,'returncode':result.returncode,'stdout':result.stdout,'stderr':result.stderr,'actual_frozen_pair_HTTP':True,'GPU_calls':0,'model_calls':0})
    assert result.returncode==0,result.stdout+result.stderr
    owner.implementation();closure=dict(s.read(s.PRIOR/'CPU_READY.json')['closure_sha256'])
    paths=list(s.ROOT.glob('*.py'))+list(s.ROOT.glob('*.json'))+[s.ROOT/'RUNBOOK.md',s.PRIOR/'CPU_READY.json',s.PRIOR/'outputs/attempt-001/OWNER_TERMINAL.json',s.PRIOR/'outputs/attempt-001/RESULT.json',ids_side/'interface.py']+oldpaths
    for path in paths+list((s.ROOT/'cpu-fixture-seal-002').rglob('*.json')):closure[str(path)]=s.sha(path)
    ready=dict(schema='b05-public-normalization-fresh12-ready-v1',status='CPU_READY_MAIN_REVIEW_NO_GPU_ADMISSION',created_utc=datetime.now(timezone.utc).isoformat(),
        argv=[str(s.NATIVE),str(s.ROOT/'owner.py'),'run','--outer-seconds','700'],launch_authority='MAIN only',
        context_units=12,paired_seed_units=24,planned_physical_calls=48,arms=['raw','normalized'],all_new_stages_and_new_raw_controls=True,
        dimensions=dimensions,generation_seed_range=[202609360000,202609360011],sampling_seed_range=[202609370000,202609370023],
        history_depth_varies_change_rows_only=True,check_revisions_fixed=1,other_generator_config=[3,1,'chain','helper-width-local-v1'],
        model=str(s.MODEL),model_alias=s.MODEL_ALIAS,adapter=None,temperature=.5,max_tokens=384,input_cap=8192,
        owner_seconds=700,science_seconds=600,external_seconds=800,concurrency=4,
        input_max_by_history_width_arm={f'{h}/{w}/{a}':max(r['input_tokens'] for r in audit if r['history_depth']==h and r['width']==w and r['arm']==a) for h,w in sorted({(r['history_depth'],r['width']) for r in audit}) for a in ('raw','normalized')},
        primary='unordered known unique-ID exact; BA and precision/recall with explicit valid-set denominators',strict_sorted_format_separate=True,unknown_is_not_wrong=True,
        normalizer_sha256=s.NORMALIZE_SHA,normalizer_computes_eligibility=False,normalizer_reads_gold=False,all_candidates_retained=True,
        identical_prior_normalizer_and_prompt_contract=True,no_annotation_or_outcome_filter=True,token_overflow_policy='stop before GPU; no automatic fallback',
        input_representation_and_explanatory_wording_jointly_change=True,natural_model_calls_per_answer=1,token_costs_not_matched=True,
        fresh_same_family_not_new_dataset=True,not_learned_decomposition=True,
        record_response_sha256_semantics='canonical parsed JSON digest; original response bytes retained separately',
        cpu_fixture='CPU_TESTS_V2.json; initial fixture missing test-only normalize alias preserved as CPU_TESTS.json; no payload changes',closure_sha256=dict(sorted(closure.items())))
    ready['identity']=s.digest(ready);s.write_x(s.READY_RUN,ready);s.verify()
    print(json.dumps({'ready':str(s.READY_RUN),'sha256':s.sha(s.READY_RUN),'identity':ready['identity'],'input_max':ready['input_max_by_history_width_arm'],'closure_files':len(closure)},indent=2))


if __name__=='__main__':main()
