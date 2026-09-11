"""Owner composition only; external service/process boundaries never launch."""
import importlib.util
from pathlib import Path

import pytest


def owner():
    path = Path(__file__).with_name('owner.py')
    assert path.exists(), 'owner wrapper missing'
    spec = importlib.util.spec_from_file_location('diagnostic_owner_test', path)
    value = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(value)
    return value


def test_missing_credential_does_not_create_output(tmp_path, monkeypatch):
    value = owner()
    output = tmp_path / 'attempt-001'
    monkeypatch.delenv('STRICT_RLM_CALIBRATION_API_KEY', raising=False)
    monkeypatch.setattr(value, 'ATTEMPT', output)
    with pytest.raises(ValueError, match='STRICT_RLM_CALIBRATION_API_KEY'):
        value.execute(output)
    assert not output.exists()


@pytest.mark.parametrize('collector_failure', [False, True])
def test_shared_deadline_exact_commands_and_release_on_collector_failure(tmp_path, monkeypatch, collector_failure):
    value = owner()
    output = tmp_path / 'attempt-001'
    events = []

    class Suite:
        def start_service(self, directory, binding, deadline):
            events.append(('start', directory, binding, deadline))

        def command(self, directory, label, argv, cap, deadline):
            events.append(('command', directory, label, argv, cap, deadline))
            if collector_failure:
                raise RuntimeError('controlled collector failure')
            value.s.write(output / 'rollout/TERMINAL.json', {'planned': 96, 'recorded': 96, 'available': 95})

        def release_service(self, directory):
            events.append(('release', directory))

    monkeypatch.setenv('STRICT_RLM_CALIBRATION_API_KEY', 'cpu-fixture-value-not-production')
    monkeypatch.setenv('CUDA_VISIBLE_DEVICES', '0')
    monkeypatch.setattr(value, 'ATTEMPT', output)
    monkeypatch.setattr(value, 'verify', lambda: {'identity': 'cpu-owner', 'scientific_ready_sha256': 'fixture'})
    monkeypatch.setattr(value, 'dependencies', lambda: Suite())
    monkeypatch.setattr(value, 'runtime_preflight', lambda: None)
    monkeypatch.setattr(value.time, 'time', lambda: 1000.0)
    monkeypatch.setattr(value.signal, 'signal', lambda *args: None)
    monkeypatch.setattr(value.signal, 'setitimer', lambda *args: None)
    result = value.execute(output)
    assert [event[0] for event in events] == ['start', 'command', 'release']
    start, command, release = events
    assert start[3] == 1180.0
    assert command[4:] == (1650, 2650.0)
    argv = command[3]
    assert argv[1] == str(value.s.ROOT / 'collect.py')
    assert argv[argv.index('--output') + 1] == str(output / 'rollout')
    assert argv[argv.index('--deadline') + 1] == '2650.0'
    assert argv[argv.index('--endpoint') + 1] == str(output / 'owned-service/service/endpoint-original.json')
    assert 'cpu-fixture-value-not-production' not in repr(argv)
    assert result['complete'] is (not collector_failure)
    assert result['released'] is True
    assert result['work_deadline_epoch'] == 2650.0
    assert result['owned_deadline_epoch'] == 2770.0


def test_actual_owner_collector_expired_deadline_retains96_nulls_and_releases(tmp_path, monkeypatch):
    """Actual collector/CLI composition; only service/network/native-runtime boundaries are fake."""
    import asyncio
    import contextlib
    from types import SimpleNamespace
    import httpx
    import collect
    import runtime_binding
    import verifiers.v1.envs.single_agent as native_env

    value = owner()
    output = tmp_path / 'attempt-001'
    binding = value.s.read(value.s.ROOT / 'inputs/BINDING.json')
    descriptor = dict(host='cpu-fixture', port=1, api_key_env='STRICT_RLM_CALIBRATION_API_KEY', base_model={'path':'/cpu/base'})
    class Client:
        def __init__(self, **kwargs): pass
        async def __aenter__(self): return self
        async def __aexit__(self, *args): pass
        async def get(self, url):
            return SimpleNamespace(raise_for_status=lambda:None, json=lambda:dict(data=[dict(id=k,root=m['path'],parent='/cpu/base') for k,m in binding['models'].items()]))
    class Env:
        def __init__(self, config): pass
        @contextlib.asynccontextmanager
        async def serving(self): yield self
        async def run_slot(self, *args): raise AssertionError('expired deadline must not submit a native request')
    events=[]
    class Suite:
        def start_service(self, stage, actual_binding, deadline):
            assert actual_binding==binding
            value.s.write(stage/'BINDING.json',binding)
            value.s.write(stage/'service/endpoint-original.json',descriptor)
        def command(self, stage, label, argv, cap, deadline):
            assert cap==1650 and deadline==2650.0
            args=collect.parse_args(argv[2:])
            assert args.output==output/'rollout' and args.deadline==2650.0
            assert asyncio.run(collect.collect(args))==0
        def release_service(self, stage): events.append('released')
    monkeypatch.setenv('STRICT_RLM_CALIBRATION_API_KEY','cpu-fixture-value-not-production')
    monkeypatch.setenv('CUDA_VISIBLE_DEVICES','0')
    monkeypatch.setattr(value,'ATTEMPT',output)
    monkeypatch.setattr(value,'verify',lambda:dict(identity='cpu',scientific_ready_sha256='fixture'))
    monkeypatch.setattr(value,'runtime_preflight',lambda:None)
    monkeypatch.setattr(value,'dependencies',lambda:Suite())
    monkeypatch.setattr(value,'time',SimpleNamespace(time=lambda:1000.0))
    monkeypatch.setattr(value.signal,'signal',lambda *args:None)
    monkeypatch.setattr(value.signal,'setitimer',lambda *args:None)
    monkeypatch.setattr(collect.s,'verify',lambda:dict(identity='cpu'))
    monkeypatch.setattr(collect.s,'source',lambda:SimpleNamespace(plan=SimpleNamespace(old=None,private=lambda *args,**kwargs:SimpleNamespace(validate_descriptor=lambda *args:None))))
    interface=SimpleNamespace(installed=lambda *args:contextlib.nullcontext(),e=SimpleNamespace(environment_config=lambda:{}))
    monkeypatch.setattr(collect.s,'interface',lambda *args:interface)
    monkeypatch.setattr(collect,'endpoint',lambda *args:{})
    monkeypatch.setattr(runtime_binding,'adapt',lambda:None)
    monkeypatch.setattr(httpx,'AsyncClient',Client)
    monkeypatch.setattr(native_env,'SingleAgentEnv',Env)
    monkeypatch.setattr(native_env,'SingleAgentEnvConfig',SimpleNamespace(model_validate=lambda value:value))
    result=value.execute(output)
    assert result['complete'] and result['released'] and events==['released']
    terminal=value.s.read(output/'rollout/TERMINAL.json')
    assert terminal['planned']==terminal['recorded']==96 and terminal['available']==0
    rows=[value.s.read(p) for p in (output/'rollout/readout/rows').glob('*.json')]
    assert len(rows)==96 and all(r['reward'] is None and r['cost']['new_physical']['calls']==0 for r in rows)
    assert all(r['cost']['reused_acquisition']['calls']==1 for r in rows)
