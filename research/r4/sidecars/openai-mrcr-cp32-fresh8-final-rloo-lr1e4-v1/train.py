"""Accepted complete runner, no rewritten optimizer or probability qualification."""
import argparse
from pathlib import Path
import core
import study
implementation=study.bound('fresh8_lr10_runner',study.SOURCE_TRAIN/'train.py',study=study,core=core)
qualify=implementation.qualify;accumulate=implementation.accumulate
preflight=implementation.preflight;run=implementation.run
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--output',type=Path,default=study.OUTPUT)
    p.add_argument('--seconds',type=int,default=study.SCIENCE_SECONDS);a=p.parse_args();run(a.output,a.seconds)
