"""Pinned exact-tag runtime in an immutable alien-control namespace."""
import contextlib,hashlib,importlib.util,json,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parent;SIDE=ROOT.parent;SOURCE=SIDE/'leaf-mnli-exact-tag-correspondence-v1';BASE=SIDE/'leaf-mnli-correspondence-v1';ATTEMPT=ROOT/'outputs/attempt-001';READY_PATH=ROOT/'READY_v2.json';NATIVE=Path('/project/alex_phd/envs/prime-rl-5990b1b/bin/python')
def sha(path):
    with Path(path).open('rb') as handle:return hashlib.file_digest(handle,'sha256').hexdigest()
def read(path): return json.loads(Path(path).read_text())
def write(path,value):
    path=Path(path);path.parent.mkdir(parents=True,exist_ok=True)
    with path.open('x') as f:json.dump(value,f,ensure_ascii=False,sort_keys=True,indent=2,allow_nan=False);f.write('\n')
def serialize(value):return json.dumps(value,ensure_ascii=False,separators=(',',':'),allow_nan=False)
def digest(value):return hashlib.sha256(json.dumps(value,sort_keys=True,separators=(',',':')).encode()).hexdigest()
def load(name,path,pin=None,aliases=None):
    if pin and sha(path)!=pin:raise ValueError('source changed: '+str(path))
    spec=importlib.util.spec_from_file_location(name,path);m=importlib.util.module_from_spec(spec);sys.modules[name]=m
    with globals()['aliases'](aliases or {}):spec.loader.exec_module(m)
    return m
@contextlib.contextmanager
def aliases(values):
    old={k:sys.modules.get(k) for k in values};sys.modules.update(values)
    try:yield
    finally:
        for k,v in old.items():sys.modules.pop(k,None) if v is None else sys.modules.__setitem__(k,v)
exact=load('alien_qualified_exact_study',SOURCE/'study.py','f9ea298030b351821a7cc46d728bd3261ad4cef7f6be9b08cf2825f2e484dff2')
base,MODEL,service,lifecycle=exact.base,exact.MODEL,exact.service,exact.lifecycle
def tokenizer():return exact.tokenizer()
def verify():
    ready=read(READY_PATH)
    if digest({k:v for k,v in ready.items() if k!='identity'})!=ready['identity']:raise ValueError('READY identity')
    for path,pin in {**ready['source_sha256'],**ready['input_sha256']}.items():
        if sha(path)!=pin:raise ValueError('closure changed: '+path)
    return ready
