"""One fixed root,24 immutable slots in sequential three-arm blocks."""
import argparse
import asyncio
import os
import time
from pathlib import Path
import study as s
import adapter

async def dispatch(plan,one,deadline):
    queue=asyncio.Queue()
    for offset in range(0,len(plan),3):
        triple=plan[offset:offset+3]
        if len(triple)!=3 or len({r['triple_id'] for r in triple})!=1 or [r['triple_order'] for r in triple]!=[0,1,2]:raise ValueError('fixed triple structure')
        queue.put_nowait(triple)
    async def worker():
        while time.time()<deadline:
            try:triple=queue.get_nowait()
            except asyncio.QueueEmpty:return
            try:
                for row in triple:
                    if time.time()>=deadline:return
                    await one(row)
            finally:queue.task_done()
    workers=[asyncio.create_task(worker()) for _ in range(4)]
    try:
        await asyncio.wait_for(asyncio.gather(*workers),max(.001,deadline-time.time()));return None
    except TimeoutError:return 'collection_wall_cap'
    finally:
        for task in workers:
            if not task.done():task.cancel()
        await asyncio.gather(*workers,return_exceptions=True)

async def collect(args):
    from verifiers.v1.env import RunSlot
    from verifiers.v1.envs.single_agent import SingleAgentEnv,SingleAgentEnvConfig
    import httpx
    spec=s.verify();binding=s.read(args.binding);descriptor=s.read(args.endpoint)
    if binding!=spec['bindings'][args.weight]:raise ValueError('actual root/child binding differs')
    model=binding['models'][binding['role_map']['root']]
    if descriptor['model_alias']!=binding['role_map']['root'] or descriptor['adapter']!={'path':model['path'],'model_sha256':model['adapter_sha256'],'config_sha256':model['config_sha256']}:raise ValueError('actual descriptor differs')
    url=f'http://{descriptor["host"]}:{descriptor["port"]}/v1'
    with httpx.Client(trust_env=False,timeout=15,headers={'Authorization':'Bearer '+os.environ[descriptor['api_key_env']]}) as client:
        response=client.get(url+'/models');response.raise_for_status();cards={v['id']:v for v in response.json()['data']}
    for alias,value in binding['models'].items():
        if cards.get(alias,{}).get('root')!=value['path'] or cards[alias].get('parent')!=descriptor['base_model']['path']:raise ValueError('live aliases/base differ')
    plan=[r for r in spec['plan'] if r['weight']==args.weight]
    if len(plan)!=24:raise ValueError('phase must contain24 episodes')
    args.output.mkdir(parents=True,exist_ok=False)
    for name,value in [('SPEC.json',spec),('PHASE.json',{'weight':args.weight,'plan':plan,'binding':binding}),('LIVE_MODELS.json',cards),('ENDPOINT.json',descriptor)]:s.write(args.output/name,value)
    st=s.stack();endpoint={**st.native.e.old.planned_endpoint(binding),'url':url,'api_key_env':descriptor['api_key_env']}
    public={c['id']:c for c in s.read(s.ROOT/'inputs/PUBLIC.json')};gold=s.read(s.ROOT/'inputs/HOST_GOLD.json');tasks=s.read(s.ROOT/'inputs/TASKS.json')
    started=time.time();deadline=min(args.deadline,started+900);rows=[];order=[]
    async def one(row):
        result={'coordinate':row,'started_epoch':time.time(),'error':None,'episode_path':None}
        order.append(row['id']);result['start_order']=len(order)-1
        try:
            context=public[row['context_id']];task=adapter.task(context,tasks[row['task_name']]['prompt'],gold[context['id']],row['task_name'],row)
            raw=(await env.run_slot(RunSlot(task),interface.e.make_context(endpoint,row))).to_record()
            path=args.output/'episodes'/(row['id']+'.json');s.write(path,raw)
            result.update(episode_path=str(path),episode_sha256=s.sha(path),task_hash=task.hash,operational_status='episode_returned')
        except asyncio.CancelledError:
            result.update(censored='collection cap affected incomplete episode',operational_status='cancelled_incomplete');raise
        except Exception as error:
            result.update(error={'type':type(error).__name__,'message':str(error)},operational_status='runtime_failure')
        finally:
            result['ended_epoch']=time.time();s.write(args.output/'rows'/(row['id']+'.json'),result);rows.append(result)
    with adapter.installed(binding,args.output,plan,public) as interface:
        env=SingleAgentEnv(SingleAgentEnvConfig.model_validate(spec['environment']))
        async with env.serving():stop=await dispatch(plan,one,deadline)
    missing=[r['id'] for r in plan if r['id'] not in {v['coordinate']['id'] for v in rows}]
    expected={r['id']:r for r in s.read(s.ROOT/'inputs/PROMPTS.json')};first={}
    for path in (args.output/'typed-audit').glob('*-result.json'):
        audit=s.read(path)
        if audit['depth']!=0:continue
        identifier=audit['coordinate']['id']
        if identifier not in first or audit['started_epoch']<first[identifier]['started_epoch']:first[identifier]=audit
    checks=[]
    for row in plan:
        actual=first.get(row['id']);body=actual.get('native_wire_request',{}).get('body') if actual else None
        checks.append({'id':row['id'],'initial_token_ids_equal':None if body is None else body['token_ids']==expected[row['id']]['token_ids'],
            'initial_root_grammar_absent':None if body is None else body['sampling_params'].get('structured_outputs') is None,
            'request_id':actual['request_id'] if actual else None})
    s.write(args.output/'INITIAL_ROOT_PROVENANCE.json',checks)
    s.write(args.output/'STATUS.json',{'recorded':len(rows),'planned':24,'not_started':missing,'stop_reason':stop,
        'started_epoch':started,'ended_epoch':time.time(),'actual_native_attempts':len(list((args.output/'typed-audit').glob('*-request.json'))),
        'recorded_does_not_imply_success':True})
    return 0 if not missing and stop is None else 1

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--weight',choices=s.WEIGHTS,required=True)
    for name in ('binding','endpoint','output'):p.add_argument('--'+name,type=Path,required=True)
    p.add_argument('--deadline',type=float,required=True);raise SystemExit(asyncio.run(collect(p.parse_args())))
