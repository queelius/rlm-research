import hashlib
import json
from pathlib import Path

import owner
import study


ROOT = Path(__file__).resolve().parent


def test_owner_wrapper_argv_uses_attempt002_and_local_collector():
    stage = study.ATTEMPT / "service-sft6"
    argv = owner.collector_argv(stage, "sft6", study.ATTEMPT / "sft6/free", 1234.0)
    assert argv[0] == str(study.NATIVE)
    assert argv[1] == str(ROOT / "collect.py")
    assert argv[argv.index("--plan") + 1] == "FREE_PLAN_SFT6.json"
    assert argv[argv.index("--stop") + 1] == "32"
    assert Path(argv[argv.index("--output") + 1]) == study.ATTEMPT / "sft6/free"


def test_ready_preserves_all_scientific_inputs_and_zero_outcomes():
    ready = json.loads((ROOT / "READY.json").read_text())
    prior = json.loads((study.ORIGINAL / "READY_v3.json").read_text())
    assert ready["scientific_inputs_identity"] == prior["identity"]
    assert ready["attempt001"]["physical_requests"] == 0
    assert ready["attempt001"]["scientific_outcomes"] == 0
    assert ready["attempt001"]["released"] is True
    for path, expected in ready["input_sha256"].items():
        assert hashlib.sha256(Path(path).read_bytes()).hexdigest() == expected


def test_ready_v2_seals_nonempty_free_transport_qualification():
    ready = json.loads((ROOT / "READY_v2.json").read_text())
    result = json.loads((ROOT / "qualification-transport-attempt-001/RESULT.json").read_text())
    assert ready["qualification"]["result_sha256"] == hashlib.sha256(
        (ROOT / "qualification-transport-attempt-001/RESULT.json").read_bytes()
    ).hexdigest()
    assert result["status"] == "PASS"
    assert result["mode"] == "free"
    assert result["root_calls"] == 2 and result["child_calls"] == 1
    assert result["bounded_view_clipped"] and result["strict_scalar_correct"]
    assert result["actual_model_calls"] == result["gpu_calls"] == 0
