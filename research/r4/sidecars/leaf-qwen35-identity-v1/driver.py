"""Frozen per-model72 calls using the qualified collector and raw wire capture."""
import argparse
import asyncio
import hashlib
import json
import os
import time
from copy import deepcopy
from pathlib import Path
import httpx
import study as s
import service


def typed_ids(tokenizer,body):
    from vllm.entrypoints.openai.chat_completion.protocol import ChatCompletionRequest
    parsed=ChatCompletionRequest.model_validate(deepcopy(body))
    return tokenizer.apply_chat_template(body['messages'],tools=[t.model_dump() for t in parsed.tools],
        add_generation_prompt=True,tokenize=True,return_dict=False,**parsed.chat_template_kwargs)


def verify(spec):
    if s.digest({k:v for k,v in spec.items() if k!='spec_id'})!=spec['spec_id']:raise ValueError('spec identity')
    for path,expected in spec['source_sha256'].items():
        if s.sha(path)!=expected:raise ValueError('source changed: '+path)
    expected=s.build_design(s.build_data());expected['rendered_prompts']=s.read(s.ROOT/'CPU_QUALIFICATION.json')['rendered_prompts']
    if expected!=spec['design']:raise ValueError('source/design changed')
    for row in expected['plan']:
        if s.serialize(s.make_request(expected,row))!=s.serialize(spec['requests'][row['id']]):raise ValueError('request order/body changed')
    for path,record in spec['weight_stat_identity'].items():
        stat=Path(path).stat()
        if [stat.st_size,stat.st_mtime_ns,stat.st_ino]!=record:raise ValueError('previously hashed shard changed')


def wire_hook(spec,output):
    by={v:k for k,v in spec['request_sha256'].items()}
    async def capture(request):
        if request.method!='POST' or not request.url.path.endswith('/chat/completions'):return
        body=json.loads(request.content);key=by[s.digest(body)]
        if request.content!=s.serialize(spec['requests'][key]).encode():raise ValueError('actual ordered HTTP body differs')
        s.write_once(output/'wire'/f'{key}.json',dict(coordinate_id=key,body_utf8=request.content.decode(),
            body_sha256=hashlib.sha256(request.content).hexdigest(),captured_epoch=time.time(),credentials_recorded=False))
    return capture


async def run(model,endpoint_path,output,deadline):
    allspec=s.read(s.ROOT/'SPEC.json');verify(allspec);spec=deepcopy(allspec)
    spec['design']['plan']=[r for r in spec['design']['plan'] if r['model']==model]
    spec['design']['coordinates']=deepcopy(spec['design']['plan'])
    endpoint=s.read(endpoint_path);service.validate_descriptor(endpoint,s.MODELS[model])
    if output.parent!=s.ROOT/'outputs':raise ValueError('output outside owned namespace')
    output.mkdir(parents=True,exist_ok=False)
    s.write_once(output/'SPEC.json',spec);s.write_once(output/'ENDPOINT.json',endpoint)
    s.write_once(output/'ATTEMPT.json',dict(started_epoch=time.time(),deadline_epoch=deadline,
        endpoint_sha256=s.sha(endpoint_path),spec_sha256=s.sha(s.ROOT/'SPEC.json')))
    reason=None;started=time.time();records=[]
    try:
        async with asyncio.timeout(max(.001,deadline-time.time())):
            url=f"http://{endpoint['host']}:{endpoint['port']}/v1"
            async with httpx.AsyncClient(headers={'Authorization':'Bearer '+os.environ[endpoint['api_key_env']]},
                    timeout=120,trust_env=False,event_hooks={'request':[wire_hook(spec,output)]}) as client:
                response=await client.get(url.removesuffix('/v1')+'/version');response.raise_for_status()
                if response.json().get('version')!='0.28.0':raise ValueError('wrong live version')
                s.write_once(output/'VERSION.json',response.json())
                response=await client.get(url+'/models');response.raise_for_status();service.validate_models(response.json(),s.MODELS[model])
                s.write_once(output/'MODELS.json',response.json())
                records,reason=await s.collect_calls(client,url,spec,output,time.monotonic()+max(.001,deadline-time.time()))
    except TimeoutError:reason='collection_deadline'
    except BaseException as error:
        reason=type(error).__name__;s.write_once(output/'ERROR.json',dict(type=reason,message=str(error)))
    finally:
        records=[s.read(p) for p in sorted((output/'calls').glob('*.json'))]
        analysis=s.summarize(spec['design'],records);s.write_once(output/'analysis.json',analysis)
        responses=[r for r in analysis['coordinates'] if r['observable']]
        if any(not r['physical_prompt']['typed_template_equal'] or not r['physical_prompt']['reported_usage_length_equal'] or r['unexpected_reasoning'] for r in responses):
            reason=reason or 'physical_prompt_or_nonthinking_unverified'
        seen={r['coordinate']['id'] for r in records}
        s.write_once(output/'STATUS.json',dict(planned=72,recorded=len(records),stop_reason=reason,elapsed_seconds=time.time()-started,
            model=model,unrun=[r['id'] for r in spec['design']['plan'] if r['id'] not in seen]))
    return 0 if reason is None and len(records)==72 else 2


def main():
    p=argparse.ArgumentParser();p.add_argument('command',choices=['verify','run']);p.add_argument('--model',choices=list(s.MODELS));p.add_argument('--endpoint',type=Path);p.add_argument('--output',type=Path);p.add_argument('--deadline',type=float);a=p.parse_args()
    if a.command=='verify':verify(s.read(s.ROOT/'SPEC.json'));print('verified; no model calls')
    else:raise SystemExit(asyncio.run(run(a.model,a.endpoint,a.output.resolve(),a.deadline)))


if __name__=='__main__':main()
