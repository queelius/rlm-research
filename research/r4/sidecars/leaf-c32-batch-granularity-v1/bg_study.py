"""Isolated native child-only study using the qualified dual-LoRA lifecycle."""
import functools
import hashlib
import importlib.util
import json
import os
from pathlib import Path
ROOT=Path(__file__).resolve().parent;SIDE=ROOT.parent;STORE=SIDE.parent;ATTEMPT=ROOT/'outputs/attempt-001'
BV=SIDE/'root-bounded-observation-view-v1'
DIAG=STORE/'analyses/root-bounded-child-error-diagnostic-2026-09-10'
SEEDS=(986901701,986901702)
def read(path):return json.loads(Path(path).read_text())
def sha(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()
def digest(value):return hashlib.sha256(json.dumps(value,sort_keys=True,separators=(',',':')).encode()).hexdigest()
def write(path,value):
    path=Path(path);path.parent.mkdir(parents=True,exist_ok=True)
    temporary=path.with_name(path.name+'.partial');temporary.write_text(json.dumps(value,sort_keys=True,indent=2,allow_nan=False)+'\n');os.replace(temporary,path)
def load(name,path,pin):
    assert sha(path)==pin
    spec=importlib.util.spec_from_file_location(name,path);module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module);return module
assert sha(BV/'READY.json')=='a5a50377a481f1db75f81fd725c80ca4f6285a55bdf095b9ba3718ca5f788478'
bv_ready=read(BV/'READY.json')
bv=load('batch_granularity_qualified_bounded',BV/'bv_study.py',bv_ready['source_sha256'][str(BV/'bv_study.py')])
NATIVE=bv.NATIVE
def dependencies():return bv.dose.dependencies()
def binding():
    value=read(BV/'BINDING_sft24_v2.json');value['study']=ROOT.name;value['campaign_id']=ROOT.name
    value['batch_granularity']=dict(scientific_role='child_only',frozen_child='c32',root_calls=0,planned=76)
    return value
@functools.lru_cache(maxsize=1)
def renderer():
    from renderers import Qwen3RendererConfig,create_renderer
    from renderers.base import load_tokenizer
    tok=load_tokenizer('/project/alex_phd/research-cache/models/Qwen--Qwen3-4B-Instruct-2507--cdbee75f17c01a7cc42f958dc650907174af0554')
    return create_renderer(tok,Qwen3RendererConfig(enable_thinking=True)),tok
def verify():
    ready=read(ROOT/'READY.json')
    if digest({k:v for k,v in ready.items() if k!='identity'})!=ready['identity']:raise ValueError('READY identity')
    for path,pin in {**ready['source_sha256'],**ready['input_sha256']}.items():
        if sha(path)!=pin:raise ValueError('frozen source changed '+path)
    return ready
