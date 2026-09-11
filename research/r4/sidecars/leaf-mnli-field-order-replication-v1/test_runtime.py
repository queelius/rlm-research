import types


def test_owner_execution_uses_all_96_slots(tmp_path, monkeypatch):
    import owner
    s = owner.s
    monkeypatch.setenv("CUDA_VISIBLE_DEVICES", "fixture-assigned-mig")
    monkeypatch.setattr(s, "ATTEMPT", tmp_path / "attempt")
    monkeypatch.setattr(s, "verify", lambda: {"identity": "fixture"})
    original_read = s.read
    monkeypatch.setattr(s, "read", lambda path: owner.p.plan() if str(path).endswith("PLAN.json") else original_read(path))
    monkeypatch.setattr(owner.module, "credential", lambda: {})
    monkeypatch.setattr(owner.module, "binding", lambda: {})
    calls = []
    def command(stage, label, argv, cap, deadline):
        calls.append(argv)
        s.write(s.ATTEMPT / "rollout/STATUS.json", {"planned": 96, "recorded": 96})
    runner = types.SimpleNamespace(start_service=lambda *args: None, command=command, release_service=lambda *args: None)
    monkeypatch.setattr(owner.module, "suite", lambda: runner)
    result = owner.execute(s.ATTEMPT)
    assert result["complete"] and result["planned"] == 96
    assert len(original_read(s.ATTEMPT / "PLANNED_NULL_ENDPOINTS.json")) == 96
    assert len(calls) == 1


def test_collector_summary_preserves_six_arms_and_context_unit():
    import collect,protocol as p
    rows=[]
    for coordinate in p.plan():
        rows.append({"coordinate":coordinate,"physical_attempt":False,"score":p.null_row(coordinate,"fixture")})
    result=collect.summarize(rows)
    assert set(result["arms"])==set(p.ARMS)
    assert all(cell["planned"]==16 and cell["null"]==16 for cell in result["arms"].values())
    assert result["cluster_unit"]=="16 fresh paired contexts; no label/seed independence"


def test_seal_uses_existing_field_order_ready_as_parent():
    import prepare
    assert prepare.parent_ready().name=="READY_v2.json"
    assert prepare.parent_ready().parent==prepare.s.FIELD_ORDER
    assert prepare.parent_ready().exists()
