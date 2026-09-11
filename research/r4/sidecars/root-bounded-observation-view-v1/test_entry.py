import sys
from pathlib import Path


def test_exact_collector_cli_and_all_null_inventory(monkeypatch, tmp_path):
    import bv_collect as c
    import bv_owner as o
    import bv_study as s

    argv = o.collector_argv(Path("/CPU/stage"), tmp_path / "free", 123.0)
    module = c.implementation()
    args = module.parse_args(argv[2:])
    assert (args.mode, args.plan, args.start, args.stop) == ("free", "FREE_PLAN.json", 0, 32)
    async def fake_run(args):
        import od_study, od_binding
        assert od_study is s and od_binding is s
    monkeypatch.setattr(module, "run", fake_run)
    monkeypatch.setattr(sys, "argv", argv[1:])
    c.main()
    inventory = o.harvest(tmp_path, s.read(s.ROOT / "inputs/EVALUATION_PLAN.json"))
    assert len(inventory) == 32
    assert all(r["reward"] is None and r["cause"] == "not_started_no_artifacts" for r in inventory)


def test_owner_declares_safe_shared_clock_and_release():
    import inspect
    import bv_owner as o

    source = inspect.getsource(o.execute)
    assert "started+1650" in source and "started+1770" in source
    assert "time.time()+120" in source
    assert "remaining(work-30,1440)" in source

