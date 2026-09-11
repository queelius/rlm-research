"""Fixed24/c32 qualified card runtime, isolated four-cell inputs and actual threshold scorer."""
import functools
import hashlib
import importlib.util
import json
from pathlib import Path
import sys
from types import SimpleNamespace
import cf_problem as problem

ROOT=Path(__file__).resolve().parent;SIDE=ROOT.parent;STORE=SIDE.parent;ATTEMPT=ROOT/'outputs/attempt-001'
PH=SIDE/'root-procedural-card-headroom-v1';PH_READY_SHA='06fc26f75af9902d8d6f371315d810612d4bdab25e073d907564cf92bedc7261'
GATE=STORE/'analyses/root-counterfactual-operator-gate-2026-09-10/GATE.json';GATE_SHA='ce10e939b210bcc11c14d47cdf27a2ab57799146f9c1670f503bb006b9c16880'
NAMESPACE='counterfactual-card-signatures-20260910-v1';SEEDS=tuple(range(984921101,984921125));CELLS=['original_U','original_P','counterfactual_U','counterfactual_P']
assert hashlib.sha256((PH/'READY.json').read_bytes()).hexdigest()==PH_READY_SHA
ph_ready=json.loads((PH/'READY.json').read_text());p=PH/'ph_study.py';assert hashlib.sha256(p.read_bytes()).hexdigest()==ph_ready['source_sha256'][str(p)]
spec=importlib.util.spec_from_file_location('counter_card_qualified_ph_study',p);ph=importlib.util.module_from_spec(spec);sys.modules[spec.name]=ph;spec.loader.exec_module(ph)
sha,read,write,digest,load,aliases=ph.sha,ph.read,ph.write,ph.digest,ph.load,ph.aliases
o,dose,NATIVE,OLD,JOINT,CHILD_SHA=ph.o,ph.dose,ph.NATIVE,ph.OLD,ph.JOINT,ph.CHILD_SHA
runtime,interface,selected,protocol=ph.runtime,ph.interface,ph.selected,ph.protocol
CT,ss=ph.CT,ph.ss
def card():return (ROOT/'CARD.txt').read_text()
def answer(records,labels,row):return problem.answer(records,labels,row)
def make_task(context,row,gold):
    task=o.qnative().make_task(context,row['question'],gold,row['id'])
    if row['card_arm'] not in ('U','P'):raise ValueError('unknown card arm')
    task.data=task.data.model_copy(update={'prompt':task.data.prompt+('' if row['card_arm']=='U' else '\n\n'+card()),'source_split':'exposed-counterfactual-query-selected-child-training-catalog'})
    return task
@functools.lru_cache(maxsize=1)
def stack():
    native=o.qnative().stack().native;rows={r['id']:r for r in read(ROOT/'inputs/FREE_PLAN.json')}
    def task(context,prompt,gold,name):
        value=make_task(context,rows[name],gold)
        if value.data.prompt!=prompt:raise ValueError('frozen four-cell native prompt changed')
        return value
    return SimpleNamespace(native=SimpleNamespace(**{**vars(native),'task':task}))
def binding():
    value=ph.binding();value.pop('procedural_card');value['study']=ROOT.name;value['campaign_id']=ROOT.name
    value['counterfactual_card']=dict(namespace=NAMESPACE,endpoints=96,blocks=24,parent_clusters=8,cells=CELLS,gate_sha256=GATE_SHA,card_sha256=sha(ROOT/'CARD.txt'),no_training=True)
    return value
def validate(value,descriptor,path):
    if value!=binding():raise ValueError('fourcell model binding changed')
    j=o.joint();v=load('counter_card_descriptor_validator',j.SOURCE/'binding.py','865e84908e4f8f198c81587605a37c003fe7f02c69bf1bbbd0fc8c495c18afd1',{'study':j.original});v.validate_descriptor(value,descriptor,sha(path))
def verify():
    ready=read(ROOT/'READY.json')
    if digest({k:v for k,v in ready.items() if k!='identity'})!=ready['identity']:raise ValueError('fourcell identity')
    for path,pin in {**ready['source_sha256'],**ready['input_sha256']}.items():dose.check(path,pin)
    return ready
