"""Explicit-path isolated reuse; starting policy is never implicitly selected."""
import contextlib
import functools
import hashlib
import importlib.util
import json
from pathlib import Path
import sys
from types import SimpleNamespace

ROOT=Path(__file__).resolve().parent;SIDE=ROOT.parent;QSR=SIDE/'root-query-sensitive-rl-v1';JOINT=SIDE/'root-joint-state-reduction-sft-v1';ATTEMPT=ROOT/'outputs/attempt-001'
NATIVE=Path('/project/alex_phd/envs/prime-rl-5990b1b/bin/python')
TRAIN=Path('/project/alex_phd/repos/rlm-bootstrap/.worktrees/a100-lora-roundtrip/gpu/training/.venv/bin/python')
CHILD_SHA='c32de1293c01bba5104eb1f123867649c71dd38e5194661ace4b17dcbbe66ba3'
SOURCE_PINS={'PUBLIC.json':'3ff6c42e81e4acf62ad99b3b3d8492d326e0499e42a5a4bf73505433a890fd56','GROUPS.json':'99984ddb15ac2b15ccf86a2cdcfa40016ff86507b5448b1ab29695187e9765c6','QUERIES.json':'3eb377878fab3537a69f34812adeb61e450863a25887d800116395a6e031b155','HOST_GOLD.json':'8e045dbfe7b21e3beed4747c17304358f1875603fdaac5d980f0ae3bc1fa9954','PLANS.json':'50f2e1270be45b0311463cf4eced466a74115ae7fc233522f030ad57a2c98187'}

def sha(path):
    with Path(path).open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
def read(path):return json.loads(Path(path).read_text())
def write(path,value):
    path=Path(path);path.parent.mkdir(parents=True,exist_ok=True)
    with path.open('x') as f:json.dump(value,f,sort_keys=True,indent=2,allow_nan=False);f.write('\n')
def digest(value):return hashlib.sha256(json.dumps(value,sort_keys=True,separators=(',',':'),allow_nan=False).encode()).hexdigest()

@contextlib.contextmanager
def aliases(mapping):
    before={k:sys.modules.get(k) for k in mapping};path=list(sys.path);sys.modules.update(mapping)
    try:yield
    finally:
        sys.path[:]=path
        for k,v in before.items():
            if v is None:sys.modules.pop(k,None)
            else:sys.modules[k]=v

def load(name,path,pin,mapping=None):
    if sha(path)!=pin:raise ValueError('qualified source changed: '+str(path))
    with aliases(mapping or {}):
        spec=importlib.util.spec_from_file_location(name,path);module=importlib.util.module_from_spec(spec);sys.modules[name]=module;spec.loader.exec_module(module)
    return module

def source_inputs():
    for name,pin in SOURCE_PINS.items():
        if sha(QSR/'inputs'/name)!=pin:raise ValueError('QSR source changed')
    return {name:read(QSR/'inputs'/name) for name in SOURCE_PINS}

@functools.lru_cache(maxsize=1)
def qsr():return load('od_qualified_qsr_study',QSR/'qsr_study.py','370628daceaaacdc552edef112b50644164fd7ac09350c91444c25abcebca19b')
@functools.lru_cache(maxsize=1)
def qnative():return load('od_qualified_qsr_native',QSR/'qsr_native.py','02aea033ef02a215577af03e18769adda0d9994e947900b310b1a7ee8356441c',{'qsr_study':qsr()})
@functools.lru_cache(maxsize=1)
def joint():return load('od_qualified_joint_study',JOINT/'joint_study.py','92a63ea4b9e871802eaab3e0497742b93380b0cc36504c000643536c2a42ba8d')

def starting_policy(path=None):
    path=Path(path) if path else ROOT/'inputs/START_BINDING.json';value=read(path)
    if value['decision']!='MAIN_APPROVED_START' or value['selection_name'] not in ('857','efab','66c'):raise ValueError('explicit approved generational start required')
    selected=value['selected'];directory=Path(selected['checkpoint'])
    for filename,key in [('adapter_model.safetensors','adapter_sha256'),('adapter_config.json','config_sha256')]:
        if sha(directory/filename)!=selected[key]:raise ValueError('starting checkpoint identity changed')
    if not value['lineage_receipt_sha256'] or sha(value['lineage_receipt_path'])!=value['lineage_receipt_sha256']:raise ValueError('starting lineage receipt changed')
    if sha(value['conversion_path'])!=value['conversion_sha256'] or sha(value['base_manifest_path'])!=value['base_manifest_sha256']:raise ValueError('conversion/base provenance changed')
    return selected

def runtime():return qsr().runtime()
def interface(output):return qnative().interface(output)
@functools.lru_cache(maxsize=1)
def stack():
    native=qnative().stack().native
    def task(context,prompt,gold,name):
        query=read(ROOT/'inputs/PROMPTS_ACCURATE.json')[name]['plain_query']
        value=qnative().make_task(context,query,gold,name)
        if value.data.prompt!=prompt:raise ValueError('exact common native prompt mismatch')
        return value
    return SimpleNamespace(native=SimpleNamespace(**{**vars(native),'task':task}))

def answer(records,labels,row):
    selected=[r for r in records if (row['scope']=='all' or r['user'] in row['users']) and labels[r['id']]==row['target']]
    if row['operator']=='count':return len(selected)
    if row['operator']=='distinct':return len({r['user'] for r in selected})
    if row['operator']=='weight':return sum(r['weight'] for r in selected)
    raise ValueError('operator')

def corpus(limit=None):
    directory=ATTEMPT/'capture';plan=read(ROOT/'inputs/TRAIN_PLAN.json')
    if limit is None:
        frozen=read(directory/'CORPUS_READY.json')
        if frozen['identity']!=verify()['identity'] or frozen['examples']!=72:raise ValueError('complete fixed72 corpus required')
        for path,pin in frozen['files_sha256'].items():
            if sha(path)!=pin:raise ValueError('corpus changed')
    return [read(directory/r['id']/'TEACHER.json') for r in plan[:limit]]

def verify():
    value=read(ROOT/'READY_v2.json')
    if digest({k:v for k,v in value.items() if k!='identity'})!=value['identity']:raise ValueError('READY identity')
    for path,pin in {**value['source_sha256'],**value['input_sha256']}.items():
        if sha(path)!=pin:raise ValueError('READY pin changed '+path)
    starting_policy();return value
