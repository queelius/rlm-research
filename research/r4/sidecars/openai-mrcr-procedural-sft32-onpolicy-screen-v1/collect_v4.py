"""V4 collector binding the READY verifier through the actual innermost run."""
import argparse,asyncio,importlib.util,sys
from pathlib import Path
import checkpoint_v4 as checkpoint
import study_v4 as study
ROOT=Path(__file__).resolve().parent;_old={n:sys.modules.get(n) for n in ('study','checkpoint')}
sys.modules.update(study=study,checkpoint=checkpoint)
try:
    _spec=importlib.util.spec_from_file_location('sft32_onpolicy_v3_collect_for_v4',ROOT/'collect_v3.py')
    source=importlib.util.module_from_spec(_spec);_spec.loader.exec_module(source)
finally:
    for _n,_v in _old.items():
        if _v is None:sys.modules.pop(_n,None)
        else:sys.modules[_n]=_v
def verify_ready():
    ready=study.read(study.READY)
    if ready.get('identity')!=study.digest({k:v for k,v in ready.items() if k!='identity'}):raise ValueError('V4 READY changed')
    for raw,expected in ready.get('closure_sha256',{}).items():
        if study.sha(Path(raw))!=expected:raise ValueError('V4 closure changed: '+raw)
    if ready.get('terminal_condition',{}).get('name')!='terminal-strip-disabled':raise ValueError('wrong terminal condition')
    if study.digest(study.schedule('train'))!=ready['inputs']['schedule_sha256']:raise ValueError('V4 schedule changed')
    return ready
_cursor=source
for _depth in range(4):
    _cursor.verify_ready=verify_ready
    _next=getattr(_cursor,'source',None)
    if _next is None:break
    _cursor=_next
async def run(phase,arm,endpoint,output,deadline):
    if phase!='train' or arm!='checkpoint32':raise ValueError('fixed V4 phase/arm differs')
    return await source.run(phase,arm,endpoint,output,deadline)
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--phase',choices=['train'],required=True);p.add_argument('--arm',choices=['checkpoint32'],required=True);p.add_argument('--endpoint',type=Path,required=True);p.add_argument('--output',type=Path,required=True);p.add_argument('--deadline',type=float,required=True);a=p.parse_args();raise SystemExit(asyncio.run(run(a.phase,a.arm,a.endpoint,a.output,a.deadline)))
