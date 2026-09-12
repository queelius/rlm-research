"""Run one authored teacher through the real short-MRCR container and fake provider."""

from __future__ import annotations

import asyncio
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import sys
import time

from aiohttp import web

import teacher


ROOT = Path(__file__).resolve().parent
SHORT = ROOT.parent / "openai-mrcr-short32-base-calibration-v1"
OUTPUT = ROOT / "cpu-teacher-container-smoke"
RECEIPT = ROOT / "CPU_TEACHER_CONTAINER_SMOKE.json"


def digest_json(value) -> str:
    return hashlib.sha256(
        json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False).encode()
    ).hexdigest()


def write_x(path: Path, value) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("x") as stream:
        json.dump(value, stream, indent=2, sort_keys=True, allow_nan=False)
        stream.write("\n")
        stream.flush()
        os.fsync(stream.fileno())


def load_short_modules():
    """Load collect with the exact short-study module in its generic import seam."""
    study_spec = importlib.util.spec_from_file_location("procedural_teacher_short_study", SHORT / "study.py")
    study = importlib.util.module_from_spec(study_spec)
    assert study_spec.loader is not None
    study_spec.loader.exec_module(study)
    previous = sys.modules.get("study")
    sys.modules["study"] = study
    try:
        collect_spec = importlib.util.spec_from_file_location(
            "procedural_teacher_short_collect", SHORT / "collect.py"
        )
        collect = importlib.util.module_from_spec(collect_spec)
        assert collect_spec.loader is not None
        collect_spec.loader.exec_module(collect)
    finally:
        if previous is None:
            sys.modules.pop("study", None)
        else:
            sys.modules["study"] = previous
    return study, collect


async def smoke() -> dict:
    if os.environ.get("CUDA_VISIBLE_DEVICES") != "":
        raise ValueError("CPU teacher smoke requires CUDA hidden")
    if OUTPUT.exists() or RECEIPT.exists():
        raise FileExistsError("teacher container smoke output already exists")
    from renderers import Qwen3RendererConfig, create_renderer
    from renderers.base import load_tokenizer
    from verifiers.v1.env import RunSlot

    study, collect = load_short_modules()
    corpus = json.loads((ROOT / "TEACHER_CORPUS_V2.json").read_text())
    episode = corpus["episodes"][0]
    record_id = episode["episode_id"]
    coordinate = next(
        row for row in study.plan() if row["record_id"] == record_id and row["repeat"] == 0
    )
    env = study.environment(study.INPUTS)
    task = next(row for row in env.taskset if row.data.name == coordinate["id"])
    source = next(row for row in study.selected() if row["id"] == record_id)
    question = Path(source["final_question_path"]).read_text()
    payload = Path(source["prompt_json_path"]).read_bytes()
    built = teacher.construct(question, json.loads(payload))
    expected_answer = built["answer"]
    expected_first = episode["turns"][0]["input_ids"][: episode["turns"][0]["prompt_length"]]
    expected_terminal = episode["turns"][1]["input_ids"][: episode["turns"][1]["prompt_length"]]
    tokenizer = create_renderer(
        load_tokenizer(str(study.MODEL)), Qwen3RendererConfig(enable_thinking=True)
    )._tokenizer
    requests = []

    async def provider(request):
        body = await request.json()
        requests.append(body)
        reply = teacher.tool_action(built["authored_code"]) if len(requests) == 1 else expected_answer
        ids = tokenizer.encode(reply, add_special_tokens=False) + [teacher.EOS]
        return web.json_response(
            {
                "request_id": f"PROCEDURAL_TEACHER_CPU_{len(requests)}",
                "usage": {
                    "prompt_tokens": len(body["token_ids"]),
                    "completion_tokens": len(ids),
                    "total_tokens": len(body["token_ids"]) + len(ids),
                },
                "choices": [
                    {
                        "token_ids": ids,
                        "finish_reason": "stop",
                        "logprobs": {
                            "content": [
                                {"token": f"token_id:{token}", "logprob": -0.5}
                                for token in ids
                            ]
                        },
                    }
                ],
            }
        )

    app = web.Application()
    app.router.add_post("/inference/v1/generate", provider)
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, "127.0.0.1", 0)
    await site.start()
    port = site._server.sockets[0].getsockname()[1]
    endpoint = {
        "model_alias": study.MODEL_ALIAS,
        "host": "127.0.0.1",
        "port": port,
        "api_key_env": "PROCEDURAL_TEACHER_CPU_KEY",
        "base_model": {"path": str(study.MODEL)},
        "adapter": None,
    }
    context = collect.model_context(endpoint, coordinate)
    before_path = os.environ.get("PATH", "")
    before_secret = os.environ.get(endpoint["api_key_env"])
    os.environ["PATH"] = str(study.RUNTIME_BIN) + os.pathsep + before_path
    os.environ[endpoint["api_key_env"]] = "cpu-fixture-not-a-service-secret"
    os.environ.setdefault("VERIFIERS_CACHE_DIR", "/project/alex_phd/cache/verifiers-prime")
    started = time.time()
    recorder = collect.v7_recorder()
    OUTPUT.mkdir(parents=True, exist_ok=False)
    try:
        with recorder.native_checkpoints(OUTPUT / "native-calls", study.MODEL_ALIAS) as native:
            async with env.serving():
                result = await asyncio.wait_for(env.run_slot(RunSlot(task), context), timeout=300)
        raw = result.to_record()
    finally:
        await runner.cleanup()
        os.environ["PATH"] = before_path
        if before_secret is None:
            os.environ.pop(endpoint["api_key_env"], None)
        else:
            os.environ[endpoint["api_key_env"]] = before_secret
    trace = raw["traces"][0]
    tool_results = [
        str((node.get("message") or {}).get("content") or "")
        for node in trace.get("nodes") or []
        if (node.get("message") or {}).get("role") == "tool"
    ]
    value = {
        "schema": "openai-mrcr-procedural-sft-teacher-container-smoke-v1",
        "record_id": record_id,
        "elapsed_seconds": time.time() - started,
        "episode_ok": raw.get("ok"),
        "stop_condition": trace.get("stop_condition"),
        "root_reply_exact": trace.get("root_reply") == expected_answer,
        "provider_requests": len(requests),
        "native_returned": sum(row.get("status") == "returned" for row in native),
        "first_provider_prefix_equal_corpus": requests[0]["token_ids"] == expected_first,
        "terminal_provider_prefix_equal_corpus": requests[1]["token_ids"] == expected_terminal,
        "first_provider_prefix_sha256": digest_json(requests[0]["token_ids"]),
        "corpus_first_prefix_sha256": digest_json(expected_first),
        "terminal_provider_prefix_sha256": digest_json(requests[1]["token_ids"]),
        "corpus_terminal_prefix_sha256": digest_json(expected_terminal),
        "tool_stdout_exact_teacher_answer_plus_newline": expected_answer + "\n" in tool_results,
        "actual_tool_result_sha256": [
            hashlib.sha256(row.encode()).hexdigest() for row in tool_results
        ],
        "heldout_records_read": 0,
        "gpu_calls": 0,
        "weighted_model_calls": 0,
        "synthetic_provider": True,
    }
    value["passed"] = bool(
        value["episode_ok"] is True
        and value["stop_condition"] == "agent_completed"
        and value["root_reply_exact"]
        and value["provider_requests"] == value["native_returned"] == 2
        and value["first_provider_prefix_equal_corpus"]
        and value["terminal_provider_prefix_equal_corpus"]
        and value["tool_stdout_exact_teacher_answer_plus_newline"]
    )
    write_x(OUTPUT / "EPISODE.json", raw)
    write_x(OUTPUT / "PROVIDER_REQUESTS.json", requests)
    write_x(RECEIPT, value)
    if not value["passed"]:
        raise ValueError("actual teacher container/prefix smoke failed")
    return value


if __name__ == "__main__":
    print(json.dumps(asyncio.run(smoke()), sort_keys=True))
