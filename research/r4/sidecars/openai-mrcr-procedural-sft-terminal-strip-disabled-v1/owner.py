"""One additive held32 owner; reuse the completed train32 manipulation gate."""
import argparse
import json
from pathlib import Path
import sys
import checkpoint
import study

old={name:sys.modules.get(name) for name in ('study','checkpoint')}
sys.modules.update(study=study,checkpoint=checkpoint)
try:
    source=study.load('terminal_strip_original_owner',study.SOURCE_EVAL/'owner.py')
finally:
    for name,value in old.items():
        if value is None:sys.modules.pop(name,None)
        else:sys.modules[name]=value

STAGE='held-checkpoint32'
OUTPUT=study.ROOT/'outputs/held-checkpoint32-001'
source.STAGES={'train':{'phase':'train','arm':'checkpoint32','output':study.TRAIN_READOUT},
               STAGE:{'phase':'held','arm':'checkpoint32','output':OUTPUT}}
held_gate=source.held_gate


def verify(stage=STAGE):
    if stage!=STAGE:raise ValueError('only additive fixed held32 stage permitted')
    return source.verify(stage)


def execute(stage,output,seconds):
    if stage!=STAGE:raise ValueError('only additive fixed held32 stage permitted')
    return source.execute(stage,output,seconds)


if __name__=='__main__':
    parser=argparse.ArgumentParser()
    parser.add_argument('command',choices=['verify','run'])
    parser.add_argument('--stage',choices=[STAGE],default=STAGE)
    parser.add_argument('--output',type=Path,default=OUTPUT)
    parser.add_argument('--outer-seconds',type=int,default=study.OWNER_SECONDS)
    a=parser.parse_args()
    if a.command=='verify':print(verify(a.stage)['identity'])
    else:
        value=execute(a.stage,a.output,a.outer_seconds)
        print(json.dumps(value,sort_keys=True));raise SystemExit(0 if value['complete'] else 1)
