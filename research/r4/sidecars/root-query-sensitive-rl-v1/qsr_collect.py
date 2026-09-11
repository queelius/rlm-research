"""Qualified collector, three counted task/runtime/endpoint-timeout seams only."""
import argparse
import ast
import asyncio
import functools
from pathlib import Path
import qsr_common as common
import qsr_native as n
import qsr_study as s

impl=s.private('collect.py',{'study':s,'native':n,'common':common})
binding_for=impl.binding_for;validate_descriptor=impl.validate_descriptor
def planned(phase):
    plans=s.read(s.ROOT/'inputs/PLANS.json')
    if phase in ('readout-unchanged','readout-trained'):return plans['readout']
    if phase.startswith('window-') and phase[7:].isdigit() and 1<=int(phase[7:])<=12:return plans['training'][str(int(phase[7:]))]
    raise ValueError('not a frozen12-window/final phase')
_verify=impl.verify_spec
@functools.lru_cache(maxsize=None)
def verify_spec(path):
    spec=_verify(path);g=spec['generation']
    if spec['phase'].startswith('window-'):
        if g is None or g['candidate_window']!=int(spec['phase'][7:]):raise ValueError('training candidate-window identity mismatch')
    elif g is not None:raise ValueError('final readout carries training generation')
    return spec
impl.planned=planned;impl.verify_spec=verify_spec
prepare_spec=impl.prepare_spec;dispatch=impl.dispatch

def composed_collect_source():
    path=s.OLD/'collect.py';s.check(path,s.OLD_MANIFEST['source_sha256'][str(path)])
    text=path.read_text();node=next(v for v in ast.parse(text).body if isinstance(v,ast.AsyncFunctionDef) and v.name=='collect');code=ast.get_source_segment(text,node)
    changes={
        "with s.aliases({'study': st.prior, 'interface': st.interface}):\n        interface = st.local.configure_interface(output)":"interface = n.interface(output)",
        "task = st.native.task(context, tasks[row['task_name']]['prompt'], gold[context['id']]['answers'][row['family']], row['task_name'])":"task = n.make_task(context, tasks[row['task_name']]['question'], gold[context['id']]['answers'][row['family']], row['task_name'])",
        "await env.run_slot(RunSlot(task), interface.e.make_context(endpoint, row))":"await asyncio.wait_for(env.run_slot(RunSlot(task), interface.e.make_context(endpoint, row)), min(180., max(.001, deadline-time.time())))",
    }
    for before,after in changes.items():
        if code.count(before)!=1:raise ValueError('qualified collector seam changed')
        code=code.replace(before,after)
    return code
exec(compile(composed_collect_source(),str(s.OLD/'collect.py')+':qsr-three-seams','exec'),impl.__dict__)
collect=impl.collect
def parse_args(argv=None):
    p=argparse.ArgumentParser();p.add_argument('--spec',type=Path,required=True);p.add_argument('--output',type=Path,required=True);p.add_argument('--deadline',type=float,required=True);return p.parse_args(argv)
if __name__=='__main__':
    a=parse_args();raise SystemExit(asyncio.run(collect(a.spec,a.output,a.deadline)))
