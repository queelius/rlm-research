"""MAIN-only 144-call, 2400-second Mistral owner."""
import argparse
from pathlib import Path
import protocol as p,study as s
module=s.load('mistral_stable_owner',s.SIDE/'leaf-mnli-stable-anchor-qwen8b-v1/owner.py','746147d7c83c45c7476b338106fbf82f837db5a0a94dfdb2a851c6ff92e29413',{'study':s,'protocol':p})
def binding():return {'schema':'released-base-single-model-binding-v1','model':'mistral','checkpoint':s.MODEL,'weights_sha256':s.sha(s.ROOT/'WEIGHTS.json'),'adapter':None}
module.binding=binding
CLOCK=module.CLOCK;validate_argv=module.validate_argv;collector_argv=module.collector_argv;credential=module.credential;preflight=module.preflight;suite=module.suite;execute=module.execute
if __name__=='__main__':
 parser=argparse.ArgumentParser();parser.add_argument('command',choices=('verify','run'));parser.add_argument('--output',type=Path,default=s.ATTEMPT);args=parser.parse_args()
 if args.command=='verify':print(s.verify()['identity'])
 else:
  result=execute(args.output);print(result);raise SystemExit(0 if result['complete'] else 1)
