"""CPU-only immutable evaluation allocation and source-derived parameter ordering."""
import argparse
from collections import Counter
import importlib.metadata
import json
import os
from pathlib import Path
import dose_study as s

OPS=('count','distinct','weight')
SUPPORTED={'count':('single','all'),'distinct':('single','union'),'weight':('union','all')}
HELDOUT={'count':'union','distinct':'all','weight':'single'}
TARGETS=('human being','entity','location','numeric value')

def new_contexts(pool):
    selected=sorted(pool,key=lambda r:s.digest([s.MASTER,'source',r['group_id']]))[:64]
    if len(selected)!=64:raise ValueError('exact64 source selection')
    contexts=[];host={};groups=[];rows=[];queries={}
    for ci in range(4):
        cid=f'dose-new-{ci:02d}';members=selected[ci*16:(ci+1)*16]
        ordered=sorted(members,key=lambda r:s.digest([s.MASTER,'order',cid,r['group_id']]))
        users=sorted(('u0','u1','u2','u3'),key=lambda u:s.digest([s.MASTER,'users',cid,u]));records=[];labels={}
        for ri,r in enumerate(ordered):
            identifier='q'+s.digest([s.MASTER,'record',cid,r['group_id']])[:12]
            records.append(dict(id=identifier,user=users[ri%4],text=r['question'],weight=1+int(s.digest([s.MASTER,'weight',r['group_id']])[:8],16)%7));labels[identifier]=r['gold']
        context=dict(id=cid,index=ci,stratum='root_new',size=16,records=records,text=''.join(json.dumps(r,sort_keys=True)+'\n' for r in records),native_context_id=98165200+ci)
        contexts.append(context);groups.append(dict(id=cid,group_ids=[r['group_id'] for r in ordered],source_partition='train',child_training_exposed=True,prepared_catalog_exposed=True));host[cid]=dict(labels=labels,answers={})
        scope_users=sorted(users,key=lambda u:s.digest([s.MASTER,'scope',cid,u]))
        for oi,op in enumerate(OPS):
            for heldout,scope in [(False,SUPPORTED[op][(ci+oi)%2]),(True,HELDOUT[op])]:
                q=dict(operator=op,scope=scope,users=scope_users[:1] if scope=='single' else scope_users[:2] if scope=='union' else sorted(users),target=TARGETS[ci])
                family=op+'-'+scope;name=cid+':'+family
                row=dict(context_id=cid,context_window_id=context['native_context_id'],task_name=name,family=family,heldout_cell=heldout,stratum='root_new',split='root_new',repeat=0,records=16,arm='typed',temperature=.5,client_path='train',role='native',evidence='raw',template=ci,question=s.protocol().question(q,ci),namespace='operator-dose-continuation-20260910-v1',seed=981651101+24+len(rows),**q)
                row['id']=s.digest(row);rows.append(row);queries[row['id']]=q;host[cid]['answers'][family]=s.original().answer(records,labels,q)
    return {'PUBLIC.json':contexts,'GROUPS.json':groups,'HOST_GOLD.json':host,'FREE_PLAN.json':rows,'QUERIES.json':queries}

def inputs():
    s.check(s.INVENTORY,s.INVENTORY_SHA);inventory=s.read(s.INVENTORY)
    for path,pin in inventory['source_sha256'].items():s.check(path,pin)
    source_path=s.SIDE/'trec-leaf-sft-v1/source/data.py'
    receipt=s.read(s.STORE/'operations/2026-09-09-allocation-5780/query-sensitive-source-availability.json')
    source=s.original().load('dose_trec_source',source_path,receipt['source_sha256'][str(source_path)])
    eligible=set(inventory['eligible_group_ids']);pool=[r for r in source.load_partitions()['train'] if r['group_id'] in eligible]
    if len(pool)!=2192:raise ValueError('source pool drift')
    values=new_contexts(pool);newrows=values['FREE_PLAN.json'];oldrows=[]
    oldprompts=s.read(s.OLD/'inputs/PROMPTS_ACCURATE.json');prompts={}
    for index,old in enumerate(s.read(s.OLD/'inputs/FREE_PLAN.json')):
        row={**old,'historical_coordinate_id':old['id'],'namespace':'operator-dose-continuation-20260910-v1','seed':981651101+index,'stratum':'exposed_repeatability'}
        row['id']=s.digest(row);oldrows.append(row);prompts[row['id']]=oldprompts[old['id']]
    ids={r['context_id'] for r in oldrows};values['PUBLIC.json']+= [c for c in s.read(s.OLD/'inputs/PUBLIC.json') if c['id'] in ids]
    values['HOST_GOLD.json'].update({k:v for k,v in s.read(s.OLD/'inputs/HOST_GOLD.json').items() if k in ids})
    values['GROUPS.json'] += [g for g in s.read(s.OLD/'inputs/GROUPS.json') if g['id'] in ids]
    values['FREE_PLAN.json']=sorted(oldrows+newrows,key=lambda r:s.digest([s.MASTER,'dispatch',r['id']]))
    public={c['id']:c for c in values['PUBLIC.json']}
    for row in newrows:
        task=s.original().qnative().make_task(public[row['context_id']],row['question'],0,row['id']);tokens=s.original().qnative().first_prefix(task)
        if len(tokens)+2048>8192:raise ValueError('initial prefix reserve')
        prompts[row['id']]=dict(prompt=task.data.prompt,token_ids=tokens,plain_query=row['question'])
    for row in oldrows:values['QUERIES.json'][row['id']]={k:row[k] for k in ('operator','scope','users','target')}
    values['PROMPTS_ACCURATE.json']=prompts
    training=s.read(s.OLD/'inputs/TRAIN_PLAN.json');probes=[];bodies={}
    for ci in range(12):
        matches=[r for r in training if r['context_id']==f'training-{ci:02d}' and r['operator']==OPS[ci%3] and r['width']==(4 if ci%2==0 else 16)]
        if len(matches)!=1:raise ValueError('fixed diagnostic selector')
        source_row=matches[0];directory=s.OLD/'outputs/attempt-001/capture'/source_row['id'];teacher=s.read(directory/'TEACHER.json');physical=directory/'physical/0001.json';record=s.read(physical)
        if record['authored_kind']!='first_producer' or record['body']['token_ids']!=teacher['turns']['first_producer']['input_ids'][:teacher['turns']['first_producer']['prompt_length']]:raise ValueError('exact teacher first prefix')
        row=dict(source_episode_id=source_row['id'],context_id=source_row['context_id'],operator=source_row['operator'],width=source_row['width'],seed=981651301+ci,source_request_path=str(physical),source_request_sha256=s.sha(physical),teacher_sha256=s.sha(directory/'TEACHER.json'),namespace='operator-dose-teacher-first-v1')
        row['id']=s.digest(row);probes.append(row);bodies[row['id']]=record['body']
    values['TEACHER_DIAGNOSTIC_PLAN.json']=probes;values['TEACHER_FIRST_REQUESTS.json']=bodies
    policies=sorted(('sft6','sft24'),key=lambda a:s.digest([s.MASTER,'policy_order',a]))
    values['EVALUATION_PLAN.json']=dict(policy_order=policies,full=[dict(policy=a,coordinate=r,available=False,reward=None) for a in policies for r in values['FREE_PLAN.json']],first_action=[dict(policy=a,coordinate=r,available=False) for a in policies for r in probes],readout_outer_seconds=6480,training_outer_seconds=4320,combined_outer_seconds=10800,no_partial24_substitution=True)
    baseline={}
    for panel in ('root_new','exposed_repeatability'):
        selected=[r for r in values['FREE_PLAN.json'] if r['stratum']==panel];counts=Counter(s.original().answer(public[r['context_id']]['records'],values['HOST_GOLD.json'][r['context_id']]['labels'],r) for r in selected)
        baseline[panel]=dict(n=len(selected),answer_histogram=dict(counts),zero_correct=counts[0],best_constant_correct=max(counts.values()),best_constants=sorted(k for k,v in counts.items() if v==max(counts.values())))
    values['BASELINES.json']=baseline
    values['PROVENANCE.json']=dict(inventory_path=str(s.INVENTORY),inventory_sha256=s.INVENTORY_SHA,selected_groups=64,pool=2192,source_sha256={**inventory['source_sha256'],str(source_path):s.sha(source_path)},selection_uses_labels_or_outcomes=False,novelty='root-unexecuted only under named inventory; prepared catalog and c32 training exposed; no global unseen claim')
    for name,value in values.items():s.write(s.ROOT/'inputs'/name,value)
    return dict(full=96,first_action=24,baselines=baseline,policy_order=policies)

def mapping():
    import torch
    from transformers import AutoConfig,AutoModelForCausalLM
    from peft import PeftConfig,get_peft_model
    from safetensors import safe_open
    from dose_train import validate_saved
    base=s.base_path();cfg=AutoConfig.from_pretrained(base,local_files_only=True)
    with torch.device('meta'):
        model=AutoModelForCausalLM.from_config(cfg,dtype=torch.bfloat16,attn_implementation='sdpa')
        adapter_config=PeftConfig.from_pretrained(s.START)
        # Match PeftModel.from_pretrained(..., is_trainable=True): saved configs are inference-only.
        adapter_config.inference_mode=False
        model=get_peft_model(model,adapter_config,autocast_adapter_dtype=True)
    names=[dict(name=n,shape=list(p.shape),dtype=str(p.dtype)) for n,p in model.named_parameters() if p.requires_grad]
    if len(names)!=504 or any(p.device.type!='meta' for p in model.parameters()) or any(r['dtype']!='torch.float32' for r in names):raise ValueError('504 FP32 meta-only parameters')
    with safe_open(s.START/'adapter_model.safetensors',framework='pt',device='cpu') as f:
        keys={n['name'].replace('.default.','.') for n in names}
        if keys!=set(f.keys()):raise ValueError('model/adapter tensor key correspondence')
        for n in names:
            if list(f.get_slice(n['name'].replace('.default.','.')).get_shape())!=n['shape']:raise ValueError('adapter shape mapping')
    saved=torch.load(s.START/'optimizer.pt',map_location='cpu',weights_only=True);validate_saved(saved,names,6)
    record=dict(parameters=names,mapping_sha256=s.digest(names),parameter_names_historically_logged=False,method='pinned CPU meta model + PEFT trainable enumeration, same source construction as original parameters() traversal; live exact ordered comparison required',adapter_sha256=s.sha(s.START/'adapter_model.safetensors'),optimizer_sha256=s.sha(s.START/'optimizer.pt'),base_config_sha256=s.sha(base/'config.json'),versions={k:importlib.metadata.version(k) for k in ('torch','transformers','peft','safetensors')},gpu_calls=0,pretrained_base_weights_loaded=False,all_adam_steps=6)
    s.write(s.ROOT/'inputs/PARAMETER_MAP.json',record);print(dict(parameters=len(names),meta_only=True))

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('command',choices=('inputs','mapping'));a=p.parse_args();print(inputs() if a.command=='inputs' else mapping())
