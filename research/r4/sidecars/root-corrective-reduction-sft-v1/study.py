"""New corrective-action study over immutable native/LoRA/lifecycle sources."""
import functools
import hashlib
import importlib.util
import json
from pathlib import Path
import sys

ROOT=Path(__file__).resolve().parent
SOURCE=ROOT.parent/'root-complete-demonstration-sft-v1'
RUNTIME=ROOT.parent/'runtime-an27-5780-v1'
ATTEMPT=ROOT/'outputs/attempt-001'
ARMS=('first_producer','corrective')
MASTER=981351001

def sha(path):
    with Path(path).open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
def read(path):return json.loads(Path(path).read_text())
def write(path,value):
    path=Path(path);path.parent.mkdir(parents=True,exist_ok=True)
    with path.open('x') as f:json.dump(value,f,indent=2,sort_keys=True,allow_nan=False);f.write('\n')
def digest(value):return hashlib.sha256(json.dumps(value,sort_keys=True,separators=(',',':'),allow_nan=False).encode()).hexdigest()
def load(name,path,pin):
    if sha(path)!=pin:raise ValueError('pinned source changed: '+str(path))
    spec=importlib.util.spec_from_file_location(name,path);m=importlib.util.module_from_spec(spec);sys.modules[name]=m;spec.loader.exec_module(m);return m

original=load('corrective_original_complete',SOURCE/'study.py','26388b27fb97379145b87cfa60aeb7b93502e6880feb2e6a7ee33e652c70c1cb')
NATIVE,TRAIN,START,START_SHA,CHILD_SHA=original.NATIVE,original.TRAIN,original.START,original.START_SHA,original.CHILD_SHA
LABELS=original.LABELS
aliases=original.aliases

@functools.lru_cache(maxsize=1)
def stack():
    st=original.stack();st.prior.ROOT=ROOT
    st.prior.context_window_id=lambda c:c['native_context_id']
    sys.path.insert(0,str(ROOT)) # Inherited imports prepend their own study directories.
    return st

def runtime():
    sys.path.insert(0,str(RUNTIME))
    import study_wrapper,lifecycle_adapter,credential_preflight
    study_wrapper.verify_runtime();lifecycle_adapter.verify();credential_preflight.require_provider_credential()
    return study_wrapper,lifecycle_adapter

def interface(output):
    wrapper,_=runtime();st=wrapper.adapt_stack(stack())
    with aliases({'interface':st.interface}):value=st.local.configure_interface(output)
    sys.path.insert(0,str(ROOT));return value

@functools.lru_cache(maxsize=1)
def verify():
    value=read(ROOT/'READY.json')
    if digest({k:v for k,v in value.items() if k!='identity'})!=value['identity']:raise ValueError('READY identity')
    for p,h in {**value['source_sha256'],**value['input_sha256']}.items():
        if sha(p)!=h:raise ValueError('READY closure changed: '+p)
    return value

def corpus(limit=None):
    directory=ATTEMPT/'capture';plan=read(ROOT/'inputs/TRAIN_PLAN.json')
    if limit is None:
        frozen=read(directory/'CORPUS_READY.json')
        if frozen['identity']!=verify()['identity'] or frozen['examples']!=32:raise ValueError('complete fixed corpus required')
        for p,h in frozen['files_sha256'].items():
            if sha(p)!=h:raise ValueError('corpus changed')
    rows=[read(directory/c['id']/'TEACHER.json') for c in plan[:limit]]
    return rows

def order():return tuple(sorted(ARMS,key=lambda x:digest([MASTER,'train',x])))
def phases():return tuple(sorted(('unchanged',*ARMS),key=lambda x:digest([MASTER,'readout',x])))
