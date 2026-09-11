"""New24-call final-interface study over immutable pilot states and released base service."""
import contextlib
import functools
import hashlib
import importlib.util
import json
from pathlib import Path
import sys

ROOT=Path(__file__).resolve().parent
SIDE=ROOT.parent
PILOT=SIDE/'root-partition-report-pilot-v1'
AUDIT=SIDE.parent/'analyses/root-partition-report-live-2026-09-09'
FREE=SIDE/'leaf-free-id-correspondence-v1'
RUNTIME=SIDE/'runtime-an27-5780-v1'
ATTEMPT=ROOT/'outputs/attempt-001'
NATIVE=Path('/project/alex_phd/envs/prime-rl-5990b1b/bin/python')

def read(path):return json.loads(Path(path).read_text())
def sha(path):
    with Path(path).open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
def serialize(value):return json.dumps(value,ensure_ascii=False,separators=(',',':'),allow_nan=False)
def digest(value):return hashlib.sha256(serialize(value).encode()).hexdigest()
def write(path,value):
    path=Path(path);path.parent.mkdir(parents=True,exist_ok=True)
    with path.open('x') as f:f.write(serialize(value)+'\n')
def load(name,path,pin):
    if sha(path)!=pin:raise ValueError('immutable source changed: '+str(path))
    spec=importlib.util.spec_from_file_location(name,path);module=importlib.util.module_from_spec(spec);sys.modules[name]=module;spec.loader.exec_module(module);return module
@contextlib.contextmanager
def aliases(values):
    old={k:sys.modules.get(k) for k in values};sys.modules.update(values)
    try:yield
    finally:
        for k,v in old.items():
            if v is None:sys.modules.pop(k,None)
            else:sys.modules[k]=v

free=load('partition_qualified_free_id_study',FREE/'study.py','63de397eb97058066ca362c6a869435f1ff571803396c406927497c0df5cb544')
MODEL=free.MODELS['qwen3']
with aliases({'study':free}):
    service=load('partition_qualified_base_service',FREE/'service.py','51215324f767d3b7fc214bed4c64e61592fb3be8223c8d5f1dd4773fae4c48cd')
    lifecycle=load('partition_qualified_base_lifecycle',FREE/'lifecycle_adapter_v3.py','759f527bbd35d866b681641262a7c21625390c233ba4e17f7c3b7ded2f443a8f')

@functools.lru_cache(maxsize=1)
def verify():
    ready=read(ROOT/'READY.json')
    if digest({k:v for k,v in ready.items() if k!='identity'})!=ready['identity']:raise ValueError('READY identity')
    for p,h in ready['source_sha256'].items():
        if sha(p)!=h:raise ValueError('READY closure changed: '+p)
    validate_weights()
    return ready

def validate_weights():
    identities=read(FREE/'WEIGHTS.json')['weight_stat_identity']
    for p,identity in identities.items():
        st=Path(p).stat()
        if [st.st_size,st.st_mtime_ns,st.st_ino]!=identity:raise ValueError('qualified base weight identity changed')
    return len(identities)

def tokenizer():
    from transformers import AutoTokenizer
    return AutoTokenizer.from_pretrained(MODEL['path'],local_files_only=True,trust_remote_code=False)
