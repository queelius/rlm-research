"""Fixed LR10x endpoint; original training32 and exposed held32, both regardless score."""
from pathlib import Path
import importlib.util
import sys

ROOT=Path(__file__).resolve().parent;SIDE=ROOT.parent;READY=ROOT/'READY.json'
PRIOR=SIDE/'openai-mrcr-cp32-fresh8-final-rloo-eval-v1'
TRAINREAD=SIDE/'openai-mrcr-cp32-fresh8-final-rloo-train-readout-v1'
TRAINING=SIDE/'openai-mrcr-cp32-fresh8-final-rloo-lr1e4-v1'
def load(name,path):
    spec=importlib.util.spec_from_file_location(name,path);m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);return m
def bound(name,path,**modules):
    saved={k:sys.modules.get(k) for k in modules};sys.modules.update(modules)
    try:return load(name,path)
    finally:
        for k,v in saved.items():
            if v is None:sys.modules.pop(k,None)
            else:sys.modules[k]=v
prior=load('fresh8_dose_eval_prior',PRIOR/'study.py')
trainread=load('fresh8_dose_eval_trainread',TRAINREAD/'study.py')
train=load('fresh8_dose_eval_training',TRAINING/'study.py')
sha=prior.sha;digest=prior.digest;read=prior.read;write_x=prior.write_x
BASE=prior.BASE;NATIVE=prior.NATIVE;TRAIN_PYTHON=train.PYTHON
ADAPTED_ALIAS=train.ALIAS;BASE_ALIAS=prior.BASE_ALIAS
SOURCE=prior.SOURCE;SOURCE_EVAL=prior.SOURCE_EVAL;ROLE_SOURCE=prior.ROLE_SOURCE
CAPS={phase:dict(science=900,owner=1100,external=1200) for phase in ('train','held')}
CONTROLS={'train':{'cp32':trainread.BASELINE,'LR1e5':TRAINREAD/'outputs/train-001'},
          'held':{'cp32':prior.CONTROLS['held']['cp32'],'LR1e5':PRIOR/'outputs/held-001'}}
BASELINES={p:v['cp32'] for p,v in CONTROLS.items()}
def phase_study(phase):
    if phase not in CAPS:raise ValueError('fixed train/held only')
    return trainread if phase=='train' else prior
def schedule(phase):return phase_study(phase).schedule(phase)
def input_dir(phase):return phase_study(phase).input_dir(phase)
def environment(phase):return phase_study(phase).environment(phase)
def source():return prior.source()
def dependencies():return prior.dependencies()
def official_grade():return prior.official_grade()
def terminal_hooks():return prior.terminal_hooks()
def verify():
    r=read(READY);assert r['identity']==digest({k:v for k,v in r.items() if k!='identity'})
    for p,h in r['closure_sha256'].items():assert sha(p)==h,p
    for p in CAPS:assert digest(schedule(p))==r['inputs'][p]['schedule_sha256']
    return r
