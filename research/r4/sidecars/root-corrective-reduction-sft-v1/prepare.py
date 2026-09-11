"""Freeze label-independent training membership and prospective readout compositions."""
import argparse
import json
import subprocess
import os
import time
import study as s

def groups(value):
    if isinstance(value,dict):
        yield from value.get('group_ids',[])
        yield from value.get('question_group_sha256',[]) if isinstance(value.get('question_group_sha256'),list) else []
        for k,v in value.items():
            if k not in ('group_ids','question_group_sha256'):yield from groups(v)
    elif isinstance(value,list):
        for x in value:yield from groups(x)

def prepare():
    prior=s.ROOT.parent/'root-interface-sft-v1/prepared-v2'
    old=s.read(prior/'PUBLIC.json');gold=s.read(prior/'HOST_GOLD.json')
    excluded=set(g for c in old if c['stratum']!='train' for g in c['group_ids'])
    sources=[prior/'PUBLIC.json',prior/'HOST_GOLD.json',s.SOURCE/'DATA_READY.json',s.SOURCE/'data/PUBLIC.json',s.SOURCE/'data/HOST_GOLD.json']
    for relative in ('root-only-credit-v1/inputs/PUBLIC.json','root-rlvr-campaign-v1/inputs/TRANSFER_PUBLIC.json',
        'root-rlvr-independent-seed-v1/inputs/TRANSFER_PUBLIC.json','leaf-composition-transfer-v1/prepared-v1/DATA.json',
        'root-curriculum-data-v1/GROUPS.json','adaptive-filter-pilot-v1/inputs/MEMBERSHIP.json'):
        path=s.ROOT.parent/relative;sources.append(path);excluded.update(groups(s.read(path)))
    heldout=s.read(s.SOURCE/'data/PUBLIC.json');heldgold=s.read(s.SOURCE/'data/HOST_GOLD.json');excluded.update(groups(heldout))
    # Sibling example-map-visibility uses this same frozen64-group readout panel.
    pool={g:(r,gold[c['id']]['coarse_by_id'][r['id']]) for c in old if c['stratum']=='train' for g,r in zip(c['group_ids'],c['records']) if g not in excluded}
    ordered=sorted(pool,key=lambda g:s.digest([s.MASTER,'source',g]))
    if len(ordered)<128:raise ValueError('training-only population too small; no evaluation borrowing')
    contexts=[];host={};train=[]
    for ci in range(8):
        gids=ordered[ci*16:(ci+1)*16]
        records=[dict(id=f'q{i+1:04}',user=f'u{i%4:02}',text=pool[g][0]['text']) for i,g in enumerate(gids)]
        c=dict(id=f'corrective-train-{ci:02}',stratum='train',native_context_id=98135100+ci,
            target='NUM' if ci%2==0 else 'HUM',query_users=['u00','u01'],helper_partition='train',records=records,group_ids=gids)
        c['text']='\n'.join(f"ID: {r['id']} || User: {r['user']} || Instance: {r['text']}" for r in records)+'\n'
        contexts.append(c);host[c['id']]=dict(labels={r['id']:pool[g][1] for r,g in zip(records,gids)})
        for qi,users in enumerate(([f'u{ci%2:02}'],['u00','u01'] if ci%2==0 else ['u02','u03'])):
            for width in (16,4):
                index=len(train);row=dict(context_id=c['id'],users=users,width=width,metadata_error=index%4==3,
                    variable=('labels','batch_labels','categories')[index%3],seed=981351101+index,
                    family='single_user' if qi==0 else 'union',split='training',index=index)
                row['id']=f'train-{index:02}-'+s.digest(row)[:12];train.append(row)
    free=[];controlled=[]
    for ci,oldcontext in enumerate(heldout):
        c={**oldcontext,'native_context_id':98135200+ci};contexts.append(c);host[c['id']]=dict(labels=heldgold[c['id']]['labels'])
        for qi,users in enumerate((['u02'],['u00','u02'],['u00'],['u00','u01'])):
            for repeat in range(2):
                row=dict(context_id=c['id'],users=users,seed=981351201+len(free),split='new_composition' if qi<2 else 'regression',family='single_user' if len(users)==1 else 'union',repeat=repeat)
                row['id']='free-'+s.digest(row);free.append(row)
            if qi<2:
                for width in (16,4):
                    row=dict(context_id=c['id'],users=users,width=width,metadata_error=False,
                        variable=('categories','labels')[width==4],seed=981351301+len(controlled),
                        split='controlled_heldout',family='single_user' if len(users)==1 else 'union')
                    row['id']='controlled-'+s.digest(row);controlled.append(row)
    assert len(train)==32 and sum(r['metadata_error'] for r in train)==8 and len(free)==32 and len(controlled)==16
    assert not set(g for c in contexts[:8] for g in c['group_ids'])&set(g for c in contexts[8:] for g in c['group_ids'])
    for name,value in [('PUBLIC.json',contexts),('HOST_GOLD.json',host),('TRAIN_PLAN.json',train),('FREE_PLAN.json',free),('CONTROLLED_PLAN.json',controlled)]:s.write(s.ROOT/'inputs'/name,value)
    template=s.read(s.SOURCE/'prepared/NATIVE_TEMPLATE.json');s.write(s.ROOT/'inputs/NATIVE_TEMPLATE.json',template)
    renderer=s.stack().native.renderer();tools=json.loads(template['tools_ordered_json']);prompts={}
    for row in train+free+controlled:
        context=next(c for c in contexts if c['id']==row['context_id']);view={**context,'query_users':row['users']}
        prompt=s.stack().prior.prompt(view,row['family'])
        ids=renderer.render([template['system'],{'role':'user','content':prompt}],tools=tools,add_generation_prompt=True).token_ids
        if len(ids)+2048>8192:raise ValueError('initial prefix budget')
        prompts[row['id']]=dict(prompt=prompt,token_ids=ids)
    s.write(s.ROOT/'inputs/PROMPTS.json',prompts)
    s.write(s.ROOT/'inputs/DATA_PROVENANCE.json',dict(source_sha256={str(p):s.sha(p) for p in sources},
        selected_training_groups=ordered[:128],excluded_groups=sorted(excluded),eligible_training_groups=len(pool),
        selection='label-independent hash rank on raw historical root-training groups',readout_groups=64,
        readout_research_exposed=True,pretraining_overlap_unknown=True,dataset_license='unknown',seed_scan='981351xxx no preexisting matches before source creation'))
    print(dict(training=32,free_per_policy=32,controlled_per_policy=16,eligible_groups=len(pool)))

def seal():
    inherited=s.read(s.ROOT.parent/'root-supplied-map-reducer-v1/READY.json')
    source=dict(inherited['source_sha256']);inputs=dict(inherited['input_sha256'])
    metrics=s.ROOT.parent/'root-example-map-visibility-v1/metrics.py';source[str(metrics)]=s.sha(metrics)
    design=s.ROOT.parent.parent/'ideas/2026-09-09-corrective-reduction-sft-design.md';inputs[str(design)]=s.sha(design)
    # This carries the already authenticated byte-identical archived supervisor mapping.
    for p in s.ROOT.glob('*.py'):source[str(p)]=s.sha(p)
    for p in s.ROOT.glob('*.md'):source[str(p)]=s.sha(p)
    for p in (s.ROOT/'inputs').glob('*.json'):inputs[str(p)]=s.sha(p)
    for p in (s.RUNTIME/'LIFECYCLE_READY_V2.json',s.RUNTIME/'credential_preflight.py',s.ROOT/'CPU_TESTS.json'):
        inputs[str(p)]=s.sha(p)
    source.update(s.read(s.RUNTIME/'LIFECYCLE_READY_V2.json')['source_sha256'])
    for p,h in {**source,**inputs}.items():
        if s.sha(p)!=h:raise ValueError('source closure drift '+p)
    value=dict(status='CPU_READY_FOR_MAIN_ACCEPTANCE',source_sha256=source,input_sha256=inputs,
        master_seed=s.MASTER,root_start_sha256=s.START_SHA,child_sha256=s.CHILD_SHA,examples=32,gate_first=8,
        arms=s.ARMS,updates=4,free_readout=96,controlled_readout=48,outer_seconds=7200,work_seconds=6900,cleanup_seconds=180,
        controlled_source_acquisitions=40,training_actual_child_calls=80,training_authored_root_calls=152,
        common_prompt='inputs/PROMPTS_ACCURATE.json',design_amendment='DESIGN_AMENDMENT.md',
        argv=[str(s.NATIVE),str(s.ROOT/'owner.py'),'run','--output',str(s.ATTEMPT)],
        qualification='CPU native token/rendering plus focused contracts; no actual model/corpus/optimizer qualification yet',gpu_calls=0,prepared_epoch=time.time())
    value['identity']=s.digest(value);s.write(s.ROOT/'READY.json',value);print(s.sha(s.ROOT/'READY.json'))

def accurate_prompts():
    previous=s.read(s.ROOT/'inputs/PROMPTS.json');template=s.read(s.ROOT/'inputs/NATIVE_TEMPLATE.json')
    renderer=s.stack().native.renderer();tools=json.loads(template['tools_ordered_json']);result={}
    for key,value in previous.items():
        old='Each has id, synthetic user metadata, and original question text.'
        if value['prompt'].count(old)!=1 or value['prompt'].count('No source semantic labels are present.')!=1:raise ValueError('common prompt amendment exact source anchors')
        prompt=value['prompt'].replace(old,'Each has exactly the fields id, user, and text: a record ID, user identifier, and original question text.').replace('No source semantic labels are present.','The records.json and context.txt files contain no category labels. Any category maps returned by children or displayed in tool observations are predictions, not dataset labels.')
        ids=renderer.render([template['system'],{'role':'user','content':prompt}],tools=tools,add_generation_prompt=True).token_ids
        if len(ids)+2048>8192:raise ValueError('accurate initial prefix budget')
        result[key]=dict(prompt=prompt,token_ids=ids)
    s.write(s.ROOT/'inputs/PROMPTS_ACCURATE.json',result)
    print({'accurate_prompts':len(result),'original_prompts_retained':True})

def qualify():
    import ast
    commands=[(s.NATIVE,['test_focused','test_native_cpu','test_owner_cpu']),(s.TRAIN,['test_learning_cpu'])]
    results=[]
    for python,modules in commands:
        argv=[str(python),'-m','unittest','-v',*modules];started=time.time()
        result=subprocess.run(argv,cwd=s.ROOT,capture_output=True,text=True,timeout=60,env={**os.environ,'CUDA_VISIBLE_DEVICES':'','PYTHONDONTWRITEBYTECODE':'1','OMP_NUM_THREADS':'2'})
        results.append(dict(argv=argv,returncode=result.returncode,stdout=result.stdout,stderr=result.stderr,elapsed_seconds=time.time()-started))
    for path in s.ROOT.glob('*.py'):ast.parse(path.read_text(),filename=str(path))
    value=dict(commands=results,passed=all(r['returncode']==0 for r in results),gpu_calls=0,service_calls=0,container_calls=0,
        source_sha256={str(p):s.sha(p) for p in s.ROOT.glob('*.py')},scope='13 native/contract plus2 tiny CPU tensor tests; no actual teacher corpus or model optimizer yet')
    s.write(s.ROOT/'CPU_TESTS.json',value)
    if not value['passed']:raise ValueError('focused qualification failed; preserve CPU_TESTS')
    print({'passed':True,'cpu_tests_sha256':s.sha(s.ROOT/'CPU_TESTS.json')})

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('command',choices=('inputs','accurate-prompts','qualify','seal','verify'));a=p.parse_args()
    if a.command=='inputs':prepare()
    elif a.command=='seal':seal()
    elif a.command=='accurate-prompts':accurate_prompts()
    elif a.command=='qualify':qualify()
    else:print(s.verify()['identity'])
