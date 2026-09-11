"""Isolated scientific-task namespace over qualified fixed6/24 native readout."""
import functools
import hashlib
import importlib.util
from pathlib import Path
import sys
from types import SimpleNamespace

ROOT=Path(__file__).resolve().parent;SIDE=ROOT.parent;STORE=SIDE.parent
ATTEMPT=ROOT/'outputs/attempt-001';MASTER=2026091500
DR=SIDE/'root-operator-dose-readout-v1'
DR_STUDY_SHA='077db97633768fe8ae0f4b9c11844bc933d32d647a436477e1bcf3b61b4a065c'
DR_READY_SHA='e51be544e14d037dcd92427310f5514609ea1f38f8ab33c176187d5433685f42'
if hashlib.sha256((DR/'dr_study.py').read_bytes()).hexdigest()!=DR_STUDY_SHA:raise ValueError('qualified study source')
spec=importlib.util.spec_from_file_location('composition_qualified_dose_readout_study',DR/'dr_study.py');dr=importlib.util.module_from_spec(spec);sys.modules[spec.name]=dr;spec.loader.exec_module(dr)
dr.dose.check(DR/'READY.json',DR_READY_SHA)
sha,read,write,digest=dr.sha,dr.read,dr.write,dr.digest
dose,o,aliases,NATIVE,OLD,JOINT,CHILD_SHA=dr.dose,dr.o,dr.aliases,dr.NATIVE,dr.OLD,dr.JOINT,dr.CHILD_SHA
TRAIN_READY_SHA=dr.TRAIN_READY_SHA;TRAINING=dr.TRAINING
load,runtime,interface,selected=dr.load,dr.runtime,dr.interface,dr.selected
INVENTORY=STORE/'ideas/2026-09-10-operator-next-training-source-inventory.json'
INVENTORY_SHA='31bec7c63b53bbb60ebbc588beea895d1ef40d2242fc546da099b4da35fdf70f'

@functools.lru_cache(maxsize=1)
def protocol():
    # Resolve inherited physical-accounting protocol against its original namespace first.
    dr.protocol()
    import ct_protocol
    return ct_protocol
def answer(records,labels,row):return protocol().answer(records,labels,row)
@functools.lru_cache(maxsize=1)
def stack():
    native=o.qnative().stack().native
    def task(context,prompt,gold,name):
        query=read(ROOT/'inputs/PROMPTS_ACCURATE.json')[name]['plain_query']
        value=o.qnative().make_task(context,query,gold,name)
        if value.data.prompt!=prompt:raise ValueError('frozen native prompt changed')
        value.data=value.data.model_copy(update={'source_split':'root-new-under-refreshed-named-inventory-child-training-and-prepared-exposed'})
        return value
    return SimpleNamespace(native=SimpleNamespace(**{**vars(native),'task':task}))
def binding(policy,chosen=None):
    value=dr.binding(policy,chosen);value['study']=ROOT.name;value['campaign_id']=ROOT.name
    value['composition_transfer']=dict(fixed_policy=policy,master_seed=MASTER,planned_contexts=8,questions_per_context=6,no_training=True)
    return value
def validate(value,descriptor,path):
    if value!=binding(value['operator_dose']['policy']):raise ValueError('composition actual binding differs')
    j=o.joint();old=load('composition_descriptor_validator',j.SOURCE/'binding.py','865e84908e4f8f198c81587605a37c003fe7f02c69bf1bbbd0fc8c495c18afd1',{'study':j.original})
    old.validate_descriptor(value,descriptor,sha(path))
def verify():
    ready=read(ROOT/'READY.json')
    if digest({k:v for k,v in ready.items() if k!='identity'})!=ready['identity']:raise ValueError('composition ready identity')
    for path,pin in {**ready['source_sha256'],**ready['input_sha256']}.items():dose.check(path,pin)
    return ready
