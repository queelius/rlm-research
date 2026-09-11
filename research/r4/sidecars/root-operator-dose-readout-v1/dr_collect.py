"""Qualified free collector; only explicit study/protocol/binding namespaces differ."""
import asyncio
import functools
import dr_study as s

@functools.lru_cache(maxsize=1)
def implementation():
    path=s.OLD/'od_collect.py';module=s.load('dose_readout_original_collector',path,s.read(s.OLD/'READY_v2.json')['source_sha256'][str(path)],{'od_study':s,'od_protocol':s.protocol()})
    with s.aliases({'od_study':s,'od_protocol':s.protocol(),'od_binding':s}):return module.implementation()

def main():
    module=implementation();args=module.parse_args()
    if args.mode!='free' or args.plan!='FREE_PLAN.json' or args.start!=0 or args.stop!=48:raise ValueError('exact frozen48 free coordinates only')
    with s.aliases({'od_study':s,'od_protocol':s.protocol(),'od_binding':s}):asyncio.run(module.run(args))
if __name__=='__main__':main()
