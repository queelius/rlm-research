"""Exact raw-string native readout for one frozen procedural-SFT stage."""

from __future__ import annotations

import argparse
import asyncio
import contextlib
import copy
import importlib.util
import itertools
import json
import math
import os
from pathlib import Path
import sys
import time
from uuid import uuid4

import checkpoint
import study


def load_with_study(name: str, path: Path):
    previous = sys.modules.get("study")
    sys.modules["study"] = study
    try:
        spec = importlib.util.spec_from_file_location(name, path)
        module = importlib.util.module_from_spec(spec)
        assert spec.loader is not None
        spec.loader.exec_module(module)
        return module
    finally:
        if previous is None:
            sys.modules.pop("study", None)
        else:
            sys.modules["study"] = previous


CAUSAL = load_with_study("procedural_eval_causal", study.SOURCE / "causal_map_v2.py")
CLASSIFY = load_with_study("procedural_eval_classify", study.SOURCE / "classify_v2.py")


def verify_ready() -> dict:
    ready = study.read(study.READY)
    if ready.get("identity") != study.digest(
        {key: value for key, value in ready.items() if key != "identity"}
    ):
        raise ValueError("evaluation READY identity changed in collector process")
    for raw, expected in ready.get("closure_sha256", {}).items():
        if study.sha(Path(raw)) != expected:
            raise ValueError("evaluation closure changed in collector process: " + raw)
    for phase in ("train", "held"):
        if study.digest(study.schedule(phase)) != ready["inputs"][phase]["schedule_sha256"]:
            raise ValueError("evaluation schedule changed in collector process")
    return ready


def role_hooks():
    directory = study.ROLE_SOURCE.parent
    previous_path = list(sys.path)
    try:
        sys.path.insert(0, str(directory))
        return study.load("procedural_eval_role_hooks", study.ROLE_SOURCE)
    finally:
        sys.path[:] = previous_path


def pending_turn_metadata(turn):
    if turn is None:
        return None
    from verifiers.v1.graph import PendingTurn

    if not isinstance(turn, PendingTurn):
        raise TypeError("expected exact PendingTurn")
    prompt = [message.model_dump(mode="json", exclude_none=True) for message in turn.prompt]
    return {
        "type": "PendingTurn",
        "trace_id": turn.trace.id,
        "prompt_sha256": study.digest(prompt),
        "prefix_node_ids": list(turn.prefix_node_ids),
        "path_len": turn.path_len,
        "tail_start": turn.tail_start,
    }


def validate_native_response(payload):
    tokens = payload.get("tokens") or {}
    prompt = tokens.get("prompt_ids") or []
    action = tokens.get("completion_ids") or []
    logs = tokens.get("completion_logprobs") or []
    if (
        not prompt
        or not action
        or any(type(value) is not int or value < 0 for value in prompt + action)
        or len(action) != len(logs)
        or any(not isinstance(value, (int, float)) or isinstance(value, bool) or not math.isfinite(value) or value > 0 for value in logs)
    ):
        raise ValueError("missing or invalid native token/logprob evidence")
    return {
        "prompt_tokens": len(prompt),
        "action_tokens": len(action),
        "completion_ids_sha256": study.digest(action),
    }


@contextlib.contextmanager
def native_checkpoints(directory: Path, aliases: set[str]):
    from verifiers.v1.clients.train import TrainClient

    original = TrainClient.get_response
    rows = []
    counter = itertools.count()

    async def get_response(client, dialect, body, sampling, session_id=None, turn=None, headers=None):
        index = next(counter)
        started = time.time()
        start = {
            "index": index,
            "started_epoch": started,
            "model": body.get("model"),
            "body": copy.deepcopy(body),
            "sampling": sampling.model_dump(mode="json"),
            "session_id": session_id,
            "turn": pending_turn_metadata(turn),
        }
        study.write_x(directory / f"{index:04d}-start.json", start)
        result = {**start, "status": "started"}
        rows.append(result)
        try:
            if body.get("model") not in aliases:
                raise ValueError("request used an unbound alias")
            response = await original(
                client, dialect, body, sampling, session_id=session_id, turn=turn, headers=headers
            )
            payload = response.model_dump(mode="json")
            evidence = validate_native_response(payload)
            if response.model != body["model"]:
                raise ValueError("response model differs from routed request")
            result.update(status="returned", response=payload, evidence=evidence)
            return response
        except BaseException as error:
            result.update(status="error", error={"type": type(error).__name__, "message": str(error)})
            raise
        finally:
            result["ended_epoch"] = time.time()
            result["wall_seconds"] = result["ended_epoch"] - started
            study.write_x(directory / f"{index:04d}-result.json", result)

    TrainClient.get_response = get_response
    try:
        yield rows
    finally:
        TrainClient.get_response = original


def model_context(endpoint, coordinate):
    from renderers import Qwen3RendererConfig
    from verifiers.v1.clients import ModelContext
    from verifiers.v1.configs.client import TrainClientConfig
    from verifiers.v1.types import SamplingConfig

    return ModelContext(
        model=endpoint["model_alias"],
        client=TrainClientConfig(
            base_url=f"http://{endpoint['host']}:{endpoint['port']}/v1",
            api_key_var=endpoint["api_key_env"],
            renderer=Qwen3RendererConfig(enable_thinking=True),
            renderer_model_name=endpoint["base_model"]["path"],
            multiplex=256,
        ),
        sampling=SamplingConfig.model_validate(
            {
                "temperature": 0.5,
                "top_p": 1.0,
                "seed": coordinate["seed"],
                "max_tokens": 2048,
                "extra_body": {"top_k": -1, "min_p": 0.0, "return_token_ids": True, "cache_salt": "0"},
            }
        ),
    )


def inspect_trace(raw, gold, native_rows, expected_prefix, censored=False):
    traces = raw.get("traces") or []
    trace = traces[0] if len(traces) == 1 else {}
    errors = [*raw.get("errors", []), *(e for item in traces for e in item.get("errors", []))]
    mapping = CAUSAL.map_trace(trace, native_rows, max_actions=6)
    returned = [
        row
        for row in native_rows
        if row.get("session_id") == trace.get("id") and row.get("status") == "returned"
    ]
    root_matches = [row for row in mapping["matches"] if row["role"] == "root"]
    first_root = min(root_matches, key=lambda row: row["audit_index"]) if root_matches else None
    actual_prefix = (
        (returned[first_root["audit_index"]].get("response") or {}).get("tokens", {}).get("prompt_ids")
        if first_root is not None and first_root["audit_index"] < len(returned)
        else None
    )
    initial_prefix_verified = actual_prefix == expected_prefix
    if not initial_prefix_verified:
        mapping["complete"] = False
    stop = "deadline_censored" if censored else trace.get("stop_condition")
    classified = CLASSIFY.classify_outcome(
        root_reply=trace.get("root_reply"),
        answer=gold["answer"],
        marker=gold["random_string_to_prepend"],
        stop_condition=stop,
        trace_ok=bool(raw.get("ok") and len(traces) == 1),
        trace_errors=errors,
        returned_root_actions=mapping["root_actions"],
        returned_child_actions=mapping["child_actions"],
        native_mapping_complete=mapping["complete"],
    )
    calls = [call for call in trace.get("calls") or [] if call.get("node") is not None]
    usage = [call.get("usage") or {} for call in calls]
    reply = trace.get("root_reply")
    return {
        **classified,
        "terminal_status": stop,
        "root_reply": reply,
        "answer": gold["answer"],
        "raw_exact": isinstance(reply, str) and reply == gold["answer"],
        "normalized_exact": isinstance(reply, str) and reply.strip() == gold["answer"].strip(),
        "trace_id": trace.get("id"),
        "error_types": [error.get("type") for error in errors],
        "causal_mapping": mapping,
        "native_mapping_complete": mapping["complete"],
        "initial_root_prefix_verified": initial_prefix_verified,
        "root_actions_returned": mapping["root_actions"],
        "child_actions_returned": mapping["child_actions"],
        "total_actions_returned": mapping["total_actions"],
        "six_total_root_child_cap_respected": mapping["cap_respected"],
        "prompt_tokens": sum(item.get("prompt_tokens", 0) for item in usage),
        "completion_tokens": sum(item.get("completion_tokens", 0) for item in usage),
        "usage_unknown_calls": sum(not bool(call.get("usage")) for call in calls),
    }


def manipulation_gate(records):
    exact = [
        row
        for row in records
        if row["derived"]["scientifically_available"]
        and row["derived"]["root_reply"] == row["derived"]["answer"]
    ]
    normalized = sum(
        row["derived"]["scientifically_available"]
        and isinstance(row["derived"]["root_reply"], str)
        and row["derived"]["root_reply"].strip() == row["derived"]["answer"].strip()
        for row in records
    )
    contexts = {row["coordinate"]["context_sha256"] for row in exact}
    complete = len(records) == 32
    available = sum(row["derived"]["scientifically_available"] for row in records)
    eligible = complete and available == 32 and len(exact) >= 8 and len(contexts) >= 4
    return {
        "eligible": eligible,
        "planned": 32,
        "recorded": len(records),
        "available": available,
        "raw_exact": len(exact),
        "normalized_exact": normalized,
        "exact_contexts": len(contexts),
        "requirements": {"raw_exact_at_least": 8, "exact_contexts_at_least": 4, "all_available": True},
    }


def summarize(records, phase, arm):
    available = [row for row in records if row["derived"]["scientifically_available"]]
    result = {
        "schema": "openai-mrcr-procedural-sft-readout-result-v1",
        "phase": phase,
        "arm": arm,
        "planned": len(study.schedule(phase)),
        "recorded": len(records),
        "complete": len(records) == len(study.schedule(phase)),
        "scientifically_available": len(available),
        "infrastructure_unavailable": len(records) - len(available),
        "raw_exact": sum(row["derived"]["raw_exact"] for row in available),
        "normalized_exact": sum(row["derived"]["normalized_exact"] for row in available),
        "official_score_sum": math.fsum(row["derived"]["reward"] for row in available),
        "root_actions": sum(row["derived"]["root_actions_returned"] for row in records),
        "child_actions": sum(row["derived"]["child_actions_returned"] for row in records),
        "prompt_tokens": sum(row["derived"]["prompt_tokens"] for row in records),
        "completion_tokens": sum(row["derived"]["completion_tokens"] for row in records),
        "usage_unknown_calls": sum(row["derived"]["usage_unknown_calls"] for row in records),
        "all_causal_mappings_complete": all(row["derived"]["native_mapping_complete"] for row in records),
        "all_initial_root_prefixes_verified": all(row["derived"]["initial_root_prefix_verified"] for row in records),
        "all_action_caps_respected": all(row["derived"]["six_total_root_child_cap_respected"] for row in records),
    }
    if phase == "train":
        result["manipulation_gate"] = manipulation_gate(records)
    return result


async def run(phase, arm, endpoint_path, output, deadline):
    from verifiers.v1.env import RunSlot
    from verifiers.v1.episode import EvalRunInfo, GroupInfo

    ready = verify_ready()
    endpoint = study.read(endpoint_path)
    binding = checkpoint.binding(arm)
    root = binding["models"][binding["role_map"]["root"]]
    if (
        endpoint.get("model_alias") != binding["role_map"]["root"]
        or endpoint.get("adapter") != {
            "path": root["path"],
            "model_sha256": root["adapter_sha256"],
            "config_sha256": root["config_sha256"],
        }
        or endpoint.get("role_binding_sha256") != study.sha(Path(endpoint_path).parents[1] / "BINDING.json")
        or not os.environ.get(endpoint["api_key_env"])
    ):
        raise ValueError("live endpoint/root binding differs")
    output.mkdir(parents=True, exist_ok=False)
    os.environ["PATH"] = str(study.source().RUNTIME_BIN) + os.pathsep + os.environ.get("PATH", "")
    os.environ.setdefault("VERIFIERS_CACHE_DIR", "/project/alex_phd/cache/verifiers-prime")
    env = study.environment(phase)
    tasks = {task.data.name: task for task in env.taskset}
    gold = study.read(study.input_dir(phase) / "HOST_GOLD.json")
    prefixes = study.read(study.input_dir(phase) / "PREFIXES.json")
    records, lock, queue = [], asyncio.Lock(), asyncio.Queue()
    for row in study.schedule(phase):
        queue.put_nowait(row)
    run_id = str(uuid4())
    native_rows = None

    async def one(coordinate):
        nonlocal native_rows
        slot = RunSlot(tasks[coordinate["id"]])
        started = time.time()
        censored = False
        try:
            episode = await asyncio.wait_for(
                env.run_slot(slot, model_context(endpoint, coordinate)),
                timeout=max(0.001, min(180, deadline - time.time())),
            )
            episode.group = GroupInfo(id=coordinate["record_id"])
            episode.record_run(EvalRunInfo(id=run_id, name=study.ROOT.name))
            raw = episode.to_record()
        except (TimeoutError, asyncio.TimeoutError):
            censored = True
            raw = {"ok": False, "errors": [{"type": "TimeoutError", "message": "coordinate censored"}], "traces": [trace.to_record() for trace in slot.traces]}
        except BaseException as error:
            raw = {"ok": False, "errors": [{"type": type(error).__name__, "message": str(error)}], "traces": [trace.to_record() for trace in slot.traces]}
        record = {
            "schema": "openai-mrcr-procedural-sft-eval-episode-v1",
            "coordinate": coordinate,
            "episode": raw,
            "episode_sha256": study.digest(raw),
            "derived": inspect_trace(
                raw,
                gold[coordinate["record_id"]],
                native_rows,
                prefixes[coordinate["id"]]["token_ids"],
                censored,
            ),
            "timing": {"started": started, "ended": time.time()},
        }
        study.write_x(output / "episodes" / (coordinate["id"] + ".json"), record)
        async with lock:
            records.append(record)

    async def worker():
        while time.time() < deadline:
            try:
                coordinate = queue.get_nowait()
            except asyncio.QueueEmpty:
                return
            try:
                await one(coordinate)
            finally:
                queue.task_done()

    hooks = role_hooks()
    with native_checkpoints(output / "native-calls", set(binding["models"])) as rows:
        native_rows = rows
        with hooks.installed_hooks(binding, output):
            async with env.serving():
                workers = [asyncio.create_task(worker()) for _ in range(4)]
                try:
                    await asyncio.wait_for(asyncio.gather(*workers), max(0.001, deadline - time.time()))
                except TimeoutError:
                    for worker_task in workers:
                        worker_task.cancel()
                    await asyncio.gather(*workers, return_exceptions=True)
    result = summarize(records, phase, arm)
    result["missing_coordinates"] = [
        row["id"] for row in study.schedule(phase) if row["id"] not in {record["coordinate"]["id"] for record in records}
    ]
    result["ready_identity"] = ready["identity"]
    result["checkpoint_receipt_sha256"] = study.sha(checkpoint.RECEIPT)
    study.write_x(output / "RESULT.json", result)
    return 0 if result["complete"] else 3


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--phase", choices=("train", "held"), required=True)
    parser.add_argument("--arm", choices=("base", "checkpoint4"), required=True)
    parser.add_argument("--endpoint", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--deadline", type=float, required=True)
    args = parser.parse_args()
    raise SystemExit(asyncio.run(run(args.phase, args.arm, args.endpoint, args.output, args.deadline)))
