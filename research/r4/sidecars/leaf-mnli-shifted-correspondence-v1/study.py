"""Pinned released-base runtime and local immutable namespace."""
import contextlib, hashlib, importlib.util, json, sys
from pathlib import Path

ROOT=Path(__file__).resolve().parent
SIDE=ROOT.parent
BASE=SIDE/'leaf-mnli-correspondence-v1'
ATTEMPT=ROOT/'outputs/attempt-001'
READY_PATH=ROOT/'READY_V2.json'
NATIVE=Path('/project/alex_phd/envs/prime-rl-5990b1b/bin/python')

def sha(path):
    with Path(path).open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
def read(path):return json.loads(Path(path).read_text())
def write(path,value):
    path=Path(path);path.parent.mkdir(parents=True,exist_ok=True)
    with path.open('x') as f:json.dump(value,f,ensure_ascii=False,sort_keys=True,indent=2,allow_nan=False);f.write('\n')
def serialize(value):return json.dumps(value,ensure_ascii=False,separators=(',',':'),allow_nan=False)
def digest(value):return hashlib.sha256(json.dumps(value,ensure_ascii=False,sort_keys=True,separators=(',',':'),allow_nan=False).encode()).hexdigest()
def load(name,path,pin):
    if sha(path)!=pin:raise ValueError('immutable source changed: '+str(path))
    spec=importlib.util.spec_from_file_location(name,path);module=importlib.util.module_from_spec(spec)
    sys.modules[name]=module;spec.loader.exec_module(module);return module
@contextlib.contextmanager
def aliases(values):
    old={k:sys.modules.get(k) for k in values};sys.modules.update(values)
    try:yield
    finally:
        for k,v in old.items():sys.modules.pop(k,None) if v is None else sys.modules.__setitem__(k,v)

base=load('mnli_shift_qualified_base',BASE/'study.py','8ad422e666972a2a9e314b5c9eb24266dd72c0286d4dfb9d48a9af8cbc156dd8')
MODEL,service,lifecycle=base.MODEL,base.service,base.lifecycle
def validate_weights():return base.validate_weights()
def tokenizer():return base.tokenizer()
def verify():
    ready=read(READY_PATH)
    if digest({k:v for k,v in ready.items() if k!='identity'})!=ready['identity']:raise ValueError('READY identity')
    for path,pin in ready['source_sha256'].items():
        if sha(path)!=pin:raise ValueError('READY closure changed: '+path)
    validate_weights();return ready
