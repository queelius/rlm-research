import hashlib
import importlib.util
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parent


def load(name):
    path = ROOT / f"{name}.py"
    assert path.exists(), f"missing repaired module: {path.name}"
    spec = importlib.util.spec_from_file_location(f"fresh_qualification_v2_{name}", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_runtime_schedule_restores_original_requested_property_order():
    study = load("study")
    rows = study.schedule()
    assert len(rows) == 48
    assert [row["seed"] for row in rows] == list(range(202609121300, 202609121348))
    assert all(
        list(row["body"]["sampling_params"]["structured_outputs"]["json"]["properties"])
        == row["requested_ids"]
        for row in rows
    )


def test_saved_native_fixture_decodes_exact_action_ids_without_choice_text():
    study = load("study")
    collect = load("collect")
    request_path = study.V1_ATTEMPT / "native/19d69f810a1aff4702a7109de1934dbc9441cac72b2d7e8d8ab8b729017e304a-REQUEST.json"
    response_path = study.V1_ATTEMPT / "native/19d69f810a1aff4702a7109de1934dbc9441cac72b2d7e8d8ab8b729017e304a-RESPONSE.json"
    assert study.sha(request_path) == "8ade0a448819cad654684056f26ed62f4b54ffc2fa0da76c5330f195cb83afd1"
    assert study.sha(response_path) == "d968398b71a3a863d66555a7d4c4aed9cffee0f9e1bd64fc1364f08f03112bfe"
    body, response = study.read(request_path), study.read(response_path)
    assert "text" not in response["choices"][0]
    requested = list(body["sampling_params"]["structured_outputs"]["json"]["properties"])
    row = {
        "coordinate_id": "actual-v1-fixture",
        "context_id": "question-sensitive-sft-train-05",
        "repeat": 0,
        "seed": 202609121300,
        "requested_ids": requested,
        "schema_ordered_json": json.dumps(body["sampling_params"]["structured_outputs"]["json"]),
        "schema_ordered_sha256": "fixture-only",
        "body": body,
    }
    record = collect.response_record(
        row, response, collect.tokenizer(), 1.0, 2.0, study.read(study.HOST_GOLD)
    )
    assert record["action_ids"] == response["choices"][0]["token_ids"]
    assert len(record["prediction"]) == 16
    assert hashlib.sha256(record["decoded_text"].encode()).hexdigest() == (
        "68864d19b2c8b2be1187bc7dc0f8dd428036cab44b62a66235e535a8badf19ff"
    )
