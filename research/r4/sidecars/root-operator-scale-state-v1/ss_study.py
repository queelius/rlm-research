"""Exact fixed24/c32 study binding over frozen corrected native composition runtime."""
import functools
import hashlib
import importlib.util
from pathlib import Path
import sys
from types import SimpleNamespace

ROOT=Path(__file__).resolve().parent;SIDE=ROOT.parent;STORE=SIDE.parent;ATTEMPT=ROOT/'outputs/attempt-001'
CT=SIDE/'root-operator-composition-transfer-v1';CT_READY_SHA='9cfd1febd1101ece4fd1f69d4a1e64909a7822f83ea0299cbc78d8e2284398b1';MASTER=2026091700
def raw_sha(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()
assert raw_sha(CT/'READY.json')==CT_READY_SHA
import json
ct_ready=json.loads((CT/'READY.json').read_text());assert raw_sha(CT/'ct_study.py')==ct_ready['source_sha256'][str(CT/'ct_study.py')]
spec=importlib.util.spec_from_file_location('scale_frozen_composition_study',CT/'ct_study.py');ct=importlib.util.module_from_spec(spec);sys.modules[spec.name]=ct;spec.loader.exec_module(ct)
sha,read,write,digest,load,aliases=ct.sha,ct.read,ct.write,ct.digest,ct.load,ct.aliases
o,dose,NATIVE,OLD,JOINT,CHILD_SHA=ct.o,ct.dose,ct.NATIVE,ct.OLD,ct.JOINT,ct.CHILD_SHA
runtime,interface=ct.runtime,ct.interface
@functools.lru_cache(maxsize=1)
def protocol():
    value=load('scale_frozen_composition_protocol',CT/'ct_protocol.py',ct_ready['source_sha256'][str(CT/'ct_protocol.py')],{'ct_study':ct})
    value.physical_cost=ct.dr.protocol().physical_cost
    return value
def answer(records,labels,row):return protocol().answer(records,labels,row)
@functools.lru_cache(maxsize=1)
def stack():
    native=o.qnative().stack().native
    def task(context,prompt,gold,name):
        query=read(ROOT/'inputs/PROMPTS_ACCURATE.json')[name]['plain_query'];value=o.qnative().make_task(context,query,gold,name)
        if value.data.prompt!=prompt:raise ValueError('frozen scale native prompt changed')
        value.data=value.data.model_copy(update={'source_split':'nested-scale-root-new-under-named-inventory-child-training-catalog-exposed'})
        return value
    return SimpleNamespace(native=SimpleNamespace(**{**vars(native),'task':task}))
def selected():
    chosen=ct.selected('sft24')
    if chosen['step']!=24 or chosen['adapter_sha256']!='94022838a64a530e1abc8daf6cd43502d8aec7d549b6bfec10dd4928b0ca9006':raise ValueError('fixed24 changed')
    return chosen
def binding():
    value=ct.binding('sft24',selected());value.pop('composition_transfer');value['study']=ROOT.name;value['campaign_id']=ROOT.name
    value['scale_state']=dict(master=MASTER,parent_clusters=4,sizes=[16,128,256],endpoints=24,no_training=True,no_batch_constraint=True)
    return value
def validate(value,descriptor,path):
    if value!=binding():raise ValueError('scale actual binding changed')
    j=o.joint();old=load('scale_descriptor_validator',j.SOURCE/'binding.py','865e84908e4f8f198c81587605a37c003fe7f02c69bf1bbbd0fc8c495c18afd1',{'study':j.original});old.validate_descriptor(value,descriptor,sha(path))
def verify():
    ready=read(ROOT/'READY.json')
    if digest({k:v for k,v in ready.items() if k!='identity'})!=ready['identity']:raise ValueError('scale identity')
    for path,pin in {**ready['source_sha256'],**ready['input_sha256']}.items():dose.check(path,pin)
    return ready
