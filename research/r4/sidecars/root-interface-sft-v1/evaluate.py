"""24 frozen free-root coordinates for one weight; native capture and no answer repair."""
import argparse
import asyncio
import contextlib
import json
import os
import time
from pathlib import Path
import study as s
import native as n

async def dispatch(plan,one,deadline,workers=4):
    """One fixed queue, no retries. Completion writes occur inside one(), including cancellation."""
    queue=asyncio.Queue()
    for row in plan:queue.put_nowait(row)
    async def worker():
        while time.time()<deadline:
            try:row=queue.get_nowait()
            except asyncio.QueueEmpty:return
            try:await one(row)
            finally:queue.task_done()
    try:await asyncio.wait_for(asyncio.gather(*(worker() for _ in range(workers))),max(0,deadline-time.time()))
    except TimeoutError:pass

def verify_binding(binding,weight,training):
    initial=n.initial_binding()
    if weight=='initial':
        if binding!=initial:raise ValueError('initial policy changed')
    else:
        result=s.read(training/'RESULT.json');selected=result['selected']
        checkpoint=Path(selected['checkpoint'])
        if not result['complete'] or selected['step']!=4 or result['starting_adapter_sha256']!=s.START_SHA:raise ValueError('fixed-final training identity')
        for filename,expected in result['files_sha256'].items():s.check(checkpoint/filename,expected)
        root=binding['role_map']['root'];model=binding['models'][root]
        if model!={'path':str(checkpoint),'adapter_sha256':selected['adapter_sha256'],'config_sha256':selected['config_sha256']}:raise ValueError('wrong final adapter')
        child=initial['fixed_child']
        if binding['fixed_child']!=child or binding['models'][child]!=initial['models'][child]:raise ValueError('fixed child changed')

async def collect(args):
    from verifiers.v1.env import RunSlot
    from verifiers.v1.envs.single_agent import SingleAgentEnv,SingleAgentEnvConfig
    ready=s.read(s.ROOT/'READY.json')
    for path,sha in ready['source_sha256'].items():s.check(path,sha)
    recipe=s.read(s.ROOT/'RECIPE.json');prepared=Path(recipe['prepared'])
    for path,sha in recipe['input_sha256'].items():s.check(path,sha)
    binding=s.read(args.binding);verify_binding(binding,args.weight,args.training)
    descriptor=s.read(args.endpoint)
    rootmodel=binding['models'][binding['role_map']['root']]
    if descriptor['model_alias']!=binding['role_map']['root'] or descriptor['adapter']!={'path':rootmodel['path'],'model_sha256':rootmodel['adapter_sha256'],'config_sha256':rootmodel['config_sha256']}:raise ValueError('endpoint adapter mismatch')
    endpoint={**n.e.old.planned_endpoint(binding),'url':f'http://{descriptor["host"]}:{descriptor["port"]}/v1','api_key_env':descriptor['api_key_env']}
    public={c['id']:c for c in s.read(prepared/'PUBLIC.json')};host=s.read(prepared/'HOST_GOLD.json');plan=s.read(prepared/'EVAL_PLAN_FINAL.json')
    args.output.mkdir(parents=True,exist_ok=False)
    os.environ['PATH']=str(n.e.capture.q.ROOTLESS/'bin')+os.pathsep+os.environ.get('PATH','')
    os.environ.setdefault('VERIFIERS_CACHE_DIR','/project/alex_phd/cache/verifiers-prime')
    s.write(args.output/'INPUTS.json',dict(ready_sha256=s.sha(s.ROOT/'READY.json'),binding=binding,endpoint=descriptor,plan=plan,child_interface=recipe['child_interface'],weight=args.weight))
    records=[];started_order=[];started=time.time();deadline=min(args.deadline,started+900)
    async def one(row):
        c=public[row['context_id']];gold=host[c['id']]['answers'][row['family']]
        task=n.task(c,s.prompt(c,row['family']),gold,row['id'])
        started_order.append(row['id'])
        result=dict(coordinate=row,weight=args.weight,gold=gold,task_hash=task.hash,started_epoch=time.time(),actual_start_order=len(started_order)-1,source_group_ids_sha256=s.digest(c['group_ids']),context_sha256=s.digest(c['text']))
        try:
            raw=(await env.run_slot(RunSlot(task),interface.e.make_context(endpoint,row))).to_record()
            s.write(args.output/'episodes'/(row['id']+'.json'),raw)
            trace=raw['traces'][0] if len(raw.get('traces',[]))==1 else {}
            audits=[s.read(p) for p in (args.output/'typed-audit').glob('*-result.json')]
            root_audits=[v for v in audits if v['coordinate']['id']==row['id'] and v['depth']==0]
            first=min(root_audits,key=lambda v:v['started_epoch'],default=None)
            last=max(root_audits,key=lambda v:v['started_epoch'],default=None)
            expected=next(v for v in s.read(prepared/'EVAL_PROMPTS.json') if v['id']==row['id'])
            if first is not None and first.get('native_wire_request'):
                actual=first['native_wire_request']['body']
                if actual['token_ids']!=expected['token_ids'] or actual['model']!=binding['role_map']['root']:raise ValueError('first actual root physical token/alias mismatch')
                result.update(first_wire_token_ids_equal=True,first_request_id=first['request_id'],first_native_wire_body=actual)
            else:result['first_wire_token_ids_equal']=None
            reply=trace.get('root_reply');completed=bool(trace.get('is_completed'))
            unavailable=not last or last.get('status')!='returned'
            result.update(reward=None if unavailable else s.endpoint(reply,gold,completed),reply=reply,completed=completed,provider_unavailable=unavailable,empty=completed and reply=='',episode_path=str(args.output/'episodes'/(row['id']+'.json')),episode_errors=raw.get('errors'),trace_errors=trace.get('errors'))
        except asyncio.CancelledError:
            result.update(reward=None,completed=False,censored='affected incomplete coordinate at cap');raise
        except Exception as error:result.update(reward=None,completed=False,error={'type':type(error).__name__,'message':str(error)})
        finally:
            result['ended_epoch']=time.time();s.write(args.output/'rows'/(row['id']+'.json'),result);records.append(result)
    # Parent freezes one native or compatible typed interface before acceptance. No HTTP-only root edits.
    with child_hooks(recipe,binding,args.output,plan,public) as interface:
        env=SingleAgentEnv(SingleAgentEnvConfig.model_validate(interface.e.environment_config()))
        async with env.serving():
            await dispatch(plan,one,deadline)
    s.write(args.output/'TERMINAL.json',dict(recorded=len(records),planned=24,complete=len(records)==24,not_started=[r['id'] for r in plan if r['id'] not in {x['coordinate']['id'] for x in records}],correct=sum(r.get('reward')==1 for r in records),observed=sum(r.get('reward') is not None for r in records),completed_empty=sum(r.get('empty',False) for r in records),elapsed_seconds=time.time()-started))
    return 0 if len(records)==24 else 1

@contextlib.contextmanager
def child_hooks(recipe,binding,output,plan,public):
    import interface
    if recipe['child_interface']['kind']!='typed_batch' or recipe['child_interface']['pins']!=interface.PINS:raise ValueError('common typed interface binding changed')
    with interface.installed(binding,output,plan,public):yield interface

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--binding',type=Path,required=True);p.add_argument('--endpoint',type=Path,required=True);p.add_argument('--weight',choices=('initial','final'),required=True);p.add_argument('--training',type=Path,required=True);p.add_argument('--output',type=Path,required=True);p.add_argument('--deadline',type=float,required=True)
    raise SystemExit(asyncio.run(collect(p.parse_args())))
