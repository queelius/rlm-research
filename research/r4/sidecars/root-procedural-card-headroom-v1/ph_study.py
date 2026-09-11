"""Fixed24/c32, original file-only free task, shared procedural card in treatment only."""
import functools
import hashlib
import importlib.util
import json
from pathlib import Path
import sys
from types import SimpleNamespace

ROOT=Path(__file__).resolve().parent;SIDE=ROOT.parent;STORE=SIDE.parent;ATTEMPT=ROOT/'outputs/attempt-001'
SS=SIDE/'root-operator-scale-state-v1';SS_READY_SHA='d10c9bb2b7a5f1e8e0d5f3146f2ccc6124d6bbda4373ca6692007af932e119ac'
NAMESPACE='procedural-card-headroom-20260910-v1';SEEDS=tuple(range(983721101,983721125))
assert hashlib.sha256((SS/'READY.json').read_bytes()).hexdigest()==SS_READY_SHA
ss_ready=json.loads((SS/'READY.json').read_text());path=SS/'ss_study.py';assert hashlib.sha256(path.read_bytes()).hexdigest()==ss_ready['source_sha256'][str(path)]
spec=importlib.util.spec_from_file_location('procedural_card_qualified_scale_study',path);ss=importlib.util.module_from_spec(spec);sys.modules[spec.name]=ss;spec.loader.exec_module(ss)
sha,read,write,digest,load,aliases=ss.sha,ss.read,ss.write,ss.digest,ss.load,ss.aliases
o,dose,NATIVE,OLD,JOINT,CHILD_SHA=ss.o,ss.dose,ss.NATIVE,ss.OLD,ss.JOINT,ss.CHILD_SHA
runtime,interface,selected,protocol,answer=ss.runtime,ss.interface,ss.selected,ss.protocol,ss.answer
CT=ss.CT

def card():return (ROOT/'CARD.txt').read_text()

def make_task(context,row,gold):
    task=o.qnative().make_task(context,row['question'],gold,row['id'])
    if row['card_arm'] not in ('U','P'):raise ValueError('original or procedural arm required')
    prompt=task.data.prompt+('' if row['card_arm']=='U' else '\n\n'+card())
    task.data=task.data.model_copy(update={'prompt':prompt,'source_split':'composition-exposed-child-training-catalog-exposed-procedural-headroom'})
    return task

@functools.lru_cache(maxsize=1)
def stack():
    native=o.qnative().stack().native;rows={r['id']:r for r in read(ROOT/'inputs/FREE_PLAN.json')}
    def task(context,prompt,gold,name):
        value=make_task(context,rows[name],gold)
        if value.data.prompt!=prompt:raise ValueError('frozen procedural-card prompt changed')
        return value
    return SimpleNamespace(native=SimpleNamespace(**{**vars(native),'task':task}))

def binding():
    value=ss.binding();value.pop('scale_state');value['study']=ROOT.name;value['campaign_id']=ROOT.name
    value['procedural_card']=dict(namespace=NAMESPACE,endpoints=48,blocks=24,arms=['U','P'],card_sha256=sha(ROOT/'CARD.txt'),no_training=True)
    return value

def validate(value,descriptor,path):
    if value!=binding():raise ValueError('procedural-card binding changed')
    j=o.joint();old=load('procedural_card_descriptor_validator',j.SOURCE/'binding.py','865e84908e4f8f198c81587605a37c003fe7f02c69bf1bbbd0fc8c495c18afd1',{'study':j.original});old.validate_descriptor(value,descriptor,sha(path))

def verify():
    ready=read(ROOT/'READY.json')
    if digest({k:v for k,v in ready.items() if k!='identity'})!=ready['identity']:raise ValueError('procedural-card identity')
    for path,pin in {**ready['source_sha256'],**ready['input_sha256']}.items():dose.check(path,pin)
    return ready
