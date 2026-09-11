"""Label-independent selection from the immutable QSR complement; host labels separate."""
import transfer_study as s

def build():
    gp=s.QSR/'inputs/GROUPS.json';pp=s.QSR/'inputs/PROVENANCE.json'
    s.check(gp,'99984ddb15ac2b15ccf86a2cdcfa40016ff86507b5448b1ab29695187e9765c6')
    s.check(pp,'6c1bce9e30f48f159ba24450883e7a1c036869eb3ae33d5bcddacc29f4d09c4b')
    proof=s.read(pp);receipt=s.read(proof['receipt_path']);s.check(proof['receipt_path'],proof['receipt_sha256'])
    for item in receipt['files']:s.check(item['path'],item['sha256'])
    for path,pin in receipt['source_sha256'].items():s.check(path,pin)
    path=s.SIDE/'trec-leaf-sft-v1/source/data.py';data=s.load('transfer_pinned_trec_data',path,receipt['source_sha256'][str(path)])
    forbidden=set(proof['excluded_group_ids']);qsr={g for c in s.read(gp) for g in c['group_ids']}
    pool=[r for r in data.load_partitions()['train'] if r['group_id'] not in forbidden|qsr]
    if len(pool)!=78 or len(qsr)!=448:raise ValueError('QSR complementary population changed')
    pool.sort(key=lambda r:s.digest([s.MASTER,'source',r['group_id']]))
    public=[];host={};groups=[];rows=[]
    for ci in range(4):
        members=pool[ci*16:(ci+1)*16];cid=f'root-transfer-{ci:02}'
        members=sorted(members,key=lambda r:s.digest([s.MASTER,'order',cid,r['group_id']]))
        records=[dict(id=f'q{j+1:04}',user=f'u{j%4:02}',text=r['question']) for j,r in enumerate(members)]
        c=dict(id=cid,stratum='root_catalog_new_child_training_exposed',native_context_id=98140200+ci,target='NUM' if ci%2==0 else 'HUM',query_users=['u01','u03'],helper_partition='train',records=records)
        c['text']='\n'.join(f"ID: {r['id']} || User: {r['user']} || Instance: {r['text']}" for r in records)+'\n'
        public.append(c);groups.append(dict(id=cid,group_ids=[r['group_id'] for r in members],source_partition='train',child_training_exposed=True))
        host[cid]=dict(labels={r['id']:m['coarse'] for r,m in zip(records,members)})
        for qi,users in enumerate((['u03'],['u01','u03'])):
            for repeat in range(2):
                row=dict(context_id=cid,users=users,family='single_user' if qi==0 else 'union',repeat=repeat,seed=981401101+ci*4+qi*2+repeat,split='root_catalog_new_child_training_exposed')
                row['id']='free-'+s.digest(row)[:16];rows.append(row)
    # Rotate complete context/query blocks; same paired schedule for all policies.
    rows.sort(key=lambda r:s.digest([s.MASTER,'dispatch',r['id']]))
    return {'PUBLIC.json':public,'HOST_GOLD.json':host,'GROUPS.json':groups,'FREE_PLAN.json':rows,
        'PROVENANCE.json':dict(master_seed=s.MASTER,source_sha256={str(gp):s.sha(gp),str(pp):s.sha(pp),proof['receipt_path']:proof['receipt_sha256'],**receipt['source_sha256']},
            historical_excluded_group_ids=sorted(forbidden),qsr_group_ids=sorted(qsr),remaining_pool_group_ids=sorted(r['group_id'] for r in pool),selected_groups=64,unused_groups=14,
            selected_without_labels_or_outcomes=True,child_training_exposed=True,globally_research_unseen=False,independent_context_clusters=4,
            boundary='Absent only from pinned53 root/prepared manifests plus legacy inventory and QSR448; prior leaf training/evaluation and outside-history/pretraining exposure disclosed')}

def prompt(context,row):
    text=s.stack().prior.prompt({**context,'query_users':row['users']},row['family'])
    a='Each has id, synthetic user metadata, and original question text.';b='No source semantic labels are present.'
    if text.count(a)!=1 or text.count(b)!=1:raise ValueError('original free prompt anchors changed')
    return text.replace(a,'Each has exactly the fields id, user, and text: a record ID, user identifier, and original question text.').replace(b,'The records.json and context.txt files contain no category labels. Any category maps returned by children or displayed in tool observations are predictions, not dataset labels.')
