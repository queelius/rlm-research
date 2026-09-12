"""Shallow original native collector, exact terminal hooks, no T1 modifications."""
import argparse
import asyncio
from pathlib import Path
import sys
import checkpoint
import study

old={n:sys.modules.get(n) for n in ('study','checkpoint')};sys.modules.update(study=study,checkpoint=checkpoint)
try:source=study.load('fixedRL_eval_original_science',study.SOURCE_EVAL/'collect.py')
finally:
    for n,v in old.items():
        if v is None:sys.modules.pop(n,None)
        else:sys.modules[n]=v
hooks=study.terminal_hooks()
def verify_ready():return study.verify()
source.verify_ready=verify_ready

async def run(phase,arm,endpoint,output,deadline):
    if phase not in study.CAPS or arm!='updated':raise ValueError('fixed phase/arm differs')
    with hooks.installed() as contract:
        code=await source.run(phase,arm,endpoint,output,deadline)
        study.write_x(output/'TERMINAL_STRIP_CONTRACT.json',contract)
        return code

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--phase',choices=tuple(study.CAPS),required=True)
    p.add_argument('--arm',choices=['updated'],required=True);p.add_argument('--endpoint',type=Path,required=True)
    p.add_argument('--output',type=Path,required=True);p.add_argument('--deadline',type=float,required=True);a=p.parse_args()
    raise SystemExit(asyncio.run(run(a.phase,a.arm,a.endpoint,a.output,a.deadline)))
