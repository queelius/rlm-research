"""Approved one-time320-group selection and180 native task prefixes; CPU only."""
import asyncio
from collections import Counter
from datetime import datetime,timezone
import hashlib
import json
import qs_study as s

def inventory():
    proof=s.read(s.ss.ROOT/'inputs/PROVENANCE.json');base=set(proof['pool_ids'])
    if len(base)!=2000:raise ValueError('pinned scale pool')
    allocator=s.load('qs_qualified_group_inventory',s.CT/'prepare.py',s.ss.ct_ready['source_sha256'][str(s.CT/'prepare.py')],{'ct_study':s.ss.ct,'ct_protocol':s.ss.protocol()})
    qualifier=s.load('qs_qualified_collision_inventory',s.CT/'qualify_inventory.py',s.ss.ct_ready['source_sha256'][str(s.CT/'qualify_inventory.py')],{'ct_study':s.ss.ct})
    current=set();used_seeds=set();public_ids=set();native_ids=set();pins={str(s.ss.ROOT/'inputs/PROVENANCE.json'):s.sha(s.ss.ROOT/'inputs/PROVENANCE.json')};rows=[]
    paths=set()
    for pattern in ('root-*/inputs/PUBLIC.json','root-*/inputs/GROUPS.json','root-*/inputs/TASKS.json','*/inputs/*PLAN*.json'):paths.update(s.SIDE.glob(pattern))
    for path in sorted(paths):
        if path.parent.parent==s.ROOT or path.parent.parent.name=='root-broad-curriculum-v1':continue
        value=s.read(path);pins[str(path)]=s.sha(path)
        if path.name in ('PUBLIC.json','GROUPS.json','TASKS.json'):
            groupids=allocator.positive_groups(value);current.update(groupids);rows.append(dict(path=str(path),sha256=s.sha(path),positive_group_count=len(groupids),basis='named selected/prepared root manifest including accepted and not-yet-executed selections'))
        used_seeds.update(allocator.seeds(value));public_ids.update(qualifier.collect(value,'id'));native_ids.update(qualifier.collect(value,'native_context_id'));native_ids.update(qualifier.collect(value,'context_window_id'))
    eligible=base-current
    if len(eligible)<320:raise ValueError('insufficient root-inventory-new groups; no substitution')
    source_path=s.SIDE/'trec-leaf-sft-v1/source/data.py';pin=s.cf_ready['source_sha256'].get(str(source_path)) or s.cf_ready['input_sha256'][str(source_path)]
    source=s.load('qs_actual_trec_source',source_path,pin);pins[str(source_path)]=pin
    pool=[r for r in source.load_partitions()['train'] if r['group_id'] in eligible]
    if len(pool)!=len(eligible) or len({r['group_id'] for r in pool})!=len(pool):raise ValueError('actual train group mapping')
    return pool,dict(created_utc=datetime.now(timezone.utc).isoformat(),base_pool=2000,eligible=len(pool),eligible_group_ids=sorted(eligible),current_excluded_group_ids=sorted(current),named_manifest_rows=rows,source_sha256=pins,selection_uses_gold_or_length=False,broad_candidate_catalog_not_reclassified_as_execution=True,source_exposure='TREC train; c32 optimizer and prepared catalog exposed; root-new under pinned named actual/accepted selection inventory'),used_seeds,public_ids,native_ids

def build(pool):
    ordered=sorted(pool,key=lambda x:(s.digest([s.NAMESPACE,'source',x['group_id']]),x['group_id']))[:320]
    if len(ordered)!=320:raise ValueError('exact320 required')
    contexts=[];groups=[];host={};all_rows=[];by_split={'train':[],'dev':[],'protected':[]}
    old=s.load('qs_qualified_layouts',s.OLD/'od_protocol.py',s.cf_ready['source_sha256'][str(s.OLD/'od_protocol.py')],{'od_study':s})
    for ci in range(20):
        split,j=('train',ci) if ci<8 else ('dev',ci-8) if ci<12 else ('protected',ci-12)
        cid=f'question-sensitive-sft-{split}-{j:02}';members=sorted(ordered[ci*16:ci*16+16],key=lambda x:(s.digest([s.NAMESPACE,'order',split,j,x['group_id']]),x['group_id']))
        records=[];labels={}
        for i,row in enumerate(members):
            gid=row['group_id'];identifier='q'+s.digest([s.NAMESPACE,'record',gid])[:12]
            records.append(dict(id=identifier,user=f'u{i%4}',text=row['question'],weight=1+int(s.digest([s.NAMESPACE,'weight',gid])[:8],16)%7));labels[identifier]=row['gold']
        context=dict(id=cid,index=ci,split=split,stratum='new_process_'+split,size=16,records=records,text=''.join(json.dumps(r,sort_keys=True)+'\n' for r in records),native_context_id=986731000+ci);contexts.append(context)
        groups.append(dict(id=cid,split=split,group_ids=[r['group_id'] for r in members],source_partition='train',child_training_exposed=True,prepared_catalog_exposed=True,source_rows=[{k:r[k] for k in ('group_id','source_path','source_line_1based')} for r in members]));host[cid]=dict(labels=labels,answers={})
        for spec in s.problem.specs(split,j):
            layout=int(s.digest([s.NAMESPACE,'style',split,j,spec['slot']])[:8],16)%4
            seed=int(s.digest([s.NAMESPACE,'capture' if split=='train' else 'readout',split,j,spec['slot']])[:8],16)%(2**31)
            row=dict(context_id=cid,parent_id=cid,context_window_id=context['native_context_id'],task_name=cid+':'+spec['slot'],family=spec['slot'],split=split,namespace=s.NAMESPACE,seed=seed,width=16,metadata_error=False,names=old.LAYOUTS[layout],layout=layout,template=0,role='native',evidence='raw',repeat=0,arm='typed',temperature=.5,client_path='train',**spec)
            row['question']=s.problem.question(row);row['id']=s.digest(row);all_rows.append(row);by_split[split].append(row)
            value=s.answer(records,labels,row)
            if value!=s.problem.enumerated_answer(records,labels,row):raise ValueError('independent truth mismatch')
            host[cid]['answers'][row['family']]=value
    dispatch=lambda rows:sorted(rows,key=lambda r:s.digest([s.NAMESPACE,'dispatch',r['split'],r['context_id'],r['slot']]))
    train=dispatch(by_split['train']);free=dispatch(by_split['protected']);dev=dispatch([r for r in by_split['dev'] if r['slot'] in ('M1','M2')])
    gates=[next(r for r in train if r['context_id']==f'question-sensitive-sft-train-{j:02}' and r['slot']==slot) for j,slot in enumerate(('T1','M1','J1','P1','P2','P3'))]
    baseline={}
    for split in by_split:
        for panel in ('all','primitive','composition'):
            selected=[r for r in by_split[split] if panel=='all' or (r['slot'].startswith('P'))==(panel=='primitive')];counts=Counter(host[r['context_id']]['answers'][r['family']] for r in selected)
            baseline[split+':'+panel]=dict(planned=len(selected),histogram={str(k):v for k,v in sorted(counts.items())},zero=counts[0],best_constant=max(counts.values()))
    policies=sorted(('unchanged','sft6'),key=lambda arm:s.digest([s.NAMESPACE,'policy-order',arm]))
    full=[dict(policy=arm,panel=panel,coordinate=r,available=False,reward=None) for panel,rows in [('dev',dev),('protected',free)] for arm in policies for r in rows]
    return dict(values={'PUBLIC.json':contexts,'GROUPS.json':groups,'HOST_GOLD.json':host,'TRAIN_PLAN.json':train,'FREE_PLAN.json':free,'DEV_PLAN.json':dev,'ALL_SPECS.json':all_rows,'GATE_PLAN.json':gates,'BASELINES.json':baseline,'EVALUATION_PLAN.json':dict(full=full,first_action=[],planned_full=160,policy_order=policies,outer_seconds=8100,owned_seconds=8070,work_seconds=7920,protected=144,development=16,training=72,no_retry=True),'START_BINDING.json':dict(decision='MAIN_APPROVED_START',selected=s.starting_policy(),base_binding=s.cf.ph.binding(),starting_policy_is_fixed24=True)},selected=[r['group_id'] for r in ordered])

def main():
    if (s.ROOT/'inputs').exists():raise FileExistsError('immutable one-time allocation; no reroll')
    pool,proof,used,existing_ids,existing_native=inventory();built=build(pool);values=built['values'];rows=values['ALL_SPECS.json']
    proposed={s.SEED,*[r['seed'] for r in rows]};ids={r['id'] for c in values['PUBLIC.json'] for r in c['records']};nativeids={c['native_context_id'] for c in values['PUBLIC.json']}
    if len(ids)!=320 or len(nativeids)!=20 or ids&existing_ids or nativeids&existing_native or proposed&used or len({r['seed'] for r in rows})!=180:raise ValueError('ID/seed collision, no automatic replacement')
    class Memory:
        def __init__(self):self.files={}
        async def write(self,name,data):self.files[name]=data
    async def files(task):
        mem=Memory();await task.setup(None,mem);return mem.files
    prompts={};checks=[];contexts={c['id']:c for c in values['PUBLIC.json']}
    for row in rows:
        task=s.make_task(contexts[row['context_id']],row,0);other=s.make_task(contexts[row['context_id']],row,999999);prefix=s.qnative().first_prefix(task);a=asyncio.run(files(task));b=asyncio.run(files(other))
        if a!=b or prefix!=s.qnative().first_prefix(other) or len(prefix)+2048>8192:raise ValueError('native/private-gold/budget admission; no reranking')
        if set(a)!={'records.json','context.txt','query.txt','batch_contract.py'} or json.loads(a['records.json'])!=contexts[row['context_id']]['records'] or a['query.txt']!=row['question'].encode():raise ValueError('exact public interface')
        prompts[row['id']]=dict(prompt=task.data.prompt,plain_query=row['question'],token_ids=prefix);checks.append(dict(id=row['id'],prefix_tokens=len(prefix),gold_independent=True,exact_four_files=True,files_sha256={k:hashlib.sha256(v).hexdigest() for k,v in a.items()}))
    proof.update(selected_group_sequence=built['selected'],selected_count=320,proposed_seed_values=sorted(proposed),seed_collisions=[],public_id_collisions=[],native_id_collisions=[],unique_public_ids=320,unique_native_ids=20)
    values.update({'PROVENANCE.json':proof,'PROMPTS_ACCURATE.json':prompts,'NATIVE_TEMPLATE.json':s.read(s.CF/'inputs/NATIVE_TEMPLATE.json')})
    for name,value in values.items():s.write(s.ROOT/'inputs'/name,value)
    s.write(s.ROOT/'CPU_INPUT_NATIVE.json',dict(rows=checks,contexts=20,groups=320,training=72,readout=160,max_prefix=max(x['prefix_tokens'] for x in checks),scientific_calls=0))
    print(dict(eligible=proof['eligible'],selected=320,contexts=20,native_tasks=len(rows),max_prefix=max(x['prefix_tokens'] for x in checks),policies=values['EVALUATION_PLAN.json']['policy_order']))
if __name__=='__main__':main()
