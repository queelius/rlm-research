"""Outcome-independent new-root-source panel; helper exposure explicitly retained."""
import hashlib
import json
import re
import subprocess
import unicodedata
from pathlib import Path

ROOT=Path(__file__).resolve().parent
STORE=ROOT.parent.parent
MASTER=981330001
FEAS=STORE/'ideas/2026-09-09-post-refill-root-feasibility.json'
APPROVAL=STORE/'ideas/2026-09-09-next-root-learning-main-approval.md'
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def digest(x):return hashlib.sha256(json.dumps(x,sort_keys=True,separators=(',',':')).encode()).hexdigest()
def read(p):return json.loads(Path(p).read_text())
def write(p,x):
    p=Path(p);p.parent.mkdir(parents=True,exist_ok=True)
    with p.open('x') as f:json.dump(x,f,sort_keys=True,indent=2);f.write('\n')
def choose(rows,excluded,stratum):
    eligible=[r for r in rows if r['question_group_sha256'] not in excluded]
    eligible.sort(key=lambda r:hashlib.sha256(f'{MASTER}|panel|{stratum}|{r["question_group_sha256"]}'.encode()).hexdigest())
    if len(eligible)<32:raise ValueError('insufficient source groups; no reselection')
    return eligible[:32]

def prepare():
    feasibility=read(FEAS);sources=feasibility['source_sha256']
    for p,h in sources.items():
        if sha(p)!=h:raise ValueError('named exclusion changed: '+p)
    split=read(next(p for p in sources if p.endswith('PROPOSED_SPLIT.json')))
    inv=read(next(p for p in sources if p.endswith('INVENTORY.json')))
    excluded={g for c in inv['old_contexts'].values() for g in c['question_group_sha256']}
    for p in sources:
        if p.endswith(('PROPOSED_SPLIT.json','INVENTORY.json')):continue
        value=read(p);contexts=value['contexts'] if isinstance(value,dict) else value
        excluded.update(g for c in contexts for g in c['group_ids'])
    raw=Path('/project/alex_phd/research-cache/2026-09-08-literature/trec-context8.6NYSkv/train_5500.label')
    if sha(raw)!=inv['source_file_sha256'][str(raw)]:raise ValueError('official TREC bytes')
    rawlines=raw.read_bytes().splitlines();public=[];host={};membership=[]
    for part,key in [('train','source_train'),('validation','validation')]:
        remaining={r['question_group_sha256'] for r in split[key]}-excluded
        want=feasibility['partitions']['helper_'+part]
        if len(remaining)!=want['remaining'] or hashlib.sha256('\n'.join(sorted(remaining)).encode()).hexdigest()!=want['remaining_set_sha256']:raise ValueError('remaining-set identity')
        chosen=choose(split[key],excluded,part)
        for offset in (0,16):
            index=len(public);identity=f'new-root-{part}-{offset//16:02d}';records=[];labels={};groups=[]
            for i,item in enumerate(chosen[offset:offset+16]):
                source_line=min(item['source_line_1based']);fine,question=rawlines[source_line-1].replace(b'\xf0',b' ').strip().decode().split(' ',1)
                normalized=' '.join(re.findall(r'\w+',unicodedata.normalize('NFKC',question).casefold()))
                if hashlib.sha256(normalized.encode()).hexdigest()!=item['question_group_sha256'] or fine.split(':')[0]!=item['coarse']:raise ValueError('representative/source identity')
                row=dict(id=f'q{i+1:04d}',user=f'u{i%4:02d}',text=question);records.append(row);labels[row['id']]=item['coarse'];groups.append(item['question_group_sha256'])
                membership.append(dict(context_id=identity,record_id=row['id'],helper_partition=part,**item,representative_source_line_1based=source_line))
            text=''.join(f'ID: {r["id"]} || User: {r["user"]} || Instance: {r["text"]}\n' for r in records)
            target=('NUM','HUM')[index%2]
            public.append(dict(id=identity,stratum='new_root_'+part,helper_partition=part,query_users=['u00','u01'],target=target,records=records,group_ids=groups,text=text))
            answers={family:sum(labels[r['id']]==target for r in records if r['user'] in users) for family,users in [('single_user',['u00']),('union',['u00','u01'])]}
            host[identity]=dict(labels=labels,answers=answers)
    selected={g for c in public for g in c['group_ids']}
    if len(selected)!=64 or selected&excluded:raise ValueError('panel groups')
    argv=['rg','-l','--glob','*.json','--glob','*.py','--glob','*.md','--glob','!**/outputs/**','--glob','!**/qualification*/**','981330[0-9]{3}',str(STORE/'sidecars'),str(STORE/'ideas')]
    result=subprocess.run(argv,capture_output=True,text=True,timeout=30)
    hits=[p for p in result.stdout.splitlines() if not p.startswith(str(ROOT)+'/') and p!=str(APPROVAL)]
    if result.returncode not in (0,1) or hits:raise ValueError('seed collision '+repr(hits))
    for name,value in [('PUBLIC.json',public),('HOST_GOLD.json',host),('MEMBERSHIP.json',membership),('EXCLUDED_GROUPS.json',sorted(excluded))]:write(ROOT/'data'/name,value)
    ready=dict(status='DATA_READY_READOUT_ONLY',master_seed=MASTER,contexts=4,groups=64,helper_train=32,helper_validation=32,
      new_root_source_relative_to_nine_named_inputs=True,globally_fresh=False,pretraining_overlap='unknown',helper_exposed=True,dataset_license='unknown',
      representative='minimum source line in normalized group',selection='label-independent SHA256 rank; no target-based filtering',reserved_for_readout=True,
      source_sha256={**sources,str(raw):sha(raw),str(FEAS):sha(FEAS),str(APPROVAL):sha(APPROVAL),str(Path(__file__)):sha(__file__)},
      data_sha256={str(p):sha(p) for p in (ROOT/'data').glob('*.json')},seed_scan=dict(argv=argv,returncode=result.returncode,hits=hits,scope='sidecars+ideas excluding outputs and qualification; not global'),gpu_calls=0)
    ready['identity']=digest(ready);write(ROOT/'DATA_READY.json',ready);print(json.dumps({'data_ready_sha256':sha(ROOT/'DATA_READY.json'),'identity':ready['identity'],'contexts':[c['id'] for c in public]}))

if __name__=='__main__':prepare()
