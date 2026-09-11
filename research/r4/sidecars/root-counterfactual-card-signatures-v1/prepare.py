"""Freeze exact GATE selection, coherent variant files, all96 native prefixes; no new selection."""
import asyncio
from collections import Counter
import hashlib
import json
import cf_study as s

class Memory:
    def __init__(self):self.files={}
    async def write(self,name,data):self.files[name]=data
async def files(task):
    m=Memory();await task.setup(None,m);return m.files
def numbers(value,needle):
    if isinstance(value,dict):
        for key,item in value.items():
            if needle in key and type(item)is int:yield item
            yield from numbers(item,needle)
    elif isinstance(value,list):
        for item in value:yield from numbers(item,needle)

def main():
    if (s.ROOT/'inputs').exists():raise FileExistsError('immutable input build already exists')
    if s.sha(s.GATE)!=s.GATE_SHA:raise ValueError('approved GATE changed')
    if s.sha(s.ROOT/'CARD.txt')!='c4afc11d1e1aa16e2cf5ca8809ea4e97e5e9ca883bbde75dcd6cb4c7ed165e59':raise ValueError('exact approved card changed')
    gate=s.read(s.GATE)
    for path,pin in gate['source_sha256'].items():s.dose.check(path,pin)
    blocks=gate['rows'];assert len(blocks)==24 and gate['summary']['all_four_pair_separated']==24
    old_public=s.read(s.CT/'inputs/PUBLIC.json');old_host=s.read(s.CT/'inputs/HOST_GOLD.json');old_prompts=s.read(s.CT/'inputs/PROMPTS_ACCURATE.json')
    inventory={};used=set();native_ids=set()
    for p in sorted(s.SIDE.glob('*/inputs/*PLAN*.json')):
        if p.parent.parent==s.ROOT:continue
        inventory[str(p)]=s.sha(p);value=s.read(p);used.update(numbers(value,'seed'));native_ids.update(numbers(value,'context_window_id'))
    if used&set(s.SEEDS):raise ValueError('fresh seed collision; no substitution')
    if native_ids&set(range(984921000,984921008)):raise ValueError('counter native context ID collision')
    public=[];host={};variant_ctx={}
    for old in old_public:
        ctx_blocks=[r for r in blocks if r['source_coordinate']['context_id']==old['id']];assert len(ctx_blocks)==3
        changed=ctx_blocks[0]['counterfactual_records'];assert all(r['counterfactual_records']==changed for r in ctx_blocks)
        for orig,new in zip(old['records'],changed):assert {k:v for k,v in orig.items() if k!='weight'}=={k:v for k,v in new.items() if k!='weight'}
        cf={**old,'id':old['id']+'-counterfactual','native_context_id':984921000+old['index'],'records':changed,'text':''.join(json.dumps(r,sort_keys=True)+'\n' for r in changed),'stratum':'exposed_counterfactual_diagnostic'}
        public.extend([old,cf]);host[old['id']]=old_host[old['id']];host[cf['id']]=dict(labels=old_host[old['id']]['labels'],answers={r['source_coordinate']['family']:r['chosen']['gold'] for r in ctx_blocks})
        variant_ctx[(old['id'],'original')]=old;variant_ctx[(old['id'],'counterfactual')]=cf
    rows=[];pairs=[]
    for position,index in enumerate(sorted(range(24),key=lambda i:s.digest([s.NAMESPACE,'dispatch',blocks[i]['source_coordinate']['id']]))):
        g=blocks[index];old=g['source_coordinate'];cells=s.CELLS[position%4:]+s.CELLS[:position%4];ids=[]
        for cell in cells:
            variant,arm=cell.split('_');ctx=variant_ctx[(old['context_id'],variant)];selected=g['chosen'] if variant=='counterfactual' else dict(target=old['target'],target_b=old['target_b'],threshold=5)
            row={**old,'source_coordinate_id':old['id'],'parent_id':old['context_id'],'context_id':ctx['id'],'context_window_id':ctx['native_context_id'],'variant':variant,'card_arm':arm,'cell':cell,'threshold':selected['threshold'],'target':selected['target'],'target_b':selected['target_b'],'seed':s.SEEDS[index],'namespace':s.NAMESPACE,'source_exposure':'root-executed-child-training-catalog-exposed'}
            row['question']=s.problem.question(row);row['task_name']=ctx['id']+':'+row['family'];row.pop('id');row['id']=s.digest(row);rows.append(row);ids.append(row['id'])
            if variant=='original':assert row['question']==old['question']
        pairs.append(dict(source_coordinate_id=old['id'],parent_id=old['context_id'],seed=s.SEEDS[index],cells=cells,ids=ids))
    assert len({r['id'] for r in rows})==96
    contexts={c['id']:c for c in public};prompts={};checks=[]
    for row in rows:
        ctx=contexts[row['context_id']];truth=s.answer(ctx['records'],host[ctx['id']]['labels'],row)
        if truth!=s.problem.enumerated_answer(ctx['records'],host[ctx['id']]['labels'],row) or truth!=host[ctx['id']]['answers'][row['family']]:raise ValueError('selected host oracle mismatch')
        task=s.make_task(ctx,row,truth);mutated=s.make_task(ctx,{**row,'gold':-999,'labels':{'private':'oracle'}},-999)
        actual=asyncio.run(files(task));native_original=s.o.qnative().make_task(ctx,row['question'],truth,row['id']);expected_files=asyncio.run(files(native_original));prefix=s.o.qnative().first_prefix(task)
        if actual!=expected_files or set(actual)!={'records.json','context.txt','query.txt','batch_contract.py'}:raise ValueError('extra/changed task files')
        if json.loads(actual['records.json'])!=ctx['records'] or [json.loads(line) for line in actual['context.txt'].decode().splitlines()]!=ctx['records']:raise ValueError('weight mirrors differ')
        if actual!=asyncio.run(files(mutated)) or prefix!=s.o.qnative().first_prefix(mutated):raise ValueError('private host gold leaked into task')
        if row['variant']=='original' and row['card_arm']=='U':
            if prefix!=old_prompts[row['source_coordinate_id']]['token_ids'] or task.data.prompt!=old_prompts[row['source_coordinate_id']]['prompt']:raise ValueError('originalU native prefix changed')
        if len(prefix)+2048>8192:raise ValueError('native budget, no crop')
        prompts[row['id']]=dict(prompt=task.data.prompt,plain_query=row['question'],token_ids=prefix)
        checks.append(dict(id=row['id'],variant=row['variant'],arm=row['card_arm'],gold=truth,prefix_tokens=len(prefix),variant_files_correct=True,private_gold_invariant=True,no_extra_task_files=True,files_sha256={k:hashlib.sha256(v).hexdigest() for k,v in actual.items()}))
    for pair in pairs:
        for variant in ('original','counterfactual'):
            cc=[c for c in checks if c['id'] in pair['ids'] and c['variant']==variant];assert len(cc)==2 and cc[0]['files_sha256']==cc[1]['files_sha256']
    values={'PUBLIC.json':public,'HOST_GOLD.json':host,'FREE_PLAN.json':rows,'PAIRS.json':pairs,'PROMPTS_ACCURATE.json':prompts,'NATIVE_TEMPLATE.json':s.read(s.CT/'inputs/NATIVE_TEMPLATE.json'),'GROUPS.json':s.read(s.CT/'inputs/GROUPS.json'),'GATE_SELECTION.json':gate,
        'BASELINES.json':dict(original=dict(zero=4,best_constant=6,planned=24),counterfactual=dict(zero=6,best_constant=6,planned=24),joint=dict(best_constant=1,ties=[0,2,6,9],planned=24)),
        'EVALUATION_PLAN.json':dict(policy_order=['sft24'],full=[dict(policy='sft24',coordinate=r,available=False,reward=None) for r in rows],first_action=[],planned_full=96,parent_clusters=8,paired_blocks=24,cells=s.CELLS,outer_seconds=3600,work_seconds=3450,owned_seconds=3570,practical_availability_gate='counterfactual_P>=counterfactual_U; original direction reported separately'),
        'PROVENANCE.json':dict(gate_sha256=s.GATE_SHA,source_sha256={**gate['source_sha256'],str(s.GATE):s.GATE_SHA,**{str(s.CT/'inputs'/n):s.sha(s.CT/'inputs'/n) for n in ('PUBLIC.json','HOST_GOLD.json','FREE_PLAN.json','PROMPTS_ACCURATE.json','GROUPS.json','NATIVE_TEMPLATE.json')}},seed_inventory_sha256=inventory,fresh_seeds=list(s.SEEDS),seed_collisions=[],counter_native_context_ids=list(range(984921000,984921008)),counter_native_context_id_collisions=[],card_sha256=s.sha(s.ROOT/'CARD.txt'),card_tokens=183,selection_unchanged=True,gold_conditioned_query_selection=True,weights_label_blind=True,exposure='root/child-training/catalog exposed, not new records')}
    for name,value in values.items():s.write(s.ROOT/'inputs'/name,value)
    s.write(s.ROOT/'CPU_INPUT_NATIVE.json',dict(rows=checks,planned=96,blocks=24,parent_clusters=8,max_prefix=max(c['prefix_tokens'] for c in checks),scientific_model_calls=0))
    print(dict(planned=96,contexts=8,variants=16,max_prefix=max(c['prefix_tokens'] for c in checks),seed_inventory=len(inventory),all_selected_host_truths_verified=True))
if __name__=='__main__':main()
