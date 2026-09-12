"""Fresh8 native RLOO, fixed original cp32 and one final-text update."""
import hashlib
import importlib.util
import json
import math
from pathlib import Path

ROOT=Path(__file__).resolve().parent;STORE=ROOT.parents[1];SIDE=ROOT.parent
OLD=SIDE/'openai-mrcr-cp32-fixed-baseline-final-rl-v1'
PRIOR=SIDE/'openai-mrcr-short-root-token-tis-two-lr-v1'
SCREEN=SIDE/'openai-mrcr-procedural-sft32-fresh8-onpolicy-screen-v1'
SOURCE_OUTPUT=SCREEN/'outputs/attempt-001'
REVIEW=STORE/'analyses/openai-mrcr-sft32-fresh8-g4-mechanism-2026-09-12'
CHECKPOINT=SIDE/'openai-mrcr-procedural-sft-continue32-v1/outputs/attempt-001/checkpoint-0032'
BASE=Path('/project/alex_phd/research-cache/models/Qwen--Qwen3-4B-Instruct-2507--cdbee75f17c01a7cc42f958dc650907174af0554')
INPUTS=ROOT/'TRAIN_INPUTS.json';READY=ROOT/'READY.json';OUTPUT=ROOT/'outputs/attempt-001'
PYTHON=Path('/project/alex_phd/repos/rlm-bootstrap/.worktrees/a100-lora-roundtrip/gpu/training/.venv/bin/python')
NATIVE=Path('/project/alex_phd/envs/prime-rl-5990b1b/bin/python')
TEMPERATURE=.5;TOKEN_TIS_CAP=2.;DENOMINATOR=32;SEED=202609280001;NP_SEED=SEED%(2**32)
LEARNING_RATE=1e-5;SCIENCE_SECONDS=900;OWNER_SECONDS=1100;EXTERNAL_SECONDS=1200
ADAPTER_SHA='020e05b23a065c1f0e3cfe36cbb0e1108acb1d6f3391e003898074556fe2d23a'
ALIAS='Qwen3-4B-Instruct-2507-mrcr-cp32-fresh8-final-rloo-step1'
REPORT_SHA='e8b0ae49b29415130e990d62cface02ab9d330b0b983d5b9db504c683d913f19'

def sha(path):
    with Path(path).open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
def digest(v):return hashlib.sha256(json.dumps(v,sort_keys=True,separators=(',',':'),allow_nan=False).encode()).hexdigest()
def read(p):return json.loads(Path(p).read_text())
def write_x(p,v):
    p=Path(p);p.parent.mkdir(parents=True,exist_ok=True)
    with p.open('x') as f:json.dump(v,f,sort_keys=True,indent=2,allow_nan=False);f.write('\n')
def load(name,path):
    spec=importlib.util.spec_from_file_location(name,path);m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);return m
positions_and_targets=load('fresh8rloo_positions',PRIOR/'study.py').positions_and_targets

def validate_inputs(data):
    rows=data['episodes'];assert len(rows)==32 and len({r['episode_id'] for r in rows})==32
    assert len({r['group_id'] for r in rows})==8 and sum(r['reward'] for r in rows)==7
    for row in rows:
        group=[r for r in rows if r['group_id']==row['group_id']]
        assert len(group)==4 and row['available'] and row['reward'] in (0,1)
        total=sum(r['reward'] for r in group)
        assert row['baseline']==total/4 and row['advantage']==(4*row['reward']-total)/3
        assert len(row['root_turns'])==int(row['advantage']!=0)
        for turn in row['root_turns']:
            assert row['actual_bare_final'];positions_and_targets(turn)
            assert len(turn['input_ids'])<=8192 and len(turn['action_ids'])<=2048
            assert len(turn['diagnostic_token_parts'])==len(turn['action_ids'])
            assert set(turn['diagnostic_token_parts'])<={'body','whitespace','eos'}
            assert len(turn['old_logprobs'])==len(turn['action_ids'])
            assert all(math.isfinite(v) and v<=0 for v in turn['old_logprobs'])
        for turn in row['zero_loss_root_turns']:
            assert turn['input_ids']==turn['prompt_ids']+turn['action_ids']
            assert turn['labels']==[-100]*len(turn['input_ids']) and not any(turn['loss_mask'])
        assert row['child_loss_tokens']==0
    assert [r['advantage'] for r in rows].count(0.)==20
    assert [r['advantage'] for r in rows].count(1.)==3
    assert [r['advantage'] for r in rows].count(-1/3)==9
    assert data['selected_action_tokens']==sum(len(t['action_ids']) for r in rows for t in r['root_turns'])
    assert data['unselected_root_action_tokens']==sum(len(t['action_ids']) for r in rows for t in r['zero_loss_root_turns'])
    return rows

def verify():
    r=read(READY);assert r['identity']==digest({k:v for k,v in r.items() if k!='identity'})
    for p,h in r['closure_sha256'].items():assert sha(p)==h,p
    assert sha(CHECKPOINT/'adapter_model.safetensors')==ADAPTER_SHA
    validate_inputs(read(INPUTS));return r
