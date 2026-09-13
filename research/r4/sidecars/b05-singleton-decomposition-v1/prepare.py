"""Outcome-blind public freeze, then host gold; actual HTTP CPU qualification and seal."""
import collections
import json
import subprocess
import interface
import owner
import study as s


def known_exposures():
    paths={s.SOURCE/'inputs/PUBLIC.json',s.ROOT.parents[1]/'ideas/b05-helper-width-feasibility-2026-09-12/public/PUBLIC.json'}
    for directory in s.ROOT.parent.glob('b05-*'):
        if directory==s.ROOT:continue
        for name in ('PUBLIC_ROOTS.json','PUBLIC_INPUTS.json','PUBLIC.json','HELD_PUBLIC.json','TRAIN_PUBLIC.json'):
            if (directory/name).is_file():paths.add(directory/name)
    roots=set();ids=set()
    def inspect(value):
        if isinstance(value,dict):
            if isinstance(value.get('root_id'),str):roots.add(value['root_id'])
            if isinstance(value.get('implementation_id'),str):ids.add(value['implementation_id'])
            for item in value.values():
                if isinstance(item,(dict,list)):inspect(item)
        elif isinstance(value,list):
            for item in value:
                if isinstance(item,(dict,list)):inspect(item)
    for path in sorted(paths):inspect(s.read(path))
    return sorted(paths),roots,ids


def main():
    assert not s.READY_RUN.exists() and not s.INPUTS.exists()
    assert s.sha(s.PRIOR/'CPU_READY.json')==s.PRIOR_SHA
    api=s.source.b05();ids_side=s.ROOT.parent/'b05-eligible-ids-interface-v1'
    with s.aliases({'study':s},ids_side):ids_interface=s.load('singleton_unchanged_list_contract',ids_side/'interface.py')
    vector=s.load('singleton_unchanged_vector_contract',s.PRIOR/'interface.py')
    oldpaths,usedroots,usedids=known_exposures();oldcounts={'root_ids':len(usedroots),'implementation_ids':len(usedids)}
    tasks=[];calls=[];prompts={};requests={};roots=[];children=[];audit=[]
    dimensions=[(6,0),(6,1),(12,2),(12,0),(20,1),(20,2)]
    scalar_tokens={str(value).lower():len(s.tokenizer().encode(json.dumps({'eligible':value}),add_special_tokens=False))+1 for value in (False,True)}
    assert max(scalar_tokens.values())<=16
    for index,(width,stage_index) in enumerate(dimensions):
        gen=202609420000+index
        root=api.generate(gen,api.StructuralConfig(width,1,1,3,1,'chain','helper-width-local-v1'))
        assert root['root_id'] not in usedroots;usedroots.add(root['root_id'])
        allids={r['implementation_id'] for stage in root['stages'] for r in stage['tables']['implementations']}
        assert not allids&usedids;usedids|=allids
        child=api.extract_child(root,stage_index);children.append(child);roots.append(api.build_safe_root_record(root))
        raw=ids_interface.render(api.render_child(child));view,_=s.normalize.public_view(raw);normal=s.normalize.normalized_view(view)
        list_prompt=s.normalize.render(raw);vector_prompt=vector.vector_prompt(list_prompt,width)
        order=[r['implementation_id'] for r in normal['stage']['effective_candidates']]
        singles=[interface.singleton_prompt(list_prompt,i) for i in range(width)]
        for i,prompt in enumerate(singles):
            projected=interface.normalized_public(prompt)
            assert projected['stage']['effective_candidates']==[normal['stage']['effective_candidates'][i]]
            assert projected['stage']['policy']==normal['stage']['policy']
        assert order==[r['implementation_id'] for r in child['stage']['tables']['implementations']]
        outputs={'list':len(s.tokenizer().encode(json.dumps({'eligible_ids':sorted(order)}),add_special_tokens=False))+1,
                 'vector':max(len(s.tokenizer().encode(json.dumps({'eligible':[value]*width}),add_special_tokens=False))+1 for value in (False,True)),
                 'singleton':max(scalar_tokens.values())}
        assert outputs['list']<=384 and outputs['vector']<=384
        tasks.append(dict(case_index=index,root_id=root['root_id'],width=width,history_depth=1,check_revisions=1,selected_stage=stage_index,generation_seed=gen,
            public_order=order,known_ids=sorted(order),raw_public_view=view,raw_prompt=raw,normalized_public_view=normal,
            list_prompt=list_prompt,vector_prompt=vector_prompt,singleton_prompts=singles))
        for repeat in (0,1):
            rootseed=202609430000+2*index+repeat;arms=['list','vector','singleton'];rotation=(index+repeat)%3;arms=arms[rotation:]+arms[:rotation]
            for arm in arms:
                for candidate_index in (range(width) if arm=='singleton' else [None]):
                    seed=rootseed+(1000+candidate_index if candidate_index is not None else 0);cap=16 if arm=='singleton' else 384
                    call=dict(root_id=root['root_id'],width=width,history_depth=1,repeat=repeat,arm=arm,kind='selection',seed=seed,root_seed=rootseed,max_tokens=cap)
                    if candidate_index is not None:call.update(candidate_index=candidate_index,candidate_id=order[candidate_index])
                    prompt=singles[candidate_index] if arm=='singleton' else list_prompt if arm=='list' else vector_prompt
                    key=s.call_id(call);request=s.request_body(prompt,seed,cap)
                    assert key not in prompts
                    calls.append(call);prompts[key]=prompt;requests[key]=request
                    audit.append(dict(call_id=key,root_id=root['root_id'],arm=arm,seed=seed,input_tokens=len(request['token_ids']),prefix_sha256=s.digest(request['token_ids']),
                        public_order_sha256=s.digest(order),label_blind_full_output_tokens=outputs[arm],output_cap=cap,actual_prefix_plus_output=len(request['token_ids'])+cap))
    assert len(calls)==176 and len(tasks)==6 and sum(t['width'] for t in tasks)==76
    assert collections.Counter(c['arm'] for c in calls)=={'singleton':152,'list':12,'vector':12}
    s.write_x(s.ROOT/'PUBLIC_ROOTS.json',{'roots':roots,'no_prior_root_or_ID_overlap':True,'generation_seed_range':[202609420000,202609420005]})
    s.write_x(s.ROOT/'EXCLUSIONS.json',{'paths_sha256':{str(p):s.sha(p) for p in oldpaths},'known_before_freeze':oldcounts,
        'scope':'All existing top-level B05 public roots/plans plus original source and width candidate inventory; IDs/root IDs, not semantic independence.'})
    s.write_x(s.INPUTS,{'schema':'b05-singleton176-plan-v1','tasks':tasks,'calls':calls,'prompts':prompts,'requests':requests})
    s.write_x(s.ROOT/'TOKEN_AUDIT.json',{'rows':audit,'no_labels_read':True,'scalar_both_values_plus_EOS_tokens':scalar_tokens,
        'whole_stage_output_caps':{'6':{'singleton':96,'whole':384},'12':{'singleton':192,'whole':384},'20':{'singleton':320,'whole':384}},
        'integer_seed_reuse_across_different_prompts_is_prospective':True,'total_compute_not_matched':True})
    host=[]
    for task,child in zip(tasks,children):
        answer=api.solve_child_reference(child);assert answer==api.solve_child_independent(child)
        gold=[r['implementation_id'] for r in answer['rows']]
        host.append(dict(root_id=task['root_id'],gold_ids=gold,candidate_truth=[key in gold for key in task['public_order']]))
    s.write_x(s.HOST,{'rows':host,'labels_computed_after_public_freeze':True,'two_independent_solvers_agree':True});s.HOST.chmod(0o600)
    command=[str(s.NATIVE),'-m','pytest','-q','test_singleton.py','--basetemp=cpu-fixture-seal-001']
    result=subprocess.run(command,cwd=s.ROOT,capture_output=True,text=True)
    s.write_x(s.ROOT/'CPU_TESTS.json',{'command':command,'returncode':result.returncode,'stdout':result.stdout,'stderr':result.stderr,
        'actual_HTTP_native_fixture':True,'GPU_calls':0,'model_calls':0,'red_receipt':'First parser/union test failed before interface.py existed; then passed after implementation.'})
    assert result.returncode==0,result.stdout+result.stderr
    owner.implementation();closure=dict(s.read(s.PRIOR/'CPU_READY.json')['closure_sha256'])
    paths=list(s.ROOT.glob('*.py'))+list(s.ROOT.glob('*.json'))+[s.ROOT/'RUNBOOK.md',s.ROOT/'PLAN.md',s.PRIOR/'CPU_READY.json',
        s.PRIOR/'outputs/attempt-001/OWNER_TERMINAL.json',s.PRIOR/'outputs/attempt-001/RESULT.json',ids_side/'interface.py']+oldpaths
    for path in paths+list((s.ROOT/'cpu-fixture-seal-001').rglob('*.json')):closure[str(path)]=s.sha(path)
    ready=dict(schema='b05-singleton-decomposition176-ready-v1',status='CPU_READY_MAIN_REVIEW_NO_GPU_ADMISSION',
        argv=[str(s.NATIVE),str(s.ROOT/'owner.py'),'run','--outer-seconds','1000'],launch_authority='MAIN only',
        context_units=6,paired_seed_units=12,stage_arm_outputs=36,planned_physical_calls=176,physical_by_arm={'list':12,'vector':12,'singleton':152},
        arms=['list','vector','singleton'],all_new_cases=True,dimensions=dimensions,history_depth=1,check_revisions=1,
        generation_seed_range=[202609420000,202609420005],root_seed_range=[202609430000,202609430011],
        singleton_seed='root_seed + 1000 + public candidate index; some seeds shared across different prompts',
        model=str(s.MODEL),model_alias=s.MODEL_ALIAS,adapter=None,temperature=.5,max_tokens={'list':384,'vector':384,'singleton':16},input_cap=8192,
        science_seconds=900,owner_seconds=1000,external_seconds=1100,concurrency=4,
        input_max_by_arm={arm:max(r['input_tokens'] for r in audit if r['arm']==arm) for arm in ('list','vector','singleton')},
        full_output_max_by_arm={arm:max(r['label_blind_full_output_tokens'] for r in audit if r['arm']==arm) for arm in ('list','vector','singleton')},
        scalar_projection='one unchanged effective candidate plus unchanged public policy/domains; positional selection only',
        scalar_contract='exactly one eligible key; literal JSON boolean; no array, numeric/string coercion, duplicate key or extra field',
        source_seed_and_public_inputs_frozen_before_gold=True,all_candidates_required_for_semantic_set=True,missing_is_unknown_not_false=True,
        invalid_known_separate_from_unavailable=True,no_eligibility_repair=True,no_gold_in_prompts=True,optimizer_steps=0,
        strict_list_sorting_separate=True,primary='semantic complete eligible set exact on all12 tasks/arm; correct/wrong/unknown separate',
        secondary='matched-valid comparisons; candidate confusion coverage, BA, recall, precision, F1/Jaccard, constants and all physical costs',
        token_costs_not_matched=True,not_learned_decomposition=True,record_response_sha256_semantics='canonical parsed JSON digest; raw response bytes separately retained',
        closure_sha256=dict(sorted(closure.items())))
    ready['identity']=s.digest(ready);s.write_x(s.READY_RUN,ready);s.verify()
    print(json.dumps({'ready':str(s.READY_RUN),'sha256':s.sha(s.READY_RUN),'identity':ready['identity'],
        'input_max':ready['input_max_by_arm'],'full_output_tokens':ready['full_output_max_by_arm'],'closure_files':len(closure)},indent=2))


if __name__=='__main__':main()
