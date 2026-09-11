"""Qualified native collection; exact16 coordinate crosswalk and root binding."""
import argparse
import asyncio
from pathlib import Path
import study as s
import binding as b
inherited=s.private('readout.py',extra={'binding':b})
collect=inherited.collect

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--weight',choices=('unchanged',*s.ARMS),required=True)
    for name in ('training','binding','endpoint','output'):p.add_argument('--'+name,type=Path,required=True)
    p.add_argument('--deadline',type=float,required=True)
    raise SystemExit(asyncio.run(collect(p.parse_args())))
