"""Exact32 bounded-view free starts through the qualified native collector."""
import asyncio
import functools
import bv_study as s

@functools.lru_cache(maxsize=1)
def implementation():
    path=s.BASE/'ae_collect.py';module=s.load('bounded_view_base_collector',path,s.base_ready['source_sha256'][str(path)],{'ae_study':s})
    with s.aliases({'ae_study':s}):return module.implementation()

def main():
    module=implementation();args=module.parse_args()
    if (args.mode,args.plan,args.start,args.stop)!=('free','FREE_PLAN.json',0,32):raise ValueError('exact32 bounded-view free inventory')
    with s.aliases({'od_study':s,'od_protocol':s.protocol(),'od_binding':s,'ae_study':s}):asyncio.run(module.run(args))

if __name__=='__main__':main()

