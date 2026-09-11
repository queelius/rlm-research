"""Four-worker native leaf collection with durable actual-dispatch checkpoints."""
import argparse
import asyncio
import hashlib
import json
import os
from pathlib import Path
import time
import httpx
import bg_study as s
import bg_protocol as p

def harvest(output,plan):
    output=Path(output);rows=[];pins={};known=dict(input=0,output=0,cached=0);unknown=dict(known);attempted=returned=0;physical=[]
    for coordinate in plan:
        path=output/'calls'/coordinate['id']/'RESULT.json'
        if path.exists():
            row=s.read(path)
            if row['coordinate']!=coordinate:raise ValueError('result coordinate identity')
        else:row=dict(coordinate=coordinate,score=p.score(None,coordinate['ids'],{},False),error='missing RESULT; raw-only response diagnostic, not primary salvage')
        rows.append(row)
    for directory in sorted((output/'calls').glob('*')):
        if not directory.is_dir():continue
        req=directory/'REQUEST.json';resp=directory/'RESPONSE.json';r=s.read(req) if req.exists() else None;v=s.read(resp) if resp.exists() else None
        for path in directory.glob('*.json'):pins[str(path)]=s.sha(path)
        if r is None:continue
        attempted+=1;returned+=v is not None;raw=(v or {}).get('raw');u=raw.get('usage',{}) if isinstance(raw,dict) else {}
        for key,val in dict(input=u.get('prompt_tokens'),output=u.get('completion_tokens'),cached=(u.get('prompt_tokens_details') or {}).get('cached_tokens')).items():
            if type(val)is int and val>=0:known[key]+=val
            else:unknown[key]+=1
        physical.append(dict(id=directory.name,request=r,response_path=str(resp) if resp.exists() else None,status=(v or {}).get('status'),received_epoch=(v or {}).get('received_epoch')))
    return dict(rows=rows,cost=dict(attempted=attempted,responses=returned,usage_known=known,unknown_usage=unknown,billing=None,dispatch_is_transport_not_gpu_acceptance=True),physical=physical,files_sha256=pins)

def summarize(rows,gold,public):
    cells={}
    for row in rows:
        c=row['coordinate'];key=(c['context_id'],c['repeat'],c['model_policy'],c['arm']);cells.setdefault(key,[]).append(row)
    result=[]
    for (context,repeat,model_policy,arm),values in cells.items():
        n=sum(r['coordinate']['n'] for r in values);correct=sum(r['score']['strict_correct'] or 0 for r in values);missing=sum(r['coordinate']['n'] for r in values if not r['score']['available']);labels={}
        for r in values:
            if r['score']['complete_map']:labels.update(r['score']['labels'])
        scalar=None;target='location' if context=='scale-state-02-256' else 'numeric value'
        truth=sum((r['weight'] if context=='scale-state-02-256' else 1) for r in public[context]['records'] if gold[context]['labels'][r['id']]==target)
        if len(labels)==len(public[context]['records']):
            scalar=sum((r['weight'] if context=='scale-state-02-256' else 1) for r in public[context]['records'] if labels[r['id']]==target)
        result.append(dict(context_id=context,repeat=repeat,model_policy=model_policy,arm=arm,planned_labels=n,strict_correct=correct,strict_bounds=[correct,correct+missing],null_labels=missing,complete_maps=sum(r['score']['complete_map'] for r in values),planned_maps=len(values),canonical_id_matches=sum(r['score']['canonical_id_matches'] or 0 for r in values),host_target_scalar=scalar,host_target_gold=truth,host_target_error=scalar-truth if scalar is not None else None,host_target_is_not_root_execution=True))
    return result

async def run(endpoint_path,output,deadline,transport=None):
    ready=s.verify();plan=s.read(s.ROOT/'inputs/PLAN.json');bodies=s.read(s.ROOT/'inputs/REQUESTS.json');gold=s.read(s.ROOT/'inputs/HOST_GOLD.json');renderer,_=s.renderer()
    endpoint=s.read(endpoint_path);output=Path(output);output.mkdir(parents=True,exist_ok=False);started=time.time();call_deadline=deadline-30
    s.write(output/'PLANNED.json',plan);s.write(output/'RUN.json',dict(identity=ready['identity'],started_epoch=started,work_deadline=deadline,call_deadline=call_deadline,workers=4,per_call_cap=90,no_model_tools_executed=True))
    queue=asyncio.Queue()
    for row in plan:queue.put_nowait(row)
    headers={'Authorization':'Bearer '+os.environ[endpoint['api_key_env']]}
    async def dispatched(request):
        info=request.extensions['science'];s.write(info['directory']/'REQUEST.json',dict(body=json.loads(request.content),body_sha256=hashlib.sha256(request.content).hexdigest(),dispatch_epoch=time.time(),prepared_epoch=info['prepared'],coordinate=info['row']))
    async with httpx.AsyncClient(headers=headers,trust_env=False,timeout=90,transport=transport,event_hooks={'request':[dispatched]}) as client:
        async def worker():
            while not queue.empty() and time.time()<call_deadline:
                row=queue.get_nowait();key=row['id'];directory=output/'calls'/key;directory.mkdir(parents=True);prepared=time.time();body=bodies[key]
                result=dict(coordinate=row,score=p.score(None,row['ids'],{},False),prepared_epoch=prepared,error=None)
                s.write(directory/'PREPARED.json',dict(coordinate=row,body=body,prepared_epoch=prepared))
                try:
                    request=client.build_request('POST',f'http://{endpoint["host"]}:{endpoint["port"]}/inference/v1/generate',json=body,headers={'x-science-call':key})
                    request.extensions['science']=dict(directory=directory,prepared=prepared,row=row)
                    response=await asyncio.wait_for(client.send(request),timeout=min(90,max(.001,call_deadline-time.time())))
                    try:raw=response.json()
                    except ValueError:raw=None
                    s.write(directory/'RESPONSE.json',dict(status=response.status_code,body=response.text,raw=raw,received_epoch=time.time()))
                    response.raise_for_status();native=p.native(raw,body,renderer)
                    result.update(native=native,score=p.score(native['content'],row['ids'],gold[row['context_id']]['labels'],True,native['tool_calls']))
                except BaseException as error:
                    result['error']=dict(type=type(error).__name__,message=str(error))
                    if isinstance(error,asyncio.CancelledError):raise
                finally:
                    result.update(ended_epoch=time.time(),elapsed_seconds=time.time()-prepared);s.write(directory/'RESULT.json',result);queue.task_done()
        tasks=[asyncio.create_task(worker()) for _ in range(4)];orchestrator_error=None
        try:await asyncio.wait_for(asyncio.gather(*tasks),timeout=max(.001,call_deadline-time.time()))
        except BaseException as error:
            orchestrator_error=dict(type=type(error).__name__,message=str(error))
            for task in tasks:task.cancel()
            await asyncio.gather(*tasks,return_exceptions=True)
    result=harvest(output,plan);s.write(output/'ROWS.json',result['rows']);s.write(output/'COST.json',{k:v for k,v in result.items() if k!='rows'});s.write(output/'STATUS.json',dict(planned=len(plan),elapsed_seconds=time.time()-started,physical=result['cost'],orchestrator_complete=orchestrator_error is None,orchestrator_error=orchestrator_error))
    return result

def parse_args(argv=None):
    ap=argparse.ArgumentParser();ap.add_argument('--endpoint',type=Path,required=True);ap.add_argument('--output',type=Path,required=True);ap.add_argument('--deadline',type=float,required=True);return ap.parse_args(argv)
def main():
    args=parse_args();asyncio.run(run(args.endpoint,args.output,args.deadline))
if __name__=='__main__':main()
