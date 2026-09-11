"""Label-independent named-history allocation and fixed40-to48 dependency table."""
import collections
import hashlib
import importlib.util
import json
from pathlib import Path

ROOT=Path(__file__).resolve().parent
SEEDS=(981281401,981281402)


def digest(value):
    return hashlib.sha256(json.dumps(value,sort_keys=True,separators=(',',':')).encode()).hexdigest()


def plan_for(contexts):
    physical,logical=[],[]
    base=['user_all','user_filter','user_free','global_shared','global_free']
    for context in contexts:
        for repeat,seed in enumerate(SEEDS):
            block=context['index']*2+repeat
            order=base[:] if block<5 else base[::-1]
            shift=block if block<5 else block-5
            order=order[shift:]+order[:shift]
            for position,job in enumerate(order):
                family,kind=job.split('_')
                controller={'all':'all16','filter':'filter16','shared':'all16','free':'free'}[kind]
                name=f'adaptive-{context["index"]:02}-{family}'
                row={'study':ROOT.name,'block':block,'context_index':context['index'],
                     'context_sha256':context['sha256'],'context_window_id':1800+context['index'],
                     'source_id':14800000+2*context['index']+(family=='global'),
                     'task_name':name,'job':job,'family':family,'controller':controller,'arm':job,
                     'seed':seed,'repeat':repeat,'temperature':.5,'client_path':'train',
                     'analysis_split':'new_named_history_excluded_leaf_train_supported',
                     'pair_id':digest([ROOT.name,block]),'pair_order':position,
                     'group_id':digest([ROOT.name,name,controller]),'dispatch_order':len(physical)}
                row['id']=digest(row);physical.append(row)
                for method in ('all16','filter16') if kind=='shared' else (controller,):
                    logical.append({'block':block,'context_index':context['index'],'seed':seed,
                                    'family':family,'method':method,'execution_id':row['id'],
                                    'shared_outcome':kind=='shared'})
    return physical,logical


def allocate():
    import experiment as e
    c=e.c
    inventory_path=ROOT.parents[1]/'ideas/2026-09-09-adaptive-question-feasibility.json'
    inventory=c.read(inventory_path);c.authenticate(inventory['source_sha256'])
    data=e.checked_import('adaptive_leaf_source',ROOT.parent/'trec-leaf-sft-v1/source/data.py',
        'b5aa353e2173c3fd48ecc36ce0596c9c3328767a7d82c8d22c57b4e0a32f0b8f')
    rows=data.load_partitions()['train']
    legacy=c.read(ROOT.parent/'trec-leaf-split-provenance-v1/INVENTORY.json')
    exclusions={f'legacy-context-{k}':set(legacy['old_contexts'][k]['question_group_sha256']) for k in ('6','8')}
    for suffix in ('root-only-credit-v1/inputs/PUBLIC.json','root-rlvr-campaign-v1/inputs/TRANSFER_PUBLIC.json',
                   'root-rlvr-independent-seed-v1/inputs/TRANSFER_PUBLIC.json','leaf-composition-transfer-v1/prepared-v1/DATA.json'):
        exclusions[suffix]={g for context in c.read(ROOT.parent/suffix)['contexts'] for g in context['group_ids']}
    exclusions['root-curriculum-data-v1/GROUPS.json']={g for x in c.read(ROOT.parent/'root-curriculum-data-v1/GROUPS.json') if x['dataset']=='trec' for g in x['group_ids']}
    forbidden=set().union(*exclusions.values())
    remaining=[r for r in rows if r['group_id'] not in forbidden]
    remaining_hash=hashlib.sha256('\n'.join(sorted(r['group_id'] for r in remaining)).encode()).hexdigest()
    if len(remaining)!=1454 or remaining_hash!=inventory['remaining_group_ids_sha256']:
        raise ValueError('named-history pool differs; parent source decision required')
    old_contexts={x['sha256'] for x in c.read(ROOT.parent/'root-rlvr-campaign-v1/inputs/TRANSFER_PUBLIC.json')['contexts']}
    old_contexts.update(x['context_sha256'] for x in c.read(ROOT.parent/'root-curriculum-data-v1/GROUPS.json') if x['dataset']=='trec')
    later={}
    for name in ('root-return-contract-factorial-v1','root-receipt-ablation-v1','root-receipt-uptake-v1','child-role-suffix-v1'):
        path=ROOT.parent/name/'inputs/TASKS.json'
        if not path.exists():raise ValueError('named catalogue missing')
        tasks=c.read(path)
        if isinstance(tasks,dict):tasks=tasks.get('tasks',tasks)
        if isinstance(tasks,dict):tasks=list(tasks.values())
        observed={t['context_sha256'] for t in tasks}
        if observed-old_contexts:raise ValueError('later catalogue adds new root contexts')
        later[str(path)]={'sha256':c.file_hash(path),'contexts':len(observed),'outside_old':0}
    ordered=sorted(remaining,key=lambda r:digest([ROOT.name,'source',r['group_id']]))[:512]
    public,host,membership=[],{},[]
    for i in range(4):
        selected=ordered[i*128:(i+1)*128]
        positions=sorted(range(128),key=lambda p:digest([ROOT.name,'user-position',i,p]))
        users={position:f'u{rank//8:02}' for rank,position in enumerate(positions)}
        records=[{'id':f'q{j+1:04}','user':users[j],'text':r['question']} for j,r in enumerate(selected)]
        text='\n'.join(f"ID: {r['id']} || User: {r['user']} || Instance: {r['text']}" for r in records)+'\n'
        context={'index':i,'id':f'adaptive-context-{i:02}','records':records,'text':text,
                 'sha256':hashlib.sha256(text.encode()).hexdigest(),'query_user':f'u{i:02}'}
        public.append(context)
        labels={r['id']:source['gold'] for r,source in zip(records,selected,strict=True)}
        for family in ('user','global'):
            name=f'adaptive-{i:02}-{family}'
            relevant=records if family=='global' else [r for r in records if r['user']==f'u{i:02}']
            host[name]={'answer':sum(labels[r['id']]=='numeric value' for r in relevant),
                        'subset_size':len(relevant),'labels_by_id':labels}
        membership.append({'context_id':context['id'],'group_ids':[r['group_id'] for r in selected],
                           'representatives':selected,'class_histogram':dict(collections.Counter(r['coarse'] for r in selected))})
    selected_ids={g for m in membership for g in m['group_ids']}
    if len(selected_ids)!=512 or selected_ids & forbidden:raise ValueError('source overlap')
    plan,logical=plan_for(public)
    c.write_once(ROOT/'inputs/PUBLIC.json',public)
    c.write_once(ROOT/'inputs/HOST_GOLD.json',host)
    c.write_once(ROOT/'inputs/MEMBERSHIP.json',membership)
    c.write_once(ROOT/'inputs/PLAN.json',plan)
    c.write_once(ROOT/'inputs/LOGICAL_CELLS.json',logical)
    c.write_once(ROOT/'inputs/PROVENANCE.json',{'inventory_path':str(inventory_path),'inventory_sha256':c.file_hash(inventory_path),
        'source_sha256':inventory['source_sha256'],'remaining_groups':len(remaining),'remaining_group_ids_sha256':remaining_hash,
        'named_exclusions':{k:len(v) for k,v in exclusions.items()},'later_catalogues':later,
        'selected_unique_groups':512,'selection_uses_labels':False,'source_partition':data.SPLIT_SHA,
        'limitation':'Named root history only; leaf-train-supported; not all-history or pretraining-clean. Dataset license unknown.'})
    return {'physical':len(plan),'logical':len(logical),'answers':{k:v['answer'] for k,v in host.items()}}


if __name__=='__main__': print(json.dumps(allocate(),sort_keys=True))
