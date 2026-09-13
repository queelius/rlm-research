"""BA18 selection update bindings; released base plus newly initialized LoRA only."""
import importlib.util
import json
import math
from pathlib import Path
import re

ROOT=Path(__file__).resolve().parent;STORE=ROOT.parents[1]
WIDTH=ROOT.parent/'b05-helper-width-v1'
spec=importlib.util.spec_from_file_location('selection_frozen_width_study',WIDTH/'study.py')
width=importlib.util.module_from_spec(spec);spec.loader.exec_module(width)
for name in ('sha','read','digest','write_x','bytes_x','load','aliases'):globals()[name]=getattr(width,name)
PRIOR=ROOT.parent/'openai-mrcr-short-root-token-tis-two-lr-v1'
OLD=ROOT.parent/'openai-mrcr-cp32-fresh8-final-rloo-v1'
REVIEW=STORE/'analyses/b05-helper-width-independent-2026-09-12'
CONFIG_SOURCE=ROOT.parent/'openai-mrcr-procedural-sft-continue32-v1/outputs/attempt-001/checkpoint-0032/adapter_config.json'
BASE=width.MODEL;NATIVE=width.NATIVE
PYTHON=Path('/project/alex_phd/repos/rlm-bootstrap/.worktrees/a100-lora-roundtrip/gpu/training/.venv/bin/python')
INPUTS=ROOT/'TRAIN_INPUTS.json';READY=ROOT/'READY.json';OUTPUT=ROOT/'outputs/attempt-001'
INIT_SEED=SEED=202609320001;NP_SEED=SEED%(2**32)
LEARNING_RATE=1e-4;DENOMINATOR=18;TEMPERATURE=.5;TOKEN_TIS_CAP=2.
SCIENCE_SECONDS=900;OWNER_SECONDS=1100;EXTERNAL_SECONDS=1200
ALIAS='Qwen3-4B-Instruct-2507-b05-flat-BA18-step1'
positions_and_targets=load('selection_original_physical_positions',PRIOR/'study.py').positions_and_targets

def reward(predicted,gold,known):
    assert predicted<=known and gold<=known and known
    positive=len(gold);negative=len(known-gold)
    recalls=([len(predicted&gold)/positive] if positive else [])+([len(known-gold-predicted)/negative] if negative else [])
    return sum(recalls)/len(recalls)

def array_mask(ids,tokenizer):
    text=tokenizer.decode(ids,skip_special_tokens=True)
    # Exact valid object and unique key; no gold or identifier content enters mask creation.
    def pairs(items):
        result={}
        for k,v in items:
            if k in result:raise ValueError('duplicate key')
            result[k]=v
        return result
    parsed=json.loads(text,object_pairs_hook=pairs)
    assert set(parsed)=={'eligible_ids'} and isinstance(parsed['eligible_ids'],list)
    match=re.search(r'"eligible_ids"\s*:\s*(\[)',text);assert match
    begin=match.start(1);value,end=json.JSONDecoder().raw_decode(text,begin)
    assert value==parsed['eligible_ids']
    mask=[];previous='';boundary=[]
    for j in range(len(ids)):
        prefix=tokenizer.decode(ids[:j+1],skip_special_tokens=True)
        assert prefix.startswith(previous) and text.startswith(prefix),'nonmonotone native token text'
        lo,hi=len(previous),len(prefix);selected=int(hi>lo and hi>begin and lo<end)
        mask.append(selected)
        if selected and (lo<begin or hi>end):boundary.append(dict(action_index=j,char_start=lo,char_end=hi))
        previous=prefix
    assert previous==text and any(mask) and ids[-1] in (151645,151643) and mask[-1]==0
    return mask,dict(array_start_char=begin,array_end_char=end,text_sha256=digest(text),
        selected_tokens=sum(mask),unselected_tokens=len(mask)-sum(mask),boundary_overlap_tokens=boundary,
        gold_used=False,rule='native tokens intersecting array including list continuation/termination; joint token boundary recorded')

def validate_inputs(data):
    rows=data['episodes'];assert len(rows)==18 and len({r['group_id'] for r in rows})==9
    assert len({r['episode_id'] for r in rows})==18
    for row in rows:
        group=[r for r in rows if r['group_id']==row['group_id']];assert len(group)==2
        other=next(r for r in group if r['episode_id']!=row['episode_id'])
        assert row['reward']==reward(set(row['predicted_ids']),set(row['gold_ids']),set(row['known_ids']))
        assert row['advantage']==row['reward']-other['reward']
        assert row['baseline']==other['reward'] and row['available']
        assert len(row['root_turns'])==1
        turn=row['root_turns'][0];positions_and_targets(turn)
        assert len(turn['input_ids'])<=8192 and len(turn['action_ids'])<=384
        assert len(row['selection_mask'])==len(turn['action_ids']) and set(row['selection_mask'])<={0,1}
        assert row['actual_loss_mask']==[0]*len(turn['prompt_ids'])+row['selection_mask']
    assert sum(r['advantage']!=0 for r in rows)==8
    assert sum(r['advantage']==0 for r in rows)==10
    assert math.isclose(sum(r['advantage'] for r in rows),0.,abs_tol=1e-14)
    return rows

def verify():
    ready=read(READY);assert ready['identity']==digest({k:v for k,v in ready.items() if k!='identity'})
    for p,h in ready['closure_sha256'].items():assert sha(p)==h,p
    validate_inputs(read(INPUTS));return ready
