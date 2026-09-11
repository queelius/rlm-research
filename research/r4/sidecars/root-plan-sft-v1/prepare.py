"""Authored targets from native initial rendering, immutable transfer prompts, READY last."""
import argparse
import ast
import json
import os
import random
import subprocess
import time
from pathlib import Path
import study as s

IDEAS=s.SIDE.parent/'ideas'
DECISIONS=[IDEAS/'2026-09-09-root-plan-sft-main-approval.md',IDEAS/'2026-09-09-root-plan-sft-lr-amendment.md',IDEAS/'2026-09-09-context-sensitive-root-next-options.md']


def inputs():
    public=s.read(s.PRIOR/'prepared-v2/PUBLIC.json');byid={c['id']:c for c in public};train=[c for c in public if c['stratum']=='train']
    plan=s.build_plan(s.read(s.PRIOR/'prepared-v2/EVAL_PLAN_FINAL.json'));evalids={r['context_id'] for r in plan}
    groups=lambda cs:{g for c in cs for g in c['group_ids']}
    if (len(train),len(groups(train)),len(evalids),len(groups([byid[c] for c in evalids])))!=(8,384,4,320):raise ValueError('immutable partition sizes')
    if groups(train)&groups([byid[c] for c in evalids]):raise ValueError('train/eval overlap')
    st=s.stack();renderer=st.native.renderer();tokenizer=renderer._tokenizer;template=s.read(s.PRIOR/'prepared-v2/NATIVE_TEMPLATE.json')
    def prefix(text):return renderer.render([template['system'],{'role':'user','content':text}],tools=json.loads(template['tools_ordered_json']),add_generation_prompt=True).token_ids
    corpora={a:[] for a in s.ARMS}
    for context in train:
        for family in ('single_user','global'):
            ids=prefix(st.prior.prompt(context,family))
            canonical=s.program(context,family,'canonical');filtered=s.program(context,family,'filter_first')
            if filtered!=(canonical.replace('selected = records','selected = relevant') if family=='single_user' else canonical):raise ValueError('minimal plan difference')
            for arm in s.ARMS:
                code=s.program(context,family,arm);ast.parse(code)
                target=tokenizer.encode(st.native.tool_action(code),add_special_tokens=False)+[151645]
                row=s.authored_row(context['id']+'-'+family,arm,context['id'],family,ids,target,code)
                if len(row['input_ids'])>8192:raise ValueError('authored target overflow; no truncation')
                corpora[arm].append(row)
    frozen={p['id']:p for p in s.read(s.PRIOR/'prepared-v2/EVAL_PROMPTS.json')};host=s.read(s.PRIOR/'prepared-v2/HOST_GOLD.json');prompts=[]
    for coordinate in plan:
        old=frozen[coordinate['source_coordinate_id']];context=byid[coordinate['context_id']];text=st.prior.prompt(context,coordinate['family'])
        if text!=old['prompt'] or prefix(text)!=old['token_ids']:raise ValueError('transfer native prefix changed')
        task=st.native.task(context,text,host[context['id']]['answers'][coordinate['family']],coordinate['id'])
        prompts.append({**old,'id':coordinate['id'],'source_coordinate_id':coordinate['source_coordinate_id'],'task_hash':task.hash})
    s.validate_prompts(plan,prompts)
    argv=['rg','-l','--glob','*.json','--glob','*.py','--glob','*.md','--glob','!**/outputs/**','--glob','!**/qualification*/**','--glob','!**/prepared*/**','981320[0-9]{3}',str(s.SIDE),str(IDEAS)]
    scan=subprocess.run(argv,capture_output=True,text=True,timeout=30)
    hits=[p for p in scan.stdout.splitlines() if not p.startswith(str(s.ROOT)+'/') and p not in [str(v) for v in DECISIONS]]
    if scan.returncode not in (0,1) or hits:raise ValueError('seed collision: '+repr(hits))
    orders=[]
    for index in range(4):
        order=list(range(16));random.Random(s.TRAIN_SEED+index).shuffle(order);orders.append([corpora['canonical'][i]['id'] for i in order])
    for arm,rows in corpora.items():s.write(s.ROOT/'prepared-v2'/f'ROWS_{arm}.json',rows)
    for name,value in [('PLAN.json',plan),('PROMPTS.json',prompts),('NATIVE_TEMPLATE.json',template)]:s.write(s.ROOT/'prepared-v2'/name,value)
    recipe=dict(schema=s.ROOT.name,master_seed=981320001,training_seed=s.TRAIN_SEED,learning_rate=1e-4,learning_rate_amendment=str(DECISIONS[1]),
      starting_adapter_sha256=s.START_SHA,starting_checkpoint=str(s.START),optimizer='fresh AdamW',weight_decay=0.,gradient_clip=1.,base_dtype='bfloat16',adapter_dtype='float32',rank=8,dropout=0,
      objective='mean over16 authored examples of action-token mean CE; no behavior likelihood/reward',updates=4,examples_per_arm=16,
      training_order=s.training_order(),phase_order=s.phase_order(),work_seconds=2280,inclusive_seconds=2400,outer_seconds=2430,training_seconds_each=360,collection_seconds_each=420,
      planned_readouts=48,selection='two fixed final4 versus unchanged low8; no selection')
    s.write(s.ROOT/'RECIPE_V2.json',recipe)
    s.write(s.ROOT/'INPUTS_V2.json',dict(train_contexts=[c['id'] for c in train],train_groups=384,eval_groups=320,unused_validation_groups=192,
      eval_contexts=sorted(evalids),examples_per_arm=16,targets_per_pass={a:sum(r['target_tokens'] for r in rows) for a,rows in corpora.items()},
      episode_orders=orders,max_train_tokens=max(len(r['input_ids']) for rows in corpora.values() for r in rows),native_prompt_matches=16,
      seed_scan=dict(argv=argv,hits=hits,returncode=scan.returncode),authored_code_executed_on_host=False,gpu_calls=0))
    print(s.read(s.ROOT/'INPUTS_V2.json'),flush=True)


def seal():
    qualification=s.read(s.ROOT/'qualification-002/RESULT.json')
    if qualification['status']!='PASS' or qualification['fake_provider_data_in_training'] or qualification['gpu_calls']:raise ValueError('native authored procedure fixture required')
    argv=[str(s.NATIVE),'-m','pytest','-q',str(s.ROOT/'test_contract.py'),str(s.ROOT/'test_runtime.py')]
    result=subprocess.run(argv,cwd=s.ROOT,env={**os.environ,'CUDA_VISIBLE_DEVICES':'','PYTHONDONTWRITEBYTECODE':'1','OMP_NUM_THREADS':'1'},capture_output=True,text=True,timeout=90)
    s.write(s.ROOT/'CPU_TESTS.json',dict(argv=argv,returncode=result.returncode,stdout=result.stdout,stderr=result.stderr,gpu_calls=0))
    if result.returncode:raise ValueError('focused tests failed')
    old=s.read(s.OLD/'READY.json');source=dict(old['source_sha256']);bound=dict(old['input_sha256'])
    for p in [s.OLD/'READY.json',*DECISIONS,*s.ROOT.glob('*.py'),*s.ROOT.glob('*.md'),s.ROOT/'CPU_TESTS.json']:source[str(p)]=s.sha(p)
    for p in [*list((s.ROOT/'prepared-v2').glob('*.json')),s.ROOT/'INPUTS_V2.json',s.ROOT/'RECIPE_V2.json',*list((s.ROOT/'qualification-002').rglob('*.json'))]:bound[str(p)]=s.sha(p)
    for folder in ('superseded-cpu-001','qualification-001','prepared'):
        for p in (s.ROOT/folder).rglob('*'):
            if p.is_file():bound[str(p)]=s.sha(p)
    for p in (s.ROOT/'INPUTS.json',s.ROOT/'RECIPE.json'):bound[str(p)]=s.sha(p)
    selection=s.read(s.START.parent/'SELECTION.json');state=s.read(s.START/'state.json')
    if selection['step']!=8 or selection['adapter_sha256']!=s.START_SHA:raise ValueError('immutable low start')
    for p in [s.START.parent/'SELECTION.json',s.START.parent/'RESULT.json',s.START/'state.json']:bound[str(p)]=s.sha(p)
    for name,h in state['files_sha256'].items():bound[str(s.START/name)]=h
    for p,h in {**source,**bound}.items():s.check(p,h)
    ready=dict(status='CPU_READY_FOR_MAIN_ACCEPTANCE',source_sha256=source,input_sha256=bound,prepared_epoch=time.time(),gpu_calls=0,
      launch_authorized_by_preparation=False,argv=[str(s.NATIVE),str(s.ROOT/'launch.py'),'run','--output',str(s.ROOT/'outputs/attempt-001')],
      verify_argv=[str(s.NATIVE),str(s.ROOT/'launch.py'),'verify'],parent_outer_seconds=2430,owned_inclusive_seconds=2400,work_seconds=2280,
      training_seconds_each=360,collection_seconds_each=420,planned_readouts=48,phases=s.phase_order(),training_order=s.training_order())
    ready['identity']=s.digest(ready);s.write(s.ROOT/'READY.json',ready);print({'ready_sha256':s.sha(s.ROOT/'READY.json'),'identity':ready['identity']},flush=True)


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('command',choices=('inputs','seal'));a=p.parse_args();(inputs if a.command=='inputs' else seal)()
