"""Original owned lifecycle; two phases, 3300 inclusive /3180 shared work."""
import argparse
from pathlib import Path
import study as s
import binding as b

inherited=s.private('launch.py',{'4500':('3300',3),'4380':('3180',1)},extra={'binding':b})
if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('command',choices=('verify','run'))
    parser.add_argument('--output',type=Path,default=s.ROOT/'outputs/attempt-001');args=parser.parse_args()
    if args.command=='verify':print({'identity':s.verify()['identity'],'gpu_calls':0})
    else:
        result=inherited.execute(args.output.resolve());print(result);raise SystemExit(0 if result['complete'] else 1)
