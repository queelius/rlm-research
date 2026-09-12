"""Fixed original fresh8 training readout; only the qualified RLOO weights change."""
from pathlib import Path
import importlib.util
import sys

ROOT=Path(__file__).resolve().parent;SIDE=ROOT.parent;READY=ROOT/'READY.json'
PRIOR=SIDE/'openai-mrcr-cp32-fresh8-final-rloo-eval-v1'
SCREEN=SIDE/'openai-mrcr-procedural-sft32-fresh8-onpolicy-screen-v1'
def load(name,path):
    spec=importlib.util.spec_from_file_location(name,path);m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);return m
def bound(name,path,**modules):
    saved={k:sys.modules.get(k) for k in modules};sys.modules.update(modules)
    try:return load(name,path)
    finally:
        for k,v in saved.items():
            if v is None:sys.modules.pop(k,None)
            else:sys.modules[k]=v
prior=load('fresh8_trainread_prior_study',PRIOR/'study.py')
screen=load('fresh8_trainread_screen_study',SCREEN/'study.py')
sha=prior.sha;digest=prior.digest;read=prior.read;write_x=prior.write_x
BASE=prior.BASE;NATIVE=prior.NATIVE;TRAIN_PYTHON=prior.TRAIN_PYTHON
ADAPTED_ALIAS=prior.ADAPTED_ALIAS;BASE_ALIAS=prior.BASE_ALIAS
SOURCE=prior.SOURCE;SOURCE_EVAL=prior.SOURCE_EVAL;ROLE_SOURCE=prior.ROLE_SOURCE
TRAINING=prior.TRAINING;train=prior.train
CAPS={'train':{'science':900,'owner':1100,'external':1200}}
BASELINE=SCREEN/'outputs/attempt-001';BASELINES={'train':BASELINE}
def schedule(phase):return screen.schedule(phase)
def input_dir(phase):return screen.input_dir(phase)
def environment(phase):return screen.environment(phase)
def source():return prior.source()
def dependencies():return prior.dependencies()
def official_grade():return prior.official_grade()
def terminal_hooks():return prior.terminal_hooks()
def verify():
    r=read(READY);assert r['identity']==digest({k:v for k,v in r.items() if k!='identity'})
    for p,h in r['closure_sha256'].items():assert sha(p)==h,p
    assert digest(schedule('train'))==r['inputs']['train']['schedule_sha256']
    return r
