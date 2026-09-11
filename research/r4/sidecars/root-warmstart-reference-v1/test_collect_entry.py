"""Real composed collector entry; intercept only external HTTP and native execution."""
import asyncio
import contextlib
import json
import time
def test_actual_owner_collector_entry_retains_all_eight_failed_slots(tmp_path,monkeypatch):
    import httpx
    import collect as c,native as n,study as s,protocol as p,owner
    from verifiers.v1.envs.single_agent import SingleAgentEnv
    output=tmp_path/'attempt';arm=p.phase_order()[0];stage=output/arm/'service';binding=s.binding(arm);s.write(stage/'BINDING.json',binding)
    root=binding['models'][binding['role_map']['root']]
    descriptor=dict(host='127.0.0.1',port=1,api_key_env='WARM_COLLECT_CPU_KEY',model_alias=binding['role_map']['root'],role_binding_sha256=s.sha(stage/'BINDING.json'),adapter=dict(path=root['path'],model_sha256=root['adapter_sha256'],config_sha256=root['config_sha256']),base_model=dict(path=str(s.qnative().stack().prior.BASE),manifest_sha256='19619b44b0bd30bf5debe0960e6dfd6acc5be8287c581727456aa5d17699c18f'))
    s.write(stage/'service/endpoint-original.json',descriptor)
    monkeypatch.setattr(s,'ATTEMPT',output);monkeypatch.setattr(s,'verify',lambda:dict(identity='cpu-collector'));monkeypatch.setenv('WARM_COLLECT_CPU_KEY','cpu-fixture-not-credential');monkeypatch.setenv('STRICT_RLM_CALIBRATION_API_KEY','cpu-fixture-not-credential')
    recursive=s.qnative().stack().native.e.capture.recursive
    monkeypatch.setattr(recursive,'serving_evidence',lambda path:{'cpu_fixture':'no model launch'});monkeypatch.setattr(recursive,'validate_serving_evidence',lambda value:None)
    attempted=[]
    class Response:
        def json(self):return dict(data=[dict(id=alias,root=model['path'],parent=descriptor['base_model']['path']) for alias,model in binding['models'].items()])
        def raise_for_status(self):pass
    class Client:
        def __init__(self,*args,**kwargs):pass
        async def __aenter__(self):return self
        async def __aexit__(self,*args):pass
        async def get(self,url):
            assert url.endswith('/models');return Response()
        async def post(self,*args,**kwargs):raise AssertionError('no acquisition or synthetic source request allowed')
    monkeypatch.setattr(httpx,'AsyncClient',Client)
    @contextlib.asynccontextmanager
    async def serving(self):yield
    async def run_slot(self,slot,context):
        attempted.append(slot.task.data.name)
        assert context.sampling.max_tokens==2048 and context.sampling.temperature==.5
        raise RuntimeError('AUTHORED_CPU_NO_NATIVE_EXECUTION')
    monkeypatch.setattr(SingleAgentEnv,'serving',serving);monkeypatch.setattr(SingleAgentEnv,'run_slot',run_slot)
    args=c.parse_args(owner.collector_argv(output,arm,time.time()+120)[2:])
    assert asyncio.run(c.run(args))==0
    rows=[s.read(path) for path in (args.output/'rows').glob('*.json')]
    assert len(rows)==8 and len(attempted)==8 and {r['coordinate']['root'] for r in rows}=={arm}
    assert all(r['reward'] is None and r['operational_success']==0 for r in rows)
    assert c.ledger(output)['total']['physical_request_attempts']==0
