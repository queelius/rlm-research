"""One scientific wrapper, explicit actual inner verifier, actual step16 arm."""
import argparse
import asyncio
from pathlib import Path
from types import ModuleType
import checkpoint
import study

path=study.ORIGINAL/'collect.py'
if study.sha(path)!='f28f98177f1c946945b2decadb35e698745570eff810a1e898a34f09a206fbb7':raise ValueError('science wrapper changed')
text=path.read_text().replace('checkpoint32','checkpoint16').replace('sft32-onpolicy-screen','sft16-onpolicy-screen')
source=ModuleType('cp16_private_g4_collector');source.__file__=str(path)
exec(compile(text,str(path)+':fixed-cp16','exec'),source.__dict__)

def verify_ready():
    ready=study.read(study.READY)
    assert ready['identity']==study.digest({k:v for k,v in ready.items() if k!='identity'})
    for raw,h in ready['closure_sha256'].items():assert study.sha(Path(raw))==h,raw
    assert ready['arm']=='checkpoint16' and ready['selected_step']==16
    assert study.digest(study.schedule('train'))==ready['inputs']['schedule_sha256']
    assert ready['terminal_condition']['name']=='terminal-strip-disabled'
    return ready

source.verify_ready=verify_ready
source.source.verify_ready=verify_ready
def __getattr__(name):return getattr(source,name)
async def run(phase,arm,endpoint,output,deadline):
    return await source.run(phase,arm,endpoint,output,deadline)

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--phase',choices=['train'],required=True);p.add_argument('--arm',choices=['checkpoint16'],required=True)
    p.add_argument('--endpoint',type=Path,required=True);p.add_argument('--output',type=Path,required=True);p.add_argument('--deadline',type=float,required=True);a=p.parse_args()
    raise SystemExit(asyncio.run(run(a.phase,a.arm,a.endpoint,a.output,a.deadline)))

