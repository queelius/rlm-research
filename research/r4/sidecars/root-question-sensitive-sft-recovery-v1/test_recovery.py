from pathlib import Path
from types import SimpleNamespace


def test_frozen_boundary_has_65_reuse_one_explicit_retry_and_six_first_attempts():
    import recovery_study as s

    rows = s.capture_boundary()
    assert len(rows) == 72
    assert [r["disposition"] for r in rows[:65]] == ["reuse_authenticated_teacher"] * 65
    assert rows[65]["disposition"] == "retry_after_pre_request_deadline_failure"
    assert rows[65]["original_physical_records"] == 0
    assert [r["disposition"] for r in rows[66:]] == ["first_attempt_after_original_unstarted"] * 6
    assert s.missing_indices(rows) == list(range(65, 72))


def test_collector_cli_is_exact_missing_tail_only(tmp_path):
    import recovery_collect as c

    args = c.parse_args([
        "--binding", str(tmp_path / "BINDING.json"), "--endpoint", str(tmp_path / "endpoint.json"),
        "--output", str(tmp_path / "capture"), "--deadline", "2000000000",
    ])
    assert (args.mode, args.plan, args.start, args.stop) == ("capture", "TRAIN_PLAN.json", 65, 72)


def test_combined_corpus_never_duplicates_reused_teacher(tmp_path, monkeypatch):
    import recovery_study as s

    original = tmp_path / "original"; recovery = tmp_path / "recovery"
    monkeypatch.setattr(s, "ORIGINAL_ATTEMPT", original); monkeypatch.setattr(s, "ATTEMPT", recovery)
    plan = [{"id": f"id{i}"} for i in range(72)]
    monkeypatch.setattr(s, "train_plan", lambda: plan)
    for i, row in enumerate(plan):
        base = original if i < 65 else recovery
        s.write(base / "capture" / row["id"] / "physical" / "0001.json", {
            "origin": "actual c32", "physical_request_attempt": True,
        })
        s.write(base / "capture" / row["id"] / "TEACHER.json", {
            "episode_id": row["id"], "coordinate": row, "prefix_ids_verified": True,
            "actual_child_records": [str(base / "capture" / row["id"] / "physical" / "0001.json")],
            "masked_history_turns": [], "turns": {"first_producer": {}, "corrective": {}, "terminal": {}},
        })
        s.write(base / "capture" / row["id"] / "EPISODE.json", {"ok": True})
        for j in range(2, 5):
            s.write(base / "capture" / row["id"] / "physical" / f"{j:04}.json", {"origin": "authored"})
    monkeypatch.setattr(s.learning(), "validate_turn", lambda turn: None)
    monkeypatch.setattr(s, "capture_boundary", lambda: [
        {"index": i, "id": row["id"], "disposition":
         ("reuse_authenticated_teacher" if i < 65 else "retry_or_first")}
        for i, row in enumerate(plan)])
    monkeypatch.setattr(s, "verify", lambda: {"identity": "CPU"})
    corpus = s.build_corpus_ready()
    assert len(corpus) == 72
    receipt = s.read(recovery / "capture" / "CORPUS_READY.json")
    assert receipt["reused_original"] == 65 and receipt["new_recovery"] == 7
    assert len(receipt["files_sha256"]) == 216


def test_owner_runs_missing_capture_then_train_then_sft_only(tmp_path, monkeypatch):
    import recovery_owner as o
    import recovery_study as s

    output = tmp_path / "attempt"; calls = []
    class Suite:
        def start_service(self, stage, binding, deadline): calls.append(("start", stage.name))
        def release_service(self, stage): calls.append(("release", stage.name))
        def command(self, stage, label, argv, cap, deadline):
            calls.append(("command", label, tuple(argv)))
            if label == "capture-missing7":
                assert "--start" not in argv  # fixed inside recovery collector
                monkeypatch.setattr(s, "ATTEMPT", output); monkeypatch.setattr(s, "build_corpus_ready", lambda: [None] * 72)
            elif label == "six-updates":
                s.write(output / "training" / "SELECTION.json", {
                    "step": 6, "checkpoint": str(output / "training/checkpoint-0006"),
                    "adapter_sha256": "a", "config_sha256": "b",
                })
    monkeypatch.setenv("CUDA_VISIBLE_DEVICES", "CPU_INTERCEPT_ONLY")
    monkeypatch.setenv("STRICT_RLM_CALIBRATION_API_KEY", "CPU")
    monkeypatch.setattr(s, "ATTEMPT", output); monkeypatch.setattr(s, "verify", lambda: {"identity": "CPU"})
    monkeypatch.setattr(s, "runtime", lambda: None); monkeypatch.setattr(s, "baseline_reference", lambda: {"planned": 80})
    monkeypatch.setattr(o, "dependencies", lambda: Suite()); monkeypatch.setattr(o.b, "binding", lambda arm: {})
    monkeypatch.setattr(o.b, "selected", lambda arm: {"step": 6})
    monkeypatch.setattr(o, "capture_binding", lambda: {})
    monkeypatch.setattr(o, "harvest", lambda out, rows: rows)
    result = o.execute(output)
    labels = [x[1] for x in calls if x[0] == "command"]
    assert labels == ["capture-missing7", "six-updates", "dev8", "protected72"]
    assert not any("unchanged" in str(x) for x in calls)
    assert result["planned_readout"] == 80
