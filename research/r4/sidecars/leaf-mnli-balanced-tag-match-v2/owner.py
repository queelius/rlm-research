"""V2 owner binding to the tested 192-slot released-base lifecycle."""
import argparse
from pathlib import Path
import protocol as p,study as s
module=s.load('tag_match_v2_owner',s.V1/'owner.py','56c7ed5dbeb8595a9d814045031b29adc7a88fb01cd7f92777afd685d59eddd5',{'study':s,'protocol':p})
CLOCK=module.CLOCK;validate_argv=module.validate_argv;collector_argv=module.collector_argv;credential=module.credential;binding=module.binding;preflight=module.preflight;suite=module.suite;execute=module.execute
if __name__=='__main__':
 a=argparse.ArgumentParser();a.add_argument('command',choices=('verify','run'));a.add_argument('--output',type=Path,default=s.ATTEMPT);x=a.parse_args()
 if x.command=='verify':print(s.verify()['identity'])
 else:
  z=execute(x.output);print(z);raise SystemExit(0 if z['complete'] else 1)
