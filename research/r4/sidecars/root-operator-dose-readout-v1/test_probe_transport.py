"""Actual12-probe loop over frozen bodies with an authored native transport."""
import asyncio
import json
import time
from types import SimpleNamespace
import httpx
import dr_study as s
import dr_probe as p

def test_all12_exact_native_requests_without_execution(tmp_path,monkeypatch):
    binding=s.binding('sft6');stage=tmp_path/'service';s.write(stage/'BINDING.json',binding);root=binding['models'][binding['role_map']['root']]
    descriptor=dict(host='127.0.0.1',port=1,api_key_env='DOSE_PROBE_CPU_KEY',model_alias=binding['role_map']['root'],role_binding_sha256=s.sha(stage/'BINDING.json'),adapter=dict(path=root['path'],model_sha256=root['adapter_sha256'],config_sha256=root['config_sha256']),base_model=dict(path=str(s.dose.base_path()),manifest_sha256=s.sha(s.dose.base_path()/'local-research-manifest.json')))
    s.write(stage/'endpoint.json',descriptor);monkeypatch.setattr(s,'verify',lambda:dict(identity='CPU'));monkeypatch.setenv('DOSE_PROBE_CPU_KEY','CPU_FIXTURE_NOT_CREDENTIAL')
    rows=s.read(s.ROOT/'inputs/TEACHER_DIAGNOSTIC_PLAN.json');byseed={r['seed']:r for r in rows};sources=s.read(s.ROOT/'inputs/TEACHER_FIRST_REQUESTS.json');renderer=s.stack().native.renderer();tokenizer=renderer._tokenizer
    code='raise RuntimeError("MUST_NOT_EXECUTE")\nreply=await rlm("fixture")';ids=tokenizer.encode(s.stack().native.tool_action(code),add_special_tokens=False)+[151645];seen=[]
    async def transport(request):
        if request.method=='GET':return httpx.Response(200,json=dict(data=[dict(id=a,root=m['path']) for a,m in binding['models'].items()]))
        assert request.url.path=='/inference/v1/generate';body=json.loads(request.content);row=byseed[body['sampling_params']['seed']];old=sources[row['id']]
        assert body=={**old,'model':binding['role_map']['root'],'sampling_params':{**old['sampling_params'],'seed':row['seed']}}
        seen.append(row['id'])
        return httpx.Response(200,json=dict(request_id='CPU_PROBE_'+row['id'],usage=dict(prompt_tokens=len(body['token_ids']),completion_tokens=len(ids)),choices=[dict(token_ids=ids,finish_reason='stop',logprobs=dict(content=[dict(token=f'token_id:{v}',logprob=-.5) for v in ids]))]))
    args=SimpleNamespace(binding=stage/'BINDING.json',endpoint=stage/'endpoint.json',output=tmp_path/'probes',deadline=time.time()+120)
    asyncio.run(p.run(args,httpx.MockTransport(transport)))
    status=s.read(args.output/'TERMINAL.json');assert len(seen)==12 and len(set(seen))==12 and status['available']==12 and status['no_programs_executed']
    assert all(r['syntactic_acquisition_intent'] and not r['executed_acquisition'] and r['programs'][0]['code']==code for r in status['rows'])
