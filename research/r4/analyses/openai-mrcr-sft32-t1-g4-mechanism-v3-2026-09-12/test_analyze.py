import analyze as a


def test_v3_binding_reaches_actual_collector_and_role_hook():
    source = a.verify_source()
    collector = a.bindings()
    schedule = collector.study.schedule("train")
    assert source["output"].endswith("outputs/attempt-003")
    assert source["collector_entry"].endswith("collect_v3.py")
    assert len(schedule) == 32
    assert [row["seed"] for row in schedule] == list(range(202609200000, 202609200032))
    assert {row["temperature"] for row in schedule} == {1.0}
    assert collector.role_hooks() is not None
    assert collector.hooks.qualify()["condition"] == "terminal-strip-disabled"


def test_incomplete_terminal_is_not_misreported_as_science(monkeypatch):
    monkeypatch.setattr(a.core, "build", lambda: {"status": "PENDING"})
    assert a.build() == {"status": "PENDING"}
