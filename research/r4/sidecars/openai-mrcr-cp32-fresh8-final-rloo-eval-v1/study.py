"""Three exact existing schedules; only the fixed new RLOO endpoint changes."""
from pathlib import Path
import importlib.util
ROOT=Path(__file__).resolve().parent;SIDE=ROOT.parent;READY=ROOT/'READY.json'
TRAINING=SIDE/'openai-mrcr-cp32-fresh8-final-rloo-v1'
PRIOR=SIDE/'openai-mrcr-cp32-fixed-baseline-final-rl-eval-v1'
REPLICA=SIDE/'openai-mrcr-cp32-fixed-baseline-final-rl-decode-replica-v1'
FOUR=SIDE/'openai-mrcr-fourneedle-ordinal-transfer-eval-v1'
def load(name,path):
    spec=importlib.util.spec_from_file_location(name,path);m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);return m
prior=load('fresh8rloo_eval_prior_study',PRIOR/'study.py')
replica=load('fresh8rloo_eval_replica_study',REPLICA/'study.py')
four=load('fresh8rloo_eval_fourneedle_study',FOUR/'study.py')
train=load('fresh8rloo_eval_training_study',TRAINING/'study.py')
sha=prior.sha;digest=prior.digest;read=prior.read;write_x=prior.write_x
BASE=train.BASE;NATIVE=train.NATIVE;TRAIN_PYTHON=train.PYTHON
ADAPTED_ALIAS=train.ALIAS;BASE_ALIAS=prior.BASE_ALIAS
SOURCE=prior.SOURCE;SOURCE_EVAL=prior.SOURCE_EVAL;ROLE_SOURCE=prior.ROLE_SOURCE
CAPS={'held':{'science':900,'owner':1100,'external':1200},
      'long':{'science':600,'owner':700,'external':800},
      'fourneedle':{'science':600,'owner':700,'external':800}}
CONTROLS={'held':{'cp32':REPLICA/'outputs/cp32-001','fixed_baseline_RL':REPLICA/'outputs/updated-001'},
          'long':{'cp32':prior.BASELINES['long']},
          'fourneedle':{'cp32':FOUR/'outputs/checkpoint32-001'}}
BASELINES={p:arms['cp32'] for p,arms in CONTROLS.items()}
def stage(phase):
    if phase not in CAPS:raise ValueError('fixed held/long/fourneedle phases only')
    return {'held':(replica,'cp32'),'long':(prior.long,'long'),'fourneedle':(four,'long')}[phase]
def schedule(phase):
    s,p=stage(phase);return s.schedule(p)
def input_dir(phase):
    s,p=stage(phase);return s.input_dir(p)
def environment(phase):
    s,p=stage(phase);return s.environment(p)
def source():return prior.source()
def dependencies():return prior.dependencies()
def official_grade():return prior.official_grade()
def terminal_hooks():return prior.terminal_hooks()
def verify():
    r=read(READY);assert r['identity']==digest({k:v for k,v in r.items() if k!='identity'})
    for p,h in r['closure_sha256'].items():assert sha(p)==h,p
    for phase in CAPS:assert digest(schedule(phase))==r['inputs'][phase]['schedule_sha256']
    return r
