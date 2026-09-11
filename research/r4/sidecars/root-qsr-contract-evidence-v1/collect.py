"""Two free sampled child sources and24 native roots; no repair or answer fallback."""
import argparse
import asyncio
import json
import os
from pathlib import Path
import time
import native as n
import protocol as p
import study as s

def metrics():return s.load('contract_evidence_metrics',s.SIDE/'root-example-map-visibility-v1/metrics.py','0ef6a89ad3655afe71226878f0296802e6b8af62b5aa295eec23e3ed151c53d3')
def cost(records):
    physical=[r for r in records if r.get('physical_request_attempt')]
    clean=[]
    for r in physical:
        body=(r.get('native_wire_response') or {}).get('body')
        if isinstance(body,str):
            try:body=json.loads(body)
            except ValueError:body=None
        clean.append(dict(native_wire_response=dict(body=body)))
    return dict(physical_request_attempts=len(physical),returned_native_completions=sum(r.get('status')=='returned' for r in physical),pretransport_rejected=sum(bool(r.get('pretransport_rejected')) for r in records),usage=metrics().usage(clean),provider_billing=None)
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
    rows=list(audits(output/'rollout/native').values())
    sources={}
    for path in (output/'rollout/acquisition-requests').glob('*.json'):sources[path.stem]=s.read(path)
    for path in (output/'rollout/acquisitions').glob('*.json'):sources[path.stem]=s.read(path)
    return dict(total=cost(rows+list(sources.values())),native=cost(rows),sources=cost(list(sources.values())),accounting='attempted transport and returned completions; attempts are not all confirmed GPU generations',provider_billing=None)
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
def extraction_request(context,row,binding):
    return dict(model=binding['fixed_child'],messages=[dict(role='system',content='You are a final-only question classifier. Return only the requested JSON object. Do not use tools or write code.'),dict(role='user',content=s.contract().request_for(context['records']))],temperature=.5,top_p=.95,top_k=-1,min_p=0.,seed=row['seed'],max_tokens=1536,repetition_penalty=1.,presence_penalty=0.,frequency_penalty=0.,return_token_ids=True,cache_salt=s.NAMESPACE,chat_template_kwargs=dict(enable_thinking=False))
def verify_source(raw,body,tokenizer):
    expected=tokenizer.apply_chat_template(body['messages'],tokenize=True,add_generation_prompt=True,enable_thinking=False,return_dict=False)
    if raw.get('model')!=body['model'] or len(raw.get('choices',[]))!=1:raise ValueError('source actual model/branch')
    choice=raw['choices'][0];message=choice.get('message') or {};out=choice.get('token_ids');usage=raw.get('usage') or {}
    if raw.get('prompt_token_ids')!=expected or not isinstance(out,list) or not out or any(type(t)!=int for t in out):raise ValueError('source actual token prefix/suffix')
    if usage.get('prompt_tokens')!=len(expected) or usage.get('completion_tokens')!=len(out):raise ValueError('source token usage')
    if message.get('role')!='assistant' or choice.get('finish_reason') not in ('stop','length','tool_calls'):raise ValueError('source native assistant branch')
    if message.get('tool_calls') or choice['finish_reason']=='tool_calls':raise ValueError('source attempted tool routing')
    if tokenizer.decode(out,skip_special_tokens=True,clean_up_tokenization_spaces=False)!=message.get('content'):raise ValueError('source native text token identity')
    return dict(content=message['content'],finish_reason=choice['finish_reason'],native_verified=True,status='returned')
def validate_endpoint(binding,descriptor,path):
    root=binding['models'][binding['role_map']['root']]
    if binding!=s.binding() or descriptor['model_alias']!=binding['role_map']['root'] or descriptor['adapter']!={'path':root['path'],'model_sha256':root['adapter_sha256'],'config_sha256':root['config_sha256']} or descriptor['role_binding_sha256']!=s.sha(path):raise ValueError('actual binding/descriptor differs')
    base=s.qnative().stack().prior.BASE
    if descriptor['base_model']['path']!=str(base) or descriptor['base_model']['manifest_sha256']!='19619b44b0bd30bf5debe0960e6dfd6acc5be8287c581727456aa5d17699c18f':raise ValueError('actual base differs')
    s.qnative().stack().native.e.capture.recursive.validate_serving_evidence(s.qnative().stack().native.e.capture.recursive.serving_evidence(Path(descriptor['log_path']) if 'log_path' in descriptor else path.parent/'service/inference.log'))
async def run(args):
    import httpx
    from verifiers.v1.env import RunSlot
    from verifiers.v1.envs.single_agent import SingleAgentEnv,SingleAgentEnvConfig
    ready=s.verify()
    # Select our sealed owner by exact path; qualified imports may change sys.path.
    with s.aliases({'study':s,'protocol':p}):owner=s.load('contract_evidence_owned_owner',s.ROOT/'owner.py',s.sha(s.ROOT/'owner.py'))
    owner.validate_paths(args);binding=s.read(args.binding);descriptor=s.read(args.endpoint);validate_endpoint(binding,descriptor,args.binding)
    contexts={c['id']:c for c in s.read(s.ROOT/'inputs/PUBLIC.json')};gold=s.read(s.ROOT/'inputs/HOST_GOLD.json');queries=s.read(s.ROOT/'inputs/QUERIES.json');plan=s.read(s.ROOT/'inputs/PLAN.json');sources=s.read(s.ROOT/'inputs/ACQUISITION_PLAN.json')
    args.output.mkdir(parents=True,exist_ok=False);started=time.time();deadline=args.deadline-15
    s.write(args.output/'RUN.json',dict(identity=ready['identity'],started_epoch=started,deadline_epoch=args.deadline,root_deadline_epoch=deadline,planned=24,source_acquisitions=2))
    s.write(args.output/'PLANNED_NULL_ENDPOINTS.json',[p.null(r,'preplanned') for r in plan])
    url=f'http://{descriptor["host"]}:{descriptor["port"]}/v1';headers={'Authorization':'Bearer '+os.environ[descriptor['api_key_env']]}
    acquired={};tokenizer=s.qnative().stack().native.renderer()._tokenizer
    async with httpx.AsyncClient(trust_env=False,headers=headers,timeout=120) as client:
        live=await client.get(url+'/models');live.raise_for_status();cards={v['id']:v for v in live.json()['data']}
        for alias,model in binding['models'].items():
            if cards.get(alias,{}).get('root')!=model['path'] or cards[alias].get('parent')!=descriptor['base_model']['path']:raise ValueError('live aliases/base differ')
        s.write(args.output/'LIVE_MODELS.json',cards)
        async def acquire(row):
            context=contexts[row['context_id']];body=extraction_request(context,row,binding)
            record=dict(coordinate=row,request=body,physical_request_attempt=False,status='unrun',native_verified=False,started_epoch=time.time(),map=p.map_state(None,[r['id'] for r in context['records']]))
            try:
                record.update(physical_request_attempt=True,status='requested');s.write(args.output/'acquisition-requests'/(row['id']+'.json'),record)
                response=await client.post(url+'/chat/completions',json=body);record['native_wire_response']=dict(http_status=response.status_code,body=response.text);response.raise_for_status();raw=response.json();record['raw_response']=raw
                # A returned completion remains physical work even if authentication fails.
                if raw.get('choices'):record['status']='returned'
                record.update(verify_source(raw,body,tokenizer));record['map']=p.map_state(record['content'],[r['id'] for r in context['records']])
            except asyncio.CancelledError:record['error']=dict(type='CancelledError',message='source shared cap');raise
            except Exception as error:record['error']=dict(type=type(error).__name__,message=str(error))
            finally:
                record['ended_epoch']=time.time();s.write(args.output/'acquisitions'/(row['id']+'.json'),record);acquired[row['context_id']]=record
        await dispatch(sources,acquire,min(deadline,time.time()+150))
    for row in sources:
        if row['context_id'] not in acquired:
            record=dict(coordinate=row,physical_request_attempt=False,status='unrun',native_verified=False,map=p.map_state(None,[r['id'] for r in contexts[row['context_id']]['records']]))
            s.write(args.output/'acquisitions'/(row['id']+'.json'),record);acquired[row['context_id']]=record
    s.write(args.output/'ACQUISITION_SEAL.json',{r['id']:s.sha(args.output/'acquisitions'/(r['id']+'.json')) for r in sources})
    out=args.output/'native';out.mkdir();interface=n.interface(out);tasks={};expectations={}
    for row in plan:
        source=acquired[row['context_id']]
        if row['evidence']=='map' and not(source['native_verified'] and source['map']['available']):continue
        task=n.task(contexts[row['context_id']],queries[row['task_name']]['question'],row,source['map']['raw'] if row['evidence']=='map' else None)
        tasks[row['id']]=task;expectations[row['id']]=n.expected(task,row)
        s.write(out/'prepared'/(row['id']+'.json'),dict(coordinate=row,expected=expectations[row['id']],task_hash=task.hash))
    results={};endpoint=dict(url=url,model=binding['role_map']['root'],renderer_model=descriptor['base_model']['path'],api_key_env=descriptor['api_key_env'])
    async def one(row):
        result=p.null(row,'native_final_not_returned');result['started_epoch']=time.time();source=acquired[row['context_id']]
        result['source_acquisition_id']=source['coordinate']['id'] if row['evidence']=='map' else None
        try:
            if row['id'] not in tasks:result['cause']='source_map_unavailable';return
            raw=(await asyncio.wait_for(env.run_slot(RunSlot(tasks[row['id']]),n.make_context(interface,endpoint,row)),min(120.,max(.001,deadline-time.time())))).to_record()
            s.write(out/'episodes'/(row['id']+'.json'),raw)
            if len(raw.get('traces',[]))!=1:raise ValueError('native trace cardinality')
            trace=raw['traces'][0];roles={k:v for k,v in audits(out).items() if v['coordinate']['id']==row['id']};capture,indices=metrics().final_capture(trace,roles)
            result.update(terminal(trace,capture,gold[row['context_id']]['answers'][row['family']]),final_request_id=capture['request_id'] if capture else None,final_branch_node_indices=indices,first_prefix_verified=any(v.get('first_prefix_verified') for v in roles.values()),trace_errors=trace.get('errors'),episode_errors=raw.get('errors'),setup_attestation=trace.get('info',{}).get('contract_evidence_setup'))
            result['map_consistent']=None;result['map_implied_answer']=None
            if row['evidence']=='map':
                implied=p.answer(contexts[row['context_id']]['records'],source['map']['labels'],queries[row['task_name']]['query']);result['map_implied_answer']=implied;result['map_consistent']=p.score(result['reply'],implied,result['available'])['reward']
            result['trace_evidence']=[dict(index=i,message=node.get('message')) for i,node in enumerate(trace['nodes']) if (node.get('message') or {}).get('role')=='tool' or (node.get('message') or {}).get('tool_calls')]
            result['actual_scoped_reduction']=None;result['state_use_audit']='actual code/observation dataflow audit required; no sampled-code reexecution'
            if result['available']:result['cause']=None
        except asyncio.CancelledError:result['cause']='shared_deadline_cancelled';raise
        except Exception as error:result.update(error=dict(type=type(error).__name__,message=str(error)),cause='native_failure_see_raw_trace')
        finally:
            roles=[v for v in audits(out).values() if v['coordinate']['id']==row['id']]
            result.update(ended_epoch=time.time(),native_cost=cost(roles),child_attempts=sum(v.get('physical_request_attempt',False) and v['depth']>0 for v in roles),reused_source_cost=cost([source]) if row['evidence']=='map' else None,hypothetical_standalone_cost=cost(roles+([source] if row['evidence']=='map' else [])))
            s.write(args.output/'rows'/(row['id']+'.json'),result);results[row['id']]=result
    with n.installed(interface,binding,out,plan,contexts,expectations):
        env=SingleAgentEnv(SingleAgentEnvConfig.model_validate(n.environment_config(interface)))
        async with env.serving():complete=await dispatch(plan,one,deadline)
    for row in plan:
        if row['id'] not in results:s.write(args.output/'rows'/(row['id']+'.json'),p.null(row,'unstarted_shared_deadline'))
    s.write(args.output/'STATUS.json',dict(complete=complete,planned=24,recorded=len(results),available=sum(r['available'] for r in results.values()),strict_correct=sum(r['reward']==1 for r in results.values()),ended_epoch=time.time()))
    return 0 if complete else 1
def parse_args(argv=None):
    ap=argparse.ArgumentParser();ap.add_argument('--binding',type=Path,required=True);ap.add_argument('--endpoint',type=Path,required=True);ap.add_argument('--output',type=Path,required=True);ap.add_argument('--deadline',type=float,required=True);return ap.parse_args(argv)
if __name__=='__main__':raise SystemExit(asyncio.run(run(parse_args())))
