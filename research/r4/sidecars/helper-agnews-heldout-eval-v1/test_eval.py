import importlib.util
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parent


def load(name):
    spec = importlib.util.spec_from_file_location(name, ROOT / f"{name}.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_builder_covers_frozen_heldout_once_with_standard_ag_schema():
    builder = load("prepare_eval")
    bundle = builder.make_inputs()
    assert len(bundle["requests"]) == 64
    ids = [identifier for row in bundle["requests"] for identifier in row["ids"]]
    assert len(ids) == len(set(ids)) == 256
    for row in bundle["requests"]:
        schema = json.loads(row["schema_ordered_json"])
        assert list(schema["properties"]) == row["ids"] == schema["required"]
        assert "Classify the primary topic of each news item" in row["request_text"]
        assert "Classify the type of answer requested" not in row["request_text"]


def test_schedule_restores_ordered_schema_and_exact_inventory():
    study = load("study")
    rows = study.schedule()
    assert len(rows) == 64
    assert len({identifier for row in rows for identifier in row["ids"]}) == 256
    assert all(row["body"]["sampling_params"]["temperature"] == 0.0 for row in rows)


def test_new_ag_arm_requires_exact_completed_step4(tmp_path):
    study = load("study")
    output = tmp_path / "attempt"
    output.mkdir()
    good = {
        "status": "COMPLETED_FOUR_UPDATES",
        "completed_optimizer_steps": 4,
        "primary_checkpoint_available": True,
        "primary_checkpoint_step": 4,
        "primary_checkpoint": str(output / "checkpoint-0004"),
        "checkpoints": [
            {"step": step, "checkpoint": str(output / f"checkpoint-{step:04d}")}
            for step in range(1, 5)
        ],
    }
    assert study.validate_training_result(good, output) == output / "checkpoint-0004"
    bad = dict(good, completed_optimizer_steps=3)
    try:
        study.validate_training_result(bad, output)
    except ValueError:
        pass
    else:
        raise AssertionError("incomplete AG training was admitted")


def test_actual_collector_dependency_builds_without_gpu_service(monkeypatch):
    monkeypatch.setenv("STRICT_RLM_CALIBRATION_API_KEY", "cpu-test-placeholder")
    study = load("study")
    suite = study.dependencies()
    assert callable(suite.start_service)
    assert callable(suite.release_service)
    import sys

    sys.path.insert(0, str(ROOT))
    try:
        owner = load("owner")
        collector = owner.collector("c32")
    finally:
        sys.path.pop(0)
    assert callable(collector.execute)
    assert callable(collector.send)
