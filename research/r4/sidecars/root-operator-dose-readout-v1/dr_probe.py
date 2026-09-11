"""Single native teacher-first requests: sampled actions retained, never executed."""
import argparse
import ast
import asyncio
import copy
from dataclasses import asdict
import json
import math
import os
from pathlib import Path
import time
import dr_study as s

def request_body(source,alias,seed):
    body=copy.deepcopy(source);body['model']=alias;body['sampling_params']['seed']=seed;return body

def authenticate(raw,renderer,tools):
    if not isinstance(raw,dict) or not isinstance(raw.get('request_id'),str) or not raw['request_id'] or len(raw.get('choices',[]))!=1:raise ValueError('one native response with request ID')
    choice=raw['choices'][0];ids=choice.get('token_ids');logs=(choice.get('logprobs') or {}).get('content')
    if not isinstance(ids,list) or not ids or any(type(v)!=int or v<0 for v in ids) or not isinstance(logs,list) or len(logs)!=len(ids):raise ValueError('native completion tokens/logprobs required')
    for token,entry in zip(ids,logs):
        value=entry.get('logprob')
        if entry.get('token')!=f'token_id:{token}' or type(value) not in (int,float) or not math.isfinite(value) or value==-9999.:raise ValueError('native token likelihood identity')
    if choice.get('finish_reason') not in ('stop','length'):raise ValueError('native finish reason')
    parsed=renderer.parse_response(ids,tools=tools);message=asdict(parsed)
    programs=[]
    for tool in message['tool_calls']:
        code=None;valid=False;calls=[]
        if tool['name']=='ipython' and tool['status']=='ok':
            try:
                args=json.loads(tool['arguments']) if isinstance(tool['arguments'],str) else tool['arguments'];code=args['code'];tree=ast.parse(code);valid=True
                calls=[n for n in ast.walk(tree) if isinstance(n,ast.Call)]
            except (TypeError,ValueError,KeyError,SyntaxError):pass
        programs.append(dict(code=code,ast_valid=valid,tool_name=tool['name'],parse_status=tool['status'],mentions_rlm_call=any(isinstance(n.func,ast.Name) and n.func.id=='rlm' for n in calls),contains_await=bool(valid and any(isinstance(n,ast.Await) for n in ast.walk(tree))),executed=False))
    return dict(message=message,completion_ids=ids,completion_logprobs=[r['logprob'] for r in logs],finish_reason=choice['finish_reason'],programs=programs,syntactic_acquisition_intent=any(r['mentions_rlm_call'] and r['contains_await'] for r in programs),executed_acquisition=False,no_code_execution=True)

async def run(args,transport=None):
    import httpx
    s.verify();binding=s.read(args.binding);descriptor=s.read(args.endpoint);s.validate(binding,descriptor,args.binding)
    rows=s.read(s.ROOT/'inputs/TEACHER_DIAGNOSTIC_PLAN.json');sources=s.read(s.ROOT/'inputs/TEACHER_FIRST_REQUESTS.json')
    renderer=s.stack().native.renderer();tools=json.loads(s.read(s.ROOT/'inputs/NATIVE_TEMPLATE.json')['tools_ordered_json'])
    args.output.mkdir(parents=True,exist_ok=False);s.write(args.output/'PLANNED_NULL.json',[dict(coordinate=r,available=False) for r in rows]);queue=asyncio.Queue()
    for row in rows:queue.put_nowait(row)
    results={};started=time.time();headers={'Authorization':'Bearer '+os.environ[descriptor['api_key_env']]}
    async with httpx.AsyncClient(trust_env=False,headers=headers,timeout=180,transport=transport) as client:
        response=await client.get(f'http://{descriptor["host"]}:{descriptor["port"]}/v1/models');response.raise_for_status();cards={r['id']:r for r in response.json()['data']}
        for alias,model in binding['models'].items():
            if cards.get(alias,{}).get('root')!=model['path']:raise ValueError('actual service model directory differs')
        async def worker():
            while not queue.empty() and time.time()<args.deadline:
                row=queue.get_nowait();target=args.output/row['id'];target.mkdir();result=dict(coordinate=row,available=False,physical_request_attempt=False,response_returned=False,usage=None)
                body=request_body(sources[row['id']],binding['role_map']['root'],row['seed'])
                s.write(target/'REQUEST.json',dict(body=body,source_path=row['source_request_path'],source_sha256=row['source_request_sha256'],changes=['model','sampling_params.seed'],expected_prompt_ids=body['token_ids']))
                try:
                    result['physical_request_attempt']=True;result['started_epoch']=time.time()
                    response=await asyncio.wait_for(client.post(f'http://{descriptor["host"]}:{descriptor["port"]}/inference/v1/generate',json=body),max(.001,min(180,args.deadline-time.time())))
                    result.update(response_returned=True,status=response.status_code);s.write(target/'RESPONSE.json',dict(status=response.status_code,body=response.text,received_epoch=time.time()))
                    raw=response.json();result['usage']=raw.get('usage');response.raise_for_status();result.update(authenticate(raw,renderer,tools),available=True,request_id=raw['request_id'],prompt_ids=body['token_ids'])
                except BaseException as error:
                    result['error']=dict(type=type(error).__name__,message=str(error))
                    if isinstance(error,asyncio.CancelledError):raise
                finally:result['ended_epoch']=time.time();results[row['id']]=result;s.write(target/'RESULT.json',result)
        tasks=[asyncio.create_task(worker()) for _ in range(4)]
        try:await asyncio.wait_for(asyncio.gather(*tasks),max(.001,args.deadline-time.time()))
        except BaseException:
            for task in tasks:task.cancel()
            await asyncio.gather(*tasks,return_exceptions=True)
    inventory=[results.get(r['id'],dict(coordinate=r,available=False,physical_request_attempt=False,response_returned=False,reason='unrun under fixed cap')) for r in rows]
    s.write(args.output/'TERMINAL.json',dict(rows=inventory,planned=12,available=sum(r['available'] for r in inventory),physical_requests=sum(r['physical_request_attempt'] for r in inventory),elapsed_seconds=time.time()-started,no_programs_executed=True))

def parse_args(argv=None):
    p=argparse.ArgumentParser()
    for n in ('binding','endpoint','output'):p.add_argument('--'+n,type=Path,required=True)
    p.add_argument('--deadline',type=float,required=True);return p.parse_args(argv)
if __name__=='__main__':asyncio.run(run(parse_args()))
