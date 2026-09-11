def test_actual_owner_anchors_protected_deadline_to_readout_service_after_dev_failure(tmp_path, monkeypatch):
    import recovery_owner_v4 as o
    import recovery_study_v3 as s

    class Clock:
        now = 1000.0
        def time(self): return self.now
        def advance(self, seconds): self.now += seconds
    clock = Clock(); protected = []
    class Suite:
        def start_service(self, stage, binding, deadline):
            clock.advance(30 if stage.name == "service-sft6" else 20)
        def release_service(self, stage): pass
        def command(self, stage, label, argv, cap, deadline):
            if label == "capture-missing7":
                clock.advance(100)
            elif label == "six-updates":
                clock.advance(500)
                s.write(output / "training/SELECTION.json", {"step": 6,
                    "checkpoint": str(output / "training/checkpoint-0006"),
                    "adapter_sha256": "a", "config_sha256": "b"})
            elif label == "dev8":
                clock.advance(40); raise RuntimeError("retained dev failure")
            elif label == "protected72": protected.append(deadline)
    output = tmp_path / "attempt"
    monkeypatch.setenv("CUDA_VISIBLE_DEVICES", "CPU_INTERCEPT_ONLY")
    monkeypatch.setenv("STRICT_RLM_CALIBRATION_API_KEY", "CPU")
    monkeypatch.setattr(s, "ATTEMPT", output); monkeypatch.setattr(o.implementation.s, "ATTEMPT", output)
    monkeypatch.setattr(o.implementation.time, "time", clock.time)
    monkeypatch.setattr(o.implementation, "alarm", lambda deadline: None)
    monkeypatch.setattr(o.implementation.s, "runtime", lambda: None)
    monkeypatch.setattr(o.implementation.s, "verify", lambda: {"identity": "V4"})
    monkeypatch.setattr(o.implementation.s, "baseline_reference", lambda: {"planned": 80})
    monkeypatch.setattr(o.implementation.s, "capture_boundary", lambda: [])
    monkeypatch.setattr(o.implementation.s, "build_corpus_ready", lambda: [None] * 72)
    monkeypatch.setattr(o.implementation, "dependencies", lambda: Suite())
    monkeypatch.setattr(o.implementation, "capture_binding", lambda: {})
    monkeypatch.setattr(o.implementation.b, "selected", lambda arm: {"step": 6})
    monkeypatch.setattr(o.implementation.b, "binding", lambda arm: {})
    monkeypatch.setattr(o.implementation, "harvest", lambda output, rows: rows)
    monkeypatch.setattr(o.implementation, "cost_ledger", lambda output: {})
    result = o.implementation.execute(output)
    # readout service began at1620; dev consumed40 after30 startup.
    assert protected == [1620 + 1950 + 40 - 90]
    assert any(e["stage"] == "sft6-dev" for e in result["error"])
