import asyncio
import importlib.util
import json
from pathlib import Path

import httpx
import pytest

ROOT = Path(__file__).resolve().parent


def driver():
    assert (ROOT / "driver.py").exists(), "schema driver missing"
    loader = importlib.util.spec_from_file_location("schema_test_driver", ROOT / "driver.py")
    mod = importlib.util.module_from_spec(loader)
    loader.loader.exec_module(mod)
    return mod


@pytest.mark.parametrize("size,calls", [(64, 48), (1, 3072)])
def test_schema_is_only_request_change_and_preserves_question_coordinates(size, calls):
    mod = driver()
    baseline = json.loads((mod.PARENT / f"SPEC-B{size:03d}.json").read_text())
    spec = mod.make_spec(size)
    assert spec["design"] == baseline["design"]
    assert len(spec["design"]["plan"]) == calls
    for row in spec["design"]["plan"]:
        old = mod.original_request(spec["design"], row)
        new = mod.make_request(spec["design"], row)
        schema = new.pop("structured_outputs")["json"]
        assert schema["type"] == "array"
        assert schema["minItems"] == schema["maxItems"] == size
        assert set(schema["items"]["enum"]) == {
            "human being",
            "location",
            "entity",
            "abbreviation",
            "numeric value",
            "description and abstract concept",
        }
        assert new == old


def test_actual_collector_dispatches_and_retains_schema_without_scoring_repair(tmp_path):
    mod = driver()
    spec = mod.make_spec(64)
    spec["design"]["plan"] = spec["design"]["plan"][:1]
    (tmp_path / "calls").mkdir()
    (tmp_path / "coordinates").mkdir()

    def reply(request):
        body = json.loads(request.content)
        assert body["structured_outputs"]["json"]["minItems"] == 64
        return httpx.Response(
            200,
            json={
                "model": body["model"],
                "choices": [{"finish_reason": "stop", "message": {"content": '["entity"]'}}],
                "usage": {"prompt_tokens": 9, "completion_tokens": 3, "total_tokens": 12},
            },
        )

    async def run():
        async with httpx.AsyncClient(transport=httpx.MockTransport(reply)) as client:
            return await mod.fixed.collect_calls(client, "http://cpu.invalid/v1", spec, tmp_path)

    records, reason = asyncio.run(run())
    assert reason is None and len(records) == 1
    assert records[0]["request"]["structured_outputs"]["json"]["maxItems"] == 64
    assert records[0]["score"]["schema_valid"] is False
    score = mod.fixed.score_coordinate(spec["design"], spec["design"]["coordinates"][0], records)
    assert score["strict_reward"] == 0 and score["predicted_count"] is None
