"""Reuse every approved large block; freeze seeds/bytes/native prefixes without outcomes."""
import asyncio
from collections import Counter
import hashlib
import json
from pathlib import Path
import ae_study as s

def walk_seeds(value):
    if isinstance(value,dict):
        for k,v in value.items():
            if k=='seed' and isinstance(v,int):yield v
            yield from walk_seeds(v)
    elif isinstance(value,list):
        for v in value:yield from walk_seeds(v)

class Memory:
    def __init__(self):self.files={}
    async def write(self,name,data):self.files[name]=data
async def files(task):
    memory=Memory();await task.setup(None,memory);return memory.files

def main():
    if (s.ROOT/'inputs').exists():raise FileExistsError('immutable input allocation')
    sources={str(s.SS/'READY.json'):s.SS_READY_SHA}
    originals=s.read(s.SS/'inputs/FREE_PLAN.json');blocks=sorted([r for r in originals if r['records'] in (128,256)],key=lambda r:(r['parent_id'],r['records'],r['operator']))
    if len(blocks)!=16:raise ValueError('all16 large blocks required')
    inventory={};used=set()
    for path in sorted(s.SIDE.glob('*/inputs/*PLAN*.json')):
        if path.parent.parent==s.ROOT:continue
        value=s.read(path);inventory[str(path)]=s.sha(path);used.update(walk_seeds(value))
    if used&set(s.SEEDS):raise ValueError('fresh paired seed collision; no automatic reselection')
    public=s.read(s.SS/'inputs/PUBLIC.json');host=s.read(s.SS/'inputs/HOST_GOLD.json')
    cids={r['context_id'] for r in blocks};public=[c for c in public if c['id'] in cids];contexts={c['id']:c for c in public}
    order=sorted(range(16),key=lambda i:s.digest([s.NAMESPACE,'dispatch',blocks[i]['id']]))
    rows=[];pairs=[]
    for position,i in enumerate(order):
        old=blocks[i];first='B' if position%2==0 else 'C';ids=[]
        for arm in (first,'C' if first=='B' else 'B'):
            row={**old,'namespace':s.NAMESPACE,'seed':s.SEEDS[i],'source_coordinate_id':old['id'],'accumulation_arm':arm,'source_exposure':'scale-exposed','stratum':'exposed'}
            row.pop('id');row['id']=s.digest(row);rows.append(row);ids.append(row['id'])
        pairs.append(dict(source_coordinate_id=old['id'],seed=s.SEEDS[i],order=ids,first_arm=first))
    prompts={};checks=[]
    for row in rows:
        context=contexts[row['context_id']];task=s.make_task(context,row,0);changed=s.make_task(context,row,999999)
        actual=asyncio.run(files(task));original=asyncio.run(files(s.o.qnative().make_task(context,row['question'],0,row['id'])))
        prefix=s.o.qnative().first_prefix(task)
        if actual!=asyncio.run(files(changed)) or prefix!=s.o.qnative().first_prefix(changed):raise ValueError('gold altered native input')
        if set(actual)!=set(original) or any(actual[k]!=original[k] for k in original if k!='batch_contract.py'):raise ValueError('records/query/context bytes changed')
        if len(prefix)+2048>8192:raise ValueError('initial prefix admission fails; no crop')
        truth=s.answer(context['records'],host[context['id']]['labels'],row)
        if truth!=host[context['id']]['answers'][row['family']]:raise ValueError('source truth changed')
        prompts[row['id']]=dict(prompt=task.data.prompt,plain_query=row['question'],token_ids=prefix)
        checks.append(dict(id=row['id'],arm=row['accumulation_arm'],prefix_tokens=len(prefix),gold=truth,gold_independent=True,files_sha256={k:hashlib.sha256(v).hexdigest() for k,v in actual.items()}))
    counts=Counter(x['gold'] for x in checks if x['arm']=='B')
    baselines=dict(per_arm=16,zero_correct=counts[0],best_constant_correct=max(counts.values()),best_constants=sorted(k for k,v in counts.items() if v==max(counts.values())),histogram={str(k):v for k,v in sorted(counts.items())})
    for name in ('FREE_PLAN.json','PUBLIC.json','HOST_GOLD.json','GROUPS.json','NATIVE_TEMPLATE.json','PROVENANCE.json'):
        p=s.SS/'inputs'/name;sources[str(p)]=s.sha(p)
    values={'PUBLIC.json':public,'HOST_GOLD.json':{k:v for k,v in host.items() if k in cids},'GROUPS.json':[g for g in s.read(s.SS/'inputs/GROUPS.json') if g['id'] in cids],
            'FREE_PLAN.json':rows,'PAIRS.json':pairs,'PROMPTS_ACCURATE.json':prompts,'NATIVE_TEMPLATE.json':s.read(s.SS/'inputs/NATIVE_TEMPLATE.json'),'BASELINES.json':baselines,
            'PROVENANCE.json':dict(source_sha256=sources,seed_inventory_sha256=inventory,fresh_seeds=list(s.SEEDS),seed_collisions=[],source_coordinate_ids=[r['id'] for r in blocks],source_selection='all fixed16 large scale blocks',source_exposure='scale-exposed child-training/catalog-exposed',no_new_source_groups=True),
            'EVALUATION_PLAN.json':dict(policy_order=['sft24'],full=[dict(policy='sft24',coordinate=r,available=False,reward=None) for r in rows],first_action=[],planned_full=32,outer_seconds=1800,owned_seconds=1770,work_seconds=1650,parent_clusters=4,paired_blocks=16,no_retry=True)}
    for name,value in values.items():s.write(s.ROOT/'inputs'/name,value)
    s.write(s.ROOT/'CPU_INPUT_NATIVE.json',dict(rows=checks,planned=32,source_blocks=16,parent_clusters=4,max_prefix=max(r['prefix_tokens'] for r in checks),scientific_model_calls=0,baselines=baselines))
    print(dict(planned=32,max_prefix=max(r['prefix_tokens'] for r in checks),baselines=baselines,inventory=len(inventory)))

if __name__=='__main__':main()
