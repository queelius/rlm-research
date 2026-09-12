"""Bind unchanged shallow native/role/terminal hooks to the new frozen task prefixes."""
import argparse
import asyncio
from pathlib import Path
import checkpoint
import study

source=study.load('literal_inspection_proven_collect',study.PARENT/'collect.py')
hooks=source.hooks;role_hooks=source.role_hooks;model_context=source.model_context
native_checkpoints=source.native_checkpoints
run=source.run

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--phase',choices=['train'],required=True);p.add_argument('--arm',choices=['checkpoint32'],required=True)
    p.add_argument('--endpoint',type=Path,required=True);p.add_argument('--output',type=Path,required=True);p.add_argument('--deadline',type=float,required=True);a=p.parse_args()
    raise SystemExit(asyncio.run(run(a.phase,a.arm,a.endpoint,a.output,a.deadline)))
