"""Freeze prospective rendering/recipe. Runtime corpus is separately sealed before training."""
import argparse
import json
import random
import subprocess
import os
import time
from pathlib import Path
import study as s

def inputs():
    data=s.read(s.ROOT/'DATA_READY.json')
    for p,h in data['data_sha256'].items():s.check(p,h)
    st=s.stack();renderer=st.native.renderer();template=s.read(s.PLAN/'prepared-v2/NATIVE_TEMPLATE.json');tools=json.loads(template['tools_ordered_json'])
    public=s.read(s.ROOT/'data/PUBLIC.json');host=s.read(s.ROOT/'data/HOST_GOLD.json');plan=[];prompts=[]
    for ci,c in enumerate(public):
        for fi,family in enumerate(('single_user','union')):
            for repeat,seed in enumerate((981330201,981330211)):
                coord=dict(context_id=c['id'],context_window_id=st.prior.context_window_id(c),arm='typed',stratum=c['stratum'],family=family,repeat=repeat,seed=seed+ci*2+fi,temperature=.5,client_path='train',helper_partition=c['helper_partition'])
                coord['id']=s.digest(coord);plan.append(coord)
                prompt=st.prior.prompt(c,family);ids=renderer.render([template['system'],{'role':'user','content':prompt}],tools=tools,add_generation_prompt=True).token_ids
                if len(ids)+2048>8192:raise ValueError('full prompt feasibility')
                task=st.native.task(c,prompt,host[c['id']]['answers'][family],coord['id'])
                if task.data.context_window_id!=coord['context_window_id'] or task.data.dataset!=s.ROOT.name:raise ValueError('native task metadata')
                prompts.append(dict(id=coord['id'],prompt=prompt,token_ids=ids,task_hash=task.hash))
    original=s.read(s.PLAN/'prepared-v2/ROWS_canonical.json')
    for row in original:s.plan.validate_authored(row)
    train_public=s.read(s.PRIOR/'prepared-v2/PUBLIC.json');train_groups={g for c in train_public if c['stratum']=='train' for g in c['group_ids']}
    if len(original)!=16 or len(train_groups)!=384 or train_groups&{g for c in public for g in c['group_ids']}:raise ValueError('training-only/eval panel disjoint')
    for name,value in [('EVAL_PLAN_FINAL.json',plan),('EVAL_PROMPTS.json',prompts),('PUBLIC.json',public),('HOST_GOLD.json',host),('ACTION_ROWS.json',original),('NATIVE_TEMPLATE.json',template)]:s.write(s.ROOT/'prepared'/name,value)
    inputs={str(p):s.sha(p) for p in (s.ROOT/'prepared').glob('*.json')}
    recipe=dict(schema=s.ROOT.name,master_seed=981330001,training_seed=s.TRAIN_SEED,learning_rate=1e-4,updates_each=4,
      action_loss='mean16(per-example token mean CE)',terminal_loss='mean16(per-example token mean CE)',terminal_weight={'action_only':0.,'action_terminal':.1},
      action_coefficient='1/(16*n_action_tokens)',terminal_coefficient='0.1/(16*n_terminal_tokens)',coefficient_mass_not_gradient_share=True,
      prepared=str(s.ROOT/'prepared'),input_sha256=inputs,child_interface=dict(kind='typed_batch',pins=st.interface.PINS),
      optimizer='fresh AdamW',weight_decay=0.,clip=1.,rank=8,base_dtype='bfloat16',adapter_dtype='float32',dropout=0,
      phase_order=s.phase_order(),training_order=s.training_order(),selection='unchanged low66c and both fixed4; never validation-selected',
      teacher_examples=16,teacher_source='same16 canonical authored actions; actual native c32 capture once each; strict corpus all16-or-stop',
      training_target='actual observed scalar even if dataset differs; no fake policy likelihood or RL admission',readouts=48,
      capture_seconds=1080,training_seconds_each=480,collection_seconds_each=420,work_seconds=3450,cleanup_seconds=120,owned_seconds=3570,outer_seconds=3600,
      empty_completed_reward=0,unavailable_reward=None,source_panel_sha256=s.sha(s.ROOT/'DATA_READY.json'))
    s.write(s.ROOT/'RECIPE.json',recipe)
    s.write(s.ROOT/'PREPARED.json',dict(data_ready_sha256=s.sha(s.ROOT/'DATA_READY.json'),action_source_sha256=s.sha(s.PLAN/'prepared-v2/ROWS_canonical.json'),action_tokens_per_pass=sum(r['target_tokens'] for r in original),max_eval_prompt_tokens=max(len(p['token_ids']) for p in prompts),readout_contexts=4,coordinates=16,task_hashes=[p['task_hash'] for p in prompts],gpu_calls=0))
    print(s.read(s.ROOT/'PREPARED.json'),flush=True)

def seal():
    old=s.read(s.PLAN/'READY_V2.json');source=dict(old['source_sha256']);bound=dict(old['input_sha256'])
    # Old approvals are historical pins; bind the current prospective clarification separately.
    approval=s.ROOT.parent.parent/'ideas/2026-09-09-next-root-learning-main-approval.md'
    data=s.read(s.ROOT/'DATA_READY.json')
    for p,h in data['source_sha256'].items():
        if p!=str(approval):s.check(p,h);bound[p]=h
    for p,h in data['data_sha256'].items():bound[p]=h
    for p in [*s.ROOT.glob('*.py'),*s.ROOT.glob('*.md'),approval]:source[str(p)]=s.sha(p)
    for p in [s.PLAN/'READY.json',s.PLAN/'READY_V2.json',s.ROOT/'DATA_READY.json',s.ROOT/'DATA_APPROVAL_PIN_AMENDMENT.json',s.ROOT/'RECIPE.json',s.ROOT/'PREPARED.json',s.ROOT/'CPU_TESTS.json',*list((s.ROOT/'prepared').glob('*.json'))]:bound[str(p)]=s.sha(p)
    for p,h in {**source,**bound}.items():s.check(p,h)
    ready=dict(status='CPU_READY_FOR_MAIN_ACCEPTANCE',source_sha256=source,input_sha256=bound,prepared_epoch=time.time(),gpu_calls=0,
      data_ready_sha256=s.sha(s.ROOT/'DATA_READY.json'),approval_normalization_clarification_sha256=s.sha(approval),
      argv=[str(s.NATIVE),str(s.ROOT/'launch.py'),'run','--output',str(s.ROOT/'outputs/attempt-001')],verify_argv=[str(s.NATIVE),str(s.ROOT/'launch.py'),'verify'],
      parent_outer_seconds=3600,owned_inclusive_seconds=3570,work_seconds=3450,cleanup_seconds=120,training_corpus='not yet captured; immutable CORPUS_READY required before any update',
      qualification='existing owned canonical real-native fixture + new stored-native graph/physical-prefix replay + real tinyPEFT objective/mask/save checks; no live model during preparation')
    ready['identity']=s.digest(ready);s.write(s.ROOT/'READY.json',ready);print({'ready_sha256':s.sha(s.ROOT/'READY.json'),'identity':ready['identity']},flush=True)

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('command',choices=('inputs','seal'));a=p.parse_args();(inputs if a.command=='inputs' else seal)()
