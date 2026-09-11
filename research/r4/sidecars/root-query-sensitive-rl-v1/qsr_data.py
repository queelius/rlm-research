"""Deterministic new-context query compositions; gold stays host-only."""
from collections import Counter
import itertools
import qsr_study as s

RECEIPT=s.STORE/'operations/2026-09-09-allocation-5780/query-sensitive-source-availability.json'
RECEIPT_SHA='c1e45c310be4979523a728fdeb20ebff70999e404723e8030f7b9472d785888b'
OPS=('count','distinct','weight');SCOPES=('single','union','all')
SUPPORTED={'count':('single','all'),'distinct':('single','union'),'weight':('union','all')}
HELDOUT={'count':'union','distinct':'all','weight':'single'}
TARGETS=('human being','entity','location','numeric value')

def excluded():
    s.check(RECEIPT,RECEIPT_SHA);receipt=s.read(RECEIPT);known=set()
    def walk(value):
        if isinstance(value,dict):
            for key,child in value.items():
                if key in ('group_id','question_group_sha256','group_ids','normalized_group_sha256'):
                    known.update(v for v in (child if isinstance(child,list) else [child]) if isinstance(v,str) and len(v)==64)
                walk(child)
        elif isinstance(value,list):
            for child in value:walk(child)
    for item in receipt['files']:
        s.check(item['path'],item['sha256']);walk(s.read(item['path']))
    for path,pin in receipt['source_sha256'].items():s.check(path,pin)
    walk(s.read(s.SIDE/'trec-leaf-split-provenance-v1/INVENTORY.json')['old_contexts'])
    return known,receipt

def answer(records,labels,query):
    selected=[r for r in records if r['user'] in query['users'] and labels[r['id']]==query['target']]
    if query['operator']=='count':return len(selected)
    if query['operator']=='distinct':return len({r['user'] for r in selected})
    if query['operator']=='weight':return sum(r['weight'] for r in selected)
    raise ValueError('unknown operator')

def question(q):
    scope='all four users' if q['scope']=='all' else ('user '+repr(q['users'][0]) if q['scope']=='single' else 'the union of users '+repr(q['users'][0])+' and '+repr(q['users'][1])+' (each record once)')
    operations={'count':'Count qualifying records','distinct':'Count distinct users having at least one qualifying record','weight':'Sum the visible record weight values of qualifying records'}
    return f"Among records belonging to {scope}, a record qualifies when its question category is {q['target']!r}. {operations[q['operator']]}. If none qualify, the result is zero. Return only Answer: N, replacing N with the exact nonnegative integer."

def query(context,operator,scope):
    ci=context['index'];users=sorted(('u0','u1','u2','u3'),key=lambda u:s.digest([s.MASTER,'scope',context['id'],u]))
    return dict(operator=operator,scope=scope,users=users[:1] if scope=='single' else users[:2] if scope=='union' else sorted(users),target=TARGETS[ci%4])

def build():
    known,receipt=excluded();source_path=s.SIDE/'trec-leaf-sft-v1/source/data.py'
    source=s.load('qsr_source_data',source_path,receipt['source_sha256'][str(source_path)])
    pool=[r for r in source.load_partitions()['train'] if r['group_id'] not in known]
    if len(pool)!=526:raise ValueError('scoped source availability changed')
    pool.sort(key=lambda r:s.digest([s.MASTER,'source',r['group_id']]))
    contexts=[];host={};groups=[];queries={};plans={'training':{},'readout':[]};offset=0
    for split in ('training','readout'):
        for ci in range(12):
            size=16 if split=='training' or ci<8 else 32;members=pool[offset:offset+size];offset+=size
            cid=f'{split}-{ci:02d}';ordered=sorted(members,key=lambda r:s.digest([s.MASTER,'order',cid,r['group_id']]))
            users=sorted(('u0','u1','u2','u3'),key=lambda u:s.digest([s.MASTER,'users',cid,u]));records=[];labels={}
            for ri,r in enumerate(ordered):
                identifier='q'+s.digest([s.MASTER,'record',cid,r['group_id']])[:12]
                records.append(dict(id=identifier,user=users[ri%4],text=r['question'],weight=1+int(s.digest([s.MASTER,'weight',r['group_id']])[:8],16)%7));labels[identifier]=r['gold']
            context=dict(id=cid,index=ci,stratum=split,size=size,records=records,text=''.join(__import__('json').dumps(r,sort_keys=True)+'\n' for r in records),native_context_id=98138200+len(contexts))
            contexts.append(context);groups.append(dict(id=cid,group_ids=[r['group_id'] for r in ordered],source_partition='train',child_training_exposed=True))
            cells=[(op,SUPPORTED[op][(ci//4+ci%4+oi)%2]) for oi,op in enumerate(OPS)] if split=='training' else list(HELDOUT.items())+[(list(SUPPORTED)[ci%3],SUPPORTED[list(SUPPORTED)[ci%3]][(ci//3)%2])]
            host[cid]=dict(labels=labels,answers={});rows=[]
            for gi,(op,scope) in enumerate(cells):
                q=query(context,op,scope);family=op+'-'+scope;name=cid+':'+family
                queries[name]=q;host[cid]['answers'][family]=answer(records,labels,q)
                for repeat in range(8 if split=='training' else 1):
                    seed=981381101+ci*24+gi*8+repeat if split=='training' else 981381701+ci*4+gi
                    row=dict(context_id=cid,context_window_id=context['native_context_id'],task_name=name,family=family,operator=op,scope=scope,heldout_cell=HELDOUT[op]==scope,stratum=split,split=split,repeat=repeat,seed=seed,records=size,arm='typed',temperature=.5,client_path='train')
                    if split=='training':row['candidate_window']=ci+1
                    row['id']=s.digest(row);rows.append(row)
            if split=='training':plans['training'][str(ci+1)]=sorted(rows,key=lambda r:s.digest([s.MASTER,'schedule',r['id']]))
            else:plans['readout'].extend(rows)
    diagnostics={'selection_uses_gold_or_model_outcomes':False,'same_context_answer_coincidences':[]}
    for phase,rows in [('training',sum(plans['training'].values(),[])),('readout',plans['readout'])]:
        counts=Counter(host[r['context_id']]['answers'][r['family']] for r in rows);best=max(counts.values())
        diagnostics[phase]=dict(planned=len(rows),answer_histogram=dict(counts),zero_correct=counts[0],best_constant_correct=best,best_constants=sorted(k for k,v in counts.items() if v==best))
    for cid,h in host.items():
        for a,b in itertools.combinations(sorted(h['answers']),2):diagnostics['same_context_answer_coincidences'].append(dict(context_id=cid,first=a,second=b,equal=h['answers'][a]==h['answers'][b]))
    return {'PUBLIC.json':contexts,'HOST_GOLD.json':host,'GROUPS.json':groups,'QUERIES.json':queries,'PLANS.json':plans,'DIAGNOSTICS.json':diagnostics,
            'PROVENANCE.json':dict(receipt_path=str(RECEIPT),receipt_sha256=RECEIPT_SHA,excluded_group_ids=sorted(known),selected_groups=448,unused_eligible=78,source_sha256=receipt['source_sha256'],novelty='Absent only from pinned53 root/prepared manifests plus legacy inventory; all child-training-exposed; outside-history and pretraining unknown',selection_uses_gold_or_model_outcomes=False)}
