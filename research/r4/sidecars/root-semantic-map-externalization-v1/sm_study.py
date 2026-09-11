"""Unique isolated fixed857/c32 namespace; no training or environment mutation."""
import contextlib
import hashlib
import importlib.util
import json
from pathlib import Path
import sys
ROOT=Path(__file__).resolve().parent;SIDE=ROOT.parent;CE=SIDE/'root-qsr-contract-evidence-v1';QSR=SIDE/'root-query-sensitive-rl-v1'
ATTEMPT=ROOT/'outputs/attempt-001';NAMESPACE='semantic-map-externalization-20260910-v1'
def sha(path):
    with Path(path).open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
def read(path):return json.loads(Path(path).read_text())
def write(path,value):
    path=Path(path);path.parent.mkdir(parents=True,exist_ok=True)
    with path.open('x') as f:json.dump(value,f,sort_keys=True,indent=2,allow_nan=False);f.write('\n')
def digest(value):return hashlib.sha256(json.dumps(value,sort_keys=True,separators=(',',':'),allow_nan=False).encode()).hexdigest()
def check(path,pin):
    if sha(path)!=pin:raise ValueError('immutable source changed: '+str(path))
@contextlib.contextmanager
def aliases(values):
    old={k:sys.modules.get(k) for k in values};path=list(sys.path);sys.modules.update(values)
    try:yield
    finally:
        sys.path[:]=path
        for k,v in old.items():
            if v is None:sys.modules.pop(k,None)
            else:sys.modules[k]=v
def load(name,path,pin,mapping=None):
    check(path,pin)
    with aliases(mapping or {}):
        spec=importlib.util.spec_from_file_location(name,path);module=importlib.util.module_from_spec(spec);sys.modules[name]=module;spec.loader.exec_module(module)
    return module
qualified=load('sm_qualified_ce_study',CE/'study.py','731d4dee08748de7c4f363ec60fb3ce122ca27faace2864e00fe6b4d42b25cf1')
qsr=qualified.qsr;NATIVE=qualified.NATIVE;RUNTIME=qualified.RUNTIME;CHILD_SHA=qualified.CHILD_SHA;INPUT_PINS=qualified.INPUT_PINS
inputs=qualified.inputs;qnative=qualified.qnative;contract=qualified.contract;runtime=qualified.runtime
REFERENCE=SIDE/'root-warmstart-reference-v1/outputs/attempt-001/released_reference/service/BINDING.json'
REFERENCE_SHA='5d1a4fa155219a2b6fe3334ebf02bcd528f7fb2563a3da615c1b7252292584b3'
def binding():
    check(REFERENCE,REFERENCE_SHA);value=read(REFERENCE);root=value['models'].pop(value['role_map']['root']);alias='strict-rlm-qwen3-4b-semantic-map-reference857-v1'
    if root['adapter_sha256']!='857a7ce6907c759a8c1b478eb53029d3b700b81c3094d8edb3394e52def9fcb6' or value['models'][value['fixed_child']]['adapter_sha256']!=CHILD_SHA:raise ValueError('fixed857/c32')
    value['models'][alias]=root;value['role_map']['root']=alias;value['study']=ROOT.name;value['no_training']=True
    for model in value['models'].values():
        check(Path(model['path'])/'adapter_model.safetensors',model['adapter_sha256']);check(Path(model['path'])/'adapter_config.json',model['config_sha256'])
    return value
def verify():
    value=read(ROOT/'READY.json')
    if digest({k:v for k,v in value.items() if k!='identity'})!=value['identity']:raise ValueError('READY identity')
    for path,pin in {**value['source_sha256'],**value['input_sha256']}.items():check(path,pin)
    binding();return value
