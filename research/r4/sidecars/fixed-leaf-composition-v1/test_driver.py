import asyncio
import importlib.util
import json
from copy import deepcopy
from pathlib import Path

import httpx
import pytest

ROOT = Path(__file__).resolve().parent
loader = importlib.util.spec_from_file_location("fixed_composition_driver", ROOT / "driver.py")
driver = importlib.util.module_from_spec(loader)
loader.loader.exec_module(driver)


def data_fixture():
    contexts, tasks, coordinates = [], [], []
    for context_index in range(6):
        records = [
            {
                "question": f"Question {context_index}-{i}?",
                "group_id": f"g{context_index}-{i}",
                "gold": driver.leaf.LABELS[i % 6],
                "source_line_1based": i + 1,
            }
            for i in range(64)
        ]
        cid = f"context-{context_index}"
        contexts.append(
            {"id": cid, "records": records, "group_ids": [r["group_id"] for r in records]}
        )
        for label in ["human being", "numeric value"]:
            name = f"{cid}-{label}"
            tasks.append(
                {
                    "name": name,
                    "context_id": cid,
                    "label": label,
                    "answer": repr([sum(r["gold"] == label for r in records)]),
                }
            )
            for repeat in range(2):
                for arm in ["original_child", "sft_child"]:
                    coordinates.append(
                        {
                            "id": f"{name}-{repeat}-{arm}",
                            "pair_id": f"{name}-{repeat}",
                            "context_window_id": context_index,
                            "task_name": name,
                            "arm": arm,
                            "repeat": repeat,
                            "seed": 100 + repeat,
                            "temperature": 0.5,
                            "dispatch_order": len(coordinates),
                        }
                    )
    return {"contexts": contexts, "tasks": tasks, "plan": coordinates}


def design_fixture():
    data = data_fixture()
    design = driver.layout_from_data(data)
    design.update(
        contract=json.loads(driver.CONTRACT.read_text()),
        definitions=driver.leaf.DEFINITIONS,
        labels=list(driver.leaf.LABELS),
        max_tokens=256,
        max_concurrent_calls=4,
        call_timeout_seconds=30,
        wall_time_cap_seconds=900,
    )
    return design


def records_for_coordinate(design, coordinate):
    rows = [r for r in design["plan"] if r["coordinate_id"] == coordinate["id"]]
    return [
        {
            "coordinate": row,
            "score": driver.leaf.score_labels(
                json.dumps(design["batches"][row["batch_id"]]["gold"]),
                design["batches"][row["batch_id"]]["gold"],
            ),
            "usage": {},
            "finish_reason": "stop",
        }
        for row in rows
    ]


def test_layout_preserves_all_coordinates_and_624_source_order_calls():
    data = data_fixture()
    design = driver.layout_from_data(data)
    assert design["coordinates"] == data["plan"]
    assert len(design["plan"]) == 624
    assert len({r["id"] for r in design["plan"]}) == 624
    first = data["plan"][0]
    calls = [r for r in design["plan"] if r["coordinate_id"] == first["id"]]
    assert len(calls) == 13 and {r["seed"] for r in calls} == {first["seed"]}
    assert [len(design["batches"][r["batch_id"]]["questions"]) for r in calls] == [5] * 12 + [4]
    assert [i for r in calls for i in design["batches"][r["batch_id"]]["record_indices"]] == list(
        range(1, 65)
    )


def test_request_is_exact_old_definitions_contract_and_gold_independent():
    design = design_fixture()
    row = design["plan"][0]
    request = driver.make_request(design, row)
    expected = driver.leaf.make_request(
        design, {**row, "arm": "definitions"}, driver.ALIASES[row["arm"]]
    )
    assert request == expected
    assert "structured_outputs" not in request and request["max_tokens"] == 256
    changed = deepcopy(design)
    changed["batches"][row["batch_id"]]["gold"] = ["LEAK_MARKER"] * 5
    changed["tasks"][0]["answer"] = "LEAK_MARKER"
    assert driver.make_request(changed, row) == request
    assert "LEAK_MARKER" not in json.dumps(request)


def test_exact_operator_count_and_items_are_separate():
    design = design_fixture()
    coordinate = design["coordinates"][0]
    records = records_for_coordinate(design, coordinate)
    result = driver.score_coordinate(design, coordinate, records)
    assert result["strict_reward"] == 1 and result["aggregate_available"]
    assert result["canonical_correct"] == 64 and result["aligned_records"] == 64
    records[0]["score"] = driver.leaf.score_labels(
        json.dumps(["location", "human being"] + design["batches"][0]["gold"][2:]),
        design["batches"][0]["gold"],
    )
    result = driver.score_coordinate(design, coordinate, records)
    assert result["strict_reward"] == 1 and result["canonical_correct"] == 62
    assert result["target_false_positives"] == [2] and result["target_false_negatives"] == [1]


@pytest.mark.parametrize(
    "bad",
    [
        '["alias", "location", "abbreviation", "entity", "description and abstract concept"]',
        '["human being"]',
        "not JSON",
    ],
)
def test_one_bad_batch_invalidates_aggregate_without_fallback(bad):
    design = design_fixture()
    coordinate = design["coordinates"][0]
    records = records_for_coordinate(design, coordinate)
    records[0]["score"] = driver.leaf.score_labels(bad, design["batches"][0]["gold"])
    result = driver.score_coordinate(design, coordinate, records)
    assert result["status"] == "model_contract_failure"
    assert result["strict_reward"] == 0 and result["predicted_count"] is None
    assert not result["aggregate_available"]


def test_infrastructure_and_incomplete_are_null_not_model_zero():
    design = design_fixture()
    coordinate = design["coordinates"][0]
    records = records_for_coordinate(design, coordinate)
    assert driver.score_coordinate(design, coordinate, records[:-1])["strict_reward"] is None
    records[0]["score"] = None
    records[0]["error"] = {"type": "HTTPStatusError"}
    result = driver.score_coordinate(design, coordinate, records)
    assert result["strict_reward"] is None and result["status"] == "infrastructure_error"


def test_binding_cannot_substitute_an_unselected_checkpoint():
    spec = {
        "selection": {
            "path": "/selection.json",
            "sha256": "s",
            "epoch": 2,
            "checkpoint": "/sft/checkpoint-0128",
        },
        "models": {
            driver.ALIASES["original_child"]: {"path": "/original"},
            driver.ALIASES["sft_child"]: {"path": "/sft/checkpoint-0128"},
        },
    }
    binding = {
        "selection_path": "/selection.json",
        "selection_sha256": "s",
        "selected_epoch": 2,
        "models": deepcopy(spec["models"]),
        "role_map": {
            "root": driver.ALIASES["original_child"],
            "children": list(driver.ALIASES.values()),
        },
        "post_training_test_consulted_for_binding": False,
    }
    driver.validate_binding(spec, binding)
    binding["models"][driver.ALIASES["sft_child"]]["path"] = "/sft/checkpoint-0064"
    with pytest.raises(ValueError, match="binding"):
        driver.validate_binding(spec, binding)


def test_mock_calls_checkpoint_without_model_or_tool_execution(tmp_path):
    design = design_fixture()
    design["plan"] = design["plan"][:4]
    expected = {driver.leaf.digest(driver.make_request(design, row)): row for row in design["plan"]}
    spec = {
        "design": design,
        "request_sha256": {
            r["id"]: driver.leaf.digest(driver.make_request(design, r)) for r in design["plan"]
        },
    }
    seen = []

    def handler(request):
        body = json.loads(request.content)
        row = expected[driver.leaf.digest(body)]
        seen.append(row["id"])
        labels = design["batches"][row["batch_id"]]["gold"]
        return httpx.Response(
            200,
            json={
                "model": body["model"],
                "choices": [
                    {
                        "message": {"content": json.dumps(labels)},
                        "finish_reason": "stop",
                        "token_ids": [1],
                    }
                ],
                "usage": {"prompt_tokens": 100, "completion_tokens": 20},
                "prompt_token_ids": [1],
            },
        )

    tmp_path.joinpath("calls").mkdir()
    tmp_path.joinpath("coordinates").mkdir()

    async def run():
        async with httpx.AsyncClient(transport=httpx.MockTransport(handler)) as client:
            return await driver.collect_calls(client, "http://example.invalid/v1", spec, tmp_path)

    records, reason = asyncio.run(run())
    assert reason is None and len(records) == 4 and len(set(seen)) == 4
    assert len(list(tmp_path.joinpath("calls").glob("*.json"))) == 4
    assert all(r["score"]["schema_valid"] for r in records)


def test_actual_service_binding_records_common_bf16_inference_cast():
    spec = driver.make_spec(driver.ROLE / "BOUND_WEIGHTS.json", driver.ROLE / "service-attempt-001")
    assert spec["server"]["lora_dtype"] == "auto"
    assert spec["server"]["model_dtype"] == "auto"
    assert spec["selection"]["checkpoint"].endswith("checkpoint-0128")
    assert len(spec["design"]["plan"]) == 624
