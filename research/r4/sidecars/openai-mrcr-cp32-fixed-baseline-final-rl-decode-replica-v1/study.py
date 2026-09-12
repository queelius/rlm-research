"""Only coordinate names/seeds change; both arms share original held task bodies."""
import importlib.util
from pathlib import Path

ROOT=Path(__file__).resolve().parent;SIDE=ROOT.parent;READY=ROOT/'READY.json'
PRIOR=SIDE/'openai-mrcr-cp32-fixed-baseline-final-rl-eval-v1'
def load(name,path):
    spec=importlib.util.spec_from_file_location(name,path);m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);return m
prior=load('decode_replica_prior_eval_study',PRIOR/'study.py')
sha=prior.sha;digest=prior.digest;read=prior.read;write_x=prior.write_x
BASE=prior.BASE;NATIVE=prior.NATIVE;SOURCE=prior.SOURCE;SOURCE_EVAL=prior.SOURCE_EVAL;ROLE_SOURCE=prior.ROLE_SOURCE
BASE_ALIAS=prior.BASE_ALIAS;ADAPTED_ALIAS=prior.ADAPTED_ALIAS
BASELINES={arm:ROOT/'outputs/cp32-001' for arm in ('cp32','updated')}
CAPS={arm:{'science':900,'owner':1100,'external':1200} for arm in ('cp32','updated')}
INPUTS=ROOT/'inputs'
local_environment=load('decode_replica_private_environment_study',SOURCE_EVAL/'study.py')
local_environment.INPUTS=INPUTS

def schedule(phase):
    if phase not in CAPS:raise ValueError('only cp32 and updated fixed arms')
    rows=[]
    for old in prior.schedule('held'):
        c={k:v for k,v in old.items() if k!='id'}
        c.update(study=ROOT.name,seed=202609270000+2*old['row_index']+old['repeat'],source_coordinate_id=old['id'])
        rows.append({**c,'id':digest(c)})
    return rows
def input_dir(phase):
    if phase not in CAPS:raise ValueError('fixed arms only')
    return INPUTS/'held'
def environment(phase):
    input_dir(phase);return local_environment.environment('held')
def source():return prior.source()
def dependencies():return prior.dependencies()
def official_grade():return prior.official_grade()
def terminal_hooks():return prior.terminal_hooks()
def verify():
    r=read(READY);assert r['identity']==digest({k:v for k,v in r.items() if k!='identity'})
    for p,h in r['closure_sha256'].items():assert sha(p)==h,p
    assert digest(schedule('cp32'))==r['schedule_sha256'] and schedule('cp32')==schedule('updated')
    return r
