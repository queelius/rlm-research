"""Freeze all24 composed blocks paired U/P; never inspect/select new outcomes."""
import asyncio
from collections import Counter
import hashlib
import ph_study as s

def seeds(value):
    if isinstance(value,dict):
        for key,item in value.items():
            if 'seed' in key.lower() and type(item)is int:yield item
            yield from seeds(item)
    elif isinstance(value,list):
        for item in value:yield from seeds(item)

class Memory:
    def __init__(self):self.files={}
    async def write(self,name,data):self.files[name]=data
async def files(task):
    memory=Memory();await task.setup(None,memory);return memory.files

def main():
    if (s.ROOT/'inputs').exists():raise FileExistsError('no input replacement or reselection')
    card_tokens=len(s.o.qnative().stack().native.renderer()._tokenizer.encode(s.card(),add_special_tokens=False))
    if not 0<card_tokens<=250:raise ValueError('MAIN card amendment required; no truncation')
    blocks=sorted([r for r in s.read(s.CT/'inputs/FREE_PLAN.json') if r['panel']=='composition'],key=lambda r:(r['context_id'],('threshold_users','maximum_weight','conditional_weight').index(r['operator'])))
    if len(blocks)!=24 or len({r['context_id'] for r in blocks})!=8:raise ValueError('all24 composed blocks required')
    inventory={};used=set()
    for path in sorted(s.SIDE.glob('*/inputs/*PLAN*.json')):
        if path.parent.parent==s.ROOT:continue
        inventory[str(path)]=s.sha(path);used.update(seeds(s.read(path)))
    if used&set(s.SEEDS):raise ValueError('fresh paired seed collision; no substitution')
    public=s.read(s.CT/'inputs/PUBLIC.json');contexts={c['id']:c for c in public};gold=s.read(s.CT/'inputs/HOST_GOLD.json');oldprompts=s.read(s.CT/'inputs/PROMPTS_ACCURATE.json')
    rows=[];pairs=[]
    for position,index in enumerate(sorted(range(24),key=lambda i:s.digest([s.NAMESPACE,'dispatch',blocks[i]['id']]))):
        old=blocks[index];first='U' if position%2==0 else 'P';ids=[]
        for arm in (first,'P' if first=='U' else 'U'):
            row={**old,'source_coordinate_id':old['id'],'card_arm':arm,'seed':s.SEEDS[index],'namespace':s.NAMESPACE,'source_exposure':'completed-composition-and-task-spec-child-training-catalog-exposed'}
            row.pop('id');row['id']=s.digest(row);rows.append(row);ids.append(row['id'])
        pairs.append(dict(source_coordinate_id=old['id'],seed=s.SEEDS[index],order=ids,first_arm=first))
    prompts={};checks=[];truths=[]
    for row in rows:
        context=contexts[row['context_id']];task=s.make_task(context,row,0);changed=s.make_task(context,{**row,'gold':99999,'labels':{'private':'location'}},99999)
        actual=asyncio.run(files(task));prefix=s.o.qnative().first_prefix(task)
        original=s.o.qnative().make_task(context,row['question'],0,row['source_coordinate_id']);basefiles=asyncio.run(files(original))
        if actual!=basefiles or actual!=asyncio.run(files(changed)) or prefix!=s.o.qnative().first_prefix(changed):raise ValueError('original input bytes or private-gold invariance failed')
        expected=oldprompts[row['source_coordinate_id']]['prompt']+('' if row['card_arm']=='U' else '\n\n'+s.card())
        if task.data.prompt!=expected or row['card_arm']=='U' and prefix!=oldprompts[row['source_coordinate_id']]['token_ids']:raise ValueError('original control/card prefix mismatch')
        if len(prefix)+2048>8192:raise ValueError('prefix budget fails; no crop')
        truth=s.answer(context['records'],gold[context['id']]['labels'],row)
        if truth!=gold[context['id']]['answers'][row['family']]:raise ValueError('host source oracle changed')
        if row['card_arm']=='U':truths.append(truth)
        prompts[row['id']]=dict(prompt=task.data.prompt,plain_query=row['question'],token_ids=prefix)
        checks.append(dict(id=row['id'],source_coordinate_id=row['source_coordinate_id'],arm=row['card_arm'],prefix_tokens=len(prefix),gold=truth,original_files_equal=True,private_gold_invariant=True,files_sha256={k:hashlib.sha256(v).hexdigest() for k,v in actual.items()}))
    counts=Counter(truths);baseline=dict(per_arm=24,zero_correct=counts[0],nonzero=24-counts[0],best_constant_correct=max(counts.values()),best_constants=sorted(k for k,v in counts.items() if v==max(counts.values())),histogram={str(k):v for k,v in sorted(counts.items())})
    values={'PUBLIC.json':public,'HOST_GOLD.json':gold,'GROUPS.json':s.read(s.CT/'inputs/GROUPS.json'),'FREE_PLAN.json':rows,'PAIRS.json':pairs,'PROMPTS_ACCURATE.json':prompts,'NATIVE_TEMPLATE.json':s.read(s.CT/'inputs/NATIVE_TEMPLATE.json'),'BASELINES.json':baseline,
            'EVALUATION_PLAN.json':dict(policy_order=['sft24'],full=[dict(policy='sft24',coordinate=r,available=False,reward=None) for r in rows],first_action=[],planned_full=48,parent_clusters=8,paired_blocks=24,outer_seconds=2700,owned_seconds=2670,work_seconds=2550,no_primitive_regression_estimand=True),
            'PROVENANCE.json':dict(source_sha256={str(s.CT/'inputs'/name):s.sha(s.CT/'inputs'/name) for name in ('PUBLIC.json','HOST_GOLD.json','GROUPS.json','FREE_PLAN.json','PROMPTS_ACCURATE.json','NATIVE_TEMPLATE.json')},seed_inventory_sha256=inventory,fresh_seeds=list(s.SEEDS),seed_collisions=[],source_coordinate_ids=[r['id'] for r in blocks],source_selection='all24 fixed composed blocks',no_new_source_groups=True,source_exposure='completed-composition/task-spec and child-training/catalog exposed',card_sha256=s.sha(s.ROOT/'CARD.txt'),card_tokens=card_tokens)}
    for name,value in values.items():s.write(s.ROOT/'inputs'/name,value)
    s.write(s.ROOT/'CPU_INPUT_NATIVE.json',dict(rows=checks,planned=48,blocks=24,parent_clusters=8,card_tokens=card_tokens,card_sha256=s.sha(s.ROOT/'CARD.txt'),max_prefix=max(r['prefix_tokens'] for r in checks),scientific_model_calls=0,baselines=baseline))
    print(dict(planned=48,card_tokens=card_tokens,max_prefix=max(r['prefix_tokens'] for r in checks),baselines=baseline,inventory=len(inventory)))

if __name__=='__main__':main()
