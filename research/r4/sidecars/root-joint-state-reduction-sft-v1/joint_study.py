"""Unique local namespace over pinned immutable corrective/native runtime dependencies."""
import functools
import hashlib
import importlib.util
import json
from pathlib import Path
import sys

ROOT=Path(__file__).resolve().parent
BASE_CORRECTIVE=ROOT.parent/'root-corrective-reduction-sft-v1'
ATTEMPT=ROOT/'outputs/attempt-001'
ARMS=('joint','reduction_stop')
MASTER=981361001

def sha(path):
    with Path(path).open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
def read(path):return json.loads(Path(path).read_text())
def write(path,value):
    path=Path(path);path.parent.mkdir(parents=True,exist_ok=True)
    with path.open('x') as f:json.dump(value,f,sort_keys=True,indent=2,allow_nan=False);f.write('\n')
def digest(value):return hashlib.sha256(json.dumps(value,sort_keys=True,separators=(',',':'),allow_nan=False).encode()).hexdigest()
def load(name,path,pin):
    if sha(path)!=pin:raise ValueError('pinned source changed: '+str(path))
    spec=importlib.util.spec_from_file_location(name,path);m=importlib.util.module_from_spec(spec);sys.modules[name]=m;spec.loader.exec_module(m);return m

source=load('joint_immutable_corrective_study',BASE_CORRECTIVE/'study.py','5e509fcc7285acb443b43f81491377eb76dbfd58e5d194e9c676a641a16246de')
original=source.original
SOURCE,RUNTIME,NATIVE,TRAIN,START,START_SHA,CHILD_SHA,LABELS,aliases=(source.SOURCE,source.RUNTIME,source.NATIVE,source.TRAIN,source.START,source.START_SHA,source.CHILD_SHA,source.LABELS,source.aliases)

@functools.lru_cache(maxsize=1)
def stack():
    st=source.stack();st.prior.ROOT=ROOT;sys.path.insert(0,str(ROOT));return st

def runtime():return source.runtime()
def interface(output):
    wrapper,_=runtime();st=wrapper.adapt_stack(stack())
    with aliases({'interface':st.interface}):value=st.local.configure_interface(output)
    sys.path.insert(0,str(ROOT));return value

@functools.lru_cache(maxsize=1)
def verify():
    value=read(ROOT/'READY.json')
    if digest({k:v for k,v in value.items() if k!='identity'})!=value['identity']:raise ValueError('READY identity')
    for p,h in {**value['source_sha256'],**value['input_sha256']}.items():
        if sha(p)!=h:raise ValueError('READY closure changed '+p)
    return value

def corpus(limit=None):
    directory=ATTEMPT/'capture';plan=read(ROOT/'inputs/TRAIN_PLAN.json')
    if limit is None:
        frozen=read(directory/'CORPUS_READY.json')
        if frozen['identity']!=verify()['identity'] or frozen['examples']!=16:raise ValueError('complete fixed16 corpus required')
        for path,pin in frozen['files_sha256'].items():
            if sha(path)!=pin:raise ValueError('corpus changed')
    return [read(directory/r['id']/'TEACHER.json') for r in plan[:limit]]

def order():return tuple(sorted(ARMS,key=lambda arm:digest([MASTER,'train',arm])))
def phases():return tuple(sorted(('unchanged',*ARMS),key=lambda arm:digest([MASTER,'readout',arm])))
