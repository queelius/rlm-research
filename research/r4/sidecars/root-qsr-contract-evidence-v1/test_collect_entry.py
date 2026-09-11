"""Actual collector entry with authored transport; no model/native execution."""
import asyncio
import contextlib
import json
import time
from types import SimpleNamespace

def test_actual_collector_keeps_invalid_source_slots_and_runs_raw(tmp_path,monkeypatch):
    import httpx
    import collect as c
    import native as n
    import study as s
    from verifiers.v1.envs.single_agent import SingleAgentEnv
    output=tmp_path/'attempt';stage=output/'service';binding=s.binding();s.write(stage/'BINDING.json',binding)
    root=binding['models'][binding['role_map']['root']]
    descriptor=dict(host='127.0.0.1',port=1,api_key_env='CONTRACT_COLLECT_CPU_KEY',model_alias=binding['role_map']['root'],role_binding_sha256=s.sha(stage/'BINDING.json'),adapter=dict(path=root['path'],model_sha256=root['adapter_sha256'],config_sha256=root['config_sha256']),base_model=dict(path=str(s.qnative().stack().prior.BASE),manifest_sha256='19619b44b0bd30bf5debe0960e6dfd6acc5be8287c581727456aa5d17699c18f'))
    s.write(stage/'service/endpoint-original.json',descriptor)
    monkeypatch.setattr(s,'ATTEMPT',output);monkeypatch.setattr(s,'verify',lambda:dict(identity='cpu-collector'));monkeypatch.setenv('CONTRACT_COLLECT_CPU_KEY','cpu-fixture-not-credential');monkeypatch.setenv('STRICT_RLM_CALIBRATION_API_KEY','cpu-fixture-not-credential')
    recursive=s.qnative().stack().native.e.capture.recursive
    monkeypatch.setattr(recursive,'serving_evidence',lambda path:{'cpu_fixture':'no model launch'});monkeypatch.setattr(recursive,'validate_serving_evidence',lambda value:None)
    public=s.read(s.ROOT/'inputs/PUBLIC.json');tokenizer=s.qnative().stack().native.renderer()._tokenizer;sent=[];attempted=[]
    class Response:
        def __init__(self,value):self.value=value;self.text=json.dumps(value);self.status_code=200
        def json(self):return self.value
        def raise_for_status(self):pass
    class Client:
        def __init__(self,*args,**kwargs):pass
        async def __aenter__(self):return self
        async def __aexit__(self,*args):pass
        async def get(self,url):return Response(dict(data=[dict(id=alias,root=model['path'],parent=descriptor['base_model']['path']) for alias,model in binding['models'].items()]))
        async def post(self,url,**kwargs):
            body=kwargs['json'];sent.append(body);index=len(sent)-1
            assert body['model']==binding['fixed_child'] and 'tools' not in body and 'structured_outputs' not in body
            reply=json.dumps({r['id']:'entity' for r in public[index]['records']}) if index==0 else '{}'
            tokens=tokenizer.encode(reply,add_special_tokens=False)+[151645]
            prompt=tokenizer.apply_chat_template(body['messages'],tokenize=True,add_generation_prompt=True,enable_thinking=False,return_dict=False)
            return Response(dict(model=body['model'],prompt_token_ids=prompt,usage=dict(prompt_tokens=len(prompt),completion_tokens=len(tokens)),choices=[dict(message=dict(role='assistant',content=reply),finish_reason='stop',token_ids=tokens)]))
    monkeypatch.setattr(httpx,'AsyncClient',Client)
    @contextlib.asynccontextmanager
    async def serving(self):yield
    async def run_slot(self,slot,context):
        attempted.append(slot.task.data.name)
        assert context.sampling.max_tokens==2048
        raise RuntimeError('AUTHORED_CPU_NO_NATIVE_EXECUTION')
    monkeypatch.setattr(SingleAgentEnv,'serving',serving);monkeypatch.setattr(SingleAgentEnv,'run_slot',run_slot)
    args=SimpleNamespace(binding=stage/'BINDING.json',endpoint=stage/'service/endpoint-original.json',output=output/'rollout',deadline=time.time()+120)
    assert asyncio.run(c.run(args))==0
    rows=[s.read(path) for path in (args.output/'rows').glob('*.json')]
    assert len(sent)==2 and len(rows)==24 and len(attempted)==18
    assert sum(row['cause']=='source_map_unavailable' for row in rows)==6
    assert all(row['reward'] is None and row['operational_success']==0 for row in rows)
    assert c.ledger(output)['sources']['physical_request_attempts']==2
