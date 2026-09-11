"""Authored first-action SFT, not sampled trajectories or behavior likelihoods."""
import functools
import hashlib
import importlib.util
import json
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
if hashlib.sha256(path.read_bytes()).hexdigest()!=PINS['study.py']:raise ValueError('pinned study changed')
spec=importlib.util.spec_from_file_location('plan_frozen_success_study',path)
old=importlib.util.module_from_spec(spec);spec.loader.exec_module(old)
for name in ('read','sha','check','write','digest','aliases','row','PRIOR','LOCAL','CONTROL','NATIVE','TRAIN','CHILD_SHA','BASE_SHA','stack','prior','ROW','SIDE'):
    globals()[name]=getattr(old,name)
START=OLD/'outputs/attempt-001/training/checkpoint-0008'
START_SHA='66cce4009628ff7d8e047f08e6fb3a29febdbf8fb3ed8303871f69860f1151d5'
TRAIN_SEED=981320002
ARMS=('canonical','filter_first')
LABELS={'HUM':'human being','LOC':'location','ABBR':'abbreviation','ENTY':'entity','DESC':'description and abstract concept','NUM':'numeric value'}


def transformed(name,path,pin,replacements,view=None,extra=None):
    check(path,pin);text=Path(path).read_text()
    for before,(after,count) in replacements.items():
        if text.count(before)!=count:raise ValueError('counted private seam changed: '+before)
        text=text.replace(before,after)
    module=ModuleType(name);module.__file__=str(path)
    with aliases({'study':view or sys.modules[__name__],**(extra or {})}):exec(compile(text,str(path),'exec'),module.__dict__)
    return module


def private(filename,view=None,extra=None):
    replacements={"'prepared/PLAN.json'":("'prepared-v2/PLAN.json'",1),"'prepared/PROMPTS.json'":("'prepared-v2/PROMPTS.json'",1)} if filename=='readout.py' else {}
    return transformed('plan_private_'+filename[:-3],OLD/filename,PINS[filename],replacements,view,extra)


def load(name,path,pin):
    path=Path(path)
    if path==ROW/'readout.py':
        return transformed(name,path,pin,{'len(prompts) != 24':('len(prompts) != 16',1)})
    if path==PRIOR/'evaluate.py':
        return transformed(name,path,pin,{'planned=24':('planned=16',1),'len(records)==24':('len(records)==16',2)},view=sys.modules['study'])
    return old.load(name,path,pin)


def program(context,family,arm):
    if arm not in ARMS or family not in ('single_user','global'):raise ValueError('training scope/strategy')
    users=context['query_users'][:1]
    relevant='records' if family=='global' else '[r for r in records if r["user"] in '+repr(users)+']'
    selected='relevant' if family=='single_user' and arm=='filter_first' else 'records'
    return ('import json\nfrom rlm.api import run as rlm\nfrom batch_contract import request_for, strict_map\n'
      'records = json.load(open("records.json"))\n'
      f'relevant = {relevant}\nselected = {selected}\nlabels = {{}}\n'
      'for offset in range(0, len(selected), 16):\n'
      '    batch = selected[offset:offset + 16]\n'
      '    child = await rlm(request_for(batch))\n'
      '    labels.update(strict_map(child.answer, [row["id"] for row in batch]))\n'
      f'print(sum(labels[r["id"]] == {LABELS[context["target"]]!r} for r in relevant))')


def authored_row(identity,arm,context,family,prefix,target,code):
    row=dict(id=identity,arm=arm,context_id=context,family=family,provenance='operator-authored initial action CE only',
      input_ids=prefix+target,prompt_length=len(prefix),labels=[-100]*len(prefix)+target,
      loss_mask=[0]*len(prefix)+[1]*len(target),target_tokens=len(target),authored_code=code)
    validate_authored(row);return row


def validate_authored(row):
    if any(k in row for k in ('old_logprobs','reward','advantage','advantages','behavior_logprobs','success')):
        raise ValueError('authored CE has no sampled behavior/reward fields')
    ids=row['input_ids'];n=row['prompt_length']
    if not 0<n<len(ids) or row['labels']!=[-100]*n+ids[n:] or row['loss_mask']!=[0]*n+[1]*(len(ids)-n):raise ValueError('action-only mask')
    if row['target_tokens']!=len(ids)-n or ids[-1]!=151645 or row['provenance']!='operator-authored initial action CE only':raise ValueError('authored native suffix boundary')
    return len(ids)-n


def build_plan(original):
    starts={'query_transfer':981320201,'length_transfer':981320301};counts=dict.fromkeys(starts,0);result=[]
    for row in original:
        group=row['stratum']
        if group=='validation':continue
        new={**row,'source_coordinate_id':row['id'],'seed':starts[group]+counts[group]};del new['id']
        new['id']=digest(new);result.append(new);counts[group]+=1
    if counts!=dict.fromkeys(starts,8):raise ValueError('fixed16 transfer population')
    return result


def validate_prompts(plan,prompts):
    frozen={p['id']:p for p in read(PRIOR/'prepared-v2/EVAL_PROMPTS.json')}
    if plan!=build_plan(read(PRIOR/'prepared-v2/EVAL_PLAN_FINAL.json')) or len(prompts)!=16:raise ValueError('transfer16 plan')
    for row,prompt in zip(plan,prompts):
        source=frozen[row['source_coordinate_id']]
        if prompt['id']!=row['id'] or prompt['prompt']!=source['prompt'] or prompt['token_ids']!=source['token_ids']:raise ValueError('initial physical prompt changed')


def phase_order():return tuple(sorted(('unchanged',*ARMS),key=lambda a:hashlib.sha256(('981320001:readout:'+a).encode()).hexdigest()))
def training_order():return tuple(sorted(ARMS,key=lambda a:hashlib.sha256(('981320001:training:'+a).encode()).hexdigest()))


@functools.lru_cache(maxsize=1)
def verify():
    ready=read(ROOT/'READY.json')
    if digest({k:v for k,v in ready.items() if k!='identity'})!=ready['identity']:raise ValueError('READY identity')
    for p,h in {**ready['source_sha256'],**ready['input_sha256']}.items():check(p,h)
    return ready
