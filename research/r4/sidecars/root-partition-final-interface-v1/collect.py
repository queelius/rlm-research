"""Twenty-four actual final calls; strict native wire identity and no answer repair."""
import argparse
import asyncio
import hashlib
import os
from pathlib import Path
import time
import study as s
import protocol as p

def verified_response(raw,body,source,tokenizer):
    if raw.get('model')!=s.MODEL['alias'] or len(raw.get('choices',[]))!=1:raise ValueError('actual model/single branch differs')
    choice=raw['choices'][0];message=choice.get('message') or {};incoming=raw.get('prompt_token_ids');outgoing=choice.get('token_ids');usage=raw.get('usage') or {}
    if incoming!=source['actual_native_prompt_token_ids'] or not isinstance(outgoing,list) or any(type(v)!=int for v in outgoing):raise ValueError('actual native token identity unavailable/different')
    if usage.get('prompt_tokens')!=len(incoming) or usage.get('completion_tokens')!=len(outgoing):raise ValueError('native token usage disagrees')
    if message.get('role')!='assistant' or choice.get('finish_reason') not in ('stop','length'):raise ValueError('unverified returned assistant branch')
    decoded=tokenizer.decode(outgoing,skip_special_tokens=True,clean_up_tokenization_spaces=False)
    if not isinstance(message.get('content'),str) or decoded!=message['content'] or message.get('tool_calls'):raise ValueError('native completion text/branch not verified')
    return message['content'],choice['finish_reason'],usage

def summarize(plan,records,sources):
    byid={r['coordinate']['id']:r for r in records};rows=[byid[r['id']] for r in plan];cells={};pairs=[]
    for kind in ('full','direct'):
        for decoder in ('free','exact'):
            selected=[r for r in rows if r['coordinate']['kind']==kind and r['coordinate']['decoder']==decoder]
            cells[kind+'/'+decoder]=dict(planned=len(selected),available=sum(r['score']['available'] for r in selected),correct=sum(r['score']['reward']==1 for r in selected),invalid=sum(r['score']['valid'] is False for r in selected),null=sum(r['score']['reward'] is None for r in selected),length=sum(r['score']['length'] for r in selected))
    for source in sources.values():
        pair={r['coordinate']['decoder']:r['score']['reward'] for r in rows if r['coordinate']['source_id']==source['id']}
        a,b=pair['free'],pair['exact'];pairs.append(dict(source_id=source['id'],world_id=source['world_id'],kind=source['kind'],partition=source['partition'],free=a,exact=b,outcome='unavailable' if a is None or b is None else 'win' if b>a else 'loss' if b<a else 'tie'))
    return dict(cells=cells,pairs=pairs,world_clusters=4,unique_full_states=8,unique_direct_worlds=4,
        new_physical_calls=sum(r['model_called'] for r in rows),historical_unique_acquisitions=24,hypothetical_acquisitions=sum(r['reused_acquisition_cost']['calls'] for r in rows),
        new_input_tokens_known=sum((r.get('usage') or {}).get('prompt_tokens',0) for r in rows),new_output_tokens_known=sum((r.get('usage') or {}).get('completion_tokens',0) for r in rows),
        usage_unknown_calls=sum(r['model_called'] and not r.get('usage') for r in rows),
        physical_new_request_seconds=sum(r['elapsed_seconds'] for r in rows if r['model_called']),
        reused_hypothetical_input_tokens=sum(r['reused_acquisition_cost']['input_tokens'] for r in rows),
        reused_hypothetical_output_tokens=sum(r['reused_acquisition_cost']['output_tokens'] for r in rows),
        reused_hypothetical_seconds=sum(r['reused_acquisition_cost']['seconds'] for r in rows),
        source_cost_note='Each full endpoint charged all3 actual historical acquisitions; hypothetical repeats are not new physical work; direct none',rows=rows)

async def run(args):
    import httpx
    import owner
    owner.validate_argv([str(s.NATIVE),str(s.ROOT/'collect.py'),'run','--endpoint',str(args.endpoint),'--output',str(args.output),'--deadline',str(args.deadline)])
    ready=s.verify();endpoint=s.read(args.endpoint);s.service.validate_descriptor(endpoint,s.MODEL)
    sources={r['id']:r for r in s.read(s.ROOT/'INPUTS.json')};gold=s.read(s.ROOT/'HOST_GOLD.json');plan=s.read(s.ROOT/'PLAN.json');requests=s.read(s.ROOT/'REQUESTS.json');tokenizer=s.tokenizer()
    args.output.mkdir(parents=True,exist_ok=False);started=time.time();records=[]
    s.write(args.output/'RUN.json',dict(identity=ready['identity'],endpoint=endpoint,planned=24,started_epoch=started,deadline=args.deadline,new_extractions=0))
    hashes={s.digest(body):identifier for identifier,body in requests.items()}
    async def wire(request):
        if request.method!='POST':return
        if not request.url.path.endswith('/chat/completions'):raise ValueError('unexpected model endpoint')
        digest=hashlib.sha256(request.content).hexdigest();identifier=hashes[digest]
        if request.content!=s.serialize(requests[identifier]).encode():raise ValueError('actual ordered wire differs')
        s.write(args.output/'wire'/f'{identifier}.json',dict(body_utf8=request.content.decode(),body_sha256=digest,credentials_recorded=False))
    iterator=iter(plan);url=f'http://{endpoint["host"]}:{endpoint["port"]}';headers={'Authorization':'Bearer '+os.environ[endpoint['api_key_env']]}
    def empty(row):
        source=sources[row['source_id']]
        return dict(coordinate=row,model_called=False,native_verified=False,score=p.score(None,gold[source['world_id']],None,available=False),reused_acquisition_cost=source['acquisition_cost'],historical_source=source['historical_call_path'],historical_source_sha256=source['historical_call_sha256'],elapsed_seconds=0.)
    async with httpx.AsyncClient(headers=headers,trust_env=False,timeout=120,event_hooks={'request':[wire]}) as client:
        cards=await client.get(url+'/v1/models');cards.raise_for_status();s.service.validate_models(cards.json(),s.MODEL)
        version=await client.get(url+'/version');version.raise_for_status()
        if version.json().get('version')!='0.28.0':raise ValueError('actual vLLM version changed')
        s.write(args.output/'LIVE_IDENTITY.json',dict(models=cards.json(),version=version.json()))
        async def worker():
            while time.time()<args.deadline:
                row=next(iterator,None)
                if row is None:return
                source=sources[row['source_id']];record=empty(row);before=time.time();body=requests[row['id']]
                try:
                    if body!=p.request(source,row['seed'],row['decoder'],s.MODEL['alias']):raise ValueError('request protocol drift')
                    record['model_called']=True;response=await client.post(url+'/v1/chat/completions',json=body)
                    record.update(http_status=response.status_code,raw_response_text=response.text);response.raise_for_status();raw=response.json();record['raw_response']=raw
                    content,finish,usage=verified_response(raw,body,source,tokenizer)
                    record.update(native_verified=True,content=content,usage=usage,score=p.score(content,gold[source['world_id']],finish))
                except asyncio.CancelledError:
                    record['error']=dict(type='CancelledError',reason='shared collection deadline',cost_unknown=True);raise
                except Exception as error:record['error']=dict(type=type(error).__name__,message=str(error))
                finally:
                    record.update(started_epoch=before,ended_epoch=time.time(),elapsed_seconds=time.time()-before)
                    s.write(args.output/'calls'/f'{row["id"]}.json',record);records.append(record)
        timeout=False
        try:
            async with asyncio.timeout(max(.001,args.deadline-time.time())):await asyncio.gather(*(worker() for _ in range(4)))
        except TimeoutError:timeout=True
    seen={r['coordinate']['id'] for r in records}
    for row in plan:
        if row['id'] not in seen:
            record=empty(row);record['error']=dict(type='Unrun',reason='shared collection deadline');s.write(args.output/'calls'/f'{row["id"]}.json',record);records.append(record)
    summary=summarize(plan,records,sources);s.write(args.output/'SUMMARY.json',summary)
    status=dict(planned=24,recorded=len(records),complete=not timeout and all('error' not in r for r in records),called=summary['new_physical_calls'],available=sum(r['score']['available'] for r in records),timeout=timeout,elapsed_seconds=time.time()-started)
    s.write(args.output/'STATUS.json',status);return status

if __name__=='__main__':
    ap=argparse.ArgumentParser();ap.add_argument('command',choices=('run',));ap.add_argument('--endpoint',type=Path,required=True);ap.add_argument('--output',type=Path,required=True);ap.add_argument('--deadline',type=float,required=True);args=ap.parse_args()
    status=asyncio.run(run(args));print(status);raise SystemExit(0 if status['complete'] else 2)
