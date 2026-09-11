"""Small explicit study boundary over authenticated native/lifecycle dependencies."""
import functools
import hashlib
import importlib.util
import sys
from pathlib import Path

ROOT=Path(__file__).resolve().parent;SIDE=ROOT.parent;OLD=SIDE/'root-accumulation-ledger-v1'
p=OLD/'study.py'
if hashlib.sha256(p.read_bytes()).hexdigest()!='f53150be0fa0a647a90a2e69d5400f7fc89ee0bba47f4e37e30b3aafe1e182d9':raise ValueError('native dependency changed')
sp=importlib.util.spec_from_file_location('bridge_frozen_study',p);old=importlib.util.module_from_spec(sp);sp.loader.exec_module(old)
for name in ('read','sha','digest','check','write','load','aliases','stack','PRIOR','ADAPTIVE','LOCAL','NATIVE'):globals()[name]=getattr(old,name)
ROOT_SHA='66cce4009628ff7d8e047f08e6fb3a29febdbf8fb3ed8303871f69860f1151d5'
CHILD_SHA=old.CHILD_SHA;MASTER=981326001;SEEDS=(981326011,981326021)
CONTEXTS=('query_transfer-00','query_transfer-01','length_transfer-00','length_transfer-01')
LABELS={'HUM':'human being','LOC':'location','ABBR':'abbreviation','ENTY':'entity','DESC':'description and abstract concept','NUM':'numeric value'}

def inputs():
    public={c['id']:c for c in read(PRIOR/'prepared-v2/PUBLIC.json')};host=read(PRIOR/'prepared-v2/HOST_GOLD.json')
    oldtasks=read(ADAPTIVE/'inputs/TASKS.json');contexts=[public[i] for i in CONTEXTS];tasks={};gold={}
    for c in contexts:
        template=oldtasks['adaptive-length_transfer-00-global']['prompt']
        if template.count('JSON list of 128 records')!=1:raise ValueError('global public prompt seam changed')
        base=template.replace('JSON list of 128 records',f'JSON list of {len(c["records"])} records');target=LABELS[c['target']]
        gold[c['id']]={'coarse_by_id':host[c['id']]['coarse_by_id'],'target_label':target,'answers':{}}
        for family in ('count','checksum'):
            question=(f'How many records in the entire file ask for an answer of category {target}?' if family=='count' else
                f'For ALL records in the entire file asking for an answer of category {target}, sum the numeric suffixes of their source IDs. For example, q0007 contributes 7. Sum each qualifying record once; an empty sum is 0.')
            prompt=base.rsplit('Question: ',1)[0]+'Question: '+question
            name='bridge-'+c['id']+'-'+family;tasks[name]={'prompt':prompt}
            ids=[i for i,label in host[c['id']]['coarse_by_id'].items() if label==c['target']]
            gold[c['id']]['answers'][family]=len(ids) if family=='count' else sum(int(i[1:]) for i in ids)
    return contexts,gold,tasks

def plan_for(contexts):
    rows=[]
    for index,c in enumerate(contexts):
        for family_i,family in enumerate(('count','checksum')):
            for repeat,seed in enumerate(SEEDS):
                pair=digest([ROOT.name,c['id'],family,seed]);arms=('array','map') if (index+family_i+repeat)%2==0 else ('map','array')
                for order,arm in enumerate(arms):
                    row={'context_id':c['id'],'context_window_id':stack().prior.context_window_id(c),'task_name':'bridge-'+c['id']+'-'+family,
                         'family':family,'arm':arm,'seed':seed,'repeat':repeat,'pair_id':pair,'pair_order':order,
                         'temperature':.5,'client_path':'train','records':len(c['records']),'stratum':c['stratum']}
                    row['id']=digest(row);rows.append(row)
    return rows

def binding():
    value=stack().native.initial_binding();value['models'].pop(value['role_map']['root'])
    alias='strict-rlm-qwen3-4b-root-low8-representation-bridge-v1'
    value['models'][alias]={'path':str(SIDE/'root-success-trajectory-sft-v1/outputs/attempt-001/training/checkpoint-0008'),
        'adapter_sha256':ROOT_SHA,'config_sha256':'118bb737297c35d96a194b642026b1e58c72f945d55ae1616eb716cfc4601728'}
    value['role_map']['root']=alias
    if value['models'][value['fixed_child']]['adapter_sha256']!=CHILD_SHA:raise ValueError('fixed child changed')
    value['representation_bridge_study']=ROOT.name;return value

@functools.lru_cache(maxsize=1)
def verify():
    ready=read(ROOT/'READY.json')
    for p,want in ready['source_sha256'].items():check(p,want)
    spec=read(ROOT/'SPEC.json')
    if spec['plan']!=plan_for(read(ROOT/'inputs/PUBLIC.json')) or len(spec['plan'])!=32 or spec['binding']!=binding():raise ValueError('frozen study changed')
    stack().local.validate_store();return spec
