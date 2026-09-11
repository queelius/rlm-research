"""Checkpointed 32-call collector; model output is never repaired or reordered."""
import argparse,asyncio,hashlib,json,os,time
from pathlib import Path
import httpx
import protocol as p
import scoring
import study as s

def summarize(rows):
    def group(values):
        available=[r for r in values if r['score']['available']];null=[r for r in values if not r['score']['available']]
        correct=sum(r['score']['strict_correct'] for r in available)
        return dict(planned=len(values),available=len(available),null=len(null),strict_correct=correct,
            strict_bounds=[correct,correct+48*len(null)],contract_valid=sum(bool(r['score']['contract_valid']) for r in available),
            shape_valid=sum(bool(r['score']['shape_valid']) for r in available),
            requested_tag_matches=sum(r['score']['tag_position_matches'] or 0 for r in available),
            shifted_named_correct_disagree=sum(r['score']['shifted_named_correct_disagree'] or 0 for r in available),
            shifted_named_disagree_items=sum(r['score']['shifted_named_disagree_items'] or 0 for r in available))
    costs=[r for r in rows if r.get('physical_attempt')];known=[r for r in costs if r.get('usage_observed')]
    return dict(arms={arm:group([r for r in rows if r['coordinate']['arm']==arm]) for arm in p.ARMS},
        costs=dict(physical_requests=len(costs),requests_with_usage=len(known),unknown_usage=len(costs)-len(known),
        prompt_tokens=sum(r['usage_observed']['prompt_tokens'] for r in known),
        completion_tokens=sum(r['usage_observed']['completion_tokens'] for r in known),provider_billing='unknown/not measured'),
        cluster_unit='8 repeated MNLI contexts; paired seeds are repeated measurements')

async def run(endpoint_path,output,deadline,transport=None):
    ready=s.verify();contexts=p.contexts();plan=s.read(s.ROOT/'PLAN.json');bodies=s.read(s.ROOT/'REQUESTS.json')
    wires=s.read(s.ROOT/'ORDERED_REQUESTS.json');prompts=s.read(s.ROOT/'PROMPT_IDS.json');native=s.read(s.ROOT/'CPU_NATIVE.json');tok=s.tokenizer()
    endpoint=s.read(endpoint_path);s.service.validate_descriptor(endpoint,s.MODEL)
    output.mkdir(parents=True,exist_ok=False);(output/'calls').mkdir();started=time.time();call_deadline=deadline-30
    s.write(output/'PLANNED_NULL_ENDPOINTS.json',[p.null_row(r,'not yet attempted') for r in plan])
    s.write(output/'RUN.json',dict(identity=ready['identity'],started_epoch=started,work_deadline=deadline,
        call_deadline=call_deadline,workers=4,request_seconds=90,no_tools_executed=True))
    results={};queue=asyncio.Queue()
    for row in plan:queue.put_nowait(row)
    headers={'Authorization':'Bearer '+os.environ[endpoint['api_key_env']],'Content-Type':'application/json'}
    base=f'http://{endpoint["host"]}:{endpoint["port"]}'
    async def dispatched(request):
        info=request.extensions['science_checkpoint'];s.write(info['directory']/'REQUEST.json',dict(
            ordered_body=request.content.decode(),body_sha256=hashlib.sha256(request.content).hexdigest(),
            expected_native_prompt_ids=info['prompt'],dispatch_epoch=time.time()));info['result']['physical_attempt']=True
    async with httpx.AsyncClient(headers=headers,trust_env=False,transport=transport,timeout=90,event_hooks={'request':[dispatched]}) as client:
        async def worker():
            while not queue.empty() and time.time()<call_deadline:
                row=queue.get_nowait();key=row['id'];ctx=contexts[row['context_index']]
                result=dict(coordinate=row,score=scoring.missing(ctx),physical_attempt=False,native_verified=False,
                    usage_observed=None,started_epoch=time.time(),error=None);directory=output/'calls'/key;directory.mkdir();wire=wires[key].encode()
                try:
                    if json.loads(wire)!=bodies[key] or hashlib.sha256(wire).hexdigest()!=native['request_wire_sha256'][key]:raise ValueError('frozen request changed')
                    request=client.build_request('POST',base+'/v1/chat/completions',content=wire)
                    request.extensions['science_checkpoint']=dict(directory=directory,prompt=prompts[key],result=result)
                    response=await asyncio.wait_for(client.send(request),timeout=min(90,max(.001,call_deadline-time.time())))
                    result['status_code']=response.status_code;s.write(directory/'RESPONSE.json',dict(status_code=response.status_code,body=response.text,received_epoch=time.time()))
                    raw=response.json();result['raw']=raw;usage=raw.get('usage') if isinstance(raw,dict) else None
                    if isinstance(usage,dict) and all(type(usage.get(k)) is int and usage[k]>=0 for k in ('prompt_tokens','completion_tokens')):result['usage_observed']={k:usage[k] for k in ('prompt_tokens','completion_tokens')}
                    response.raise_for_status();message,finish,_=scoring.verified_response(raw,prompts[key],tok)
                    result.update(native_verified=True,finish_reason=finish,length_capped=finish=='length',score=scoring.score(message,ctx,row['arm']))
                except BaseException as caught:
                    result['error']=dict(type=type(caught).__name__,message=str(caught))
                    if isinstance(caught,asyncio.CancelledError):raise
                finally:
                    result['elapsed_seconds']=time.time()-result['started_epoch'];results[key]=result;s.write(directory/'RESULT.json',result);queue.task_done()
        tasks=[asyncio.create_task(worker()) for _ in range(4)];failure=None
        try:await asyncio.wait_for(asyncio.gather(*tasks),timeout=max(.001,call_deadline-time.time()))
        except BaseException as caught:
            failure=dict(type=type(caught).__name__,message=str(caught))
            for task in tasks:task.cancel()
            await asyncio.gather(*tasks,return_exceptions=True)
    rows=[results.get(r['id'],dict(coordinate=r,score=scoring.missing(contexts[r['context_index']]),physical_attempt=False,
        native_verified=False,usage_observed=None,error=dict(type='PlannedNULL',message='cap before dispatch'))) for r in plan]
    s.write(output/'ROWS.json',rows);s.write(output/'SUMMARY.json',summarize(rows))
    status=dict(planned=32,recorded=len(rows),available=sum(r['score']['available'] for r in rows),
        physical_attempts=sum(r['physical_attempt'] for r in rows),inventory_complete=len(rows)==32,
        all_native_finals_available=all(r['score']['available'] for r in rows),orchestrator_error=failure,elapsed_seconds=time.time()-started)
    s.write(output/'STATUS.json',status);return status

if __name__=='__main__':
    ap=argparse.ArgumentParser();ap.add_argument('command',choices=('run',));ap.add_argument('--endpoint',required=True,type=Path)
    ap.add_argument('--output',required=True,type=Path);ap.add_argument('--deadline',required=True,type=float);a=ap.parse_args()
    import owner;owner.validate_argv([str(s.NATIVE),str(s.ROOT/'collect.py'),'run','--endpoint',str(a.endpoint),'--output',str(a.output),'--deadline',str(a.deadline)])
    print(asyncio.run(run(a.endpoint,a.output,a.deadline)))

