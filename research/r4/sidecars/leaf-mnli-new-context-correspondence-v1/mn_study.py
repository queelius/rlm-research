"""Unique study namespace and pinned released-base native/runtime dependencies."""
import contextlib
import hashlib
import importlib.util
import json
from pathlib import Path
import sys

ROOT=Path(__file__).resolve().parent;SIDE=ROOT.parent;BASE=SIDE/'leaf-mnli-correspondence-v1';SOURCE=SIDE/'leaf-mnli-exact-tag-correspondence-v1'
ATTEMPT=ROOT/'outputs/attempt-001';READY_PATH=ROOT/'READY.json';NATIVE=Path('/project/alex_phd/envs/prime-rl-5990b1b/bin/python')
FEASIBILITY=SIDE.parent/'analyses/mnli-new-context-feasibility-2026-09-10'
SELECTED_SHA='402f5597796325aa80399f7e8a1f28141b86b6fd0166dbfcf9dd0d99af312372'
FEASIBILITY_SHA='0b32e370cccc1008b13dd2375014896ac46e372548671905270b7669062c04ff'
PINS={'protocol.py':'6ff27543e240e653c777391f836ef7b361e740265efe7d959971e516222f3b13','collect.py':'53c9f05634aa0dc60731e96325c3f969fae8257ba63beafe57bd9c738c224b7d','owner.py':'6161e7eaf855c936f38a6b8f8a4ab7b47380d22dd896d6861422781af8247277','scoring.py':'a0f28f9c4c7e337ec1586343790468a6ea4d5bb670e6e3c54725e16d35d0b596'}
def sha(path):
    with Path(path).open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
def read(path):return json.loads(Path(path).read_text())
def write(path,value):
    path=Path(path);path.parent.mkdir(parents=True,exist_ok=True)
    with path.open('x') as f:json.dump(value,f,ensure_ascii=False,sort_keys=True,indent=2,allow_nan=False);f.write('\n')
def serialize(value):return json.dumps(value,ensure_ascii=False,separators=(',',':'),allow_nan=False)
def digest(value):return hashlib.sha256(json.dumps(value,ensure_ascii=False,sort_keys=True,separators=(',',':'),allow_nan=False).encode()).hexdigest()
@contextlib.contextmanager
def aliases(values):
    old={k:sys.modules.get(k) for k in values};old_path=list(sys.path);sys.modules.update(values)
    try:yield
    finally:
        sys.path[:]=old_path
        for k,v in old.items():sys.modules.pop(k,None) if v is None else sys.modules.__setitem__(k,v)
def load(name,path,pin):
    if sha(path)!=pin:raise ValueError('immutable source changed: '+str(path))
    spec=importlib.util.spec_from_file_location(name,path);module=importlib.util.module_from_spec(spec);sys.modules[name]=module;spec.loader.exec_module(module);return module
base=load('mn_new_context_qualified_base',BASE/'study.py','8ad422e666972a2a9e314b5c9eb24266dd72c0286d4dfb9d48a9af8cbc156dd8')
MODEL,service,lifecycle=base.MODEL,base.service,base.lifecycle
def tokenizer():return base.tokenizer()
def validate_weights():return base.validate_weights()
def verify():
    ready=read(READY_PATH)
    if digest({k:v for k,v in ready.items() if k!='identity'})!=ready['identity']:raise ValueError('READY identity')
    for path,pin in ready['source_sha256'].items():
        if sha(path)!=pin:raise ValueError('READY closure changed: '+path)
    if sha(ROOT/'DATA.json')!=SELECTED_SHA or sha(FEASIBILITY/'FEASIBILITY_V2.json')!=FEASIBILITY_SHA:raise ValueError('frozen input selection changed')
    validate_weights();return ready
