"""Proven raw MRCR collector rebound to balanced32 and two fixed endpoints."""
import argparse,asyncio,importlib.util,sys
from pathlib import Path
import checkpoint,study
old={n:sys.modules.get(n) for n in ('study','checkpoint')};sys.modules.update(study=study,checkpoint=checkpoint)
try:
    spec=importlib.util.spec_from_file_location('balanced32_collect_source',study.SOURCE_EVAL/'collect.py');source=importlib.util.module_from_spec(spec);spec.loader.exec_module(source)
finally:
    for n,v in old.items():
        if v is None:sys.modules.pop(n,None)
        else:sys.modules[n]=v

def verify_ready():
    ready=study.read(study.READY)
    if ready.get('identity')!=study.digest({k:v for k,v in ready.items() if k!='identity'}):raise ValueError('READY identity changed')
    for p,h in ready['closure_sha256'].items():
        if study.sha(Path(p))!=h:raise ValueError('closure changed: '+p)
    if study.digest(study.schedule())!=ready['inputs']['schedule_sha256']:raise ValueError('schedule changed')
    return ready
source.verify_ready=verify_ready
hooks=study.terminal_hooks()
async def run(phase,arm,endpoint,output,deadline):
    if phase!='long' or arm not in ('cp32','lr1e4'):raise ValueError('fixed phase/arm differs')
    with hooks.installed() as contract:
        code=await source.run(phase,arm,endpoint,output,deadline)
        study.write_x(output/'TERMINAL_STRIP_CONTRACT.json',contract)
        return code
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--phase',choices=['long'],required=True);p.add_argument('--arm',choices=['cp32','lr1e4'],required=True);p.add_argument('--endpoint',type=Path,required=True);p.add_argument('--output',type=Path,required=True);p.add_argument('--deadline',type=float,required=True);a=p.parse_args();raise SystemExit(asyncio.run(run(a.phase,a.arm,a.endpoint,a.output,a.deadline)))
