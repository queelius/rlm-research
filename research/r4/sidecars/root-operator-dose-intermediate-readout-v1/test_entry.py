import asyncio
import sys

import id_collect as collect
import id_owner as owner
import id_probe as probe
import id_study as s


def test_actual_owner_to_collector_entry_uses_new_namespace(tmp_path, monkeypatch):
    stage = tmp_path / "service-sft18"; destination = tmp_path / "sft18/free"
    argv = owner.collector_argv("sft18", stage, destination, 1234.5)
    args = collect.parse_args(argv[2:])
    assert (args.plan, args.start, args.stop, args.mode, args.output) == ("FREE_PLAN_sft18.json", 0, 16, "free", destination)
    module = collect.implementation(); seen = []
    async def fake_run(actual):
        import od_binding
        import od_protocol
        import od_study
        assert module.s is s
        assert od_study is s and od_binding is s and od_protocol is s.protocol()
        assert actual.plan == "FREE_PLAN_sft18.json"
        seen.append(actual)
    monkeypatch.setattr(module, "run", fake_run)
    collect.main(argv[2:])
    assert len(seen) == 1


def test_probe_entry_uses_all12_new_seed_requests(tmp_path, monkeypatch):
    stage = tmp_path / "service-sft12"; destination = tmp_path / "sft12/probes"
    argv = owner.probe_argv(stage, destination, 2345.0)
    args = probe.parse_args(argv[2:])
    assert (args.output, args.deadline) == (destination, 2345.0)
    module = probe.implementation(); seen = []
    async def fake_run(actual):
        assert module.s is s
        assert len(s.read(s.ROOT / "inputs/TEACHER_DIAGNOSTIC_PLAN.json")) == 12
        seen.append(actual)
    monkeypatch.setattr(module, "run", fake_run)
    probe.main(argv[2:])
    assert len(seen) == 1
