"""Outcome-blind G4 train16 plus held12 freeze; host prevalence diagnostics only."""
from datetime import datetime,timezone
import json
import subprocess
import owner
import study as s


def main():
    assert not s.READY_RUN.exists() and s.sha(s.PRIOR/'CPU_READY.json')==s.PRIOR_SHA
    api=s.source.b05();ids_side=s.ROOT.parent/'b05-eligible-ids-interface-v1'
    with s.aliases({'study':s},ids_side):ids=s.load('varied_unchanged_ID_source_renderer',ids_side/'interface.py')
    oldpaths=[s.SOURCE/'inputs/PUBLIC.json',s.ROOT.parents[1]/'ideas/b05-helper-width-feasibility-2026-09-12/public/PUBLIC.json',s.TRAIN/'HELD_PUBLIC.json']
    oldpaths+=sorted(p for p in s.ROOT.parent.glob('b05-*/PUBLIC_ROOTS.json') if p.parent!=s.ROOT)
    old=[r.get('safe_root',r) for p in oldpaths for r in s.read(p)['roots']]
    usedroots={r['root_id'] for r in old};usedids={i['implementation_id'] for r in old for stage in r['stages'] for i in stage['tables']['implementations']}
    train_dims=[(6 if i<8 else 12,1 if i%8<4 else 3,1,i%3) for i in range(16)]
    held_dims=[(width,history,checks,i%3) for i,(width,history,checks) in enumerate((w,h,c) for w in (6,12,20) for h in (1,3) for c in (1,3))]
    plans={};children=[];roots=[];token_audit=[]
    for split,dims,genbase,samplebase,G in [('train',train_dims,202609440000,202609450000,4),('held',held_dims,202609460000,202609470000,2)]:
        tasks=[];calls=[];prompts={};requests={}
        for index,(width,history,checks,stage_index) in enumerate(dims):
            generation_seed=genbase+index;root=api.generate(generation_seed,api.StructuralConfig(width,history,checks,3,1,'chain','helper-width-local-v1'))
            assert root['root_id'] not in usedroots;usedroots.add(root['root_id'])
            allids={i['implementation_id'] for stage in root['stages'] for i in stage['tables']['implementations']}
            assert not usedids&allids;usedids|=allids
            child=api.extract_child(root,stage_index);children.append((split,child));roots.append({'split':split,'safe_root':api.build_safe_root_record(root)})
            raw=ids.render(api.render_child(child));view,_=s.normalize.public_view(raw);normal=s.normalize.normalized_view(view)
            prompt=s.interface.vector_prompt(s.normalize.render(raw),width)
            order=[r['implementation_id'] for r in normal['stage']['effective_candidates']]
            assert order==[r['implementation_id'] for r in child['stage']['tables']['implementations']] and len(order)==width
            tasks.append(dict(split=split,root_id=root['root_id'],width=width,history_depth=history,check_revisions=checks,selected_stage=stage_index,generation_seed=generation_seed,
                public_order=order,known_ids=sorted(order),raw_prompt=raw,raw_public_view=view,normalized_public_view=normal,prompt=prompt))
            for repeat in range(G):
                seed=samplebase+G*index+repeat
                call=dict(root_id=root['root_id'],width=width,history_depth=history,check_revisions=checks,repeat=repeat,arm='vector',kind='selection',seed=seed,max_tokens=384)
                key=s.call_id(call);request=s.request_body(prompt,seed,384)
                calls.append(call);prompts[key]=prompt;requests[key]=request
                token_audit.append(dict(split=split,call_id=key,root_id=root['root_id'],seed=seed,input_tokens=len(request['token_ids']),prefix_sha256=s.digest(request['token_ids']),
                    public_order_sha256=s.digest(order),output_cap=384))
        plans[split]={'schema':f'b05-varied-vector-{split}-public-v1','tasks':tasks,'calls':calls,'prompts':prompts,'requests':requests,'G':G}
    # Both train and held public cases/requests freeze before any host labels are computed.
    s.write_x(s.INPUTS,plans['train']);s.write_x(s.HELD,plans['held'])
    s.write_x(s.ROOT/'PUBLIC_ROOTS.json',{'roots':roots,'disjoint_all_prior_roots_and_candidate_IDs':True,'prior_public_files':[str(p) for p in oldpaths]})
    s.write_x(s.ROOT/'TOKEN_AUDIT.json',{'rows':token_audit,'outcome_blind':True,'held_calls_not_executed':True})
    host=[];baselines=[]
    for split,child in children:
        answer=api.solve_child_reference(child);assert answer==api.solve_child_independent(child)
        task=next(t for t in plans[split]['tasks'] if t['root_id']==next(r['safe_root']['root_id'] for r in roots if r['split']==split and r['safe_root']['stages'][child['child_index']]['child_id']==child['child_id']))
        gold=[r['implementation_id'] for r in answer['rows']];n=len(task['public_order']);p=len(gold)
        host.append(dict(split=split,root_id=task['root_id'],gold_ids=gold))
        baselines.append(dict(split=split,root_id=task['root_id'],width=n,history_depth=task['history_depth'],check_revisions=task['check_revisions'],
            positives=p,negatives=n-p,positive_fraction=p/n,all_true_exact=p==n,all_false_exact=p==0,
            all_true_BA=(1. if p==n else 0. if p==0 else .5),all_false_BA=(1. if p==0 else 0. if p==n else .5)))
    s.write_x(s.HOST,{'rows':host,'labels_computed_after_both_public_freezes':True,'two_independent_solvers_agree':True});s.HOST.chmod(0o600)
    s.write_x(s.ROOT/'HOST_BASELINES.json',{'rows':baselines,'model_outputs_seen':False,'no_label_based_selection':True,
        'summary':{split:{'cases':len([r for r in baselines if r['split']==split]),'candidates':sum(r['width'] for r in baselines if r['split']==split),
            'positives':sum(r['positives'] for r in baselines if r['split']==split),'all_true_exact_cases':sum(r['all_true_exact'] for r in baselines if r['split']==split),
            'all_false_exact_cases':sum(r['all_false_exact'] for r in baselines if r['split']==split)} for split in ('train','held')}})
    command=[str(s.NATIVE),'-m','pytest','-q','test_rollouts.py','--basetemp=cpu-fixture-seal-001']
    test=subprocess.run(command,cwd=s.ROOT,capture_output=True,text=True)
    s.write_x(s.ROOT/'CPU_TESTS.json',{'command':command,'returncode':test.returncode,'stdout':test.stdout,'stderr':test.stderr,'model_calls':0,'GPU_calls':0,'actual_native_HTTP_fixture':True})
    assert test.returncode==0,test.stdout+test.stderr
    owner.implementation();closure=dict(s.read(s.PRIOR/'CPU_READY.json')['closure_sha256'])
    paths=list(s.ROOT.glob('*.py'))+list(s.ROOT.glob('*.json'))+[s.ROOT/'RUNBOOK.md',s.PRIOR/'CPU_READY.json',s.PRIOR/'outputs/attempt-001/OWNER_TERMINAL.json',s.PRIOR/'outputs/attempt-001/RESULT.json']+oldpaths
    for p in paths+list((s.ROOT/'cpu-fixture-seal-001').rglob('*.json')):closure[str(p)]=s.sha(p)
    ready=dict(schema='b05-varied-vector-rollouts64-ready-v1',status='CPU_READY_MAIN_REVIEW_NO_GPU_ADMISSION',created_utc=datetime.now(timezone.utc).isoformat(),
        argv=[str(s.NATIVE),str(s.ROOT/'owner.py'),'run','--outer-seconds','700'],launch_authority='MAIN only',
        planned_physical_calls=64,context_units=16,G=4,train_dimensions=train_dims,held_context_units=12,held_dimensions=held_dims,held_physical_calls_this_run=0,
        generation_train=[202609440000,202609440015],sampling_train=[202609450000,202609450063],generation_held=[202609460000,202609460011],sampling_held=[202609470000,202609470023],
        model=str(s.MODEL),model_alias=s.MODEL_ALIAS,adapter=None,temperature=.5,max_tokens=384,input_cap=8192,science_seconds=600,owner_seconds=700,external_seconds=800,concurrency=4,
        max_input_by_split={split:max(r['input_tokens'] for r in token_audit if r['split']==split) for split in ('train','held')},
        no_gold_in_prompts=True,all_candidates_retained=True,all_groups_and_invalids_retained=True,no_output_driven_filter=True,
        before_outcome_host_baselines='HOST_BASELINES.json; alltrue/allfalse/exact/BA and per-case positive fractions',
        output_schema='unchanged exact full literal-boolean eligible vector in public effective_candidates order',
        diagnostics='full-valid G4 candidate correctness contrasts; joint BA/exact contrasts; native boolean/token offsets and structural boundary overlaps; no masks/loss',
        held_check_revision_shift_explicit=True,no_optimizer_no_LoRA_init=True,future_local_vs_joint_credit_not_implemented=True,
        record_response_sha256_semantics='canonical parsed JSON digest; raw response bytes separately retained',closure_sha256=dict(sorted(closure.items())))
    ready['identity']=s.digest(ready);s.write_x(s.READY_RUN,ready);s.verify()
    print(json.dumps({'ready':str(s.READY_RUN),'sha256':s.sha(s.READY_RUN),'identity':ready['identity'],'max_input':ready['max_input_by_split'],
        'host_baselines':s.read(s.ROOT/'HOST_BASELINES.json')['summary'],'closure_files':len(closure)},indent=2))


if __name__=='__main__':main()
