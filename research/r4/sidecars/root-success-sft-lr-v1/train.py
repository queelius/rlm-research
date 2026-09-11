"""Exactly two authenticated LR substitutions; unchanged eight-pass trainer."""
import argparse
import traceback
import uuid
from pathlib import Path
import study as s

inherited=s.private('train.py',{'2e-5':('1e-4',2)})
if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('command',choices=('verify','run'))
    parser.add_argument('--output',type=Path,default=s.ROOT/'outputs/attempt-001/training')
    args=parser.parse_args()
    try:print({'identity':inherited.verify()[0]['identity'],'gpu_calls':0} if args.command=='verify' else inherited.run(args.output))
    except BaseException as error:
        if args.output.exists():s.write(args.output/('FAILURE-'+uuid.uuid4().hex+'.json'),{'type':type(error).__name__,'message':str(error),'traceback':traceback.format_exc()})
        raise
