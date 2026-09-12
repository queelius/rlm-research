"""V2 collector with unchanged science and corrected service-bound study."""
import argparse,asyncio,importlib.util,sys
from pathlib import Path
import checkpoint_v2 as checkpoint
import study_v2 as study
ROOT=Path(__file__).resolve().parent;_old={n:sys.modules.get(n) for n in ('study','checkpoint')};sys.modules.update(study=study,checkpoint=checkpoint)
try:
    _spec=importlib.util.spec_from_file_location('mrcr_long_v1_collect_for_v2',ROOT/'collect.py')
    source=importlib.util.module_from_spec(_spec);_spec.loader.exec_module(source)
finally:
    for _n,_v in _old.items():
        if _v is None:sys.modules.pop(_n,None)
        else:sys.modules[_n]=_v
verify_ready=source.verify_ready
async def run(phase,arm,endpoint,output,deadline):return await source.run(phase,arm,endpoint,output,deadline)
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--phase',choices=['long'],required=True);p.add_argument('--arm',choices=['base','checkpoint32'],required=True);p.add_argument('--endpoint',type=Path,required=True);p.add_argument('--output',type=Path,required=True);p.add_argument('--deadline',type=float,required=True);a=p.parse_args();raise SystemExit(asyncio.run(run(a.phase,a.arm,a.endpoint,a.output,a.deadline)))
