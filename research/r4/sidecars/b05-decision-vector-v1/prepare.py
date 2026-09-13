"""Freeze new normalized public cases and both output interfaces before host labels."""
from datetime import datetime,timezone
import json
import subprocess
import interface
import owner
import study as s


def main():
    assert not s.READY_RUN.exists() and s.sha(s.PRIOR/'CPU_READY.json')==s.PRIOR_SHA
    api=s.source.b05();ids_side=s.ROOT.parent/'b05-eligible-ids-interface-v1'
    with s.aliases({'study':s},ids_side):ids_interface=s.load('vector_unchanged_list_contract',ids_side/'interface.py')
    oldpaths=[s.SOURCE/'inputs/PUBLIC.json',s.ROOT.parents[1]/'ideas/b05-helper-width-feasibility-2026-09-12/public/PUBLIC.json',s.TRAIN/'HELD_PUBLIC.json',s.PRIOR/'PUBLIC_ROOTS.json']
    oldroots=[r.get('safe_root',r) for path in oldpaths for r in s.read(path)['roots']]
    usedroots={r['root_id'] for r in oldroots};usedids={i['implementation_id'] for root in oldroots for stage in root['stages'] for i in stage['tables']['implementations']}
    dimensions=[(1,6,0),(1,6,1),(1,12,2),(1,12,0),(1,20,1),(1,20,2),(3,6,0),(3,6,1),(3,6,2),(3,12,0),(3,12,1),(3,12,2)]
    tasks=[];calls=[];prompts={};requests={};roots=[];children=[];audit=[]
    for index,(history,width,stage_index) in enumerate(dimensions):
        generation_seed=202609380000+index
        root=api.generate(generation_seed,api.StructuralConfig(width,history,1,3,1,'chain','helper-width-local-v1'))
        assert root['root_id'] not in usedroots;usedroots.add(root['root_id'])
        allids={i['implementation_id'] for stage in root['stages'] for i in stage['tables']['implementations']}
        assert not allids&usedids;usedids|=allids
        child=api.extract_child(root,stage_index);children.append(child);roots.append(api.build_safe_root_record(root))
        raw=ids_interface.render(api.render_child(child));view,_=s.normalize.public_view(raw);normal=s.normalize.normalized_view(view)
        list_prompt=s.normalize.render(raw);vector_prompt=interface.vector_prompt(list_prompt,width)
        order=[r['implementation_id'] for r in normal['stage']['effective_candidates']]
        assert order==[r['implementation_id'] for r in child['stage']['tables']['implementations']] and len(order)==width
        assert list_prompt.split('Return exactly one JSON object',1)[0]==vector_prompt.split('Return exactly one JSON object',1)[0]
        # Worst-case full output examples are public, label-blind token-fit diagnostics only.
        full_outputs={'list':{'eligible_ids':sorted(order)},'vector':{'eligible':[False]*width}}
        output_tokens={arm:len(s.tokenizer().encode(json.dumps(value),add_special_tokens=False))+1 for arm,value in full_outputs.items()}
        assert max(output_tokens.values())<=384
        tasks.append(dict(root_id=root['root_id'],width=width,history_depth=history,check_revisions=1,selected_stage=stage_index,generation_seed=generation_seed,
            public_order=order,known_ids=sorted(order),raw_public_view=view,raw_prompt=raw,normalized_public_view=normal,list_prompt=list_prompt,vector_prompt=vector_prompt))
        for repeat in (0,1):
            seed=202609390000+2*index+repeat
            for arm in (('list','vector') if (index+repeat)%2==0 else ('vector','list')):
                call=dict(root_id=root['root_id'],width=width,history_depth=history,repeat=repeat,arm=arm,kind='selection',seed=seed,max_tokens=384)
                key=s.call_id(call);prompt=list_prompt if arm=='list' else vector_prompt;request=s.request_body(prompt,seed,384)
                calls.append(call);prompts[key]=prompt;requests[key]=request
                audit.append(dict(call_id=key,root_id=root['root_id'],arm=arm,seed=seed,input_tokens=len(request['token_ids']),prefix_sha256=s.digest(request['token_ids']),
                    public_order_sha256=s.digest(order),label_blind_full_output_tokens=output_tokens[arm],output_cap=384))
    assert len(calls)==48 and len(tasks)==12
    s.write_x(s.ROOT/'PUBLIC_ROOTS.json',{'roots':roots,'no_prior_root_or_ID_overlap':True,'generation_seed_range':[202609380000,202609380011]})
    s.write_x(s.INPUTS,{'schema':'b05-normalized-list-vs-decision-vector48-plan-v1','tasks':tasks,'calls':calls,'prompts':prompts,'requests':requests})
    s.write_x(s.ROOT/'TOKEN_AUDIT.json',{'rows':audit,'no_labels_read':True,'output_lengths_not_matched':True})
    # Only after the complete public plan is immutable are host labels computed.
    host=[]
    for task,child in zip(tasks,children):
        answer=api.solve_child_reference(child);assert answer==api.solve_child_independent(child)
        host.append({'root_id':task['root_id'],'gold_ids':[r['implementation_id'] for r in answer['rows']]})
    s.write_x(s.HOST,{'rows':host,'labels_computed_after_public_freeze':True,'two_independent_solvers_agree':True});s.HOST.chmod(0o600)
    command=[str(s.NATIVE),'-m','pytest','-q','test_vector.py','--basetemp=cpu-fixture-seal-001']
    result=subprocess.run(command,cwd=s.ROOT,capture_output=True,text=True)
    s.write_x(s.ROOT/'CPU_TESTS.json',{'command':command,'returncode':result.returncode,'stdout':result.stdout,'stderr':result.stderr,
        'actual_HTTP_native_fixture':True,'GPU_calls':0,'model_calls':0,'parser_red_before_implementation':'test_vector_requires_literal_bools_exact_length_and_public_order failed: decision vector parser not implemented'})
    assert result.returncode==0,result.stdout+result.stderr
    owner.implementation();closure=dict(s.read(s.PRIOR/'CPU_READY.json')['closure_sha256'])
    paths=list(s.ROOT.glob('*.py'))+list(s.ROOT.glob('*.json'))+[s.ROOT/'RUNBOOK.md',s.PRIOR/'CPU_READY.json',s.PRIOR/'outputs/attempt-001/OWNER_TERMINAL.json',s.PRIOR/'outputs/attempt-001/RESULT.json',ids_side/'interface.py']+oldpaths
    for path in paths+list((s.ROOT/'cpu-fixture-seal-001').rglob('*.json')):closure[str(path)]=s.sha(path)
    ready=dict(schema='b05-decision-vector48-ready-v1',status='CPU_READY_MAIN_REVIEW_NO_GPU_ADMISSION',created_utc=datetime.now(timezone.utc).isoformat(),
        argv=[str(s.NATIVE),str(s.ROOT/'owner.py'),'run','--outer-seconds','700'],launch_authority='MAIN only',
        context_units=12,paired_seed_units=24,planned_physical_calls=48,arms=['list','vector'],all_new_cases=True,dimensions=dimensions,
        generation_seed_range=[202609380000,202609380011],sampling_seed_range=[202609390000,202609390023],
        model=str(s.MODEL),model_alias=s.MODEL_ALIAS,adapter=None,temperature=.5,max_tokens=384,input_cap=8192,
        science_seconds=600,owner_seconds=700,external_seconds=800,concurrency=4,
        input_max_by_arm={arm:max(r['input_tokens'] for r in audit if r['arm']==arm) for arm in ('list','vector')},
        label_blind_full_output_max_by_arm={arm:max(r['label_blind_full_output_tokens'] for r in audit if r['arm']==arm) for arm in ('list','vector')},
        normalized_records_and_policy_identical=True,only_output_contract_suffix_differs=True,output_interface_and_lengths_differ=True,
        vector_contract='exactly one eligible key; exact public candidate count; literal booleans; map by effective_candidates array order only',
        invalid_or_unknown_ids_remain_none=True,no_partial_credit_on_invalid=True,exact_denominator_all24_attempts_per_arm=True,
        primary='unordered selected-ID exact; strict list sorting separate; vector strict literal schema required',
        secondary='matched-valid paired BA; explicit valid-set precision/recall and denominators; all invalid-known and unknown separately',
        normalizer_computes_eligibility=False,no_gold_in_prompts=True,no_eligibility_filter_or_repair=True,all_candidates_retained=True,
        natural_calls_per_answer=1,token_costs_not_matched=True,history_groups_different_instances_not_causal=True,not_learned_decomposition=True,
        record_response_sha256_semantics='canonical parsed JSON digest; raw response bytes separately retained',closure_sha256=dict(sorted(closure.items())))
    ready['identity']=s.digest(ready);s.write_x(s.READY_RUN,ready);s.verify()
    print(json.dumps({'ready':str(s.READY_RUN),'sha256':s.sha(s.READY_RUN),'identity':ready['identity'],'input_max':ready['input_max_by_arm'],
        'full_output_tokens':ready['label_blind_full_output_max_by_arm'],'closure_files':len(closure)},indent=2))


if __name__=='__main__':main()
