"""Isolated fixed-six continuation identities and qualified source composition."""
import functools
import hashlib
import importlib.util
import json
from pathlib import Path
import sys
from types import SimpleNamespace

ROOT=Path(__file__).resolve().parent;SIDE=ROOT.parent;STORE=SIDE.parent
OLD=SIDE/'root-operator-diverse-sft-v1';RECOVERY=SIDE/'root-operator-diverse-sft-completion-v1'
START=RECOVERY/'outputs/attempt-001/training/checkpoint-0006'
ATTEMPT=ROOT/'outputs/attempt-001'
START_SHA='efe7efc1b7b1ed642d04a1bee0ea4a3d5a6c1ac5b9575f89ad22d3e3ac2518cb'
CORPUS_SHA='207d36997fe82c390a82e3b27c4e3ad863ba5fdc07f00574cbd2084e80792ea9'
INVENTORY=STORE/'ideas/2026-09-10-operator-next-training-source-inventory.json'
INVENTORY_SHA='31bec7c63b53bbb60ebbc588beea895d1ef40d2242fc546da099b4da35fdf70f'
MASTER=981651003

def sha(path):
    with Path(path).open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
def read(path):return json.loads(Path(path).read_text())
def write(path,value):
    path=Path(path);path.parent.mkdir(parents=True,exist_ok=True)
    with path.open('x') as f:json.dump(value,f,sort_keys=True,indent=2,allow_nan=False);f.write('\n')
def digest(value):return hashlib.sha256(json.dumps(value,sort_keys=True,separators=(',',':'),allow_nan=False).encode()).hexdigest()
def check(path,pin):
    if sha(path)!=pin:raise ValueError('source pin mismatch: '+str(path))

@functools.lru_cache(maxsize=1)
def original():
    path=OLD/'od_study.py';check(path,'3d437ec69d3a1f0dfa038e5c7bbd7dcd770c512b39660385cc9a6759e29d2143')
    spec=importlib.util.spec_from_file_location('dose_original_study',path);m=importlib.util.module_from_spec(spec);sys.modules[spec.name]=m;spec.loader.exec_module(m);return m
def load(name,path,mapping=None):
    pin=read(OLD/'READY_v2.json')['source_sha256'].get(str(path))
    if pin is None:raise ValueError('not in original source closure '+str(path))
    return original().load(name,path,pin,mapping)
@functools.lru_cache(maxsize=1)
def learning():return load('dose_original_learning',OLD/'od_learning.py',{'od_study':original()})
@functools.lru_cache(maxsize=1)
def protocol():return load('dose_original_protocol',OLD/'od_protocol.py',{'od_study':original()})
def corpus():
    check(OLD/'outputs/attempt-001/capture/CORPUS_READY.json',CORPUS_SHA)
    return original().corpus()
def model_loader(output):
    o=original();j=o.joint();view=SimpleNamespace(**{**vars(j),'START':START,'START_SHA':START_SHA})
    m=o.load('dose_original_model_loader',o.JOINT/'train.py','6491520cf407642f9607413621591cb1dd5c6b139f96c90d784880f4f1f6e405',{'joint_study':view,'joint_learning':learning()})
    m.SEED=981451003
    return m.load_model(output)
def base_path():return original().joint().original.prior().BASE
def dependencies():
    r=original().load('dose_original_recovery',RECOVERY/'recovery.py',read(RECOVERY/'READY.json')['source_sha256'][str(RECOVERY/'recovery.py')])
    return r.dependencies()
def verify():
    value=read(ROOT/'READY.json')
    if digest({k:v for k,v in value.items() if k!='identity'})!=value['identity']:raise ValueError('identity')
    for p,h in {**value['source_sha256'],**value['input_sha256']}.items():check(p,h)
    check(START/'adapter_model.safetensors',START_SHA);corpus();return value
