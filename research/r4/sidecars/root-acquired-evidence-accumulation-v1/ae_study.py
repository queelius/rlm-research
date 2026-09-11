"""Isolated fixed24/c32 scale reuse with batch versus cumulative return package."""
import functools
import hashlib
import importlib.util
import json
from pathlib import Path
import sys
from types import SimpleNamespace

ROOT=Path(__file__).resolve().parent;SIDE=ROOT.parent;STORE=SIDE.parent;ATTEMPT=ROOT/'outputs/attempt-001'
SS=SIDE/'root-operator-scale-state-v1';SS_READY_SHA='d10c9bb2b7a5f1e8e0d5f3146f2ccc6124d6bbda4373ca6692007af932e119ac'
NAMESPACE='acquired-evidence-accumulation-20260910-v1';SEEDS=tuple(range(981721101,981721117))
assert hashlib.sha256((SS/'READY.json').read_bytes()).hexdigest()==SS_READY_SHA
ss_ready=json.loads((SS/'READY.json').read_text());path=SS/'ss_study.py';assert hashlib.sha256(path.read_bytes()).hexdigest()==ss_ready['source_sha256'][str(path)]
spec=importlib.util.spec_from_file_location('accumulation_qualified_scale_study',path);ss=importlib.util.module_from_spec(spec);sys.modules[spec.name]=ss;spec.loader.exec_module(ss)
sha,read,write,digest,load,aliases=ss.sha,ss.read,ss.write,ss.digest,ss.load,ss.aliases
o,dose,NATIVE,OLD,JOINT,CHILD_SHA=ss.o,ss.dose,ss.NATIVE,ss.OLD,ss.JOINT,ss.CHILD_SHA
runtime,interface,selected,protocol,answer=ss.runtime,ss.interface,ss.selected,ss.protocol,ss.answer

@functools.lru_cache(maxsize=1)
def task_protocol():return load('accumulation_task_local_protocol',ROOT/'ae_protocol.py',sha(ROOT/'ae_protocol.py'))

def make_task(context,row,gold):
    task=o.qnative().make_task(context,row['question'],gold,row['id']);original_setup=task.setup;original_finalize=task.finalize
    arm=row['accumulation_arm']
    async def setup(trace,runtime):
        await original_setup(trace,runtime)
        await runtime.write('batch_contract.py',task_protocol().helper_bytes(arm))
        # Not advertised: no initial ledger file / additional source-state channel.
    async def finalize(trace,runtime):
        await original_finalize(trace,runtime)
        try:
            raw=await runtime.read('.decoder_calls.jsonl',max_bytes=16*1024*1024)
            trace.info['decoder_ledger']=dict(raw=raw.decode(),sha256=hashlib.sha256(raw).hexdigest(),trust='runtime-writable decoder transcript; corroborate native returns and program dataflow',genuine_child_provenance_established=False)
        except Exception as error:
            trace.info['decoder_ledger']=dict(raw=None,error_type=type(error).__name__,message=str(error),genuine_child_provenance_established=False)
    task.setup=setup;task.finalize=finalize
    task.data=task.data.model_copy(update={'prompt':task.data.prompt+task_protocol().extra_prompt(arm),'source_split':'scale-exposed-child-training-catalog-exposed-cumulative-decoder-package'})
    return task

@functools.lru_cache(maxsize=1)
def stack():
    native=o.qnative().stack().native;rows={r['id']:r for r in read(ROOT/'inputs/FREE_PLAN.json')}
    def task(context,prompt,gold,name):
        value=make_task(context,rows[name],gold)
        if value.data.prompt!=prompt:raise ValueError('frozen accumulation prompt changed')
        return value
    return SimpleNamespace(native=SimpleNamespace(**{**vars(native),'task':task}))

def binding():
    value=ss.binding();value.pop('scale_state');value['study']=ROOT.name;value['campaign_id']=ROOT.name
    value['acquired_accumulation']=dict(namespace=NAMESPACE,endpoints=32,blocks=16,arms=['B','C'],structural_admission_only=True,no_training=True)
    return value

def validate(value,descriptor,path):
    if value!=binding():raise ValueError('accumulation binding changed')
    j=o.joint();old=load('accumulation_descriptor_validator',j.SOURCE/'binding.py','865e84908e4f8f198c81587605a37c003fe7f02c69bf1bbbd0fc8c495c18afd1',{'study':j.original});old.validate_descriptor(value,descriptor,sha(path))

def verify():
    ready=read(ROOT/'READY.json')
    if digest({k:v for k,v in ready.items() if k!='identity'})!=ready['identity']:raise ValueError('accumulation identity')
    for path,pin in {**ready['source_sha256'],**ready['input_sha256']}.items():dose.check(path,pin)
    return ready
