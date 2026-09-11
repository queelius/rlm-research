"""Pinned bindings for task-aware selective recheck."""
import functools
import hashlib
import importlib.util
import json
import os
from pathlib import Path

ROOT = Path(__file__).parent
SIDE = ROOT.parent
ATTEMPT = ROOT / "outputs/attempt-001"
BASE = SIDE / "root-supplied-plan-selective-recheck-v1"
NATIVE = Path("/project/alex_phd/envs/prime-rl-5990b1b/bin/python")

def read(path): return json.loads(Path(path).read_text())
def sha(path): return hashlib.sha256(Path(path).read_bytes()).hexdigest()
def digest(value): return hashlib.sha256(json.dumps(value,sort_keys=True,separators=(",",":")).encode()).hexdigest()
def write(path,value):
    path=Path(path);path.parent.mkdir(parents=True,exist_ok=True);tmp=path.with_name(path.name+".partial")
    tmp.write_text(json.dumps(value,sort_keys=True,indent=2,allow_nan=False)+"\n");os.replace(tmp,path)

@functools.lru_cache(maxsize=1)
def base_study():
    spec=importlib.util.spec_from_file_location("taskaware_base_study",BASE/"study.py")
    module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module);return module

def dependencies(): return base_study().dependencies()
def renderer(): return base_study().renderer()
def binding():
    value=base_study().binding();value["study"]=ROOT.name;value["campaign_id"]=ROOT.name
    value["batch_granularity"]={"scientific_role":"task_aware_two_sample_recheck","fixed_child":"c32","planned":48,"root_calls":0}
    return value
def verify():
    ready=read(ROOT/"READY.json");identity=ready["identity"]
    assert digest({k:v for k,v in ready.items() if k!="identity"})==identity
    for group in ("source_sha256","input_sha256"):
        for path,pin in ready[group].items():
            if sha(path)!=pin:raise ValueError("frozen closure changed: "+path)
    return ready

