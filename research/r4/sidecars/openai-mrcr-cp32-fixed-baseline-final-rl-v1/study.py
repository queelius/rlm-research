"""Fixed original cp32 native batch; no mixed-group gate for this new objective."""
import hashlib
import importlib.util
import json
import math
from pathlib import Path

ROOT=Path(__file__).resolve().parent;STORE=ROOT.parents[1];SIDE=ROOT.parent
PRIOR=SIDE/'openai-mrcr-short-root-token-tis-two-lr-v1'
SCREEN=SIDE/'openai-mrcr-procedural-sft32-onpolicy-screen-v1'
SOURCE_OUTPUT=SCREEN/'outputs/attempt-004'
REVIEW=STORE/'analyses/openai-mrcr-sft32-g4-mechanism-2026-09-12'
CHECKPOINT=SIDE/'openai-mrcr-procedural-sft-continue32-v1/outputs/attempt-001/checkpoint-0032'
BASE=Path('/project/alex_phd/research-cache/models/Qwen--Qwen3-4B-Instruct-2507--cdbee75f17c01a7cc42f958dc650907174af0554')
INPUTS=ROOT/'TRAIN_INPUTS.json';READY=ROOT/'READY.json';OUTPUT=ROOT/'outputs/attempt-001'
PYTHON=Path('/project/alex_phd/repos/rlm-bootstrap/.worktrees/a100-lora-roundtrip/gpu/training/.venv/bin/python')
NATIVE=Path('/project/alex_phd/envs/prime-rl-5990b1b/bin/python')
TEMPERATURE=.5;TOKEN_TIS_CAP=2.;DENOMINATOR=32;SEED=202609220001;NP_SEED=SEED%(2**32)
LEARNING_RATE=1e-5;SCIENCE_SECONDS=900;OWNER_SECONDS=1100;EXTERNAL_SECONDS=1200
ADAPTER_SHA='020e05b23a065c1f0e3cfe36cbb0e1108acb1d6f3391e003898074556fe2d23a'
ALIAS='Qwen3-4B-Instruct-2507-mrcr-cp32-fixedbaseline-final-step1'

def sha(path):
    with Path(path).open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
def digest(v):return hashlib.sha256(json.dumps(v,sort_keys=True,separators=(',',':'),allow_nan=False).encode()).hexdigest()
def read(p):return json.loads(Path(p).read_text())
def write_x(p,v):
    p=Path(p);p.parent.mkdir(parents=True,exist_ok=True)
    with p.open('x') as f:json.dump(v,f,sort_keys=True,indent=2,allow_nan=False);f.write('\n')
def load(name,path):
    spec=importlib.util.spec_from_file_location(name,path);m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);return m

_prior=load('fixedbaseline_original_positions',PRIOR/'study.py')
positions_and_targets=_prior.positions_and_targets

def validate_inputs(data):
    rows=data['episodes']
    assert len(rows)==32 and len({x['group_id'] for x in rows})==8
    assert sum(x['reward'] for x in rows)==28 and len({x['episode_id'] for x in rows})==32
    for x in rows:
        assert sum(z['group_id']==x['group_id'] for z in rows)==4
        assert x['reward'] in (0,1) and x['advantage']==x['reward']-.5
        assert x['available'] and x['actual_bare_final'] and len(x['root_turns'])==1
        turn=x['root_turns'][0];positions_and_targets(turn)
        assert len(turn['input_ids'])<=8192 and len(turn['action_ids'])<=2048
        assert len(turn['diagnostic_token_parts'])==len(turn['action_ids'])
        assert set(turn['diagnostic_token_parts'])<={'body','whitespace','eos'}
        assert len(x['zero_loss_root_turns'])==1
        for z in x['zero_loss_root_turns']:
            assert z['input_ids']==z['prompt_ids']+z['action_ids']
            assert z['labels']==[-100]*len(z['input_ids']) and z['loss_mask']==[0]*len(z['input_ids'])
        assert x['child_loss_tokens']==0
    assert sum(len(x['root_turns'][0]['action_ids']) for x in rows)==10420
    return rows

def verify():
    r=read(READY);assert r['identity']==digest({k:v for k,v in r.items() if k!='identity'})
    for p,h in r['closure_sha256'].items():assert sha(p)==h,p
    assert sha(CHECKPOINT/'adapter_model.safetensors')==ADAPTER_SHA
    validate_inputs(read(INPUTS));return r

