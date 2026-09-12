"""Native root calibration collector; no service lifecycle and no optimizer."""

from __future__ import annotations

import argparse
import asyncio
import contextlib
import copy
import itertools
import json
import math
import os
from pathlib import Path
import time
from uuid import uuid4

import study


def environment(directory):
    from verifiers.v1.envs.single_agent import SingleAgentEnv, SingleAgentEnvConfig
    # Import registers the already-qualified taskset and harness IDs.
    study.old_module()
    return SingleAgentEnv(SingleAgentEnvConfig.model_validate(study.environment_config(directory)))


def model_context(endpoint, coordinate):
    from renderers import Qwen3RendererConfig
    from verifiers.v1.clients import ModelContext
    from verifiers.v1.configs.client import TrainClientConfig
    from verifiers.v1.types import SamplingConfig
    return ModelContext(model=endpoint["model_alias"], client=TrainClientConfig(
        base_url=f"http://{endpoint['host']}:{endpoint['port']}/v1",
        api_key_var=endpoint["api_key_env"], renderer=Qwen3RendererConfig(enable_thinking=True),
        renderer_model_name=endpoint["base_model"]["path"], multiplex=256),
        sampling=SamplingConfig.model_validate({"temperature": 0.5, "top_p": 1.0,
            "seed": coordinate["seed"], "max_tokens": 2048,
            "extra_body": {"top_k": -1, "min_p": 0.0, "return_token_ids": True,
                "cache_salt": "0"}}))


def validate_native_response(payload):
    tokens = payload.get("tokens") or {}
    prompt = tokens.get("prompt_ids") or []; action = tokens.get("completion_ids") or []
    logs = tokens.get("completion_logprobs") or []
    if (not prompt or not action or any(type(value) is not int or value < 0 for value in prompt + action)
            or len(action) != len(logs)
            or any(isinstance(value, bool) or not isinstance(value, (int, float))
                   or not math.isfinite(value) or value > 0 for value in logs)):
        raise ValueError("missing, invalid, or misaligned native token/logprob evidence")
    return {"prompt_tokens": len(prompt), "action_tokens": len(action),
        "completion_ids_sha256": study.digest(action), "completion_logprobs": logs}


@contextlib.contextmanager
def native_checkpoints(directory, expected_alias):
    from verifiers.v1.clients.train import TrainClient
    original = TrainClient.get_response; counter = itertools.count(); rows = []

    async def get_response(client, dialect, body, sampling, session_id=None, turn=None, headers=None):
        index = next(counter); stem = f"{index:04d}"; started = time.time()
        start = {"index": index, "started_epoch": started, "model": body.get("model"),
            "body": copy.deepcopy(body), "sampling": sampling.model_dump(mode="json"),
            "session_id": session_id, "turn": turn}
        study.write_x(directory / (stem + "-start.json"), start)
        result = {**start, "status": "started"}; rows.append(result)
        try:
            if body.get("model") != expected_alias:
                raise ValueError("root or child used a non-base alias")
            response = await original(client, dialect, body, sampling, session_id=session_id,
                turn=turn, headers=headers)
            payload = response.model_dump(mode="json")
            evidence = validate_native_response(payload)
            if response.model != expected_alias:
                raise ValueError("native response model alias changed")
            result.update(status="returned", response=payload, evidence=evidence,
                finish_reason=response.finish_reason)
            return response
        except BaseException as error:
            result.update(status="error", error={"type": type(error).__name__, "message": str(error)})
            raise
        finally:
            result["ended_epoch"] = time.time(); result["wall_seconds"] = result["ended_epoch"] - started
            study.write_x(directory / (stem + "-result.json"), result)

    TrainClient.get_response = get_response
    try:
        yield rows
    finally:
        TrainClient.get_response = original


def inspect_trace(raw, target, censored=False):
    traces = raw.get("traces") or []
    errors = [*raw.get("errors", []), *(error for trace in traces for error in trace.get("errors", []))]
    trace = traces[0] if len(traces) == 1 else {}
    valid = bool(raw.get("ok") and len(traces) == 1 and not errors
        and trace.get("stop_condition") == "agent_completed"
        and isinstance(trace.get("root_reply"), str) and trace["root_reply"].strip())
    if censored: status = "deadline_censored"
    elif valid: status = "completed"
    elif trace.get("stop_condition") == "max_turns": status = "turn_limit_no_valid_final"
    else: status = "unavailable"
    nodes = trace.get("nodes") or []; calls = trace.get("calls") or []
    metrics = trace.get("metrics") or {}; child_calls = int(metrics.get("sub_rlm_num_calls") or 0)
    tool_calls = []
    for node in nodes:
        message = node.get("message") or {}
        for call in message.get("tool_calls") or []:
            if call.get("name") == "ipython": tool_calls.append(call.get("arguments") or "")
    mentions = sum("context.txt" in value for value in tool_calls)
    score = study.score_terminal(trace.get("root_reply"), target, status)
    return {**score, "terminal_status": status, "stop_condition": trace.get("stop_condition"),
        "error_types": [error.get("type") for error in errors], "model_calls": len(calls),
        "root_calls": max(0, len(calls) - child_calls), "child_calls": child_calls,
        "python_calls": len(tool_calls), "context_path_mentions_in_python": mentions,
        "real_external_inspection": mentions > 0 and any(
            (node.get("message") or {}).get("role") == "tool" for node in nodes),
        "action_tokens": sum(sum(node.get("mask") or []) for node in nodes if node.get("sampled") is True),
        "input_tokens": sum((call.get("usage") or {}).get("prompt_tokens", 0) for call in calls),
        "output_tokens": sum((call.get("usage") or {}).get("completion_tokens", 0) for call in calls)}


def summarize(records):
    groups = []
    for row in study.selected_rows():
        items = [record for record in records if record["coordinate"]["row_id"] == row["row_id"]]
        scores = [record["derived"]["official_score"] for record in items
                  if record["derived"]["official_score"] is not None]
        distinct = []
        for score in scores:
            if not any(abs(score - other) <= 1e-12 for other in distinct): distinct.append(score)
        groups.append({"row_id": row["row_id"], "slot": row["slot"], "recorded": len(items),
            "available_scores": scores, "score_range": max(scores)-min(scores) if scores else None,
            "mixed": len(distinct) >= 2})
    values = [record["derived"]["official_score"] for record in records
              if record["derived"]["official_score"] is not None]
    complete = len(records) == 32
    mixed = sum(group["mixed"] for group in groups)
    inspected = sum(record["derived"]["real_external_inspection"] for record in records)
    protocol_good = complete and all(record["error"] is None for record in records)
    mean = sum(values)/len(values) if values else None
    eligible = bool(protocol_good and inspected > 0 and mixed >= 2 and mean is not None and mean < 0.90)
    return {"schema": "mrcr-v3-root-procedure-calibration-result-v1",
        "complete": complete, "recorded": len(records), "planned": 32,
        "available_scores": len(values), "mean_official_score_available": mean,
        "mixed_groups": mixed, "groups": groups, "real_inspection_episodes": inspected,
        "turn_limit_without_valid_final": sum(r["derived"]["terminal_status"] == "turn_limit_no_valid_final" for r in records),
        "deadline_censored": sum(r["derived"]["terminal_status"] == "deadline_censored" for r in records),
        "total_root_calls": sum(r["derived"]["root_calls"] for r in records),
        "total_child_calls": sum(r["derived"]["child_calls"] for r in records),
        "future_root_rl_gate": {"eligible": eligible, "requirements": {
            "mixed_groups_at_least": 2, "mean_official_score_below": 0.90,
            "protocol_good": True, "real_external_inspection": True}},
        "claim_boundary": "Eight targets over one underlying context; calibration only, not held-out or generalization."}


async def run(spec_path, endpoint_path, output, deadline):
    from verifiers.v1.env import RunSlot
    spec = study.read(spec_path); endpoint = study.read(endpoint_path)
    if spec != study.read(study.ROOT / "SPEC.json") or study.sha(spec_path) != study.sha(study.ROOT / "SPEC.json"):
        raise ValueError("actual specification differs from sealed source")
    if endpoint.get("model_alias") != study.MODEL_ALIAS or endpoint.get("adapter") is not None:
        raise ValueError("actual endpoint is not the released no-adapter model")
    if Path(endpoint["base_model"]["path"]).resolve() != study.MODEL.resolve():
        raise ValueError("actual endpoint base path changed")
    if not os.environ.get(endpoint["api_key_env"]): raise ValueError("private endpoint credential missing")
    output.mkdir(parents=True, exist_ok=False); study.write_x(output / "SPEC.json", spec)
    os.environ["PATH"] = str(study.ROOT / "bin") + os.pathsep + os.environ.get("PATH", "")
    context_sha = spec["context_sha256"]
    os.environ["MRCR_CALIBRATION_CONTEXT"] = str(study.ROOT / "inputs/contexts" / (context_sha + ".txt"))
    os.environ.setdefault("VERIFIERS_CACHE_DIR", "/project/alex_phd/cache/verifiers-prime")
    env = environment(study.ROOT / "inputs"); tasks = {task.data.name: task for task in env.taskset}
    gold = study.read(study.ROOT / "inputs/HOST_GOLD.json"); records = []; lock = asyncio.Lock()
    queue = asyncio.Queue()
    for coordinate in study.plan(): queue.put_nowait(coordinate)
    run_id = str(uuid4())
    async def one(coordinate):
        from verifiers.v1.episode import EvalRunInfo, GroupInfo
        slot = RunSlot(tasks[coordinate["id"]]); started = time.time(); censored = False
        try:
            episode = await asyncio.wait_for(env.run_slot(slot, model_context(endpoint, coordinate)),
                timeout=max(0.001, min(180, deadline-time.time())))
            episode.group = GroupInfo(id=coordinate["row_id"])
            episode.record_run(EvalRunInfo(id=run_id, name=study.ROOT.name)); raw = episode.to_record()
        except (TimeoutError, asyncio.TimeoutError):
            censored = True; raw = {"ok": False, "errors": [{"type": "TimeoutError",
                "message": "coordinate deadline censored"}], "traces": [t.to_record() for t in slot.traces]}
        except BaseException as error:
            raw = {"ok": False, "errors": [{"type": type(error).__name__, "message": str(error)}],
                "traces": [t.to_record() for t in slot.traces]}
        record = {"schema": "mrcr-v3-root-procedure-episode-v1", "coordinate": coordinate,
            "episode": raw, "episode_sha256": study.digest(raw),
            "derived": inspect_trace(raw, gold[coordinate["row_id"]], censored=censored),
            "error": None if raw.get("ok") else raw.get("errors"),
            "timing": {"started": started, "ended": time.time()}}
        study.write_x(output / "episodes" / (coordinate["id"] + ".json"), record)
        async with lock:
            records.append(record); study.write_x(output / "progress" / f"{len(records):03d}.json", summarize(records))
    async def worker():
        while time.time() < deadline:
            try: coordinate = queue.get_nowait()
            except asyncio.QueueEmpty: return
            try: await one(coordinate)
            finally: queue.task_done()
    with native_checkpoints(output / "native-calls", study.MODEL_ALIAS):
        async with env.serving():
            workers = [asyncio.create_task(worker()) for _ in range(4)]
            try: await asyncio.wait_for(asyncio.gather(*workers), max(0.001, deadline-time.time()))
            except TimeoutError:
                for task in workers: task.cancel()
                await asyncio.gather(*workers, return_exceptions=True)
    missing = [row["id"] for row in study.plan() if row["id"] not in {r["coordinate"]["id"] for r in records}]
    result = {**summarize(records), "missing_coordinates": missing,
        "native_call_results": len(list((output / "native-calls").glob("*-result.json")))}
    study.write_x(output / "RESULT.json", result)
    return 0 if result["complete"] else 3


if __name__ == "__main__":
    parser = argparse.ArgumentParser(); parser.add_argument("--spec", type=Path, required=True)
    parser.add_argument("--endpoint", type=Path, required=True); parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--deadline", type=float, required=True); args = parser.parse_args()
    raise SystemExit(asyncio.run(run(args.spec, args.endpoint, args.output, args.deadline)))

