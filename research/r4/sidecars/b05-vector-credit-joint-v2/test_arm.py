"""Focused actual response-joint V2 entry regressions."""

import os
import study


def test_actual_preflight_and_cpu_guard(monkeypatch):
    import train
    ready, rows = train.preflight()
    assert ready["credit_mode"] == "joint" and len(rows) == 64
    assert isinstance(rows[0]["reward"], list) and isinstance(rows[0]["advantage"], list)
    monkeypatch.setenv("CUDA_VISIBLE_DEVICES", "")
    try: train.trainer.run(study, study.OUTPUT, study.SCIENCE_SECONDS)
    except RuntimeError as error: assert str(error) == "CPU_ENTRY_VERIFIED: MAIN must assign one GPU before training"
    else: raise AssertionError("CPU training guard absent")
    assert not study.OUTPUT.exists() and os.environ["CUDA_VISIBLE_DEVICES"] == ""
