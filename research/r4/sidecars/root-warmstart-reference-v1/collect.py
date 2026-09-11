"""One fixed-root eight-slot native phase; full planned NULLs and physical evidence."""
import argparse
import asyncio
import json
import os
from pathlib import Path
import time
import native as n
import protocol as p
import study as s

def metrics():return s.load('warm_reference_metrics',s.SIDE/'root-example-map-visibility-v1/metrics.py','0ef6a89ad3655afe71226878f0296802e6b8af62b5aa295eec23e3ed151c53d3')
def cost(records):
    physical=[r for r in records if r.get('physical_request_attempt')]
    clean=[];returned=0
    for r in physical:
        body=(r.get('native_wire_response') or {}).get('body')
        if isinstance(body,str):
            try:body=json.loads(body)
            except ValueError:body=None
        clean.append(dict(native_wire_response=dict(body=body)))
        returned+=bool(isinstance(body,dict) and body.get('choices'))
    return dict(physical_request_attempts=len(physical),returned_native_completions=returned,parsed_native_completions=sum(r.get('status')=='returned' for r in physical),pretransport_rejected=sum(bool(r.get('pretransport_rejected')) for r in records),usage=metrics().usage(clean),provider_billing=None)
def audits(output):
    result={}
    for path in sorted((output/'audit').glob('*-request.json')):
        r=s.read(path);result[r['request_id']]=r
    for path in sorted((output/'physical-requests').glob('*.json')):
        r=s.read(path);result[r['request_id']]=r
    for path in sorted((output/'audit').glob('*-result.json')):
        r=s.read(path);result[r['request_id']]=r
    return result
def ledger(output):
    by_root={arm:cost(list(audits(output/arm/'rollout/native').values())) for arm in s.ROOTS}
    return dict(total=cost([r for arm in s.ROOTS for r in audits(output/arm/'rollout/native').values()]),by_root=by_root,accounting='attempted transport and returned completions, not all confirmed GPU generations',provider_billing=None)
def terminal(trace,capture,gold):
    response=(capture or {}).get('native_response') or {};message=response.get('message') or {};reply=trace.get('root_reply')
    available=(capture or {}).get('status')=='returned' and response.get('finish_reason') in ('stop','length') and not message.get('tool_calls') and isinstance(reply,str) and message.get('content')==reply
    return {**p.score(reply,gold,available),'reply':reply,'finish_reason':response.get('finish_reason')}
async def dispatch(rows,one,deadline):
    queue=asyncio.Queue()
    for row in rows:queue.put_nowait(row)
    async def worker():
        while time.time()<deadline:
            try:row=queue.get_nowait()
            except asyncio.QueueEmpty:return
            try:await one(row)
            finally:queue.task_done()
    tasks=[asyncio.create_task(worker()) for _ in range(4)]
    try:await asyncio.wait_for(asyncio.gather(*tasks),max(.001,deadline-time.time()))
    except TimeoutError:return False
    finally:
        for task in tasks:
            if not task.done():task.cancel()
        await asyncio.gather(*tasks,return_exceptions=True)
    return queue.empty()
def validate_endpoint(binding,descriptor,path,arm):
    root=binding['models'][binding['role_map']['root']]
    if binding!=s.binding(arm) or descriptor['model_alias']!=binding['role_map']['root'] or descriptor['adapter']!={'path':root['path'],'model_sha256':root['adapter_sha256'],'config_sha256':root['config_sha256']} or descriptor['role_binding_sha256']!=s.sha(path):raise ValueError('actual binding/descriptor differs')
    base=s.qnative().stack().prior.BASE
    if descriptor['base_model']['path']!=str(base) or descriptor['base_model']['manifest_sha256']!='19619b44b0bd30bf5debe0960e6dfd6acc5be8287c581727456aa5d17699c18f':raise ValueError('actual base differs')
    s.qnative().stack().native.e.capture.recursive.validate_serving_evidence(s.qnative().stack().native.e.capture.recursive.serving_evidence(Path(descriptor['log_path']) if 'log_path' in descriptor else path.parent/'service/inference.log'))
async def run(args):
    import httpx
    from verifiers.v1.env import RunSlot
    from verifiers.v1.envs.single_agent import SingleAgentEnv,SingleAgentEnvConfig
    ready=s.verify()
    with s.aliases({'study':s,'protocol':p}):owner=s.load('warm_reference_owned_owner',s.ROOT/'owner.py',s.sha(s.ROOT/'owner.py'))
    owner.validate_paths(args);binding=s.read(args.binding);descriptor=s.read(args.endpoint);validate_endpoint(binding,descriptor,args.binding,args.root)
    contexts={c['id']:c for c in s.read(s.ROOT/'inputs/PUBLIC.json')};gold=s.read(s.ROOT/'inputs/HOST_GOLD.json');queries=s.read(s.ROOT/'inputs/QUERIES.json');plan=[r for r in s.read(s.ROOT/'inputs/PLAN.json') if r['root']==args.root]
    if len(plan)!=8:raise ValueError('eight preplanned phase slots')
    args.output.mkdir(parents=True,exist_ok=False);started=time.time();deadline=args.deadline-15
    s.write(args.output/'RUN.json',dict(identity=ready['identity'],root=args.root,started_epoch=started,deadline_epoch=args.deadline,root_deadline_epoch=deadline,planned=8))
    s.write(args.output/'PLANNED_NULL_ENDPOINTS.json',[p.null(r,'preplanned') for r in plan])
    url=f'http://{descriptor["host"]}:{descriptor["port"]}/v1';headers={'Authorization':'Bearer '+os.environ[descriptor['api_key_env']]}
    async with httpx.AsyncClient(trust_env=False,headers=headers,timeout=15) as client:
        live=await client.get(url+'/models');live.raise_for_status();cards={v['id']:v for v in live.json()['data']}
        for alias,model in binding['models'].items():
            if cards.get(alias,{}).get('root')!=model['path'] or cards[alias].get('parent')!=descriptor['base_model']['path']:raise ValueError('live aliases/base differ')
        s.write(args.output/'LIVE_MODELS.json',cards)
    out=args.output/'native';out.mkdir();interface=n.interface(out);tasks={};expectations={}
    for row in plan:
        task=n.task(contexts[row['context_id']],queries[row['task_name']]['question'],row)
        tasks[row['id']]=task;expectations[row['id']]=n.expected(task,row)
        frozen=s.read(s.ROOT/'inputs/NATIVE_PREPARATION.json')['expected'][row['id']]
        if expectations[row['id']]!=frozen:raise ValueError('prepared native prefix changed')
        s.write(out/'prepared'/(row['id']+'.json'),dict(coordinate=row,expected=expectations[row['id']],task_hash=task.hash))
    results={};endpoint=dict(url=url,model=binding['role_map']['root'],renderer_model=descriptor['base_model']['path'],api_key_env=descriptor['api_key_env'])
    async def one(row):
        result=p.null(row,'native_final_not_returned');result['started_epoch']=time.time()
        try:
            raw=(await asyncio.wait_for(env.run_slot(RunSlot(tasks[row['id']]),n.make_context(interface,endpoint,row)),min(120.,max(.001,deadline-time.time())))).to_record()
            s.write(out/'episodes'/(row['id']+'.json'),raw)
            if len(raw.get('traces',[]))!=1:raise ValueError('native trace cardinality')
            trace=raw['traces'][0];roles={k:v for k,v in audits(out).items() if v['coordinate']['id']==row['id']};capture,indices=metrics().final_capture(trace,roles)
            result.update(terminal(trace,capture,gold[row['context_id']]['answers'][row['family']]),final_request_id=capture['request_id'] if capture else None,final_branch_node_indices=indices,first_prefix_verified=any(v.get('first_prefix_verified') for v in roles.values()),trace_errors=trace.get('errors'),episode_errors=raw.get('errors'),setup_attestation=trace.get('info',{}).get('warm_reference_setup'))
            result['trace_evidence']=[dict(index=i,message=node.get('message')) for i,node in enumerate(trace['nodes']) if (node.get('message') or {}).get('role')=='tool' or (node.get('message') or {}).get('tool_calls')]
            result['actual_scoped_reduction']=None;result['state_use_audit']='actual code/observation audit required; no sampled-code reexecution'
            if result['available']:result['cause']=None
        except asyncio.CancelledError:result['cause']='shared_deadline_cancelled';raise
        except Exception as error:result.update(error=dict(type=type(error).__name__,message=str(error)),cause='native_failure_see_raw_trace')
        finally:
            roles=[v for v in audits(out).values() if v['coordinate']['id']==row['id']]
            result.update(ended_epoch=time.time(),native_cost=cost(roles),child_attempts=sum(v.get('physical_request_attempt',False) and v['depth']>0 for v in roles))
            s.write(args.output/'rows'/(row['id']+'.json'),result);results[row['id']]=result
    with n.installed(interface,binding,out,plan,contexts,expectations):
        env=SingleAgentEnv(SingleAgentEnvConfig.model_validate(n.environment_config(interface)))
        async with env.serving():complete=await dispatch(plan,one,deadline)
    for row in plan:
        if row['id'] not in results:s.write(args.output/'rows'/(row['id']+'.json'),p.null(row,'unstarted_shared_deadline'))
    s.write(args.output/'STATUS.json',dict(complete=complete,root=args.root,planned=8,recorded=len(results),available=sum(r['available'] for r in results.values()),strict_correct=sum(r['reward']==1 for r in results.values()),ended_epoch=time.time()))
    return 0 if complete else 1
def parse_args(argv=None):
    ap=argparse.ArgumentParser();ap.add_argument('--root',choices=tuple(s.ROOTS),required=True);ap.add_argument('--binding',type=Path,required=True);ap.add_argument('--endpoint',type=Path,required=True);ap.add_argument('--output',type=Path,required=True);ap.add_argument('--deadline',type=float,required=True);return ap.parse_args(argv)
if __name__=='__main__':raise SystemExit(asyncio.run(run(parse_args())))
