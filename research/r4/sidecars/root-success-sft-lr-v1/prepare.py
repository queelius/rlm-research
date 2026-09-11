"""Reuse sealed corpus, qualify fresh native prompt crosswalk, seal last."""
import argparse
import json
import os
import random
import subprocess
import time
from pathlib import Path
import study as s

DESIGN=s.SIDE.parent/'ideas/2026-09-09-success-sft-learning-rate-design.md'


def inputs():
    ready=s.read(s.OLD/'READY.json')
    s.check(s.OLD/'READY.json','ced16becb584a709d7da0faa122b5343def395168909d52d66eb762fe6ef3a9c')
    # No native teacher re-export: authenticate the already qualified immutable corpus.
    for name in ('EPISODES.json','AUDIT.json'):
        path=s.OLD/'prepared'/name;s.check(path,ready['input_sha256'][str(path)])
    corpus=s.read(s.OLD/'prepared/EPISODES.json');audit=s.read(s.OLD/'prepared/AUDIT.json')
    assert (len(corpus),sum(len(e['turns']) for e in corpus),sum(s.validate_turn(t) for e in corpus for t in e['turns']))==(27,114,15256)
    orders=[]
    for index in range(8):
        order=list(range(27));random.Random(s.TRAIN_SEED+index).shuffle(order)
        orders.append([corpus[i]['episode_id'] for i in order])
    if orders!=audit['episode_orders']:raise ValueError('paired training order differs')
    plan=s.build_plan(s.read(s.PRIOR/'prepared-v2/EVAL_PLAN_FINAL.json'))
    original={p['id']:p for p in s.read(s.PRIOR/'prepared-v2/EVAL_PROMPTS.json')}
    public={c['id']:c for c in s.read(s.PRIOR/'prepared-v2/PUBLIC.json')}
    host=s.read(s.PRIOR/'prepared-v2/HOST_GOLD.json')
    template=s.read(s.PRIOR/'prepared-v2/NATIVE_TEMPLATE.json')
    st=s.stack();renderer=st.native.renderer();prompts=[]
    for coordinate in plan:
        old=original[coordinate['source_coordinate_id']];context=public[coordinate['context_id']]
        text=st.prior.prompt(context,coordinate['family'])
        ids=renderer.render([template['system'],{'role':'user','content':text}],tools=json.loads(template['tools_ordered_json']),add_generation_prompt=True).token_ids
        if ids!=old['token_ids'] or text!=old['prompt']:raise ValueError('native physical prompt changed')
        task=st.native.task(context,text,host[context['id']]['answers'][coordinate['family']],coordinate['id'])
        prompts.append({**old,'id':coordinate['id'],'source_coordinate_id':coordinate['source_coordinate_id'],'task_hash':task.hash})
    s.validate_prompts(plan,prompts)
    argv=['rg','-l','--glob','*.json','--glob','*.py','--glob','*.md','--glob','!**/outputs/**','--glob','!**/qualification*/**','--glob','!**/prepared*/**','981314[0-9]{3}',str(s.SIDE),str(s.SIDE.parent/'ideas')]
    scan=subprocess.run(argv,capture_output=True,text=True,timeout=30)
    hits=[p for p in scan.stdout.splitlines() if not p.startswith(str(s.ROOT)+'/') and p!=str(DESIGN)]
    if scan.returncode not in (0,1) or hits:raise ValueError('fresh seed collision: '+repr(hits))
    for name,value in [('EPISODES.json',corpus),('PLAN.json',plan),('PROMPTS.json',prompts)]:s.write(s.ROOT/'prepared'/name,value)
    if s.sha(s.ROOT/'prepared/EPISODES.json')!=s.sha(s.OLD/'prepared/EPISODES.json'):raise ValueError('corpus bytes differ')
    recipe={**s.read(s.OLD/'RECIPE.json'),'schema':s.ROOT.name,'master_seed':981314001,'learning_rate':1e-4,
      'control_learning_rate':2e-5,'control_adapter_sha256':s.LOW_SHA,'phase_order':s.phase_order(),
      'selection':'existing low fixed8 versus new high fixed8; no checkpoint selection','work_seconds':3180,'inclusive_seconds':3300,'outer_seconds':3330,'paired_readout_episodes':48}
    s.write(s.ROOT/'RECIPE.json',recipe)
    s.write(s.ROOT/'INPUTS.json',{'corpus_source':str(s.OLD/'prepared/EPISODES.json'),'corpus_sha256':s.sha(s.OLD/'prepared/EPISODES.json'),
        'corpus_reexported':False,'episodes':27,'root_turns':114,'targets_per_pass':15256,'total_targets':122048,
        'episode_orders':orders,'native_prompt_matches':24,'shared_training_seed_intentional':981308002,
        'seed_scan':{'argv':argv,'hits':hits,'returncode':scan.returncode},'phase_order':s.phase_order(),'gpu_calls':0})
    print({'prepared':True,'native_prompt_matches':24,'phase_order':s.phase_order(),'gpu_calls':0},flush=True)


def seal():
    argv=[str(s.NATIVE),'-m','pytest','-q',str(s.ROOT/'tests/test_adapter.py')]
    result=subprocess.run(argv,cwd=s.ROOT,env={**os.environ,'CUDA_VISIBLE_DEVICES':'','PYTHONDONTWRITEBYTECODE':'1','OMP_NUM_THREADS':'1'},capture_output=True,text=True,timeout=90)
    report={'argv':argv,'returncode':result.returncode,'stdout':result.stdout,'stderr':result.stderr,'gpu_calls':0}
    s.write(s.ROOT/('CPU_TESTS.json' if result.returncode==0 else 'FAILED_CPU_TESTS.json'),report)
    if result.returncode:raise ValueError('focused tests failed')
    inherited=s.read(s.OLD/'READY.json');source=dict(inherited['source_sha256']);bound=dict(inherited['input_sha256'])
    for p in [s.OLD/'READY.json',DESIGN]:source[str(p)]=s.sha(p)
    for p in list(s.ROOT.glob('*.py'))+list(s.ROOT.glob('*.md'))+list((s.ROOT/'tests').glob('*.py'))+[s.ROOT/'CPU_TESTS.json']:source[str(p)]=s.sha(p)
    for p in list((s.ROOT/'prepared').glob('*.json'))+[s.ROOT/'INPUTS.json',s.ROOT/'RECIPE.json']:bound[str(p)]=s.sha(p)
    lowdir=s.OLD/'outputs/attempt-001/training';selection=s.read(lowdir/'SELECTION.json')
    if selection['step']!=8 or selection['adapter_sha256']!=s.LOW_SHA:raise ValueError('low fixed8 changed')
    checkpoint=Path(selection['checkpoint']);state=s.read(checkpoint/'state.json')
    for p in [lowdir/'SELECTION.json',lowdir/'RESULT.json',checkpoint/'state.json']:bound[str(p)]=s.sha(p)
    for name,h in state['files_sha256'].items():bound[str(checkpoint/name)]=h
    for p,h in {**source,**bound}.items():s.check(p,h)
    ready={'status':'CPU_READY_FOR_MAIN_ACCEPTANCE','source_sha256':source,'input_sha256':bound,
      'prepared_epoch':time.time(),'gpu_calls':0,'launch_authorized_by_preparation':False,
      'argv':[str(s.NATIVE),str(s.ROOT/'launch.py'),'run','--output',str(s.ROOT/'outputs/attempt-001')],
      'verify_argv':[str(s.NATIVE),str(s.ROOT/'launch.py'),'verify'],'parent_outer_seconds':3330,'owned_inclusive_seconds':3300,
      'training_seconds':1200,'work_seconds':3180,'collection_seconds_each':900,'phases':s.phase_order(),'planned_readouts':48}
    ready['identity']=s.digest(ready);s.write(s.ROOT/'READY.json',ready)
    print({'ready_sha256':s.sha(s.ROOT/'READY.json'),'identity':ready['identity'],'source_paths':len(source),'input_paths':len(bound)},flush=True)


if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('command',choices=('inputs','seal'));args=parser.parse_args()
    (inputs if args.command=='inputs' else seal)()
