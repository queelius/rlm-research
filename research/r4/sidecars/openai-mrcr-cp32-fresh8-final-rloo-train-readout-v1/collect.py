"""Reuse exact qualified native collector and terminal hooks; no decoding changes."""
import argparse
import asyncio
from pathlib import Path
import checkpoint
import study
adapter=study.bound('fresh8_trainread_collector',study.PRIOR/'collect.py',study=study,checkpoint=checkpoint)
source=adapter.source;hooks=adapter.hooks;verify_ready=adapter.verify_ready;run=adapter.run
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--phase',choices=['train'],required=True)
    p.add_argument('--arm',choices=['updated'],required=True);p.add_argument('--endpoint',type=Path,required=True)
    p.add_argument('--output',type=Path,required=True);p.add_argument('--deadline',type=float,required=True);a=p.parse_args()
    raise SystemExit(asyncio.run(run(a.phase,a.arm,a.endpoint,a.output,a.deadline)))
