"""Exposed-context output-field-order experiment; qualified base service."""
import contextlib, hashlib, importlib.util, json, sys
from pathlib import Path

ROOT=Path(__file__).resolve().parent;SIDE=ROOT.parent
QUALIFIED=SIDE/'leaf-mnli-new-context-alien-correspondence-v1';SOURCE=SIDE/'leaf-mnli-exact-tag-correspondence-v1'
BASE=SIDE/'leaf-mnli-correspondence-v1';ATTEMPT=ROOT/'outputs/attempt-001';READY_PATH=ROOT/'READY_v2.json'
NATIVE=Path('/project/alex_phd/envs/prime-rl-5990b1b/bin/python')
def sha(path):
    with Path(path).open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
def read(path):return json.loads(Path(path).read_text())
def write(path,value):
    path=Path(path);path.parent.mkdir(parents=True,exist_ok=True)
    with path.open('x') as f:json.dump(value,f,ensure_ascii=False,sort_keys=True,indent=2,allow_nan=False);f.write('\n')
def serialize(value):return json.dumps(value,ensure_ascii=False,separators=(',',':'),allow_nan=False)
def digest(value):return hashlib.sha256(json.dumps(value,sort_keys=True,separators=(',',':')).encode()).hexdigest()
@contextlib.contextmanager
def aliases(values):
    old={k:sys.modules.get(k) for k in values};sys.modules.update(values)
    try:yield
    finally:
        for k,v in old.items():sys.modules.pop(k,None) if v is None else sys.modules.__setitem__(k,v)
def load(name,path,pin=None,aliases_map=None):
    if pin and sha(path)!=pin:raise ValueError('source changed: '+str(path))
    spec=importlib.util.spec_from_file_location(name,path);m=importlib.util.module_from_spec(spec);sys.modules[name]=m
    with aliases(aliases_map or {}):spec.loader.exec_module(m)
    return m
qualified=load('visible_reference_qualified_study',QUALIFIED/'study.py','58839d48f34d13c623be7ae580dbd0343573a0facc559f33bb1fa4982b0fe138')
base,MODEL,service,lifecycle=qualified.base,qualified.MODEL,qualified.service,qualified.lifecycle
ALIEN=qualified.ALIEN
def tokenizer():return qualified.tokenizer()
def verify():
    ready=read(READY_PATH)
    if digest({k:v for k,v in ready.items() if k!='identity'})!=ready['identity']:raise ValueError('READY identity')
    for path,pin in {**ready['source_sha256'],**ready['input_sha256']}.items():
        if sha(path)!=pin:raise ValueError('closure changed: '+path)
    return ready

PRIOR = SIDE / 'leaf-mnli-visible-reference-disambiguation-v1'
