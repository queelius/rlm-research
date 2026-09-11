"""Exact two-root binding and fresh three-arm plan; no evaluation outcome reads."""
import contextlib
import functools
import hashlib
import importlib.util
import json
import sys
from pathlib import Path

ROOT=Path(__file__).resolve().parent;SIDE=ROOT.parent;STORE=SIDE.parent
OLD=SIDE/'root-accumulation-ledger-v1'
TRAINING=SIDE/'root-success-trajectory-sft-v1/outputs/attempt-001/training'
NATIVE=Path('/project/alex_phd/envs/prime-rl-5990b1b/bin/python')
MASTER=981312001;SEEDS=(981312011,981312021)
ARMS=('map','always_counts','coverage_first')
WEIGHTS=tuple(sorted(('efab','success_sft8'),key=lambda x:hashlib.sha256(f'{MASTER}:{x}'.encode()).hexdigest()))
READY_SHA='4ccf83e1ea83357838d774514250e231c55bcc2a0d2494b88543db2c33b07561'
FINAL_SHA='66cce4009628ff7d8e047f08e6fb3a29febdbf8fb3ed8303871f69860f1151d5'
CONFIG_SHA='118bb737297c35d96a194b642026b1e58c72f945d55ae1616eb716cfc4601728'
STATE_SHA='506fc355e19b3201822ee1f6fb88eca1edd23e04219787b1d84484598f9531f2'
RESULT_SHA='d3279d748b618e0b50103e066c2680e1d3b59c1a13a37c36243d58812611a4a0'
def read(path):return json.loads(Path(path).read_text())
def sha(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()
def digest(value):return hashlib.sha256(json.dumps(value,sort_keys=True,separators=(',',':')).encode()).hexdigest()
def check(path,want):
    if sha(path)!=want:raise ValueError('frozen source changed: '+str(path))
def write(path,value):
    path=Path(path);path.parent.mkdir(parents=True,exist_ok=True)
    with path.open('x') as stream:json.dump(value,stream,indent=2,sort_keys=True,allow_nan=False);stream.write('\n')
def load(name,path,want):
    check(path,want);spec=importlib.util.spec_from_file_location(name,path);m=importlib.util.module_from_spec(spec);sys.modules[name]=m;spec.loader.exec_module(m);return m
@contextlib.contextmanager
def aliases(mapping):
    old={k:sys.modules.get(k) for k in mapping};sys.modules.update(mapping)
    try:yield
    finally:
        for k,v in old.items():
            if v is None:sys.modules.pop(k,None)
            else:sys.modules[k]=v
@functools.lru_cache(maxsize=1)
def old_pins():
    check(OLD/'READY.json',READY_SHA);return read(OLD/'READY.json')['source_sha256']
@functools.lru_cache(maxsize=1)
def original():return load('coverage_original_study',OLD/'study.py',old_pins()[str(OLD/'study.py')])
def stack():
    # Inherited imports prepend old study directories; preserve our entrypoint namespace.
    paths=list(sys.path)
    try:
        with aliases({'study':original()}):return original().stack()
    finally:sys.path[:]=paths
@functools.lru_cache(maxsize=1)
def contract():return load('coverage_batch_contract',SIDE/'adaptive-filter-pilot-v1/batch_contract.py','d2c7f8df62a4190930dbf3e14f7e68cfb27cc573898bbc343117e8d97190bd88')
def inputs():return tuple(read(OLD/'inputs'/name) for name in ('PUBLIC.json','HOST_GOLD.json','TASKS.json'))
def plan_for(contexts):
    plan=[]
    for weight in WEIGHTS:
        for i,context in enumerate(contexts):
            for repeat,seed in enumerate(SEEDS):
                index=2*i+repeat;rotation=index%3;arms=ARMS[rotation:]+ARMS[:rotation]
                matched=digest([ROOT.name,context['id'],seed]);triple=digest([matched,weight])
                for position,arm in enumerate(arms):
                    row={'weight':weight,'arm':arm,'context_id':context['id'],
                        'context_window_id':stack().prior.context_window_id(context),'task_name':'adaptive-'+context['id']+'-global',
                        'family':'global','records':len(context['records']),'seed':seed,'repeat':repeat,
                        'temperature':.5,'client_path':'train','matched_coordinate':matched,'triple_id':triple,'triple_order':position,
                        'block_order':index,'exposure':'four_named_exposed_validation_contexts'}
                    plan.append({**row,'id':digest(row)})
    return plan
@functools.lru_cache(maxsize=1)
def final8_identity():
    ready_path=TRAINING.parents[2]/'READY.json'
    check(ready_path,'ced16becb584a709d7da0faa122b5343def395168909d52d66eb762fe6ef3a9c')
    check(TRAINING/'RESULT.json',RESULT_SHA);result=read(TRAINING/'RESULT.json')
    chosen=result['selected'];cp=TRAINING/'checkpoint-0008'
    if not result['complete'] or result['optimizer_steps']!=8 or chosen['step']!=8 or chosen['checkpoint']!=str(cp) or result['identity']!=read(ready_path)['identity']:raise ValueError('fixed final8 unavailable')
    if chosen['adapter_sha256']!=FINAL_SHA or chosen['config_sha256']!=CONFIG_SHA or chosen['state_sha256']!=STATE_SHA:raise ValueError('fixed final8 identity differs')
    check(cp/'state.json',STATE_SHA);state=read(cp/'state.json')
    if state['step']!=8 or state['identity']!=result['identity']:raise ValueError('fixed final8 state differs')
    for name,want in state['files_sha256'].items():check(cp/name,want)
    check(cp/'adapter_model.safetensors',FINAL_SHA);check(cp/'adapter_config.json',CONFIG_SHA)
    return chosen
def binding(weight):
    if weight not in WEIGHTS:raise ValueError('unknown fixed root')
    value=read(OLD/'SPEC.json')['binding'];old=value['role_map']['root'];model=value['models'].pop(old)
    if weight=='success_sft8':
        selected=final8_identity();model={'path':selected['checkpoint'],'adapter_sha256':FINAL_SHA,'config_sha256':CONFIG_SHA}
    elif model['adapter_sha256']!='efab2913e7fe9f5f9b381ae6eb67bb56071070f86b237e6145f98654816aad64':raise ValueError('efab changed')
    alias='strict-rlm-qwen3-4b-root-coverage-'+weight+'-v1'
    value['models'][alias]=model;value['role_map']['root']=alias
    if value['models'][value['fixed_child']]['adapter_sha256']!='c32de1293c01bba5104eb1f123867649c71dd38e5194661ace4b17dcbbe66ba3':raise ValueError('fixed child differs')
    value['ledger_study']=ROOT.name;value['coverage_root']=weight
    return value
def verify():
    ready=read(ROOT/'READY.json')
    for path,want in ready['source_sha256'].items():check(path,want)
    spec=read(ROOT/'SPEC.json')
    if spec['plan']!=plan_for(read(ROOT/'inputs/PUBLIC.json')) or spec['bindings']!={w:binding(w) for w in WEIGHTS}:raise ValueError('plan or bindings changed')
    stack().local.validate_store();return spec
