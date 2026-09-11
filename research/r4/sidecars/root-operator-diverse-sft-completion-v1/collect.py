"""Original native collector; only recovery checkpoint directory differs."""
import asyncio
import recovery as r

def main():
    r.verify();module=r.collector();args=module.parse_args()
    if (args.mode,args.plan,args.start,args.stop)!=('free','FREE_PLAN.json',0,24):raise ValueError('only original24 fixed-SFT6 coordinates')
    if args.output.resolve()!=(r.ATTEMPT/'sft6/free').resolve():raise ValueError('exact completion output')
    if args.binding.resolve()!=(r.ATTEMPT/'service-sft6/BINDING.json').resolve() or args.endpoint.resolve()!=(r.ATTEMPT/'service-sft6/service/endpoint-original.json').resolve():raise ValueError('exact completion service')
    with r.s.aliases({'od_study':r.s,'od_protocol':r.protocol(),'od_binding':r.binding_module()}):asyncio.run(module.run(args))

if __name__=='__main__':main()
