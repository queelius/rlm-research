"""Qualified original free-runtime seam; no training or service calls on import."""
import functools
import hashlib
import importlib.util
import json
from pathlib import Path
import sys

ROOT=Path(__file__).resolve().parent
SIDE=ROOT.parent
OLD=SIDE/'root-joint-state-reduction-sft-v1'
QSR=SIDE/'root-query-sensitive-rl-v1'
ATTEMPT=ROOT/'outputs/attempt-001'
MASTER=981401001
ARMS=('unchanged','joint','reduction_stop')

def sha(path):
    with Path(path).open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
def read(path):return json.loads(Path(path).read_text())
def write(path,value):
    path=Path(path);path.parent.mkdir(parents=True,exist_ok=True)
    with path.open('x') as f:json.dump(value,f,sort_keys=True,indent=2,allow_nan=False);f.write('\n')
def digest(value):return hashlib.sha256(json.dumps(value,sort_keys=True,separators=(',',':'),allow_nan=False).encode()).hexdigest()
def check(path,pin):
    if sha(path)!=pin:raise ValueError('source changed '+str(path))
def load(name,path,pin):
    check(path,pin);spec=importlib.util.spec_from_file_location(name,path);m=importlib.util.module_from_spec(spec);sys.modules[name]=m;spec.loader.exec_module(m);return m

source=load('transfer_qualified_joint_study',OLD/'joint_study.py','92a63ea4b9e871802eaab3e0497742b93380b0cc36504c000643536c2a42ba8d')
NATIVE,RUNTIME,START,START_SHA,CHILD_SHA,LABELS,aliases=(source.NATIVE,source.RUNTIME,source.START,source.START_SHA,source.CHILD_SHA,source.LABELS,source.aliases)
BASE_CORRECTIVE=source.BASE_CORRECTIVE

def stack():
    st=source.stack();st.prior.ROOT=ROOT;sys.path.insert(0,str(ROOT));return st
def runtime():return source.runtime()
def interface(output):
    wrapper,_=runtime();st=wrapper.adapt_stack(stack())
    with aliases({'interface':st.interface}):value=st.local.configure_interface(output)
    sys.path.insert(0,str(ROOT));return value
def phases():return tuple(sorted(ARMS,key=lambda arm:digest([MASTER,'phase',arm])))
def verify():
    value=read(ROOT/'READY.json')
    if digest({k:v for k,v in value.items() if k!='identity'})!=value['identity']:raise ValueError('READY identity')
    for path,pin in {**value['source_sha256'],**value['input_sha256']}.items():check(path,pin)
    return value

@functools.lru_cache(maxsize=1)
def original_binding():
    with aliases({'joint_study':source}):return load('transfer_qualified_joint_binding',OLD/'joint_binding.py','c1dfea29f9c745904128bcb892afc15f6659561c977bcb2c7b170a98723ad509')

@functools.lru_cache(maxsize=1)
def original_protocol():
    with aliases({'joint_study':source}):return load('transfer_qualified_joint_protocol',OLD/'joint_protocol.py','9cd776cf132784d0c589266d89e2e9613fd83a6f3126ff1a5f95657d6359a8b7')
