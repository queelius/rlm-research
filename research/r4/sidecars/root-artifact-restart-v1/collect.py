"""48 fresh native root sessions; no source replay or historical token substitution."""
import argparse
import asyncio
import json
import os
import time
from pathlib import Path
import protocol as p
import study as s

def metrics():
    return s.load('restart_native_final_metrics',s.ROOT.parent/'root-example-map-visibility-v1/metrics.py','0ef6a89ad3655afe71226878f0296802e6b8af62b5aa295eec23e3ed151c53d3')

def audits(directory,coordinate):
    typed=[s.read(path) for path in (directory/'typed-audit').glob('*-request.json')]
    ids={v['request_id'] for v in typed if v['coordinate']['id']==coordinate}
    result={v['request_id']:v for path in (directory/'role-audit').glob('*-result.json') if (v:=s.read(path))['request_id'] in ids}
    for path in (directory/'role-audit').glob('*-request.json'):
        value=s.read(path)
        if value['request_id'] in ids:result.setdefault(value['request_id'],{**value,'status':'missing result','native_response':None})
    return result

def planned_results(plan,results):
    return [results.get(row['id'],p.null_row(row,'unrun or incomplete; retained row/failure artifacts are authoritative')) for row in plan]

async def collect(args):
    import httpx
    from verifiers.v1.env import RunSlot
    from verifiers.v1.envs.single_agent import SingleAgentEnv,SingleAgentEnvConfig
    ready=s.verify();s.runtime();m=metrics();binding=s.read(args.binding);descriptor=s.read(args.endpoint)
    if binding!=s.read(s.ROOT/'inputs/BINDING.json'):raise ValueError('fixed unchanged low66c/c32 binding changed')
    original=s.source().original
    validator=original.plan.private('binding.py',view=original.plan.old)
    validator.validate_descriptor(binding,descriptor,s.sha(args.binding))
    headers={'Authorization':'Bearer '+os.environ[descriptor['api_key_env']]}
    async with httpx.AsyncClient(trust_env=False,timeout=15,headers=headers) as client:
        response=await client.get(f'http://{descriptor["host"]}:{descriptor["port"]}/v1/models');response.raise_for_status()
        cards={c['id']:c for c in response.json()['data']}
    for alias,model in binding['models'].items():
        if cards.get(alias,{}).get('root')!=model['path'] or cards[alias].get('parent')!=descriptor['base_model']['path']:raise ValueError('actual service model card differs')
    args.output.mkdir(parents=True,exist_ok=False);started=time.time();deadline=min(args.deadline,started+1800)
    plan=s.read(s.ROOT/'inputs/PLAN.json');states={v['source_id']:v for v in s.read(s.ROOT/'inputs/STATES.json')}
    packages=s.read(s.ROOT/'inputs/PACKAGES.json');public={c['id']:c for c in s.read(s.ROOT/'inputs/PUBLIC.json')}
    host=s.read(s.ROOT/'inputs/HOST_GOLD.json');prompts={r['id']:r for r in s.read(s.ROOT/'inputs/PROMPTS.json')}
    s.write(args.output/'INPUTS.json',dict(identity=ready['identity'],binding=binding,descriptor=descriptor,models=cards,started_epoch=started,deadline_epoch=deadline))
    s.write(args.output/'PLANNED_NULL_ENDPOINTS.json',[p.null_row(row,'planned') for row in plan])
    out=args.output/'readout';out.mkdir();interface=s.interface(out);results={}
    endpoint={**s.stack().native.e.old.planned_endpoint(binding),'url':f'http://{descriptor["host"]}:{descriptor["port"]}/v1','api_key_env':descriptor['api_key_env']}
    async def one(row):
        state=states[row['source_id']];context=public[row['context_id']];files=packages[row['source_id']]
        result=p.null_row(row,'not yet returned');result['started_epoch']=time.time()
        try:
            prompt=prompts[row['id']];task=s.task(context,prompt['prompt'],state['goal'],row,files,out/'setup')
            if task.hash!=prompt['task_hash']:raise ValueError('prepared fresh task hash differs')
            raw=(await asyncio.wait_for(env.run_slot(RunSlot(task),interface.e.make_context(endpoint,row)),min(180,max(0,deadline-time.time())))).to_record()
            path=out/'episodes'/(row['id']+'.json');s.write(path,raw)
            trace=raw['traces'][0] if len(raw.get('traces',[]))==1 else {};roles=audits(out,row['id'])
            roots=[roles[c['acp']['request_id']] for c in trace['calls'] if roles[c['acp']['request_id']]['depth']==0]
            if not roots or roots[0]['native_wire_request']['body']['token_ids']!=prompt['token_ids']:raise ValueError('actual new-user native prefix differs')
            for role in roles.values():
                alias=binding['role_map']['root'] if role['depth']==0 else binding['fixed_child']
                if role['actual_alias']!=alias or role['model_sha256']!=binding['models'][alias]['adapter_sha256']:raise ValueError('actual root/child identity differs')
            final,node_ids=m.final_capture(trace,roles)
            relevant=[r['id'] for r in context['records'] if r['user'] in row['users']]
            gold=sum(host[context['id']]['labels'][k]==context['target'] for k in relevant)
            labels={k:v for name,text in files.items() if name.startswith('state/map-') for k,v in json.loads(text).items()}
            result.update(m.score(trace,final,gold),gold=gold,completed=True,episode_path=str(path),episode_sha256=s.sha(path),
                first_native_prompt_verified=True,final_branch_indices=node_ids,final_request_id=final['request_id'] if final else None,
                evidence=m.evidence(trace,node_ids,labels,relevant,s.source().LABELS[context['target']],m.score(trace,final,gold)['available']),
                actual_artifact_retrieval=None,actual_scoped_reduction=None,actual_data_flow_requires_code_and_return_audit=True,
                native_tool_timing=trace.get('tools'),setup_attestation_path=str(out/'setup'/(row['id']+'.json')))
            result.pop('unavailable_reason',None)
        except asyncio.CancelledError:
            result.update(unavailable_reason='cancelled at inclusive work deadline');raise
        except Exception as error:
            result.update(error=dict(type=type(error).__name__,message=str(error)),reward=None,available=False,completed=False)
        finally:
            roles=audits(out,row['id']);result.update(ended_epoch=time.time(),new_child_calls=sum(v['depth']>0 for v in roles.values()),
                cost=m.pipeline_cost(m.usage(list(roles.values())),state['historical_cost']),source_id=row['source_id'],
                historical_child_seconds=state['historical_child_seconds'],source_capture_gross_seconds=state['source_capture_gross_seconds'],
                source_pre_cut_observed_seconds=state['source_pre_cut_observed_seconds'],historical_shared_not_new=True,
                native_request_ids=list(roles),package_sha256=state['package_sha256'])
            s.write(out/'rows'/(row['id']+'.json'),result);results[row['id']]=result
    with interface.installed(binding,out,plan,public):
        env=SingleAgentEnv(SingleAgentEnvConfig.model_validate(interface.e.environment_config()))
        async with env.serving():
            queue=asyncio.Queue()
            for row in plan:queue.put_nowait(row)
            async def worker():
                while time.time()<deadline:
                    try:row=queue.get_nowait()
                    except asyncio.QueueEmpty:return
                    await one(row)
            try:await asyncio.wait_for(asyncio.gather(*(worker() for _ in range(4))),max(0,deadline-time.time()))
            except TimeoutError:pass
    final=planned_results(plan,results)
    for row in final:
        if row['coordinate']['id'] not in results:s.write(out/'rows'/(row['coordinate']['id']+'.json'),row)
    s.write(args.output/'TERMINAL.json',dict(planned=48,recorded=len(final),available=sum(r['available'] for r in final),correct=sum(r['reward']==1 for r in final),
        results=final,elapsed_seconds=time.time()-started,source_states=16,historical_physical_acquisitions=40,new_source_acquisitions=0,
        interpretation='all-fresh state representation/restart; not exact native historical continuation'))
    s.write(args.output/'OUTPUT_INVENTORY.json',{str(path):s.sha(path) for path in args.output.rglob('*.json')})
    return 0

def parse_args(argv=None):
    parser=argparse.ArgumentParser()
    for name in ('binding','endpoint','output'):parser.add_argument('--'+name,type=Path,required=True)
    parser.add_argument('--deadline',type=float,required=True);return parser.parse_args(argv)

if __name__=='__main__':raise SystemExit(asyncio.run(collect(parse_args())))
