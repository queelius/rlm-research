"""Isolated diagnostic namespace; qualified QSR and actual an27 seams only."""
import functools
import hashlib
import importlib.util
import json
from pathlib import Path
import sys

ROOT=Path(__file__).resolve().parent;SIDE=ROOT.parent;QSR=SIDE/'root-query-sensitive-rl-v1'
ATTEMPT=ROOT/'outputs/attempt-001';NAMESPACE='root-warmstart-reference-v1'
def sha(path):
    with Path(path).open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
def read(path):return json.loads(Path(path).read_text())
def write(path,value):
    path=Path(path);path.parent.mkdir(parents=True,exist_ok=True)
    with path.open('x') as f:json.dump(value,f,sort_keys=True,indent=2,allow_nan=False);f.write('\n')
def digest(v):return hashlib.sha256(json.dumps(v,sort_keys=True,separators=(',',':'),allow_nan=False).encode()).hexdigest()
def check(path,pin):
    if sha(path)!=pin:raise ValueError('source identity changed: '+str(path))
def load(name,path,pin):
    check(path,pin);spec=importlib.util.spec_from_file_location(name,path);m=importlib.util.module_from_spec(spec);sys.modules[name]=m;spec.loader.exec_module(m);return m
qsr=load('warm_reference_qualified_qsr',QSR/'qsr_study.py','370628daceaaacdc552edef112b50644164fd7ac09350c91444c25abcebca19b')
aliases=qsr.aliases;NATIVE=qsr.NATIVE;RUNTIME=qsr.RUNTIME;CHILD_SHA=qsr.CHILD_SHA
INPUT_PINS={'PUBLIC.json':'3ff6c42e81e4acf62ad99b3b3d8492d326e0499e42a5a4bf73505433a890fd56','GROUPS.json':'99984ddb15ac2b15ccf86a2cdcfa40016ff86507b5448b1ab29695187e9765c6','PROVENANCE.json':'6c1bce9e30f48f159ba24450883e7a1c036869eb3ae33d5bcddacc29f4d09c4b','QUERIES.json':'3eb377878fab3537a69f34812adeb61e450863a25887d800116395a6e031b155','TASKS.json':'082050c100e3f7eb997ac626d332a27979218c9e8d09688286f3b4af7baaf6f8','HOST_GOLD.json':'8e045dbfe7b21e3beed4747c17304358f1875603fdaac5d980f0ae3bc1fa9954','PLANS.json':'50f2e1270be45b0311463cf4eced466a74115ae7fc233522f030ad57a2c98187'}
def inputs():
    for name,pin in INPUT_PINS.items():check(QSR/'inputs'/name,pin)
    return {name:read(QSR/'inputs'/name) for name in INPUT_PINS}
@functools.lru_cache(maxsize=1)
def qnative():
    with aliases({'qsr_study':qsr}):return load('warm_reference_qualified_native',QSR/'qsr_native.py','02aea033ef02a215577af03e18769adda0d9994e947900b310b1a7ee8356441c')
@functools.lru_cache(maxsize=1)
def contract():return load('warm_reference_batch',SIDE/'adaptive-filter-pilot-v1/batch_contract.py','d2c7f8df62a4190930dbf3e14f7e68cfb27cc573898bbc343117e8d97190bd88')
def runtime():return qsr.runtime()
ROOTS={
'released_reference':dict(path=str(SIDE/'single-gpu-self-sft-control-v1/inputs/step0-peft-key-conversion-v2'),adapter_sha256='857a7ce6907c759a8c1b478eb53029d3b700b81c3094d8edb3394e52def9fcb6',config_sha256='e6828a7cbb97028a871958e71ba6b8a75ac4887c25008ac4dbf7366bd298fbc4'),
'interface4':dict(path=str(SIDE/'root-interface-sft-local-runtime-v1/outputs/attempt-001/training/checkpoint-0004'),adapter_sha256='efab2913e7fe9f5f9b381ae6eb67bb56071070f86b237e6145f98654816aad64',config_sha256='d665754d496ad234fd441cfb340d2f597a8f13e7763a3f0592bf28720ef85a57'),
'success8':dict(path=str(SIDE/'root-success-trajectory-sft-v1/outputs/attempt-001/training/checkpoint-0008'),adapter_sha256='66cce4009628ff7d8e047f08e6fb3a29febdbf8fb3ed8303871f69860f1151d5',config_sha256='118bb737297c35d96a194b642026b1e58c72f945d55ae1616eb716cfc4601728')}
def binding(arm):
    model=ROOTS[arm];old=read(SIDE/'leaf-role-routing-v1/BOUND_WEIGHTS.json');child='strict-rlm-qwen3-4b-role-sft-selected-v1';root='strict-rlm-qwen3-4b-warm-reference-'+arm+'-v1'
    if old['models'][child]['adapter_sha256']!=CHILD_SHA:raise ValueError('fixed child differs')
    models={root:model,child:old['models'][child]}
    for value in models.values():
        check(Path(value['path'])/'adapter_model.safetensors',value['adapter_sha256']);check(Path(value['path'])/'adapter_config.json',value['config_sha256'])
    return {**old,'models':models,'role_map':dict(root=root,children=[child]),'fixed_child':child,'fixed_root':dict(arm=arm,model=model,selection='prospective fixed checkpoint, no performance selection'),'study':ROOT.name,'diagnostic_no_training':True}
def verify():
    ready=read(ROOT/'READY.json')
    if digest({k:v for k,v in ready.items() if k!='identity'})!=ready['identity']:raise ValueError('READY canonical identity')
    for path,pin in {**ready['source_sha256'],**ready['input_sha256']}.items():check(path,pin)
    for arm in ROOTS:binding(arm)
    return ready
