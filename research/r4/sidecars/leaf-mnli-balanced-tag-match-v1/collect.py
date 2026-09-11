"""Checkpointed four-worker collector for the frozen 192 endpoints."""
import argparse,asyncio,hashlib,json,os,time
from pathlib import Path
import httpx
import owner,protocol as p,scoring,study as s

def summarize(rows):
 out=scoring.summarize(rows);used=[x for x in rows if x.get('physical_attempt')];known=[x for x in used if x.get('usage_observed')]
 out['costs']={'physical_requests':len(used),'requests_with_usage':len(known),'unknown_usage':len(used)-len(known),'prompt_tokens':sum(x['usage_observed']['prompt_tokens'] for x in known),'completion_tokens':sum(x['usage_observed']['completion_tokens'] for x in known),'provider_billing':'unknown/not measured'};return out

async def run(endpoint_path,output,deadline,transport=None):
 ready=s.verify();contexts=p.contexts();plan=s.read(s.ROOT/'PLAN.json');bodies=s.read(s.ROOT/'REQUESTS.json');wires=s.read(s.ROOT/'ORDERED_REQUESTS.json');prompts=s.read(s.ROOT/'PROMPT_IDS.json');native=s.read(s.ROOT/'CPU_NATIVE.json');tok=s.tokenizer();endpoint=s.read(endpoint_path);s.service.validate_descriptor(endpoint,s.MODEL)
 output.mkdir(parents=True,exist_ok=False);(output/'calls').mkdir();started=time.time();call_deadline=deadline-30;s.write(output/'PLANNED_NULL_ENDPOINTS.json',[p.null_row(x,'not yet attempted') for x in plan]);s.write(output/'RUN.json',{'identity':ready['identity'],'started_epoch':started,'work_deadline':deadline,'call_deadline':call_deadline,'workers':4,'request_seconds':90,'no_tools_executed':True})
 results={};queue=asyncio.Queue()
 for row in plan:queue.put_nowait(row)
 headers={'Authorization':'Bearer '+os.environ[endpoint['api_key_env']],'Content-Type':'application/json'};base=f"http://{endpoint['host']}:{endpoint['port']}"
 async def dispatched(request):
  info=request.extensions['science_checkpoint'];s.write(info['directory']/'REQUEST.json',{'ordered_body':request.content.decode(),'body_sha256':hashlib.sha256(request.content).hexdigest(),'expected_native_prompt_ids':info['prompt'],'dispatch_epoch':time.time()});info['result']['physical_attempt']=True
 async with httpx.AsyncClient(headers=headers,trust_env=False,transport=transport,timeout=90,event_hooks={'request':[dispatched]}) as client:
  async def worker():
   while not queue.empty() and time.time()<call_deadline:
    row=queue.get_nowait();key=row['id'];context=contexts[row['context_index']];result={'coordinate':row,'score':scoring.missing(context),'physical_attempt':False,'native_verified':False,'usage_observed':None,'started_epoch':time.time(),'error':None};directory=output/'calls'/key;directory.mkdir();wire=wires[key].encode()
    try:
     if json.loads(wire)!=bodies[key] or hashlib.sha256(wire).hexdigest()!=native['request_wire_sha256'][key]:raise ValueError('frozen request changed')
     request=client.build_request('POST',base+'/v1/chat/completions',content=wire);request.extensions['science_checkpoint']={'directory':directory,'prompt':prompts[key],'result':result};response=await asyncio.wait_for(client.send(request),timeout=min(90,max(.001,call_deadline-time.time())));result['status_code']=response.status_code;s.write(directory/'RESPONSE.json',{'status_code':response.status_code,'body':response.text,'received_epoch':time.time()});raw=response.json();result['raw']=raw;usage=raw.get('usage') if isinstance(raw,dict) else None
     if isinstance(usage,dict) and all(type(usage.get(n)) is int and usage[n]>=0 for n in ('prompt_tokens','completion_tokens')):result['usage_observed']={n:usage[n] for n in ('prompt_tokens','completion_tokens')}
     response.raise_for_status();message,finish,_=scoring.verified_response(raw,prompts[key],tok);result.update(native_verified=True,finish_reason=finish,length_capped=finish=='length',score=scoring.score(message,context,row['arm']))
    except BaseException as caught:
     result['error']={'type':type(caught).__name__,'message':str(caught)}
     if isinstance(caught,asyncio.CancelledError):raise
    finally:
     result['elapsed_seconds']=time.time()-result['started_epoch'];results[key]=result;s.write(directory/'RESULT.json',result);queue.task_done()
  tasks=[asyncio.create_task(worker()) for _ in range(4)];failure=None
  try:await asyncio.wait_for(asyncio.gather(*tasks),timeout=max(.001,call_deadline-time.time()))
  except BaseException as caught:
   failure={'type':type(caught).__name__,'message':str(caught)}
   for task in tasks:task.cancel()
   await asyncio.gather(*tasks,return_exceptions=True)
 rows=[results.get(row['id'],{'coordinate':row,'score':scoring.missing(contexts[row['context_index']]),'physical_attempt':False,'native_verified':False,'usage_observed':None,'error':{'type':'PlannedNULL','message':'cap before dispatch'}}) for row in plan];s.write(output/'ROWS.json',rows);s.write(output/'SUMMARY.json',summarize(rows));status={'planned':192,'recorded':len(rows),'available':sum(x['score']['available'] for x in rows),'physical_attempts':sum(x['physical_attempt'] for x in rows),'inventory_complete':len(rows)==192,'all_native_finals_available':all(x['score']['available'] for x in rows),'orchestrator_error':failure,'elapsed_seconds':time.time()-started};s.write(output/'STATUS.json',status);return status

if __name__=='__main__':
 a=argparse.ArgumentParser();a.add_argument('command',choices=('run',));a.add_argument('--endpoint',required=True,type=Path);a.add_argument('--output',required=True,type=Path);a.add_argument('--deadline',required=True,type=float);x=a.parse_args();owner.validate_argv([str(s.NATIVE),str(s.ROOT/'collect.py'),'run','--endpoint',str(x.endpoint),'--output',str(x.output),'--deadline',str(x.deadline)]);print(asyncio.run(run(x.endpoint,x.output,x.deadline)))
