"""Reviewed BA18 one-step owner math; only local facade and unchanged held-source path."""
import argparse
from pathlib import Path
import types
import study as s
import core

path=s.ORIGINAL/'train.py';text=path.read_text()
before="s.ROOT/'HELD_PUBLIC.json'";assert text.count(before)==1
text=text.replace(before,"s.ORIGINAL/'HELD_PUBLIC.json'")
implementation=types.ModuleType('BA18_dose_original_train');implementation.__file__=str(path)
with s.aliases({'study':s,'core':core},s.ROOT):exec(compile(text,str(path),'exec'),implementation.__dict__)
preflight=implementation.preflight;run=implementation.run

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--output',type=Path,required=True);p.add_argument('--seconds',type=int,required=True);a=p.parse_args()
    run(a.output,a.seconds)
