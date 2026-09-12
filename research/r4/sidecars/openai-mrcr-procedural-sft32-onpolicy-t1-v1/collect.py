"""Shallow T1.0 adapter over the proven hook-wrapped G4 collector."""
from __future__ import annotations
import argparse,asyncio,importlib.util,sys
from pathlib import Path
import checkpoint,study
_old={n:sys.modules.get(n) for n in ('study','checkpoint')};sys.modules.update(study=study,checkpoint=checkpoint)
try:
    s=importlib.util.spec_from_file_location('mrcr_t1_g4_source',study.SOURCE_SCREEN/'collect.py');source=importlib.util.module_from_spec(s);s.loader.exec_module(source)
finally:
    for n,v in _old.items():
        if v is None:sys.modules.pop(n,None)
        else:sys.modules[n]=v
def verify_ready():
    ready=study.read(study.READY)
    if ready['identity']!=study.digest({k:v for k,v in ready.items() if k!='identity'}):raise ValueError('T1 READY changed')
    for p,h in ready['closure_sha256'].items():
        if study.sha(Path(p))!=h:raise ValueError('T1 closure changed: '+p)
    if study.digest(study.schedule('train'))!=ready['inputs']['schedule_sha256']:raise ValueError('T1 schedule changed')
    return ready
def model_context(endpoint,coordinate):
    from renderers import Qwen3RendererConfig
    from verifiers.v1.clients import ModelContext
    from verifiers.v1.configs.client import TrainClientConfig
    from verifiers.v1.types import SamplingConfig
    if coordinate['temperature']!=1.0:raise ValueError('T1 coordinate changed')
    return ModelContext(model=endpoint['model_alias'],client=TrainClientConfig(base_url=f"http://{endpoint['host']}:{endpoint['port']}/v1",api_key_var=endpoint['api_key_env'],renderer=Qwen3RendererConfig(enable_thinking=True),renderer_model_name=endpoint['base_model']['path'],multiplex=256),sampling=SamplingConfig.model_validate({'temperature':1.0,'top_p':1.0,'seed':coordinate['seed'],'max_tokens':2048,'extra_body':{'top_k':-1,'min_p':0.0,'return_token_ids':True,'cache_salt':'0'}}))
source.verify_ready=verify_ready;source.source.verify_ready=verify_ready;source.source.model_context=model_context
async def run(phase,arm,endpoint,output,deadline):
    if phase!='train' or arm!='checkpoint32':raise ValueError('fixed T1 phase/arm differs')
    return await source.run(phase,arm,endpoint,output,deadline)
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--phase',choices=['train'],required=True);p.add_argument('--arm',choices=['checkpoint32'],required=True);p.add_argument('--endpoint',type=Path,required=True);p.add_argument('--output',type=Path,required=True);p.add_argument('--deadline',type=float,required=True);a=p.parse_args();raise SystemExit(asyncio.run(run(a.phase,a.arm,a.endpoint,a.output,a.deadline)))
