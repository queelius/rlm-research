"""Immutable nested source allocation; no gold/length/outcome selection."""
import asyncio
from collections import Counter
import hashlib
from pathlib import Path
import json
import ss_study as s

SIZES=(16,128,256)
def build(pool):
    selected=sorted(pool,key=lambda r:s.digest([s.MASTER,'source',r['group_id']]))[:1024]
    if len(selected)!=1024:raise ValueError('1024 unique source groups required')
    contexts=[];parents=[];groups=[];host={};rows=[];queries={}
    for ci in range(4):
        parent=f'scale-state-{ci:02d}';members=sorted(selected[ci*256:(ci+1)*256],key=lambda r:s.digest([s.MASTER,'order',parent,r['group_id']]))
        records=[];labels={}
        for i,source in enumerate(members):
            identifier='q'+s.digest([s.MASTER,'record',parent,source['group_id']])[:12]
            records.append(dict(id=identifier,user=f'u{i%4}',text=source['question'],weight=1+int(s.digest([s.MASTER,'weight',source['group_id']])[:8],16)%7));labels[identifier]=source['gold']
        parents.append(dict(id=parent,group_ids=[r['group_id'] for r in members],source_rows=[{k:r[k] for k in ('group_id','source_path','source_line_1based')} for r in members]))
        for si,size in enumerate(SIZES):
            cid=f'{parent}-{size}';batch=records[:size];context=dict(id=cid,parent_id=parent,index=ci*3+si,stratum='root_new',size=size,records=batch,text=''.join(json.dumps(r,sort_keys=True)+'\n' for r in batch),native_context_id=982617000+ci*3+si)
            contexts.append(context);groups.append(dict(id=cid,parent_id=parent,group_ids=[r['group_id'] for r in members[:size]],source_partition='train',child_training_exposed=True,prepared_catalog_exposed=True));host[cid]=dict(labels={r['id']:labels[r['id']] for r in batch},answers={})
            for oi,spec in enumerate([s.protocol().specs(ci)[0],s.protocol().specs(ci)[2]]):
                row=dict(context_id=cid,parent_id=parent,context_window_id=context['native_context_id'],task_name=cid+':'+spec['operator'],family=spec['operator'],heldout_cell=size>16,stratum='root_new',split='root_new',repeat=0,records=size,arm='typed',temperature=.5,client_path='train',role='native',evidence='raw',namespace='operator-scale-state-20260910-v1',seed=s.MASTER+1+ci*2+oi,**spec)
                row['id']=s.digest(row);rows.append(row);queries[row['id']]=spec
                truth=s.answer(batch,labels,row)
                if truth!=s.protocol().enumerated_answer(batch,labels,row):raise ValueError('independent oracle disagreement')
                host[cid]['answers'][row['family']]=truth
    ordered=sorted(rows,key=lambda r:s.digest([s.MASTER,'dispatch',r['parent_id'],r['records'],r['operator']]))
    baseline={}
    for key in ('all','count','weight_sum','16','128','256'):
        selected_rows=[r for r in rows if key=='all' or r['operator']==key or str(r['records'])==key];counts=Counter(host[r['context_id']]['answers'][r['family']] for r in selected_rows)
        baseline[key]=dict(n=len(selected_rows),histogram={str(k):v for k,v in sorted(counts.items())},zero_correct=counts[0],best_constant_correct=max(counts.values()),best_constants=sorted(k for k,v in counts.items() if v==max(counts.values())))
    return {'PUBLIC.json':contexts,'PARENTS.json':parents,'GROUPS.json':groups,'HOST_GOLD.json':host,'FREE_PLAN.json':ordered,'QUERIES.json':queries,'BASELINES.json':baseline,'EVALUATION_PLAN.json':dict(policy_order=['sft24'],full=[dict(policy='sft24',coordinate=r,available=False,reward=None) for r in ordered],first_action=[],planned_full=24,outer_seconds=2400,owned_seconds=2370,work_seconds=2220,nested_source_clusters=4,paired_across_sizes=True,no_retry=True)}

def main():
    if (s.ROOT/'inputs').exists():raise FileExistsError('no allocation overwrite or resampling')
    proof=s.read(s.CT/'inputs/PROVENANCE.json');excluded={g for c in s.read(s.CT/'inputs/GROUPS.json') for g in c['group_ids']};pool_ids=set(proof['eligible_group_ids'])-excluded
    if len(pool_ids)!=2000 or s.digest(sorted(pool_ids))!='bf77c583123f7dce3ff99826de24265f3af6ed0d902afc0021896ad46b3660e9':raise ValueError('approved pool changed; MAIN amendment required')
    allocator=s.load('scale_prior_inventory',s.CT/'prepare.py',s.ct_ready['source_sha256'][str(s.CT/'prepare.py')],{'ct_study':s.ct,'ct_protocol':s.protocol()})
    current=set();manifest_pins={};used_seeds=set();existing_ids=set();existing_native=set()
    qualifier=s.load('scale_prior_collision',s.CT/'qualify_inventory.py',s.ct_ready['source_sha256'][str(s.CT/'qualify_inventory.py')],{'ct_study':s.ct})
    paths=set()
    for pattern in ('root-*/inputs/PUBLIC.json','root-*/inputs/GROUPS.json','root-*/inputs/TASKS.json','*/inputs/*PLAN*.json'):paths.update(s.SIDE.glob(pattern))
    for path in sorted(paths):
        if path.parent.parent==s.ROOT or path.parent.parent.name=='root-broad-curriculum-v1':continue
        value=s.read(path);manifest_pins[str(path)]=s.sha(path)
        if path.name in ('PUBLIC.json','GROUPS.json','TASKS.json'):current.update(allocator.positive_groups(value))
        used_seeds.update(allocator.seeds(value));existing_ids.update(qualifier.collect(value,'id'));existing_native.update(qualifier.collect(value,'native_context_id'));existing_native.update(qualifier.collect(value,'context_window_id'))
    if pool_ids&current:raise ValueError('new accepted/root exposure changes approved pool; no substitution')
    if {s.MASTER,*range(s.MASTER+1,s.MASTER+25)}&used_seeds:raise ValueError('new seed collision; no substitution')
    source_path=s.SIDE/'trec-leaf-sft-v1/source/data.py';source=s.load('scale_raw_trec',source_path,s.ct_ready['input_sha256'].get(str(source_path)) or s.ct_ready['source_sha256'][str(source_path)])
    pool=[r for r in source.load_partitions()['train'] if r['group_id'] in pool_ids];values=build(pool)
    ranked=sorted(pool_ids,key=lambda gid:s.digest([s.MASTER,'source',gid]))[:1024]
    if s.digest(ranked)!='d52903c9a0f72fc9caa5ff1c83302bc30e1241da9bbad9bee697eb861f594e3d':raise ValueError('preview source sequence changed')
    ids={r['id'] for c in values['PUBLIC.json'] for r in c['records']};nativeids={c['native_context_id'] for c in values['PUBLIC.json']}
    if len(ids)!=1024 or len(nativeids)!=12 or ids&existing_ids or nativeids&existing_native:raise ValueError('public/native identifier collision; no reranking')
    class Memory:
        def __init__(self):self.files={}
        async def write(self,name,data):self.files[name]=data
    async def files(task):
        memory=Memory();await task.setup(None,memory);return memory.files
    prompts={};checks=[];contexts={c['id']:c for c in values['PUBLIC.json']}
    for row in values['FREE_PLAN.json']:
        context=contexts[row['context_id']];task=s.o.qnative().make_task(context,row['question'],0,row['id']);changed=s.o.qnative().make_task(context,row['question'],999999,row['id']);prefix=s.o.qnative().first_prefix(task);a=asyncio.run(files(task));b=asyncio.run(files(changed))
        if a!=b or prefix!=s.o.qnative().first_prefix(changed) or len(prefix)+2048>8192:raise ValueError('native admission; no resampling/cropping')
        if set(a)!={'records.json','context.txt','query.txt','batch_contract.py'} or json.loads(a['records.json'])!=context['records'] or a['query.txt']!=row['question'].encode():raise ValueError('unchanged file-only interface')
        prompts[row['id']]=dict(prompt=task.data.prompt,plain_query=row['question'],token_ids=prefix)
        checks.append(dict(id=row['id'],prefix_tokens=len(prefix),files_sha256={k:hashlib.sha256(v).hexdigest() for k,v in a.items()},gold_independent=True))
    values['PROMPTS_ACCURATE.json']=prompts;values['NATIVE_TEMPLATE.json']=s.read(s.CT/'inputs/NATIVE_TEMPLATE.json')
    values['PROVENANCE.json']=dict(pool_ids=sorted(pool_ids),pool_count=2000,selected_group_sequence=ranked,selected_count=1024,source_sequence_sha256=s.digest(ranked),pool_sha256=s.digest(sorted(pool_ids)),excluded_composition_groups=sorted(excluded),source_sha256={**proof['source_sha256'],**proof['seed_inventory_sha256'],**manifest_pins,str(s.CT/'inputs/PROVENANCE.json'):s.sha(s.CT/'inputs/PROVENANCE.json'),str(s.CT/'inputs/GROUPS.json'):s.sha(s.CT/'inputs/GROUPS.json')},selection_uses_labels_or_length=False,source_novelty='only named root inventory; child training/catalog exposed',unique_public_ids=len(ids),unique_native_ids=len(nativeids),id_collisions=[],seed_collisions=[])
    for name,value in values.items():s.write(s.ROOT/'inputs'/name,value)
    s.write(s.ROOT/'CPU_INPUT_NATIVE.json',dict(rows=checks,planned=24,max_prefix=max(r['prefix_tokens'] for r in checks),source_allocated_once=True,model_calls=0,baselines=values['BASELINES.json']))
    print(dict(planned=24,groups=1024,pool=2000,max_prefix=max(r['prefix_tokens'] for r in checks),baselines=values['BASELINES.json']))
if __name__=='__main__':main()
