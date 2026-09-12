"""Original raw collector inside the scoped terminal-strip-disabled context."""
import argparse
import asyncio
from pathlib import Path
import sys

import checkpoint
import hooks
import study

old={name:sys.modules.get(name) for name in ('study','checkpoint')}
sys.modules.update(study=study,checkpoint=checkpoint)
try:
    source=study.load('terminal_strip_original_collector',study.SOURCE_EVAL/'collect.py')
finally:
    for name,value in old.items():
        if value is None:sys.modules.pop(name,None)
        else:sys.modules[name]=value


async def run(phase,arm,endpoint,output,deadline):
    if phase!='held' or arm!='checkpoint32':raise ValueError('only fixed cp32 held32 ablation permitted')
    with hooks.installed() as contract:
        code=await source.run(phase,arm,endpoint,output,deadline)
        study.write_x(output/'TERMINAL_STRIP_CONTRACT.json',contract)
        return code


if __name__=='__main__':
    parser=argparse.ArgumentParser()
    parser.add_argument('--phase',choices=['held'],required=True)
    parser.add_argument('--arm',choices=['checkpoint32'],required=True)
    parser.add_argument('--endpoint',type=Path,required=True)
    parser.add_argument('--output',type=Path,required=True)
    parser.add_argument('--deadline',type=float,required=True)
    a=parser.parse_args()
    raise SystemExit(asyncio.run(run(a.phase,a.arm,a.endpoint,a.output,a.deadline)))

