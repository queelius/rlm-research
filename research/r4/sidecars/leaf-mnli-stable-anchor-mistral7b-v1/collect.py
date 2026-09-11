"""Qualified 144-slot collector rebound to Mistral-native prompts and authentication."""
import argparse,asyncio
from pathlib import Path
import owner,protocol as p,scoring,study as s
module=s.load('mistral_stable_collect',s.SIDE/'leaf-mnli-stable-anchor-qwen8b-v1/collect.py','60e4f0cdd8f9bb0090c98eec1afc2b89ae16c3353d58012bb2878e0f4977749e',{'study':s,'protocol':p,'scoring':scoring,'owner':owner});run,summarize=module.run,module.summarize
if __name__=='__main__':
 parser=argparse.ArgumentParser();parser.add_argument('command',choices=('run',));parser.add_argument('--endpoint',required=True,type=Path);parser.add_argument('--output',required=True,type=Path);parser.add_argument('--deadline',required=True,type=float);args=parser.parse_args();owner.validate_argv([str(s.NATIVE),str(s.ROOT/'collect.py'),'run','--endpoint',str(args.endpoint),'--output',str(args.output),'--deadline',str(args.deadline)]);print(asyncio.run(run(args.endpoint,args.output,args.deadline)))
