"""Fixed public inputs and private adapters; no current RL outcome dependency."""
import contextlib
import functools
import hashlib
import importlib.util
import json
import sys
from pathlib import Path

ROOT=Path(__file__).resolve().parent;SIDE=ROOT.parent
PRIOR=SIDE/'root-interface-sft-v1';ADAPTIVE=SIDE/'root-adaptive-rlvr-v1';LOCAL=SIDE/'root-interface-sft-local-runtime-v1'
NATIVE=Path('/project/alex_phd/envs/prime-rl-5990b1b/bin/python')
ROOT_SHA='efab2913e7fe9f5f9b381ae6eb67bb56071070f86b237e6145f98654816aad64'
CHILD_SHA='c32de1293c01bba5104eb1f123867649c71dd38e5194661ace4b17dcbbe66ba3'
SEEDS=(981306011,981306021);MASTER=981306001
def read(path):return json.loads(Path(path).read_text())
def sha(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()
def digest(value):return hashlib.sha256(json.dumps(value,sort_keys=True,separators=(',',':')).encode()).hexdigest()
def check(path,want):
    if sha(path)!=want:raise ValueError('frozen source changed: '+str(path))
def write(path,value):
    path=Path(path);path.parent.mkdir(parents=True,exist_ok=True)
    with path.open('x') as stream:json.dump(value,stream,indent=2,sort_keys=True,allow_nan=False);stream.write('\n')
def load(name,path,want=None):
    if want:check(path,want)
    spec=importlib.util.spec_from_file_location(name,path);m=importlib.util.module_from_spec(spec);sys.modules[name]=m;spec.loader.exec_module(m);return m
@contextlib.contextmanager
def aliases(mapping):
    saved={k:sys.modules.get(k) for k in mapping};sys.modules.update(mapping)
    try:yield
    finally:
        for k,v in saved.items():
            if v is None:sys.modules.pop(k,None)
            else:sys.modules[k]=v

@functools.lru_cache(maxsize=1)
def stack():
    prior=load('ledger_adaptive_study',ADAPTIVE/'study.py','df4e519f7e2fc932e2ae136fdcdada5896391330b67d9d4fc46f0e71d22822a6')
    with aliases({'study':prior}):native=load('ledger_adaptive_native',ADAPTIVE/'native.py','5d0c2e9421e28ba4f937671baa6ca03b347ec39af9167e8620dd0ac1bf400fda')
    return native.stack()

def inputs():
    public=read(PRIOR/'prepared-v2/PUBLIC.json');gold=read(PRIOR/'prepared-v2/HOST_GOLD.json')
    contexts=[next(c for c in public if c['id']==f'validation-{i:02d}') for i in range(4)]
    tasks=read(ADAPTIVE/'inputs/TASKS.json')
    return contexts,{c['id']:gold[c['id']]['answers']['global'] for c in contexts},tasks

def plan_for(contexts):
    rows=[]
    for index,context in enumerate(contexts):
        for repeat,seed in enumerate(SEEDS):
            arms=('map','ledger') if (index+repeat)%2==0 else ('ledger','map')
            pair=digest([ROOT.name,context['id'],seed])
            for position,arm in enumerate(arms):
                row={'context_id':context['id'],'context_window_id':stack().prior.context_window_id(context),
                     'task_name':'adaptive-'+context['id']+'-global','family':'global','arm':arm,'seed':seed,
                     'repeat':repeat,'pair_id':pair,'pair_order':position,'temperature':.5,'client_path':'train',
                     'exposure':'four_named_exposed_validation_contexts','records':len(context['records'])}
                row['id']=digest(row);rows.append(row)
    return rows

def binding():
    value=stack().native.initial_binding();old=value['role_map']['root'];value['models'].pop(old)
    selected=read(LOCAL/'outputs/attempt-001/training/RESULT.json')['selected']
    if selected['step']!=4 or selected['adapter_sha256']!=ROOT_SHA:raise ValueError('not fixed final4')
    alias='strict-rlm-qwen3-4b-root-interface-final4-ledger-v1'
    value['models'][alias]={'path':selected['checkpoint'],'adapter_sha256':ROOT_SHA,'config_sha256':selected['config_sha256']}
    value['role_map']['root']=alias
    if value['models'][value['fixed_child']]['adapter_sha256']!=CHILD_SHA:raise ValueError('child changed')
    value['ledger_study']=ROOT.name;return value

def verify():
    ready=read(ROOT/'READY.json')
    for path,want in ready['source_sha256'].items():check(path,want)
    spec=read(ROOT/'SPEC.json')
    if spec['plan']!=plan_for(read(ROOT/'inputs/PUBLIC.json')) or spec['binding']!=binding():raise ValueError('plan/binding changed')
    stack().local.validate_store()
    return spec
