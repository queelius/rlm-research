import hashlib
import json
from pathlib import Path

import collect
import owner
import protocol
import study


ROOT = Path(__file__).resolve().parent


def test_owner_argv_targets_attempt002_local_collector(tmp_path):
    stage = study.ATTEMPT / "owned-service"
    argv = owner.collector_argv(stage, study.ATTEMPT, 12345.0)
    parsed = owner.validate_argv(argv)
    assert argv[1] == str(ROOT / "collect.py")
    assert parsed["output"] == study.ATTEMPT / "rollout"
    assert parsed["endpoint"] == stage / "service/endpoint-original.json"
    assert parsed["deadline"] == 12345.0


def test_actual_collector_module_has_96_row_entry():
    rows = protocol.plan()
    assert len(rows) == 96
    assert callable(collect.run)
    assert callable(collect.summarize)
    nulls = [protocol.null_row(row, "fixture") for row in rows]
    summary = collect.summarize(
        [{"coordinate": row, "physical_attempt": False, "score": null} for row, null in zip(rows, nulls)]
    )
    assert all(cell["planned"] == 16 for cell in summary["arms"].values())


def test_ready_preserves_scientific_inputs_and_records_zero_science_failure():
    ready = json.loads((ROOT / "READY.json").read_text())
    prior = json.loads((study.ORIGINAL / "READY.json").read_text())
    assert ready["scientific_inputs_identity"] == prior["identity"]
    assert ready["attempt001"]["physical_requests"] == 0
    assert ready["attempt001"]["released"] is True
    for name, expected in ready["scientific_input_sha256"].items():
        assert hashlib.sha256((ROOT / name).read_bytes()).hexdigest() == expected

