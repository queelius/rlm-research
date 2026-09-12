import asyncio
import json
import os
from pathlib import Path
import time

from aiohttp import web
import pytest


os.environ.setdefault("STRICT_RLM_CALIBRATION_API_KEY", "cpu-fixture")


def test_plans_pair_fresh_seeds_and_only_prompt_condition_changes():
    import collect
    import study

    plain = study.make_plan("budgeted_plain")
    syntax = study.make_plan("budgeted_syntax_example")
    assert len(plain) == len(syntax) == 24
    assert [row["seed"] for row in plain] == list(range(202609123000, 202609123024))
    assert [row["seed"] for row in syntax] == list(range(202609123000, 202609123024))
    for left, right in zip(plain, syntax, strict=True):
        assert left["pair_id"] == right["pair_id"]
        assert left["source_plan_id"] == right["source_plan_id"]
        assert left["seed"] == right["seed"]
        assert left["source_context_id"] == right["source_context_id"]
        assert left["task_name"] == right["task_name"]
        assert left["syntax_condition"] == "budgeted_plain"
        assert right["syntax_condition"] == "budgeted_syntax_example"

    public = collect.public()
    plain_prompt = study.root_prompt(public[plain[0]["context_id"]], plain[0])
    syntax_prompt = study.root_prompt(public[syntax[0]["context_id"]], syntax[0])
    assert "Toy syntax illustration" not in plain_prompt
    assert "Toy syntax illustration" in syntax_prompt
    assert "placeholder variables" in syntax_prompt
    assert "not actual record IDs" in syntax_prompt
    assert "does not tell you which records" in syntax_prompt
    assert plain_prompt != syntax_prompt


@pytest.mark.parametrize("condition", ["budgeted_plain", "budgeted_syntax_example"])
def test_actual_collector_slot_uses_frozen_prompt_and_produces_finite_final(
    tmp_path, monkeypatch, condition
):
    asyncio.run(_run_slot(tmp_path, monkeypatch, condition))


async def _run_slot(tmp_path, monkeypatch, condition):
    import httpx

    import collect
    import study

    collect.activate(condition)
    row = study.make_plan(condition)[0]
    study.PREFIX_INPUT = tmp_path / "PREFIXES.json"
    study.PREFIX_INPUT.write_text(json.dumps(study.build_prefixes()))
    study.prefixes.cache_clear()
    binding = collect.binding()
    native = study.terminal_study().qs.qnative().stack().native
    renderer = native.renderer()
    all_ids = study.saved_map(row)["requested_ids"]
    selected = all_ids[:2]
    calls = []
    code = (
        "from map_api import classify, finish\n"
        f"chosen={selected!r}\n"
        "labels=classify(chosen)\n"
        "finish(0,chosen)\n"
        "print(0)"
    )

    def completion(text, request_id):
        token_ids = renderer._tokenizer.encode(text, add_special_tokens=False) + [151645]
        return {
            "request_id": request_id,
            "usage": {
                "prompt_tokens": len(calls[0]["token_ids"]) if calls else 0,
                "completion_tokens": len(token_ids),
                "total_tokens": (len(calls[0]["token_ids"]) if calls else 0) + len(token_ids),
            },
            "choices": [
                {
                    "token_ids": token_ids,
                    "finish_reason": "stop",
                    "logprobs": {
                        "content": [
                            {"token": f"token_id:{token_id}", "logprob": -0.1}
                            for token_id in token_ids
                        ]
                    },
                }
            ],
        }

    async def generate(request):
        body = await request.json()
        calls.append(body)
        text = native.tool_action(code) if len(calls) == 1 else "Answer: 0"
        return web.json_response(completion(text, f"SYNTAX_CPU_{len(calls)}"))

    app = web.Application()
    app.router.add_post("/inference/v1/generate", generate)
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, "127.0.0.1", 0)
    await site.start()
    monkeypatch.setenv("SYNTAX_CPU_KEY", "cpu-fixture")
    collect.TASKS = tmp_path / "TASKS.json"
    collect.TASKS.write_text(json.dumps(collect.build_task_tables()))
    collect.activate(condition)
    descriptor = {
        "host": "127.0.0.1",
        "port": site._server.sockets[0].getsockname()[1],
        "api_key_env": "SYNTAX_CPU_KEY",
        "base_model": {"path": str(study.terminal_study().qs.qnative().stack().prior.BASE)},
    }
    spec = {
        "phase": study.phase(condition),
        "plan": [row],
        "descriptor": descriptor,
        "binding": binding,
        "cap_seconds": 90,
        "environment": collect.environment_config(),
    }
    spec_path = tmp_path / "SPEC.json"
    spec_path.write_text(json.dumps(spec))
    output = tmp_path / "rollout"
    implementation = collect.collect.__globals__
    old_verify = implementation["verify_spec"]
    implementation["verify_spec"] = lambda _path: spec

    class ModelResponse:
        def raise_for_status(self):
            return None

        def json(self):
            return {
                "data": [
                    {
                        "id": alias,
                        "root": model["path"],
                        "parent": descriptor["base_model"]["path"],
                    }
                    for alias, model in binding["models"].items()
                ]
            }

    class ModelClient:
        def __init__(self, *args, **kwargs):
            pass

        def __enter__(self):
            return self

        def __exit__(self, *args):
            return False

        def get(self, url):
            assert url.endswith("/v1/models")
            return ModelResponse()

    monkeypatch.setattr(httpx, "Client", ModelClient)
    try:
        status = await collect.collect(spec_path, output, time.time() + 90)
    finally:
        implementation["verify_spec"] = old_verify
        await runner.cleanup()

    assert status == 0
    row_receipt = json.loads((output / "rows" / f"{row['id']}.json").read_text())
    assert row_receipt["error"] is None
    assert row_receipt["task_hash"] == collect.task_tables()[condition][row["task_name"]]["task_hash"]
    record = json.loads((output / "episodes" / f"{row['id']}.json").read_text())
    trace = record["traces"][0]
    evidence = trace["info"]["budgeted_evidence"]
    assert trace["root_reply"] == "Answer: 0"
    assert trace["rewards"]["correctness"]["score"] in (0.0, 1.0)
    assert evidence["state"]["finished"] is True
    assert evidence["state"]["declared_answer"] == 0
    assert evidence["state"]["acquired_ids"] == selected
    assert len(calls) == 2
    assert calls[0]["token_ids"] == study.prefixes()[row["id"]]["token_ids"]
    task = collect.make_task_from_row(row)
    assert study.prefixes()[row["id"]]["prompt_sha256"] == study.sha_text(task.data.prompt)
