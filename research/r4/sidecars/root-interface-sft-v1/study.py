"""Outcome-independent public allocation, authored targets and exact current-action masks."""
import hashlib
import importlib.util
import json
import re
import sys
from pathlib import Path

ROOT=Path(__file__).resolve().parent
STORE=ROOT.parents[1]
BASE=Path('/project/alex_phd/research-cache/models/Qwen--Qwen3-4B-Instruct-2507--cdbee75f17c01a7cc42f958dc650907174af0554')
START=ROOT.parent/'root-recovered-child-continuation-v1/outputs/attempt-001/round-08/training/checkpoint-8'
START_SHA='473210b18c4be163cd46a894614cb14934a7908e45bd97f96720928a7770ccdd'
MEMO=STORE/'ideas/2026-09-09-adaptive-root-training-feasibility.json'
NATIVE=Path('/project/alex_phd/envs/prime-rl-5990b1b/bin/python')
TRAIN=Path('/project/alex_phd/repos/rlm-bootstrap/.worktrees/a100-lora-roundtrip/gpu/training/.venv/bin/python')
LABELS=dict(zip(('HUM','LOC','ABBR','ENTY','DESC','NUM'),('human being','location','abbreviation','entity','description and abstract concept','numeric value')))
HELPER='import json\nfrom rlm.api import run as rlm\nfrom batch_contract import request_for, strict_map\nrecords = json.load(open("records.json"))\nbatch = records[:4]\nchild = await rlm(request_for(batch))\nlabels = strict_map(child.answer, [row["id"] for row in batch])\nprint(labels)'

def sha(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()
def digest(v):return hashlib.sha256(json.dumps(v,sort_keys=True,separators=(',',':')).encode()).hexdigest()
def read(path):return json.loads(Path(path).read_text())
def write(path,value):
    path=Path(path);path.parent.mkdir(parents=True,exist_ok=True)
    with path.open('x') as f:json.dump(value,f,indent=2,sort_keys=True,allow_nan=False);f.write('\n')
def check(path,expected):
    if sha(path)!=expected:raise ValueError('identity changed: '+str(path))
def load(name,path,expected):
    check(path,expected)
    spec=importlib.util.spec_from_file_location(name,path);m=importlib.util.module_from_spec(spec)
    sys.modules[name]=m;spec.loader.exec_module(m);return m

def build_data():
    memo=read(MEMO)
    for path,expected in memo['source_sha256'].items():check(path,expected)
    d=load('interface_leaf_data',ROOT.parent/'trec-leaf-sft-v1/source/data.py',memo['source_sha256'][str(ROOT.parent/'trec-leaf-sft-v1/source/data.py')])
    partitions=d.load_partitions()
    train={r['group_id']:r for r in partitions['train']}
    inv=read(ROOT.parent/'trec-leaf-split-provenance-v1/INVENTORY.json')
    excluded=set().union(*(set(inv['old_contexts'][k]['question_group_sha256']) for k in ('6','8')))
    for p in ('root-only-credit-v1/inputs/PUBLIC.json','root-rlvr-campaign-v1/inputs/TRANSFER_PUBLIC.json','root-rlvr-independent-seed-v1/inputs/TRANSFER_PUBLIC.json','leaf-composition-transfer-v1/prepared-v1/DATA.json'):
        excluded.update(g for c in read(ROOT.parent/p)['contexts'] for g in c['group_ids'])
    excluded.update(g for c in read(ROOT.parent/'root-curriculum-data-v1/GROUPS.json') if c['dataset']=='trec' for g in c['group_ids'])
    excluded.update(g for c in read(ROOT.parent/'adaptive-filter-pilot-v1/inputs/MEMBERSHIP.json') for g in c['group_ids'])
    remaining=set(train)-excluded
    assert len(remaining)==942 and hashlib.sha256('\n'.join(sorted(remaining)).encode()).hexdigest()==memo['partitions']['source_train']['remaining_set_sha256']
    ns=memo['candidate_namespace'];ordered=sorted(remaining,key=lambda g:digest([ns,'source',g]))
    public=[];host={}
    for spec in memo['candidate_contexts']:
        n=spec['records'];gids=ordered[spec['source_offset']:spec['source_offset']+n]
        assert digest(gids)==spec['ordered_group_ids_sha256']
        assert hashlib.sha256('\n'.join(sorted(gids)).encode()).hexdigest()==spec['group_ids_sha256']
        positions=sorted(range(n),key=lambda p:digest([ns,'user-position',spec['id'],p]))
        users={p:f'u{rank//8:02}' for rank,p in enumerate(positions)}
        records=[dict(id=f'q{j+1:04}',user=users[j],text=train[g]['question']) for j,g in enumerate(gids)]
        labels={r['id']:train[g]['coarse'] for r,g in zip(records,gids)}
        gold={family:sum(labels[r['id']]==spec['target'] for r in records if family=='global' or r['user'] in spec['query_users'][:2 if family=='two_user_union' else 1]) for family in ('single_user','global','two_user_union')}
        assert gold==spec['post_allocation_host_gold']
        text='\n'.join(f"ID: {r['id']} || User: {r['user']} || Instance: {r['text']}" for r in records)+'\n'
        public.append({k:spec[k] for k in ('id','stratum','query_users','target')}|dict(records=records,group_ids=gids,text=text))
        host[spec['id']]=dict(answers=gold,coarse_by_id=labels)
    return public,host,dict(unique_groups=896,unallocated=46,memo_sha256=sha(MEMO),source_sha256=memo['source_sha256'],leaf_partition='train',license='Underlying TREC license not established; public pretraining/historical exposure unknown',named_exclusion_union=len(excluded))

def question(c,family):
    scope='in the entire file' if family=='global' else ('from user '+c['query_users'][0] if family=='single_user' else 'from either user '+c['query_users'][0]+' or '+c['query_users'][1])
    return f'How many records {scope} ask for an answer of category {LABELS[c["target"]]}?'

def prompt(c,family):
    contract=ROOT.parent/'adaptive-filter-pilot-v1/batch_contract.py'
    import ast
    tree=ast.parse(contract.read_text())
    definitions=next(ast.literal_eval(n.value) for n in tree.body if isinstance(n,ast.Assign) and any(isinstance(t,ast.Name) and t.id=='DEFINITIONS' for t in n.targets))
    return (f'The public file records.json contains a JSON list of {len(c["records"])} records. Each has id, synthetic user metadata, and original question text. context.txt is a readable copy. Count records, not users. No source semantic labels are present.\n\n'+definitions+
      '\nYou can use Python and ordinary await rlm(prompt) to ask a child for help. batch_contract.py provides pure request_for(batch) and strict_map(raw, ids). The former omits user metadata; the latter rejects duplicate/missing/unknown IDs, non-object JSON, trailing text and noncanonical labels. It does not repair output or check semantic correctness. You decide subsets, batching, aggregation and recovery; no helper use is required.\n\nOptional API example (first four records only, NOT the final answer):\n```python\n'+HELPER+'\n```\n\nReturn only Answer: N, where N is a nonnegative decimal integer.\nQuestion: '+question(c,family))

def metadata(c,index,kind):
    if kind=='divisibility':
        divisor=index+2
        q=f'How many record IDs in records.json have an integer suffix divisible by {divisor}? Use public metadata only, not question semantics. Return only Answer: N.'
        expression=f'sum(int(r["id"][1:]) % {divisor} == 0 for r in records)'
        answer=sum(int(r['id'][1:])%divisor==0 for r in c['records'])
    elif kind=='users':
        n=1+3*index
        q=f'How many distinct users occur in the first {n} records of records.json? Use public metadata only, not question semantics. Return only Answer: N.'
        expression=f'len({{r["user"] for r in records[:{n}]}})'
        answer=len({r['user'] for r in c['records'][:n]})
    else:raise ValueError('unknown metadata task')
    return q,'import json\nrecords = json.load(open("records.json"))\nprint('+expression+')',answer

def plan(public):
    rows=[]
    for stratum,scopes,repeats,start in [('validation',('single_user','global'),1,981284101),('query_transfer',('single_user','two_user_union'),2,981284201),('length_transfer',('single_user','global'),2,981284301)]:
        index=0
        for c in (c for c in public if c['stratum']==stratum):
            for family in scopes:
                for repeat in range(repeats):
                    row=dict(context_id=c['id'],context_window_id=context_window_id(c),arm='typed',stratum=stratum,family=family,repeat=repeat,seed=start+index,temperature=.5,client_path='train')
                    row['id']=digest(row);rows.append(row);index+=1
    return rows

def context_window_id(c):
    strata={'train':0,'validation':1,'query_transfer':2,'length_transfer':3}
    return 24000+strata[c['stratum']]*100+int(c['id'].rsplit('-',1)[1])

def training_row(name,kind,prefix,target):
    if not prefix or not target or target[-1]!=151645 or len(prefix)+len(target)>8192:raise ValueError('no truncation/invalid terminator')
    return dict(id=name,kind=kind,input_ids=prefix+target,labels=[-100]*len(prefix)+target,prompt_length=len(prefix),target_tokens=len(target),source='operator-authored SFT; no behavior likelihood')

def endpoint(reply,gold,completed):
    if not completed or not isinstance(reply,str):return None
    m=re.fullmatch(r'Answer: ([0-9]+)',reply.strip())
    return int(bool(m) and int(m.group(1))==gold)
