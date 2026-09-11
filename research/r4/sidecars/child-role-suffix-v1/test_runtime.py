"""Focused contract regressions; all fixtures are operator-authored CPU code."""
import asyncio
import ast
from pathlib import Path
from types import SimpleNamespace
import pytest


def runtime():
    # Preparation RED: missing implementation is an explicit missing-contract failure.
    assert (Path(__file__).parent / 'runtime.py').exists(), 'suffix runtime not implemented'
    import runtime as r
    return r


def test_real_message_construction_keeps_root_and_tools_changes_child_once():
    r = runtime()
    original = r.role.NANO_SOURCE.read_text()
    assert r.patch_engine(original, 'control') == r.role.patch_engine(original)
    changed = r.patch_engine(original, 'child_role_suffix')
    tree = ast.parse(changed)
    cls = next(n for n in tree.body if isinstance(n, ast.ClassDef) and n.name == 'RLMEngine')
    start = next(n for n in cls.body if isinstance(n, ast.AsyncFunctionDef) and n.name == '_start')
    # Execute only the actual message construction nodes, not the runtime or model code.
    block = next(n.body for n in ast.walk(start) if isinstance(n,ast.Try)
                 and any(isinstance(x,ast.Assign) and any(isinstance(t,ast.Name) and t.id=='system_prompt' for t in x.targets) for x in n.body))
    begin = next(i for i,n in enumerate(block) if isinstance(n,ast.Assign)
                 and any(isinstance(t,ast.Name) and t.id=='system_prompt' for t in n.targets))
    end = next(i for i,n in enumerate(block) if isinstance(n,ast.Assign)
               and any(isinstance(t,ast.Attribute) and t.attr=='_messages' for t in n.targets))
    for depth in (0,1,2):
        self = SimpleNamespace(runtime_config=SimpleNamespace(invocation=SimpleNamespace(depth=depth)),
            _active_tools=['unchanged'], _load_system_prompt=lambda tools:'Original coding system')
        scope = {'self':self, 'prompt':'Return the answer types only.'}
        exec(compile(ast.Module(body=block[begin:end+1],type_ignores=[]),'trusted_message_fixture','exec'),scope)
        expected = 'Original coding system' + ('\n\n'+r.SUFFIX if depth==1 else '')
        assert self._messages == [{'role':'system','content':expected},
                                  {'role':'user','content':'Return the answer types only.'}]
        assert self._active_tools == ['unchanged']
    with pytest.raises(ValueError): r.patch_engine(changed,'child_role_suffix')
    with pytest.raises(ValueError): r.patch_engine(original+'\n','control')


def test_concurrent_coordinate_isolation_and_reset():
    r = runtime()
    async def exercise():
        async def setup():
            first = dict(r.COORDINATE.get())
            await asyncio.sleep(.01)
            assert r.COORDINATE.get() == first
            return first['arm']
        assert await asyncio.gather(*[r.run_coordinate({'arm':arm,'id':arm},setup)
            for arm in ('control','child_role_suffix')]) == ['control','child_role_suffix']
        assert r.COORDINATE.get() is None
        async def failure(): raise RuntimeError('fixture')
        with pytest.raises(RuntimeError): await r.run_coordinate({'arm':'control','id':'failed'},failure)
        assert r.COORDINATE.get() is None
    asyncio.run(exercise())


def test_dispatch_ceiling_does_not_invent_sent_or_sampled_requests(tmp_path):
    r = runtime()
    guard=r.DispatchBudget(tmp_path,2)
    for i in range(2): guard.before_dispatch({'request_id':str(i),'depth':1})
    with pytest.raises(r.DispatchPrevented): guard.before_dispatch({'request_id':'denied','depth':1})
    assert guard.sent==2 and guard.prevented==1 and guard.exhausted.is_set()
    rows=[r.read(p) for p in sorted(tmp_path.glob('*.json'))]
    assert [x['dispatch_attempted'] for x in rows]==[True,True,False]
    assert all(x['sampled_completion'] is None for x in rows)


def test_observable_recovered_error_is_not_null_and_empty_not_repaired():
    r=runtime()
    wrong={'ok':True,'answer':'Answer: 99','reward':0}
    assert r.outcome_state(wrong,False,True)['observable_reward']==0
    assert r.outcome_state(wrong,False,True)['recovered_provider_error']
    assert r.outcome_state({'ok':True,'answer':'','reward':0},False,False)['empty_final']
    assert r.outcome_state(wrong,True,True)['observable_reward'] is None
    assert r.outcome_state({'ok':False,'answer':None,'reward':None},False,True)['observable_reward'] is None
