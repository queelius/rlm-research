"""Freeze all24 composed tasks with matched U/P/J, never select on outcomes."""
import asyncio
import hashlib
import json
from pathlib import Path
import ts_study as s

def seeds(value):
    result=set()
    if isinstance(value,dict):
        for k,v in value.items():
            if 'seed' in k.lower() and type(v)is int:result.add(v)
            result.update(seeds(v))
    elif isinstance(value,list):
        for v in value:result.update(seeds(v))
    return result
def main():
    if (s.ROOT/'inputs').exists():raise FileExistsError('no input replacement or resampling')
    inherited=s.read(s.CT/'inputs/FREE_PLAN.json');chosen=sorted([r for r in inherited if r['panel']=='composition'],key=lambda r:(r['context_id'],('threshold_users','maximum_weight','conditional_weight').index(r['operator'])))
    assert len(chosen)==24 and len({r['context_id'] for r in chosen})==8
    pins={str(p):s.sha(p) for p in s.SIDE.glob('*/inputs/*PLAN*.json') if p.parent.parent!=s.ROOT}
    used=set().union(*(seeds(s.read(p)) for p in pins));assert not used&set(range(s.MASTER,s.MASTER+25)),'fresh seed collision; no substitution'
    public=s.read(s.CT/'inputs/PUBLIC.json');contexts={c['id']:c for c in public};gold=s.read(s.CT/'inputs/HOST_GOLD.json');oldprompts=s.read(s.CT/'inputs/PROMPTS_ACCURATE.json');rows=[];anti=[]
    for index,original in enumerate(chosen):
        context=contexts[original['context_id']];labels=gold[context['id']]['labels'];records=context['records'];answer=s.answer(records,labels,original)
        assert answer==gold[context['id']]['answers'][original['family']]
        alternatives=dict(pooled_a_weight=sum(r['weight'] for r in records if labels[r['id']]==original['target']),pooled_b_weight=sum(r['weight'] for r in records if labels[r['id']]==original['target_b']),a_record_count=sum(labels[r['id']]==original['target'] for r in records))
        alternatives['threshold_on_pooled_a']=int(alternatives['pooled_a_weight']>5)
        anti.append(dict(source_id=original['id'],context_id=original['context_id'],family=original['family'],gold=answer,alternatives=alternatives,equality={k:v==answer for k,v in alternatives.items()},selection_uses_equality=False))
        arms=('U','P','J');cycle=arms[index%3:]+arms[:index%3]
        for slot,arm in enumerate(cycle):
            row={**original,'source_coordinate_id':original['id'],'interface_arm':arm,'seed':s.MASTER+index+1,'namespace':'operator-task-spec-20260910-v1','pair_index':index,'arm_order_slot':slot};row.pop('id');row['id']=s.digest(row);rows.append(row)
    rows.sort(key=lambda r:(s.digest([s.MASTER,'dispatch',r['pair_index']]),r['arm_order_slot']))
    assert len({r['id'] for r in rows})==72 and sum(x['gold']==0 for x in anti)==4
    class Memory:
        def __init__(self):self.files={}
        async def write(self,name,content):self.files[name]=content
    async def files(task):
        memory=Memory();await task.setup(trace=None,runtime=memory);return memory.files
    prompts={};checks=[];by_pair={}
    for row in rows:
        context=contexts[row['context_id']];task=s.make_task(context,row,0);changed=s.make_task(context,{**row,'gold':10001,'labels':{'hidden':'numeric value'}},10001)
        actual=asyncio.run(files(task));other=asyncio.run(files(changed));prefix=s.o.qnative().first_prefix(task)
        assert actual==other and prefix==s.o.qnative().first_prefix(changed)
        assert len(prefix)+2048<=8192,'fixed prefix budget exceeded; no cropping/substitution'
        original=s.o.qnative().make_task(context,row['question'],0,row['source_coordinate_id']);basefiles=asyncio.run(files(original));assert {k:actual[k] for k in basefiles}==basefiles and set(basefiles)=={'records.json','context.txt','query.txt','batch_contract.py'}
        expected=set(basefiles)|({'task.txt'} if row['interface_arm']=='P' else {'task.json'} if row['interface_arm']=='J' else set());assert set(actual)==expected
        if row['interface_arm']=='U':assert prefix==oldprompts[row['source_coordinate_id']]['token_ids'] and task.data.prompt==oldprompts[row['source_coordinate_id']]['prompt']
        by_pair.setdefault(row['pair_index'],{})[row['interface_arm']]=actual
        prompts[row['id']]=dict(prompt=task.data.prompt,plain_query=row['question'],token_ids=prefix)
        checks.append(dict(id=row['id'],source_id=row['source_coordinate_id'],arm=row['interface_arm'],prefix_tokens=len(prefix),files_sha256={k:hashlib.sha256(v).hexdigest() for k,v in actual.items()},original_files_equal=True,private_labels_gold_invariant=True))
    for arms in by_pair.values():
        assert s.task_protocol().prose(json.loads(arms['J']['task.json'])).encode()==arms['P']['task.txt']
    values={'PUBLIC.json':public,'HOST_GOLD.json':gold,'GROUPS.json':s.read(s.CT/'inputs/GROUPS.json'),'FREE_PLAN.json':rows,'PROMPTS_ACCURATE.json':prompts,'NATIVE_TEMPLATE.json':s.read(s.CT/'inputs/NATIVE_TEMPLATE.json'),'ANTI_COINCIDENCE.json':anti,'TASK_SPECS.json':{r['id']:s.task_protocol().spec(r) for r in rows},'EVALUATION_PLAN.json':dict(policy_order=['sft24'],full=[dict(policy='sft24',coordinate=r,available=False,reward=None) for r in rows],first_action=[],planned_full=72,paired_tasks=24,arms=['U','P','J'],outer_seconds=3900,owned_seconds=3870,work_seconds=3720)}
    inputs={str(s.CT/'inputs'/name):s.sha(s.CT/'inputs'/name) for name in ('PUBLIC.json','HOST_GOLD.json','GROUPS.json','FREE_PLAN.json','PROMPTS_ACCURATE.json','NATIVE_TEMPLATE.json')}
    values['PROVENANCE.json']=dict(source_sha256=inputs,seed_inventory_sha256=pins,seed_collisions=[],source_selection='All24 declared composed tasks in8 prior exposed contexts, no primitive efficacy panel, no model/gold/equality filtering',source_coordinate_ids=[r['id'] for r in chosen],master=s.MASTER,source_exposure='completed composition study plus child-training/catalog exposed',new_source_groups=0)
    for name,value in values.items():s.write(s.ROOT/'inputs'/name,value)
    s.write(s.ROOT/'CPU_INPUT_NATIVE.json',dict(rows=checks,planned=72,pairs=24,max_prefix=max(x['prefix_tokens'] for x in checks),all_original_files_identical=True,prose_json_field_equivalence=True,no_model_calls=True,zero_gold_pairs=4,nonzero_gold_pairs=20))
    print(dict(planned=72,pairs=24,max_prefix=max(x['prefix_tokens'] for x in checks),source_selection='all composed',seed_files=len(pins),input_sha256=s.sha(s.ROOT/'inputs/FREE_PLAN.json')))
if __name__=='__main__':main()
