"""Actual Prime server-argument boundary, without executing inference."""
import importlib
import json

import study


def test_actual_prime_worker_registry_overrides_config_and_repaired_entrypoint(monkeypatch):
    from prime_rl.configs.inference import InferenceConfig
    server = importlib.import_module('prime_rl.inference.vllm.server')
    api = importlib.import_module('vllm.entrypoints.openai.api_server')
    entry = study.load('report_v2_actual_entry_fixture', study.ROOT / 'engine_entry_v2.py')
    config = InferenceConfig.model_validate(study.read(study.ATTEMPT / 'RUNTIME.json'))
    captured = []
    async def no_model(args): captured.append(args.worker_extension_cls)
    monkeypatch.setattr(api, 'run_server', no_model)
    # This is the real server(config), real namespace/argument validation and
    # original hardcoded assignment. Only its final GPU server launch is stubbed.
    server.server(config)
    assert captured == [entry.EXPECTED]
    monkeypatch.setitem(server.WORKER_EXTENSION_CLS, 'filesystem', entry.EXPECTED)
    entry.install_registry()
    server.server(config)
    assert captured == [entry.EXPECTED, entry.TARGET]


def test_repaired_owner_defers_actual_dispatch_and_preserves_science():
    import owner_v2
    module = owner_v2.implementation()
    assert module.study.ATTEMPT.name == 'attempt-002'
    assert module.collect.study.schedule() == study.schedule()
    assert module.metrics.study.selected() == study.selected()
    assert module.study.OWNER_SECONDS == 1700 and module.study.SCIENCE_SECONDS == 1320
    assert 'ACTUAL_DISPATCH.json' not in module.execute.__code__.co_consts
    wrapper = study.load('report_v2_wrapper_fixture', study.ROOT / 'service_wrapper_v2.py')
    built = wrapper.build(study.ROOT / 'NEVER_CREATED_CPU_FIXTURE')
    assert 'engine_entry_v2.py' in built.main.__code__.co_consts
    assert json.loads(json.dumps(study.schedule())) == module.study.schedule()
