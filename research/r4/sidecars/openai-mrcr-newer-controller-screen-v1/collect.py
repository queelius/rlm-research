"""Eight fixed two-turn RLM episodes for one exact released model."""
import argparse
import asyncio
import os
from pathlib import Path
import time
import study as s
import metrics
from native_capture import capture


def model_context(endpoint,coordinate):
    from verifiers.v1.clients import ModelContext
    from verifiers.v1.configs.client import TrainClientConfig
    from verifiers.v1.types import SamplingConfig
    return ModelContext(model=endpoint['model_alias'],client=TrainClientConfig(
        base_url=f"http://{endpoint['host']}:{endpoint['port']}/v1",api_key_var=endpoint['api_key_env'],
        renderer=s.renderer_config(coordinate['arm']),renderer_model_name=endpoint['base_model']['path'],
        multiplex=256,headers={s.HEADER:coordinate['id']}),sampling=SamplingConfig.model_validate({
            'temperature':.5,'top_p':1.,'seed':coordinate['seed'],'max_tokens':1024,
            'extra_body':{'top_k':-1,'min_p':0.,'return_token_ids':True,'cache_salt':'0'}}))


async def run(arm,endpoint_path,output,deadline):
    from verifiers.v1.env import RunSlot
    s.verify();s.bind_arm(arm);s.configure_runtime();endpoint=s.read(endpoint_path)
    assert endpoint['model_alias']==s.MODEL_ALIAS and endpoint.get('adapter') is None
    assert endpoint['base_model']==s.MODELS[arm] and os.environ.get(endpoint['api_key_env'])
    output.mkdir(parents=True,exist_ok=False);started=time.time()
    assert 0<deadline-started<=601
    coordinates=s.plan(arm);env=s.environment(arm);tasks={t.data.name:t for t in env.taskset}
    records=[];queue=asyncio.Queue()
    for coordinate in coordinates:queue.put_nowait(coordinate)
    s.write_x(output/'RUN.json',{'arm':arm,'ready_sha256':s.sha(s.ROOT/'READY.json'),
        'deadline_epoch':deadline,'started_epoch':started,'planned_episodes':8,'max_physical_calls':16,
        'endpoint_sha256':s.sha(endpoint_path),'binding':s.binding(arm)})
    async def one(coordinate,native):
        began=time.time();slot=RunSlot(tasks[coordinate['id']])
        s.write_x(output/'episode-starts'/f"{coordinate['id']}.json",{'coordinate':coordinate,'started_epoch':began})
        try:
            episode=await asyncio.wait_for(env.run_slot(slot,model_context(endpoint,coordinate)),max(.001,min(180,deadline-time.time())))
            raw=episode.to_record()
        except BaseException as error:
            raw={'ok':False,'errors':[{'type':type(error).__name__,'message':str(error)}],
                 'traces':[trace.to_record() for trace in slot.traces]}
        record={'coordinate':coordinate,'episode':raw,'episode_sha256':s.digest(raw),
                'derived':metrics.inspect(raw,coordinate,native),'started_epoch':began,'ended_epoch':time.time()}
        s.write_x(output/'episodes'/f"{coordinate['id']}.json",record);records.append(record)
        s.write_x(output/'progress'/f'{len(records):03d}.json',metrics.summarize(records,arm))
    async def worker(native):
        while time.time()<deadline:
            try:coordinate=queue.get_nowait()
            except asyncio.QueueEmpty:return
            try:await one(coordinate,native)
            finally:queue.task_done()
    with capture(output/'native-calls',coordinates) as native:
        async with env.serving():
            workers=[asyncio.create_task(worker(native)) for _ in range(4)]
            try:await asyncio.wait_for(asyncio.gather(*workers),max(.001,deadline-time.time()))
            except TimeoutError:
                for task in workers:task.cancel()
                await asyncio.gather(*workers,return_exceptions=True)
    result={**metrics.summarize(records,arm),'elapsed_seconds':time.time()-started,
        'missing_coordinates':[x['id'] for x in coordinates if x['id'] not in {r['coordinate']['id'] for r in records}],
        'native_files':{suffix:len(list((output/'native-calls').glob('*-'+suffix+'.json')))
                        for suffix in ('start','result','wire-request','wire-response')}}
    s.write_x(output/'RESULT.json',result)
    return 0 if result['complete_inventory'] else 3


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--arm',choices=s.ARMS,required=True)
    p.add_argument('--endpoint',type=Path,required=True);p.add_argument('--output',type=Path,required=True)
    p.add_argument('--deadline',type=float,required=True);a=p.parse_args()
    raise SystemExit(asyncio.run(run(a.arm,a.endpoint,a.output,a.deadline)))
