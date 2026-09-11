"""Freeze previously selected training data and fresh composition/seed plans, CPU only."""
import argparse
import ast
import json
import os
import subprocess
import time
import joint_study as s

def plans():
    public=s.read(s.BASE_CORRECTIVE/'inputs/PUBLIC.json');train=[];free=[];control=[]
    for ci,c in enumerate(public[:8]):
        for qi,users in enumerate(([f'u{ci%2:02}'],['u00','u01'] if ci%2==0 else ['u02','u03'])):
            index=len(train);row=dict(context_id=c['id'],users=users,width=(16,4)[(ci//2+ci+qi)%2],variable=('label_bank','predictions','collected_labels','category_store')[(ci+qi)%4],metadata_error=False,seed=981361101+index,family='single_user' if qi==0 else 'union',split='training',index=index)
            row['id']='train-'+str(index).zfill(2)+'-'+s.digest(row)[:12];train.append(row)
    for ci,c in enumerate(public[8:]):
        for qi,users in enumerate((['u03'],['u01','u03'])):
            for repeat in range(2):
                row=dict(context_id=c['id'],users=users,seed=981361201+len(free),family='single_user' if qi==0 else 'union',split='heldout_new_composition_research_exposed_data',repeat=repeat)
                row['id']='free-'+s.digest(row)[:16];free.append(row)
            row=dict(context_id=c['id'],users=users,width=(16,4)[(ci+qi)%2],variable=('retained_predictions','acquired_categories')[(ci+qi)%2],metadata_error=False,seed=981361301+len(control),family='single_user' if qi==0 else 'union',split='heldout_controlled_unseen_alias')
            row['id']='controlled-'+s.digest(row)[:16];control.append(row)
    return {'TRAIN_PLAN.json':train,'FREE_PLAN.json':free,'CONTROLLED_PLAN.json':control,'DIAGNOSTIC_PLAN.json':train[:4]}

def prepare():
    values=plans();public=s.read(s.BASE_CORRECTIVE/'inputs/PUBLIC.json')
    for ci,c in enumerate(public):c['native_context_id']=98136200+ci
    for name,value in {**values,'PUBLIC.json':public,'HOST_GOLD.json':s.read(s.BASE_CORRECTIVE/'inputs/HOST_GOLD.json'),'NATIVE_TEMPLATE.json':s.read(s.BASE_CORRECTIVE/'inputs/NATIVE_TEMPLATE.json')}.items():s.write(s.ROOT/'inputs'/name,value)
    renderer=s.stack().native.renderer();template=s.read(s.ROOT/'inputs/NATIVE_TEMPLATE.json');tools=json.loads(template['tools_ordered_json']);prompts={}
    for row in values['TRAIN_PLAN.json']+values['FREE_PLAN.json']+values['CONTROLLED_PLAN.json']:
        context=next(c for c in public if c['id']==row['context_id']);prompt=s.stack().prior.prompt({**context,'query_users':row['users']},row['family'])
        before='Each has id, synthetic user metadata, and original question text.'
        if prompt.count(before)!=1 or prompt.count('No source semantic labels are present.')!=1:raise ValueError('exact common prompt anchors changed')
        prompt=prompt.replace(before,'Each has exactly the fields id, user, and text: a record ID, user identifier, and original question text.').replace('No source semantic labels are present.','The records.json and context.txt files contain no category labels. Any category maps returned by children or displayed in tool observations are predictions, not dataset labels.')
        ids=renderer.render([template['system'],dict(role='user',content=prompt)],tools=tools,add_generation_prompt=True).token_ids
        if len(ids)+2048>8192:raise ValueError('native prompt budget')
        prompts[row['id']]=dict(prompt=prompt,token_ids=ids)
    s.write(s.ROOT/'inputs/PROMPTS_ACCURATE.json',prompts)
    sources=[s.BASE_CORRECTIVE/'inputs'/name for name in ('PUBLIC.json','HOST_GOLD.json','DATA_PROVENANCE.json','TRAIN_PLAN.json','NATIVE_TEMPLATE.json')]
    s.write(s.ROOT/'inputs/DATA_PROVENANCE.json',dict(source_sha256={str(path):s.sha(path) for path in sources},training_groups=[g for c in public[:8] for g in c['group_ids']],heldout_groups=[g for c in public[8:] for g in c['group_ids']],prior_research_exposed=True,selected_before_new_outcomes=True,selection='same8 original label-independent training contexts; no old evaluation traces',fresh_user_compositions=[['u03'],['u01','u03']],gate_members=[r['id'] for r in values['TRAIN_PLAN.json'][:4]],training_diagnostic_members='fixed first4 training states; not heldout',master_seed=s.MASTER))
    s.write(s.ROOT/'inputs/PROTOCOL.json',dict(outer_seconds=5400,work_seconds=5100,owned_seconds=5280,cleanup_reserve_seconds=180,outer_margin_seconds=120,stage_caps=dict(capture=900,gate=180,each_training=600,total_training=1200,readiness_each=180,free_each=480,controlled_each=240,diagnostic_each=120),stage_caps_intersect_shared_work=True,training=16,authored_training_turns=72,training_child_calls=40,controlled_sources=8,controlled_source_child_calls=20,heldout_readout=72,training_diagnostics=12,planned=84,updates=4,role_mass=dict(joint=dict(acquisition=.45,reduction=.50,terminal=.05),reduction_stop=dict(reduction=.95,terminal=.05)),free_generation=dict(temperature=.5,top_p=1,max_tokens=2048,context=8192,per_episode_seconds=180,workers=4),qualification='no actual corpus or model gradients yet'))
    print(dict(training=16,free_per_policy=16,controlled_per_policy=8,diagnostic_per_policy=4))

def qualify():
    results=[]
    for python,modules in ((s.NATIVE,['test_protocol','test_learning','test_native','test_entrypoints']),(s.TRAIN,['test_tensor'])):
        argv=[str(python),'-m','unittest','-v',*modules];started=time.time()
        result=subprocess.run(argv,cwd=s.ROOT,capture_output=True,text=True,timeout=60,env={**os.environ,'CUDA_VISIBLE_DEVICES':'','PYTHONDONTWRITEBYTECODE':'1','OMP_NUM_THREADS':'2'})
        results.append(dict(argv=argv,returncode=result.returncode,stdout=result.stdout,stderr=result.stderr,elapsed_seconds=time.time()-started))
    for path in s.ROOT.glob('*.py'):ast.parse(path.read_text(),filename=str(path))
    value=dict(passed=all(r['returncode']==0 for r in results),commands=results,gpu_calls=0,service_calls=0,container_calls=0,source_sha256={str(p):s.sha(p) for p in s.ROOT.glob('*.py')})
    s.write(s.ROOT/'CPU_TESTS.json',value)
    if not value['passed']:raise ValueError('focused CPU qualification failed; retained report')
    print(s.sha(s.ROOT/'CPU_TESTS.json'))

def seal():
    inherited=s.read(s.BASE_CORRECTIVE/'READY.json');source=dict(inherited['source_sha256']);inputs=dict(inherited['input_sha256'])
    source.update({str(p):s.sha(p) for p in s.ROOT.glob('*.py')});source.update({str(p):s.sha(p) for p in s.ROOT.glob('*.md')})
    inputs.update({str(p):s.sha(p) for p in (s.ROOT/'inputs').glob('*.json')})
    for path in (s.ROOT/'CPU_TESTS.json',s.BASE_CORRECTIVE/'READY.json',s.ROOT.parent.parent/'ideas/2026-09-09-joint-acquisition-reduction-sft-design.md'):inputs[str(path)]=s.sha(path)
    for path,pin in {**source,**inputs}.items():
        if s.sha(path)!=pin:raise ValueError('source closure changed '+path)
    if not s.read(s.ROOT/'CPU_TESTS.json')['passed']:raise ValueError('focused CPU tests required')
    value=dict(status='CPU_READY_FOR_MAIN_ACCEPTANCE',source_sha256=source,input_sha256=inputs,protocol=s.read(s.ROOT/'inputs/PROTOCOL.json'),root_start_sha256=s.START_SHA,child_sha256=s.CHILD_SHA,master_seed=s.MASTER,argv=[str(s.NATIVE),str(s.ROOT/'owner.py'),'run','--output',str(s.ATTEMPT)],gpu_calls=0,prepared_epoch=time.time())
    value['identity']=s.digest(value);s.write(s.ROOT/'READY.json',value);print(s.sha(s.ROOT/'READY.json'))

if __name__=='__main__':
    ap=argparse.ArgumentParser();ap.add_argument('command',choices=('inputs','qualify','seal','verify'));args=ap.parse_args()
    if args.command=='inputs':prepare()
    elif args.command=='qualify':qualify()
    elif args.command=='seal':seal()
    else:print(s.verify()['identity'])
