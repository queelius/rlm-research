"""Unchanged 24-row native collector with two-arm authenticated binding."""
import argparse
import asyncio
from pathlib import Path
import study as s
import binding as b

inherited=s.private('readout.py',{'exact three-arm binding and fresh coordinate crosswalk only':('exact two-arm LR binding and fresh coordinate crosswalk only',1)},extra={'binding':b})
if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--weight',choices=('low','high'),required=True)
    for name in ('training','binding','endpoint','output'):parser.add_argument('--'+name,type=Path,required=True)
    parser.add_argument('--deadline',type=float,required=True)
    raise SystemExit(asyncio.run(inherited.collect(parser.parse_args())))
