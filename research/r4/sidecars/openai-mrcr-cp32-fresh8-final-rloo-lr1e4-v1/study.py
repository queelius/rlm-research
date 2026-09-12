"""Single LR10x arm; identical original cp32, frozen batch, RNG and objective."""
from pathlib import Path
import importlib.util
import sys

def load(name,path):
    spec=importlib.util.spec_from_file_location(name,path);m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);return m
def bound(name,path,**modules):
    saved={k:sys.modules.get(k) for k in modules};sys.modules.update(modules)
    try:return load(name,path)
    finally:
        for k,v in saved.items():
            if v is None:sys.modules.pop(k,None)
            else:sys.modules[k]=v
SOURCE_TRAIN=Path(__file__).resolve().parent.parent/'openai-mrcr-cp32-fresh8-final-rloo-v1'
original=load('fresh8_lr10_original_study',SOURCE_TRAIN/'study.py')
for name in dir(original):
    if not name.startswith('_') and name!='load':globals()[name]=getattr(original,name)
ROOT=Path(__file__).resolve().parent;READY=ROOT/'READY.json';OUTPUT=ROOT/'outputs/attempt-001'
LEARNING_RATE=1e-4
ALIAS='Qwen3-4B-Instruct-2507-mrcr-cp32-fresh8-final-rloo-lr1e4-step1'

def verify():
    r=read(READY);assert r['identity']==digest({k:v for k,v in r.items() if k!='identity'})
    for p,h in r['closure_sha256'].items():assert sha(p)==h,p
    assert sha(CHECKPOINT/'adapter_model.safetensors')==ADAPTER_SHA
    assert INPUTS==original.INPUTS and SEED==original.SEED and LEARNING_RATE==1e-4
    for name in ('PARENT_BINDING.json','PARENT_CHECKPOINT_QUALIFICATION.json'):
        assert sha(ROOT/name)==sha(SOURCE_TRAIN/name)
    validate_inputs(read(INPUTS));return r
