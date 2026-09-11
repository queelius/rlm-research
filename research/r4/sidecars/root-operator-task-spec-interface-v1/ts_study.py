"""Exact fixed24/c32 binding, common original files, redundant task description."""
import functools
import hashlib
import importlib.util
import json
from pathlib import Path
import sys
from types import SimpleNamespace

ROOT=Path(__file__).resolve().parent;SIDE=ROOT.parent;STORE=SIDE.parent;ATTEMPT=ROOT/'outputs/attempt-001';MASTER=2026091900
SS=SIDE/'root-operator-scale-state-v1';SS_READY_SHA='d10c9bb2b7a5f1e8e0d5f3146f2ccc6124d6bbda4373ca6692007af932e119ac'
assert hashlib.sha256((SS/'READY.json').read_bytes()).hexdigest()==SS_READY_SHA
ss_ready=json.loads((SS/'READY.json').read_text());path=SS/'ss_study.py';assert hashlib.sha256(path.read_bytes()).hexdigest()==ss_ready['source_sha256'][str(path)]
_spec=importlib.util.spec_from_file_location('task_spec_qualified_scale_study',path);ss=importlib.util.module_from_spec(_spec);sys.modules[_spec.name]=ss;_spec.loader.exec_module(ss)
sha,read,write,digest,load,aliases=ss.sha,ss.read,ss.write,ss.digest,ss.load,ss.aliases
o,dose,NATIVE,OLD,JOINT,CHILD_SHA=ss.o,ss.dose,ss.NATIVE,ss.OLD,ss.JOINT,ss.CHILD_SHA
runtime,interface,selected,protocol,answer=ss.runtime,ss.interface,ss.selected,ss.protocol,ss.answer
CT=ss.CT
@functools.lru_cache(maxsize=1)
def task_protocol():return load('task_spec_public_metadata',ROOT/'ts_protocol.py',sha(ROOT/'ts_protocol.py'))
def make_task(context,row,gold):
    task=o.qnative().make_task(context,row['question'],gold,row['id']);original_setup=task.setup
    filename,content=task_protocol().file_content(row)
    async def setup(trace,runtime):
        await original_setup(trace,runtime)
        if filename:await runtime.write(filename,content)
    task.setup=setup
    task.data=task.data.model_copy(update={'prompt':task.data.prompt+task_protocol().extra_prompt(row),'source_split':'prior-composition-exposed-task-parameter-interface'})
    return task
@functools.lru_cache(maxsize=1)
def stack():
    native=o.qnative().stack().native;rows={r['id']:r for r in read(ROOT/'inputs/FREE_PLAN.json')}
    def task(context,prompt,gold,name):
        value=make_task(context,rows[name],gold)
        if value.data.prompt!=prompt:raise ValueError('task-spec frozen native prompt changed')
        return value
    return SimpleNamespace(native=SimpleNamespace(**{**vars(native),'task':task}))
def binding():
    value=ss.binding();value.pop('scale_state');value['study']=ROOT.name;value['campaign_id']=ROOT.name
    value['task_spec']=dict(endpoints=72,tasks=24,arms=['U','P','J'],master=MASTER,no_training=True)
    return value
def validate(value,descriptor,path):
    if value!=binding():raise ValueError('task-spec binding changed')
    j=o.joint();old=load('task_spec_original_descriptor',j.SOURCE/'binding.py','865e84908e4f8f198c81587605a37c003fe7f02c69bf1bbbd0fc8c495c18afd1',{'study':j.original});old.validate_descriptor(value,descriptor,sha(path))
def verify():
    ready=read(ROOT/'READY.json')
    if digest({k:v for k,v in ready.items() if k!='identity'})!=ready['identity']:raise ValueError('task-spec identity')
    for path,pin in {**ready['source_sha256'],**ready['input_sha256']}.items():dose.check(path,pin)
    return ready
