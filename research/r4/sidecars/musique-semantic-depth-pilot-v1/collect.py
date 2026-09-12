"""Fixed four-arm collector using the accepted base-model native RLM runtime."""
import argparse
import asyncio
import contextlib
import json
import os
from pathlib import Path
import time
import musique_study as s
from native_audit import capture
import scoring


def model_context(endpoint,coordinate):
    from renderers import Qwen3RendererConfig
    from verifiers.v1.clients import ModelContext
    from verifiers.v1.configs.client import TrainClientConfig
    from verifiers.v1.types import SamplingConfig
    return ModelContext(model=endpoint['model_alias'],client=TrainClientConfig(
        base_url=f"http://{endpoint['host']}:{endpoint['port']}/v1",api_key_var=endpoint['api_key_env'],
        renderer=Qwen3RendererConfig(enable_thinking=True),renderer_model_name=endpoint['base_model']['path'],
        multiplex=256,headers={s.HEADER:coordinate['id']}),sampling=SamplingConfig.model_validate({
            'temperature':.5,'top_p':1.,'seed':coordinate['seed'],'max_tokens':1024,
            'extra_body':{'top_k':-1,'min_p':0.,'return_token_ids':True,'cache_salt':'0'}}))


async def direct(endpoint,coordinate):
    from verifiers.v1.clients.train import TrainClient
    from verifiers.v1.dialects import ChatDialect
    ctx=model_context(endpoint,coordinate);client=TrainClient(ctx.client)
    task=next(row for row in s.read(s.INPUTS/'tasks_question_only.json') if row['name']==coordinate['id'])
    try:
        response=await client.get_response(ChatDialect(),{'model':s.MODEL_ALIAS,
            'messages':[{'role':'user','content':task['prompt']}]},ctx.sampling,
            session_id='question_only_'+coordinate['id'])
        return {'ok':True,'traces':[],'direct_response':response.model_dump(mode='json')}
    finally:await client.close()


async def run(endpoint_path,output,deadline):
    from verifiers.v1.env import RunSlot
    s.verify();s.configure_runtime();endpoint=s.read(endpoint_path)
    if endpoint.get('model_alias')!=s.MODEL_ALIAS or endpoint.get('adapter') is not None:
        raise ValueError('no-adapter model identity differs')
    if Path(endpoint['base_model']['path']).resolve()!=s.MODEL.resolve():raise ValueError('base weights path differs')
    if not os.environ.get(endpoint['api_key_env']):raise ValueError('private credential unavailable')
    output.mkdir(parents=True,exist_ok=False);started=time.time()
    coordinates=s.plan();envs={arm:s.environment(arm) for arm in s.ARMS[:3]}
    tasks={arm:{task.data.name:task for task in env.taskset} for arm,env in envs.items()}
    records=[];queue=asyncio.Queue()
    for coordinate in coordinates:queue.put_nowait(coordinate)
    s.write_x(output/'RUN.json',{'ready_sha256':s.sha(s.ROOT/'READY.json'),'started_epoch':started,
        'fixed_deadline_epoch':deadline,'planned':48,'worker_concurrency':4,'endpoint_sha256':s.sha(endpoint_path),
        'binding':s.binding(),'selection_inputs_sha256':s.sha(s.INPUTS/'MANIFEST.json')})

    async def one(coordinate,native):
        began=time.time();slot=None
        s.write_x(output/'episode-starts'/f"{coordinate['id']}.json",{'coordinate':coordinate,'started_epoch':began})
        try:
            if coordinate['arm']=='question_only':coro=direct(endpoint,coordinate)
            else:
                slot=RunSlot(tasks[coordinate['arm']][coordinate['id']])
                coro=envs[coordinate['arm']].run_slot(slot,model_context(endpoint,coordinate))
            value=await asyncio.wait_for(coro,max(.001,min(180,deadline-time.time())))
            raw=value if coordinate['arm']=='question_only' else value.to_record()
        except BaseException as error:
            raw={'ok':False,'errors':[{'type':type(error).__name__,'message':str(error)}],
                 'traces':[trace.to_record() for trace in slot.traces] if slot else []}
        record={'coordinate':coordinate,'episode':raw,'episode_sha256':s.digest(raw),
                'derived':scoring.inspect(raw,coordinate,native),
                'timing':{'started_epoch':began,'ended_epoch':time.time()}}
        s.write_x(output/'episodes'/f"{coordinate['id']}.json",record);records.append(record)
        s.write_x(output/'progress'/f'{len(records):03d}.json',scoring.summarize(records,native))

    async def worker(native):
        while time.time()<deadline:
            try:coordinate=queue.get_nowait()
            except asyncio.QueueEmpty:return
            try:await one(coordinate,native)
            finally:queue.task_done()

    with capture(output/'native-calls',coordinates) as native:
        async with contextlib.AsyncExitStack() as stack:
            for env in envs.values():await stack.enter_async_context(env.serving())
            workers=[asyncio.create_task(worker(native)) for _ in range(4)]
            try:await asyncio.wait_for(asyncio.gather(*workers),max(.001,deadline-time.time()))
            except TimeoutError:
                for worker_task in workers:worker_task.cancel()
                await asyncio.gather(*workers,return_exceptions=True)
    module=__import__('sys').modules.get('mrcr_rootless_document_baseline_v2')
    s.write_x(output/'RUNTIME_INSTALL_PROVENANCE.json',getattr(module,'INSTALL_PROVENANCE',{}))
    completed={r['coordinate']['id'] for r in records}
    result={**scoring.summarize(records,native),'elapsed_seconds':time.time()-started,
        'missing_coordinates':[c['id'] for c in coordinates if c['id'] not in completed],
        'native_start_files':len(list((output/'native-calls').glob('*-start.json'))),
        'native_result_files':len(list((output/'native-calls').glob('*-result.json'))),
        'native_wire_request_files':len(list((output/'native-calls').glob('*-wire-request.json'))),
        'native_wire_response_files':len(list((output/'native-calls').glob('*-wire-response.json')))}
    s.write_x(output/'RESULT.json',result)
    return 0 if result['complete'] else 3


if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--endpoint',type=Path,required=True)
    parser.add_argument('--output',type=Path,required=True);parser.add_argument('--deadline',type=float,required=True)
    args=parser.parse_args();raise SystemExit(asyncio.run(run(args.endpoint,args.output,args.deadline)))
