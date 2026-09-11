"""Freeze eight balanced exposed blocks and the complete32 bounded-view factorial."""
import asyncio
from collections import Counter
import hashlib
import itertools
import json
from pathlib import Path

import bv_study as s

def walk_seeds(value):
    if isinstance(value,dict):
        for key,item in value.items():
            if key=='seed' and isinstance(item,int):yield item
            yield from walk_seeds(item)
    elif isinstance(value,list):
        for item in value:yield from walk_seeds(item)

class Memory:
    def __init__(self):self.files={}
    async def write(self,name,data):self.files[name]=data
    async def run(self,*args,**kwargs):raise AssertionError('finalize is not part of input preparation')
async def files(task):
    memory=Memory();await task.setup(None,memory);return memory.files

def select_blocks(rows):
    groups={}
    for row in rows:groups.setdefault((row['parent_id'],row['records']),[]).append(row)
    if len(groups)!=8 or any({r['operator'] for r in value}!={'count','weight_sum'} for value in groups.values()):raise ValueError('expected paired operators for eight parent-size groups')
    keys=sorted(groups);candidates=[]
    for choices in itertools.product((0,1),repeat=8):
        picked=[sorted(groups[key],key=lambda r:r['operator'])[choice] for key,choice in zip(keys,choices)]
        if Counter(r['operator'] for r in picked)!={'count':4,'weight_sum':4}:continue
        ordered=sorted(r['id'] for r in picked);score=int(hashlib.sha256(json.dumps([s.NAMESPACE,ordered],separators=(',',':')).encode()).hexdigest(),16)
        candidates.append((score,ordered,picked))
    return sorted(min(candidates,key=lambda x:(x[0],x[1]))[2],key=lambda r:(r['parent_id'],r['records']))

def main():
    inputs=s.ROOT/'inputs'
    if inputs.exists():raise FileExistsError('immutable bounded-view inputs already exist')
    old_rows=[r for r in s.read(s.base.SS/'inputs/FREE_PLAN.json') if r['records'] in (128,256)]
    blocks=select_blocks(old_rows)
    inventory={};used=set()
    for path in sorted(s.SIDE.glob('*/inputs/*PLAN*.json')):
        if path.parent.parent==s.ROOT:continue
        value=s.read(path);inventory[str(path)]=s.sha(path);used.update(walk_seeds(value))
    if used&set(s.SEEDS):raise ValueError('bounded-view seed collision; no reselection')
    old_public=s.read(s.base.SS/'inputs/PUBLIC.json');old_host=s.read(s.base.SS/'inputs/HOST_GOLD.json')
    context_ids={r['context_id'] for r in blocks};public=[c for c in old_public if c['id'] in context_ids];contexts={c['id']:c for c in public}
    cells=[('B',20000),('C',4096),('B',4096),('C',20000)];rows=[];pairs=[]
    for index,old in enumerate(blocks):
        block_id=s.digest([s.NAMESPACE,'block',old['id']]);order=[]
        for arm,cap in cells[index%4:]+cells[:index%4]:
            row={**old,'namespace':s.NAMESPACE,'seed':s.SEEDS[index],'source_coordinate_id':old['id'],'block_id':block_id,'return_arm':arm,'view_bytes':cap,'source_exposure':'scale-and-accumulation-exposed','stratum':'exposed-mechanism'}
            row.pop('id');row['id']=s.digest(row);rows.append(row);order.append(row['id'])
        pairs.append(dict(block_id=block_id,source_coordinate_id=old['id'],parent_id=old['parent_id'],records=old['records'],operator=old['operator'],seed=s.SEEDS[index],order=order))
    prompts={};checks=[]
    for row in rows:
        context=contexts[row['context_id']];task=s.make_task(context,row,0);changed=s.make_task(context,row,999999)
        actual=asyncio.run(files(task));changed_files=asyncio.run(files(changed));base_files=asyncio.run(files(s.base.make_task(context,{**row,'accumulation_arm':row['return_arm']},0)))
        if actual!=changed_files:raise ValueError('gold altered task files')
        if set(actual)!=set(base_files)|{'.observation_view.json'} or any(actual[name]!=data for name,data in base_files.items()):raise ValueError('bounded view changed task files beyond neutral config')
        config=json.loads(actual['.observation_view.json'])
        if config!={'schema':'bounded-observation-view-config-v1','max_bytes':row['view_bytes']}:raise ValueError('view config differs')
        prefix=s.base.o.qnative().first_prefix(task)
        if prefix!=s.base.o.qnative().first_prefix(changed) or len(prefix)+2048>8192:raise ValueError('initial native prefix/gold admission changed')
        truth=s.base.answer(context['records'],old_host[context['id']]['labels'],row)
        prompts[row['id']]=dict(prompt=task.data.prompt,plain_query=row['question'],token_ids=prefix)
        checks.append(dict(id=row['id'],block_id=row['block_id'],return_arm=row['return_arm'],view_bytes=row['view_bytes'],prefix_tokens=len(prefix),gold=truth,gold_independent=True,files_sha256={name:hashlib.sha256(data).hexdigest() for name,data in actual.items()}))
    gate_root=s.STORE/'analyses/root-acquired-evidence-accumulation-live-2026-09-10'
    gate_files=['REPORT.md','FINAL_SEAL.json','MECHANISMS.json','RAW_DIAGNOSTICS.json','CUMULATIVE_DIAGNOSTIC_CHECK.json','AUDIT_v3.json']
    gate_pins={str(gate_root/name):s.sha(gate_root/name) for name in gate_files}
    growing=['382e8583e3513c36d05d9ab2663f8e2c9ba66c2b81be95b04e967056bce2b7bb','f794db585942e7f798ead2c71a0cb6430341aaeabc5238d36d6f0d22dc2b9fa5','5be192619d7c8ba0471a360aae4929f3579b80a0b778a2e62072063fc4053659','5bc6569f2801c544cf2c528c3fac1474510e45291cd60a4b34ab3a06bf539f1c','64085855cf3ba98a8a1c1384c3f6b6e1d38792a1be42ff9c46e0bb833d841a54','00c398c7bb0ceea719d85c43ac7ddbeab29d8d6aa08903f146c5307bb330b5be']
    mechanism=dict(schema='bounded-view-mechanism-gate-v1',status='satisfied-before-input-freeze',source_sha256=gate_pins,http400_overcontext=13,http400_overcontext_root=10,http400_overcontext_child_unaffected_by_view=3,cumulative_growing_snapshots=6,cumulative_last_snapshot_in_rejected_request=4,executed_accumulated_reductions=0,growing_coordinate_ids=growing,interpretation='root context-pressure mechanism established; efficacy not established')
    source_pins={str(s.base.SS/'inputs/FREE_PLAN.json'):s.sha(s.base.SS/'inputs/FREE_PLAN.json'),str(s.base.SS/'inputs/PUBLIC.json'):s.sha(s.base.SS/'inputs/PUBLIC.json'),str(s.base.SS/'inputs/HOST_GOLD.json'):s.sha(s.base.SS/'inputs/HOST_GOLD.json'),**gate_pins}
    baselines=Counter(x['gold'] for x in checks if x['return_arm']=='B' and x['view_bytes']==20000)
    values={'PUBLIC.json':public,'HOST_GOLD.json':{k:v for k,v in old_host.items() if k in context_ids},'FREE_PLAN.json':rows,'PAIRS.json':pairs,'PROMPTS_ACCURATE.json':prompts,'NATIVE_TEMPLATE.json':s.read(s.base.SS/'inputs/NATIVE_TEMPLATE.json'),'MECHANISM_GATE.json':mechanism,
            'BASELINES.json':dict(per_cell=8,zero_correct=baselines[0],best_constant_correct=max(baselines.values()),histogram={str(k):v for k,v in sorted(baselines.items())}),
            'PROVENANCE.json':dict(source_sha256=source_pins,seed_inventory_sha256=inventory,fresh_seeds=list(s.SEEDS),seed_collisions=[],selection_algorithm='enumerate balanced one-operator-per-parent-size assignments; minimize integer SHA256(namespace, ordered source IDs)',selected_source_coordinate_ids=[r['id'] for r in blocks],source_exposure='scale-and-accumulation-exposed; not fresh replication',no_outcome_filtering=True),
            'EVALUATION_PLAN.json':dict(policy_order=['sft24'],full=[dict(policy='sft24',coordinate=r,available=False,reward=None) for r in rows],planned_full=32,outer_seconds=1800,owned_seconds=1770,work_seconds=1650,parent_clusters=4,paired_blocks=8,no_retry=True)}
    for name,value in values.items():s.write(inputs/name,value)
    s.write(s.ROOT/'CPU_INPUT_NATIVE.json',dict(rows=checks,planned=32,blocks=8,parent_clusters=4,selection=[{k:r[k] for k in ('id','parent_id','records','operator')} for r in blocks],mechanism_gate=mechanism,scientific_model_calls=0))
    print(dict(planned=32,blocks=8,operators=Counter(r['operator'] for r in blocks),inventory=len(inventory)))

if __name__=='__main__':main()
