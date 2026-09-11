"""Label-blind source allocation and actual native prefix/file qualification, CPU only."""
import asyncio
from collections import Counter
from datetime import datetime,timezone
import hashlib
import json
from pathlib import Path
import re
import unicodedata
import ct_study as s
import ct_protocol as p

def normalized(text):return hashlib.sha256(' '.join(re.findall(r'\w+',unicodedata.normalize('NFKC',text).casefold())).encode()).hexdigest()
def positive_groups(value):
    found=set()
    if isinstance(value,dict):
        for key,item in value.items():
            if key in ('group_id','normalized_group_sha256','question_group_sha256') and isinstance(item,str):found.add(item)
            elif key=='group_ids' and isinstance(item,list):found.update(x for x in item if isinstance(x,str))
            elif key in ('text','question') and isinstance(item,str):found.add(normalized(item))
            elif isinstance(item,(dict,list)):found.update(positive_groups(item))
    elif isinstance(value,list):
        for item in value:found.update(positive_groups(item))
    return found
def seeds(value):
    found=set()
    if isinstance(value,dict):
        for key,item in value.items():
            if key in ('seed','master_seed','sampling_seed') and type(item)==int:found.add(item)
            elif isinstance(item,(dict,list)):found.update(seeds(item))
    elif isinstance(value,list):
        for item in value:found.update(seeds(item))
    return found
def inventory():
    s.dose.check(s.INVENTORY,s.INVENTORY_SHA);old=s.read(s.INVENTORY)
    for path,pin in old['source_sha256'].items():s.dose.check(path,pin)
    exclusions=set();rows=[];source_pins={str(s.INVENTORY):s.INVENTORY_SHA,**old['source_sha256']}
    paths=set()
    for pattern in ('root-*/inputs/PUBLIC.json','root-*/inputs/GROUPS.json','root-*/inputs/TASKS.json'):
        paths.update(s.SIDE.glob(pattern))
    # Broad PUBLIC is a candidate catalog, not a selected root manifest. Its actual execution inventory
    # is already pinned in the2192 receipt; do not turn mere prepared presence into root execution.
    for path in sorted(paths):
        if path.parent.parent==s.ROOT or path.parent.parent.name=='root-broad-curriculum-v1':continue
        value=s.read(path);groups=positive_groups(value);exclusions.update(groups);source_pins[str(path)]=s.sha(path)
        rows.append(dict(path=str(path),sha256=s.sha(path),positive_group_count=len(groups),basis='conservative named selected/prepared experiment input; excludes even unrun selected coordinates'))
    recent=s.TRAINING/'inputs/GROUPS.json';new=set(g for c in s.read(recent) if c['id'].startswith('dose-new-') for g in c['group_ids'])
    if len(new)!=64 or not new<=set(old['eligible_group_ids']):raise ValueError('recent64 source drift')
    exclusions.update(new);eligible=set(old['eligible_group_ids'])-exclusions
    receipt=s.read(s.STORE/'operations/2026-09-09-allocation-5780/query-sensitive-source-availability.json');source=s.SIDE/'trec-leaf-sft-v1/source/data.py'
    data=s.load('composition_pinned_trec_source',source,receipt['source_sha256'][str(source)])
    pool=[r for r in data.load_partitions()['train'] if r['group_id'] in eligible]
    if len(pool)!=len(eligible) or len(pool)<128:raise ValueError('bounded eligible pool')
    seedpaths=sorted(q for q in s.SIDE.glob('*/inputs/*PLAN*.json') if q.parent.parent!=s.ROOT)
    used=set();seedpins={}
    for path in seedpaths:used.update(seeds(s.read(path)));seedpins[str(path)]=s.sha(path)
    proposed={s.MASTER,*range(s.MASTER+1,s.MASTER+49)}
    if proposed&used:raise ValueError('prospective seed collision; stop without automatic replacement')
    return pool,dict(created_utc=datetime.now(timezone.utc).isoformat(),original_inventory=str(s.INVENTORY),original_sha256=s.INVENTORY_SHA,original_eligible=2192,recent_groups64=sorted(new),refreshed_eligible=len(pool),eligible_group_ids=sorted(eligible),excluded_positive_groups=sorted(exclusions),named_manifest_rows=rows,source_sha256=source_pins,seed_inventory_sha256=seedpins,proposed_seed_values=sorted(proposed),observed_seed_collision=[],selection_uses_labels_or_answers=False,broad_candidate_catalog_not_reclassified_as_executed=True,scope='named root input inventories only, not globally unseen; c32 training and prepared catalog exposed')

def main():
    if (s.ROOT/'inputs').exists():raise FileExistsError('immutable preparation; no overwrite or reroll')
    pool,receipt=inventory();selected=sorted(pool,key=lambda r:s.digest([s.MASTER,'source',r['group_id']]))[:128]
    contexts=[];groups=[];host={};rows=[];prompts={};queries={};native=[]
    class Memory:
        def __init__(self):self.files={}
        async def write(self,name,value):self.files[name]=value
    async def files(task):
        memory=Memory();await task.setup(None,memory);return memory.files
    for ci in range(8):
        cid=f'composition-new-{ci:02d}';members=selected[ci*16:(ci+1)*16];ordered=sorted(members,key=lambda r:s.digest([s.MASTER,'order',cid,r['group_id']]))
        users=sorted(p.USERS,key=lambda u:s.digest([s.MASTER,'users',cid,u]));records=[];labels={}
        for ri,source in enumerate(ordered):
            identifier='q'+s.digest([s.MASTER,'record',cid,source['group_id']])[:12]
            records.append(dict(id=identifier,user=users[ri%4],text=source['question'],weight=1+int(s.digest([s.MASTER,'weight',source['group_id']])[:8],16)%7));labels[identifier]=source['gold']
        context=dict(id=cid,index=ci,stratum='root_new',size=16,records=records,text=''.join(json.dumps(r,sort_keys=True)+'\n' for r in records),native_context_id=982615000+ci);contexts.append(context)
        groups.append(dict(id=cid,group_ids=[r['group_id'] for r in ordered],source_partition='train',child_training_exposed=True,prepared_catalog_exposed=True,source_rows=[{k:r[k] for k in ('group_id','source_path','source_line_1based')} for r in ordered]));host[cid]=dict(labels=labels,answers={})
        for oi,spec in enumerate(p.specs(ci)):
            row=dict(context_id=cid,context_window_id=context['native_context_id'],task_name=cid+':'+spec['operator'],family=spec['operator'],heldout_cell=spec['panel']=='composition',stratum='root_new',split='root_new',repeat=0,records=16,arm='typed',temperature=.5,client_path='train',role='native',evidence='raw',template=ci,namespace='operator-composition-transfer-20260910-v1',seed=s.MASTER+1+ci*6+oi,**spec)
            row['id']=s.digest(row);rows.append(row);queries[row['id']]=spec
            truth=p.answer(records,labels,row)
            if truth!=p.enumerated_answer(records,labels,row):raise ValueError('independent oracle disagreement')
            host[cid]['answers'][row['family']]=truth
            task=s.o.qnative().make_task(context,row['question'],0,row['id']);changed=s.o.qnative().make_task(context,row['question'],999999,row['id']);tokens=s.o.qnative().first_prefix(task)
            if len(tokens)+2048>8192:raise ValueError('native prefix admission fails; do not rerank')
            a=asyncio.run(files(task));b=asyncio.run(files(changed))
            if a!=b or s.o.qnative().first_prefix(changed)!=tokens:raise ValueError('host gold affects native body')
            if json.loads(a['records.json'])!=records or a['query.txt']!=row['question'].encode():raise ValueError('native source files changed')
            prompts[row['id']]=dict(prompt=task.data.prompt,token_ids=tokens,plain_query=row['question'])
            native.append(dict(id=row['id'],prefix_tokens=len(tokens),files_sha256={n:hashlib.sha256(v).hexdigest() for n,v in a.items()},gold_independent=True,policy_independent=True))
    # Latin rotations balance every operator over positions;8 is not divisible by6, so residual1/2 counts are disclosed.
    context_order=sorted(range(8),key=lambda ci:s.digest([s.MASTER,'dispatch-context',ci]));ordered_rows=[]
    for ci in context_order:
        block=[r for r in rows if r['template']==ci]
        ordered_rows.extend(block[(position+ci)%6] for position in range(6))
    policies=sorted(('sft6','sft24'),key=lambda policy:s.digest([s.MASTER,'policy-order',policy]))
    baseline={}
    for key in (*p.OPERATORS,'primitive','composition','all'):
        chosen=[r for r in rows if key=='all' or r['operator']==key or r['panel']==key];counts=Counter(host[r['context_id']]['answers'][r['family']] for r in chosen)
        baseline[key]=dict(n=len(chosen),answer_histogram={str(k):v for k,v in sorted(counts.items())},zero_correct=counts[0],nonzero=len(chosen)-counts[0],best_constant_correct=max(counts.values()),best_constants=sorted(k for k,v in counts.items() if v==max(counts.values())))
    values={'PUBLIC.json':contexts,'GROUPS.json':groups,'HOST_GOLD.json':host,'FREE_PLAN.json':ordered_rows,'QUERIES.json':queries,'PROMPTS_ACCURATE.json':prompts,'BASELINES.json':baseline,'PROVENANCE.json':receipt,'NATIVE_TEMPLATE.json':s.read(s.OLD/'inputs/NATIVE_TEMPLATE.json'),'EVALUATION_PLAN.json':dict(policy_order=policies,full=[dict(policy=policy,coordinate=row,available=False,reward=None) for policy in policies for row in ordered_rows],first_action=[],planned_full=96,planned_probes=0,outer_seconds=6480,work_seconds=6300,owned_seconds=6450,dispatch='hash-fixed context order, cyclic within-context six-family order shared by both policies; residual positions1or2',no_rerolls=True)}
    for name,value in values.items():s.write(s.ROOT/'inputs'/name,value)
    s.write(s.ROOT/'CPU_INPUT_NATIVE.json',dict(rows=native,full=48,policies=2,max_prefix=max(r['prefix_tokens'] for r in native),all_native_prefixes_equal=True,all_files_policy_independent=True,oracle_agreement=True))
    print(dict(pool=len(pool),selected=128,full=96,policy_order=policies,max_prefix=max(r['prefix_tokens'] for r in native),baselines=baseline))

if __name__=='__main__':main()
