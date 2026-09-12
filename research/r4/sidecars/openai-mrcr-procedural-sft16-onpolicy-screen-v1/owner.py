"""Same finite service lifecycle, fixed checkpoint16 metadata and target."""
import argparse
import json
from pathlib import Path
from types import ModuleType
import checkpoint
import study

path=study.ORIGINAL/'owner.py'
if study.sha(path)!='2d43db859a301d2a0ff950eef8b3d8a47d19a319502ff2eff7dd9e62f40ed062':raise ValueError('owner source changed')
text=path.read_text().replace('checkpoint32','checkpoint16').replace('sft32-onpolicy-screen','sft16-onpolicy-screen')
_module=ModuleType('cp16_private_g4_owner');_module.__file__=str(path)
exec(compile(text,str(path)+':fixed-cp16','exec'),_module.__dict__)
OUTPUT=_module.OUTPUT;execute=_module.execute
def verify():
    ready=_original_verify()
    evidence=study.read(study.ROOT/'CPU_TESTS.json')
    assert evidence['returncode']==0 and evidence['tests_passed']==2 and evidence['ready_sha256']==study.sha(study.READY)
    return ready
_original_verify=_module.verify
_module.verify=verify
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('command',choices=['verify','run']);p.add_argument('--output',type=Path,default=OUTPUT);p.add_argument('--outer-seconds',type=int,default=study.OWNER_SECONDS);a=p.parse_args()
    if a.command=='verify':print(verify()['identity'])
    else:
        v=execute(a.output,a.outer_seconds);print(json.dumps(v,sort_keys=True));raise SystemExit(0 if v['complete'] else 1)

