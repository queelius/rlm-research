"""Exact48 free starts; original native final and all physical records retained."""
import asyncio
import functools
import ph_study as s

@functools.lru_cache(maxsize=1)
def implementation():
    path=s.OLD/'od_collect.py';module=s.load('procedural_card_original_collector',path,s.read(s.OLD/'READY_v2.json')['source_sha256'][str(path)],{'od_study':s,'od_protocol':s.protocol()})
    with s.aliases({'od_study':s,'od_protocol':s.protocol(),'od_binding':s}):return module.implementation()

def main():
    module=implementation();args=module.parse_args()
    if (args.mode,args.plan,args.start,args.stop)!=('free','FREE_PLAN.json',0,48):raise ValueError('exact48 free-only inventory')
    with s.aliases({'od_study':s,'od_protocol':s.protocol(),'od_binding':s}):asyncio.run(module.run(args))

if __name__=='__main__':main()

