"""Catch wrong schedule/alias/setup or unrebound inner native collector."""
from pathlib import Path
import asyncio
import hashlib
import importlib

ROOT=Path(__file__).resolve().parent

def test_exact_training_inputs_and_real_environment_native_prefix():
    assert (ROOT/'study.py').exists(), 'training readout is not implemented'
    s=importlib.import_module('study');c=importlib.import_module('collect')
    cp=importlib.import_module('checkpoint')
    plan=s.schedule('train');assert len(plan)==32 and len({r['record_id'] for r in plan})==8
    assert plan==s.screen.schedule('train')
    assert sorted(r['seed'] for r in plan)==list(range(202609250000,202609250032))
    saved={s.read(p)['coordinate']['id']:s.read(p) for p in (s.BASELINE/'science/episodes').glob('*.json')}
    assert set(saved)=={r['id'] for r in plan}
    assert all(saved[r['id']]['coordinate']==r for r in plan)
    env=s.environment('train');tasks=list(env.taskset)
    assert {t.data.name for t in tasks}==set(saved)
    class Runtime:
        def __init__(self):self.files={}
        async def write(self,path,data):self.files[path]=data
        async def read(self,path):return self.files[path]
    async def setup():
        for task in tasks:
            rt=Runtime();await task.setup(None,rt)
            assert hashlib.sha256(rt.files['/context.json']).hexdigest()==task.data.document_sha256
    asyncio.run(setup())
    prefixes=s.read(s.input_dir('train')/'PREFIXES.json')
    for row in plan:
        endpoint={'model_alias':s.ADAPTED_ALIAS,'host':'127.0.0.1','port':1,
                  'api_key_env':'FIXTURE_KEY','base_model':{'path':str(s.BASE)}}
        sampling=c.source.model_context(endpoint,row).sampling.model_dump(mode='json')
        assert sampling['temperature']==.5 and sampling['seed']==row['seed'] and sampling['max_tokens']==2048
        assert prefixes[row['id']]['token_ids']
    assert c.source.study is s and c.source.checkpoint is cp
    assert c.source.verify_ready is c.verify_ready
    assert cp.binding('updated')['role_map']['root']==s.ADAPTED_ALIAS
    assert cp.verify_checkpoint()==s.read(s.PRIOR/'CHECKPOINT_QUALIFICATION.json')
