"""Exact existing held/long payloads; only the fixed qualified root adapter changes."""
import hashlib
import importlib.util
import json
from pathlib import Path

ROOT=Path(__file__).resolve().parent;SIDE=ROOT.parent;READY=ROOT/'READY.json'
TRAINING=SIDE/'openai-mrcr-cp32-fixed-baseline-final-rl-v1'
SHORT=SIDE/'openai-mrcr-procedural-sft-terminal-strip-disabled-v1'
LONG=SIDE/'openai-mrcr-long-transfer-eval-v1'
SOURCE_EVAL=SIDE/'openai-mrcr-procedural-sft-eval-v1'

def load(name,path):
    spec=importlib.util.spec_from_file_location(name,path);m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);return m
def sha(path):
    with Path(path).open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
def read(path):return json.loads(Path(path).read_text())
def digest(value):return hashlib.sha256(json.dumps(value,sort_keys=True,separators=(',',':'),allow_nan=False).encode()).hexdigest()
def write_x(path,value):
    path=Path(path);path.parent.mkdir(parents=True,exist_ok=True)
    with path.open('x') as f:json.dump(value,f,indent=2,sort_keys=True,allow_nan=False);f.write('\n')

train=load('fixedRL_eval_trainer_study',TRAINING/'study.py')
short=load('fixedRL_eval_short_study',SHORT/'study.py')
long=load('fixedRL_eval_long_study',LONG/'study_v2.py')
BASE=train.BASE;NATIVE=train.NATIVE;TRAIN_PYTHON=train.PYTHON
ADAPTED_ALIAS=train.ALIAS;BASE_ALIAS=short.BASE_ALIAS;SOURCE=short.SOURCE;ROLE_SOURCE=short.ROLE_SOURCE
BASELINES={'held':SHORT/'outputs/held-checkpoint32-001','long':LONG/'outputs/checkpoint32-002'}
CAPS={'held':{'science':600,'owner':900,'external':1000},'long':{'science':900,'owner':1100,'external':1200}}
def prior(phase):
    if phase not in CAPS:raise ValueError('only fixed held and long stages')
    return short if phase=='held' else long
def schedule(phase):return prior(phase).schedule(phase)
def input_dir(phase):return prior(phase).input_dir(phase)
def environment_config(phase):return prior(phase).environment_config(phase)
def environment(phase):return prior(phase).environment(phase)
def source():return short.source()
def dependencies():return short.dependencies()
def official_grade():return short.official_grade()
def terminal_hooks():return long.terminal_hooks()
def verify():
    r=read(READY);assert r['identity']==digest({k:v for k,v in r.items() if k!='identity'})
    for p,h in r['closure_sha256'].items():assert sha(p)==h,p
    for phase in CAPS:assert digest(schedule(phase))==r['inputs'][phase]['schedule_sha256']
    return r
