"""Isolated namespace over pinned qualified semantic-map dependencies."""
import contextlib
import hashlib
import importlib.util
import json
from pathlib import Path
import sys

ROOT=Path(__file__).resolve().parent;SIDE=ROOT.parent;SM=SIDE/'root-semantic-map-externalization-v1'
ATTEMPT=ROOT/'outputs/attempt-001';NAMESPACE='canonical-source-loader-20260910-v1'
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
qualified=load('cl_qualified_sm_study',SM/'sm_study.py','ce14a7aedb835031607f5e8f96cc6f58315f3d4bc6bcac4d86a3344c923a5c42')
CE=qualified.CE;QSR=qualified.QSR;NATIVE=qualified.NATIVE;RUNTIME=qualified.RUNTIME;CHILD_SHA=qualified.CHILD_SHA
INPUT_PINS=qualified.INPUT_PINS;inputs=qualified.inputs;qnative=qualified.qnative;contract=qualified.contract;runtime=qualified.runtime
REFERENCE=qualified.REFERENCE;REFERENCE_SHA=qualified.REFERENCE_SHA
def binding():
    value=qualified.binding();root=value['models'].pop(value['role_map']['root']);alias='strict-rlm-qwen3-4b-canonical-loader-reference857-v1'
    value['models'][alias]=root;value['role_map']['root']=alias;value['study']=ROOT.name;return value
def verify():
    value=read(ROOT/'READY.json')
    if digest({k:v for k,v in value.items() if k!='identity'})!=value['identity']:raise ValueError('READY identity')
    for path,pin in {**value['source_sha256'],**value['input_sha256']}.items():check(path,pin)
    binding();return value
