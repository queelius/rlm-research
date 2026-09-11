"""Authenticated private control reuse; new identities, seeds and numerical LR only."""
import functools
import hashlib
import importlib.util
import sys
from pathlib import Path
from types import ModuleType

ROOT=Path(__file__).resolve().parent
OLD=ROOT.parent/'root-success-trajectory-sft-v1'
PINS={'study.py':'054f2002064549de9fbe883402effb112b20e81b0047bf99db235a5384384fe8',
 'train.py':'9f7c06f4be456b8273dd7cd439d6730b3096ae9d8bd355e75f3e710b5222792b',
 'binding.py':'a2490666c82d961544121b3141d4616fc4539a25ed975dbaef9a08b6403849f4',
 'readout.py':'7932ec4acaadebd5309022d62803e375e0dd34142b847461f1a9d7a9fe4e6262',
 'launch.py':'3b148684a1de6a0fdb04f76ed5ddde14cd6fd1a19064115afb40a0ec3ca6fa5d'}
path=OLD/'study.py'
if hashlib.sha256(path.read_bytes()).hexdigest()!=PINS['study.py']:raise ValueError('control source changed')
spec=importlib.util.spec_from_file_location('lr_frozen_control_study',path)
old=importlib.util.module_from_spec(spec);spec.loader.exec_module(old)
for name in ('read','sha','check','write','digest','load','aliases','row','PRIOR','LOCAL','CONTROL','NATIVE','TRAIN','CONTROL_SHA','CHILD_SHA','BASE_SHA','START','TRAIN_SEED','validate_turn','stack','prior','ROW','SIDE','SCREEN','ADAPTIVE'):
    globals()[name]=getattr(old,name)
LOW_SHA='66cce4009628ff7d8e047f08e6fb3a29febdbf8fb3ed8303871f69860f1151d5'


def private(filename,replacements=None,extra=None,view=None):
    source=OLD/filename;check(source,PINS[filename]);text=source.read_text()
    for before,(after,count) in (replacements or {}).items():
        if text.count(before)!=count:raise ValueError('counted private seam changed: '+before)
        text=text.replace(before,after)
    module=ModuleType('lr_private_'+filename[:-3]);module.__file__=str(source)
    with aliases({'study':view or sys.modules[__name__],**(extra or {})}):
        exec(compile(text,str(source),'exec'),module.__dict__)
    return module


def build_plan(original):
    starts={'validation':981314101,'query_transfer':981314201,'length_transfer':981314301}
    counts=dict.fromkeys(starts,0);result=[]
    for row in original:
        group=row['stratum'];new={**row,'source_coordinate_id':row['id'],'seed':starts[group]+counts[group]}
        del new['id'];new['id']=digest(new);result.append(new);counts[group]+=1
    if counts!=dict.fromkeys(starts,8):raise ValueError('fixed24 population changed')
    return result


def validate_prompts(plan,prompts):
    frozen={p['id']:p for p in read(PRIOR/'prepared-v2/EVAL_PROMPTS.json')}
    if plan!=build_plan(read(PRIOR/'prepared-v2/EVAL_PLAN_FINAL.json')) or len(prompts)!=24:raise ValueError('plan changed')
    for row,prompt in zip(plan,prompts):
        source=frozen[row['source_coordinate_id']]
        if prompt['id']!=row['id'] or prompt['prompt']!=source['prompt'] or prompt['token_ids']!=source['token_ids']:
            raise ValueError('native prompt changed')


def phase_order():return tuple(sorted(('low','high'),key=lambda arm:hashlib.sha256(('981314001:'+arm).encode()).hexdigest()))


@functools.lru_cache(maxsize=1)
def verify():
    ready=read(ROOT/'READY.json')
    if digest({k:v for k,v in ready.items() if k!='identity'})!=ready['identity']:raise ValueError('READY identity')
    for p,h in {**ready['source_sha256'],**ready['input_sha256']}.items():check(p,h)
    return ready


control_selected=old.control_selected
