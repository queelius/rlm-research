import asyncio
import importlib
import sys
import time
from pathlib import Path

ROOT=Path(__file__).resolve().parent
sys.path.insert(0,str(ROOT))


def test_actual_collector_dispatches16_and_waits_for_cancellation(tmp_path,monkeypatch):
    s = importlib.import_module('study')
    plan = s.build_plan(s.read(s.PRIOR / 'prepared-v2/EVAL_PLAN_FINAL.json'))
    frozen = {p['id']: p for p in s.read(s.PRIOR / 'prepared-v2/EVAL_PROMPTS.json')}
    prompts = [{**frozen[r['source_coordinate_id']], 'id':r['id']} for r in plan]
    with s.aliases({'study':s}):
        cross = s.load('plan_test_cross', s.ROW/'readout.py', 'f447b808a9c346ca1517442c798e3bce585ce8e65861d7c0df54f26789dd2a43')
    collector, _ = cross.compose(plan,prompts)
    assert collector.collect.__globals__['time'].time() > 0
    done=[]
    async def one(row): done.append(row['id'])
    asyncio.run(collector.dispatch(plan,one,time.time()+5))
    assert len(done)==16 and set(done)=={r['id'] for r in plan}
    async def cancelled():
        flushed=[]
        async def slow(row):
            try: await asyncio.sleep(2)
            finally: flushed.append(row['id'])
        await collector.dispatch(plan,slow,time.time()+.02)
        assert len(flushed)==4
    asyncio.run(cancelled())
    # Exercise the actual collector's terminal-cardinality literals without a runtime/model.
    from types import SimpleNamespace
    import contextlib
    import verifiers.v1.env as env_module
    import verifiers.v1.envs.single_agent as agent_module
    class Raw:
        def to_record(self):return {'traces':[{'root_reply':'','is_completed':True}]}
    class Env:
        def __init__(self,config):pass
        @contextlib.asynccontextmanager
        async def serving(self):yield self
        async def run_slot(self,*args):return Raw()
    monkeypatch.setattr(env_module,'RunSlot',lambda task:task)
    monkeypatch.setattr(agent_module,'SingleAgentEnv',Env)
    monkeypatch.setattr(agent_module,'SingleAgentEnvConfig',SimpleNamespace(model_validate=lambda config:config))
    public=[{'id':r['context_id'],'group_ids':[],'text':'fixture'} for r in plan]
    host={r['context_id']:{'answers':{r['family']:0 for r in plan}} for r in plan}
    binding={'role_map':{'root':'root'},'models':{'root':{'path':'fixture','adapter_sha256':'a','config_sha256':'c'}}}
    descriptor={'model_alias':'root','adapter':{'path':'fixture','model_sha256':'a','config_sha256':'c'},'host':'unused','port':0,'api_key_env':'UNUSED'}
    values={'READY.json':{'source_sha256':{}},'RECIPE.json':{'prepared':str(tmp_path),'input_sha256':{},'child_interface':{}},
      'BINDING.json':binding,'endpoint.json':descriptor,'PUBLIC.json':public,'HOST_GOLD.json':host,'EVAL_PLAN_FINAL.json':plan}
    original_s=collector.s
    monkeypatch.setattr(collector,'s',SimpleNamespace(ROOT=tmp_path,read=lambda p:values[Path(p).name],check=lambda *a:None,
      sha=lambda p:'fixture',write=s.write,digest=s.digest,prompt=lambda *a:'fixture',endpoint=lambda *a:0))
    monkeypatch.setattr(collector,'verify_binding',lambda *a:None)
    fake_e=SimpleNamespace(old=SimpleNamespace(planned_endpoint=lambda b:{}),capture=SimpleNamespace(q=SimpleNamespace(ROOTLESS=tmp_path)),
       environment_config=lambda:{},make_context=lambda *a:None)
    monkeypatch.setattr(collector,'n',SimpleNamespace(e=fake_e,task=lambda *a:SimpleNamespace(hash='fixture')))
    @contextlib.contextmanager
    def hooks(*args):yield SimpleNamespace(e=fake_e)
    monkeypatch.setattr(collector,'child_hooks',hooks)
    monkeypatch.setenv('PATH',__import__('os').environ.get('PATH',''))
    monkeypatch.setenv('VERIFIERS_CACHE_DIR',str(tmp_path/'cache'))
    args=SimpleNamespace(binding=tmp_path/'BINDING.json',endpoint=tmp_path/'endpoint.json',weight='unchanged',training=tmp_path,
       output=tmp_path/'actual-collector',deadline=time.time()+5)
    assert asyncio.run(collector.collect(args))==0
    terminal=s.read(args.output/'TERMINAL.json')
    assert terminal['planned']==16 and terminal['recorded']==16 and terminal['complete']
    assert len(list((args.output/'rows').glob('*.json')))==16



def test_owned_execute_runs_two_training_three_phases48_and_shared_caps(tmp_path,monkeypatch):
    from types import SimpleNamespace
    s=importlib.import_module('study')
    with s.aliases({'study':s}):
        binding=s.load('plan_test_actual_binding',ROOT/'binding.py',s.sha(ROOT/'binding.py'))
    with s.aliases({'study':s,'binding':binding}):
        m=s.load('plan_test_actual_launch',ROOT/'launch.py',s.sha(ROOT/'launch.py'))
    s=m.s; output=tmp_path/'outputs/attempt-001'; phases=['unchanged','canonical','filter_first']; commands=[]
    monkeypatch.setattr(s,'ROOT',tmp_path)
    monkeypatch.setattr(s,'verify',lambda:{'identity':'fixture'})
    monkeypatch.setattr(s,'sha',lambda p:'fixture')
    monkeypatch.setattr(s,'phase_order',lambda:tuple(phases))
    monkeypatch.setattr(m.b,'selected',lambda arm:{'step':8})
    monkeypatch.setattr(m.b,'binding',lambda arm,chosen:{'arm':arm})
    monkeypatch.setattr(m.b,'training_source',lambda arm:tmp_path/arm)
    class Process:
        pid=123;returncode=0
        def wait(self,timeout): assert 0<timeout<=360;return 0
    monkeypatch.setattr(m.subprocess,'Popen',lambda *a,**k:Process())
    life=SimpleNamespace(observe=lambda pid:{'pid':pid},safe_observation=lambda x:x)
    def command(stage,name,argv,cap,work):
        commands.append(argv)
        s.write(stage/'rollout/TERMINAL.json',{'planned':16,'recorded':16,'complete':True})
    suite=SimpleNamespace(life=life,stop_child=lambda *a:None,start_service=lambda *a:None,release_service=lambda *a:None,command=command)
    monkeypatch.setattr(m,'dependencies',lambda:suite)
    monkeypatch.setattr(m.signal,'signal',lambda *a:None)
    monkeypatch.setattr(m.signal,'setitimer',lambda *a:None)
    monkeypatch.setenv('CUDA_VISIBLE_DEVICES','fixture-no-GPU')
    terminal=m.execute(output)
    assert terminal['complete'],terminal
    assert sum(v['terminal']['planned'] for v in terminal['stages'])==48
    assert [a[a.index('--weight')+1] for a in commands]==phases
    run=s.read(output/'RUN.json')
    assert run['deadline_epoch']-run['started_epoch']==2400
    assert run['work_deadline_epoch']-run['started_epoch']==2280


def test_real_four_full_pass_adam_updates_and_checkpoint_chain(tmp_path):
    import torch
    from types import SimpleNamespace
    s=importlib.import_module('study')
    t=s.private('train.py',view=s.old)
    torch.manual_seed(17)
    class TinyLoRA(torch.nn.Module):
        def __init__(self):
            super().__init__();self.base=torch.nn.Embedding(16,4);self.base.weight.requires_grad=False
            self.lora=torch.nn.Linear(4,16,bias=False)
        def forward(self,input_ids,**kwargs):return SimpleNamespace(logits=self.lora(self.base(input_ids)))
    model=TinyLoRA();initial=model.lora.weight.detach().clone();frozen=model.base.weight.detach().clone()
    optimizer=torch.optim.AdamW(model.lora.parameters(),lr=1e-4,weight_decay=0.)
    assert not optimizer.state
    episodes=[{'episode_id':str(i),'turns':[dict(id=str(i),input_ids=[1,2,3,4],prompt_length=2,labels=[-100,-100,3,4])]} for i in range(16)]
    previous=None
    for step in range(1,5):
        metric=t.update(model,optimizer,episodes,'cpu')
        assert (metric['episodes'],metric['root_turns'],metric['target_tokens'])==(16,16,32)
        assert metric['mass_sum']==1. and {int(v['step']) for v in optimizer.state.values()}=={step}
        assert all(v['coefficient_fp32']==1/32 for v in metric['turn_losses'])
        # Actual optimizer/RNG state roundtrip; toy weights are not research model checkpoints.
        path=tmp_path/f'optimizer-{step}.pt';torch.save(optimizer.state_dict(),path)
        saved=torch.load(path,weights_only=True);assert {int(v['step']) for v in saved['state'].values()}=={step}
        assert saved['param_groups'][0]['lr']==1e-4
        current=s.sha(path);assert current!=previous;previous=current
    assert torch.equal(model.base.weight,frozen) and not torch.equal(model.lora.weight,initial)


def test_fixture_coordinate_has_trusted_context_id():
    import ast
    source=ast.parse((ROOT/'qualify.py').read_text())
    coordinates=[n for n in ast.walk(source) if isinstance(n,ast.Call) and isinstance(n.func,ast.Name) and n.func.id=='dict' and any(k.arg=='id' and isinstance(k.value,ast.Name) and k.value.id=='name' for k in n.keywords)]
    assert len(coordinates)==1 and 'context_window_id' in {k.arg for k in coordinates[0].keywords}


def test_actual_corrected_native_fixture_observations_and_target_masks():
    s=importlib.import_module('study');result=s.read(ROOT/'qualification-002/RESULT.json')
    assert result['status']=='PASS' and result['physical_cpu_provider_requests']==7 and not result['fake_provider_data_in_training']
    for arm in s.ARMS:
        path=ROOT/'qualification-002'/arm;raw=s.read(path/'EPISODE.json');trace=raw['traces'][0]
        tool=[n for n in trace['nodes'] if n['message'].get('role')=='tool']
        assert len(tool)==1 and tool[0]['message']['content']=='2\n'
        assert not tool[0]['sampled'] and not any(tool[0]['mask']) and tool[0]['logprobs']==[]
        rows=s.read(ROOT/'prepared-v2'/f'ROWS_{arm}.json');row=next(r for r in rows if r['id']=='train-00-single_user')
        target=row['input_ids'][row['prompt_length']:]
        assert sum([v for v,m in zip(n['token_ids'],n['mask']) if m]==target for n in trace['nodes'] if n['sampled'])==1
        audits=[s.read(p) for p in (path/'typed-audit').glob('*-result.json')]
        roots=sorted([a for a in audits if a['depth']==0],key=lambda a:a['started_epoch'])
        assert roots[0]['native_wire_request']['body']['token_ids']==row['input_ids'][:row['prompt_length']]
        assert all(not a['native_wire_request']['body']['sampling_params'].get('structured_outputs') for a in roots)
        child=[a for a in audits if a['depth']==1]
        assert len(child)==(2 if arm=='canonical' else 1)
        assert all(a['decision']['apply'] and a['native_wire_request']['body']['sampling_params']['structured_outputs']['json']==a['decision']['schema'] for a in child)
