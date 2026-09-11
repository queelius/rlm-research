"""CPU verifier/collector/readout entrypoints; owned.py alone starts serving."""
import argparse
import asyncio
import json
from pathlib import Path
import experiment as e

if __name__=='__main__':
    parser=argparse.ArgumentParser()
    parser.add_argument('command',choices=('verify','collect','analyze'))
    parser.add_argument('--spec',type=Path)
    parser.add_argument('--output',type=Path,default=e.ROOT/'outputs/attempt-001')
    args=parser.parse_args()
    if args.command=='collect': raise SystemExit(asyncio.run(e.collect(args.spec,args.output)))
    if args.command=='verify':
        from owned import verify_ready
        value=verify_ready()
        print(json.dumps({'planned':len(value['plan']),'gpu_calls':0}))
    else:
        import results
        value=results.analyze(args.output)
        print(json.dumps({'planned':value['planned'],'recorded':value['recorded'],'gpu_calls':0}))
