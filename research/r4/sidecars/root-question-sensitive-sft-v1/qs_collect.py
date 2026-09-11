"""Qualified actual capture/free runner; exact72/8 plans in isolated namespaces."""
import argparse
import asyncio
import functools
from pathlib import Path
import qs_study as s
import qs_protocol as p
import qs_binding as b
@functools.lru_cache(maxsize=1)
def implementation():
    path=s.OLD/'od_collect.py';module=s.load('qs_qualified_operator_collector',path,s.cf_ready['source_sha256'][str(path)],{'od_study':s,'od_protocol':p})
    with s.aliases({'od_study':s,'od_protocol':p,'od_binding':b}):return module.implementation()
def parse_args(argv=None):
    ap=argparse.ArgumentParser();ap.add_argument('--mode',choices=('capture','free'),required=True);ap.add_argument('--plan',choices=('TRAIN_PLAN.json','FREE_PLAN.json','DEV_PLAN.json'),required=True)
    for name in ('binding','endpoint','output'):ap.add_argument('--'+name,type=Path,required=True)
    ap.add_argument('--start',type=int,default=0);ap.add_argument('--stop',type=int,required=True);ap.add_argument('--deadline',type=float,required=True);args=ap.parse_args(argv)
    if (args.mode,args.plan,args.start,args.stop) not in (('capture','TRAIN_PLAN.json',0,72),('free','FREE_PLAN.json',0,72),('free','DEV_PLAN.json',0,8)):raise ValueError('exact approved capture/readout inventory')
    return args
def main():
    args=parse_args();module=implementation()
    with s.aliases({'od_study':s,'od_protocol':p,'od_binding':b}):asyncio.run(module.run(args))
if __name__=='__main__':main()
