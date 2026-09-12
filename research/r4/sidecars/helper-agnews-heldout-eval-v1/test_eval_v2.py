import importlib.util
from pathlib import Path


ROOT = Path(__file__).resolve().parent
SPEC = importlib.util.spec_from_file_location("ag_eval_owner_v2", ROOT / "owner_v2.py")
owner = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(owner)


def fixtures():
    gold = {f"id-{index:03d}": "World" for index in range(256)}
    calls = []
    for start in range(0, 256, 4):
        ids = [f"id-{index:03d}" for index in range(start, start + 4)]
        calls.append(
            {
                "call_id": f"call-{start:03d}",
                "dataset": "ag_news",
                "ids": ids,
                "status": "returned_valid",
                "prediction": {identifier: "World" for identifier in ids},
                "prompt_tokens": 10,
                "completion_tokens": 5,
                "cached_prompt_tokens": 3,
                "wall_seconds": 0.1,
            }
        )
    return calls, {"labels": gold}


def test_summarize_exact64_maps_has_ag256_and_no_phantom_trec():
    calls, gold = fixtures()
    result = owner.summarize(calls, gold)
    assert result["complete"] is True
    assert set(result["datasets"]) == {"ag_news"}
    assert result["datasets"]["ag_news"]["predictions"] == 256
    assert result["datasets"]["ag_news"]["unavailable_predictions"] == 0
    assert result["inventory"]["missing_ids"] == []


def test_summarize_missing_map_reports_four_unavailable_not_negative():
    calls, gold = fixtures()
    result = owner.summarize(calls[:-1], gold)
    assert result["complete"] is False
    assert result["datasets"]["ag_news"]["predictions"] == 252
    assert result["datasets"]["ag_news"]["unavailable_predictions"] == 4
    assert len(result["inventory"]["missing_ids"]) == 4
