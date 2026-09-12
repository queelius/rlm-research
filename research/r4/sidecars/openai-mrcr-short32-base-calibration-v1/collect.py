"""Collect the frozen OpenAI MRCR short32 base calibration."""

from __future__ import annotations

import argparse
import asyncio
import functools
import importlib.util
import json
import math
import os
from pathlib import Path
import sys
import time
from uuid import uuid4

import study


@functools.lru_cache(maxsize=1)
def v7_recorder():
    """Load the sealed V7 recorder with its own generic-module namespace."""
    names = (
        "study",
        "study_v3",
        "study_v4",
        "study_v5",
        "study_v6",
        "collect",
        "collect_v4",
        "collect_v5",
        "collect_v6",
    )
    before = {name: sys.modules.get(name) for name in names}
    old_path = list(sys.path)
    try:
        for name in names:
            sys.modules.pop(name, None)
        sys.modules["study"] = study.v7_study()
        sys.path.insert(0, str(study.V7))
        spec = importlib.util.spec_from_file_location(
            "short32_v7_collect", study.V7 / "collect_v7.py"
        )
        module = importlib.util.module_from_spec(spec)
        sys.modules[spec.name] = module
        assert spec.loader is not None
        spec.loader.exec_module(module)
        return module
    finally:
        sys.path[:] = old_path
        for name, module in before.items():
            if module is None:
                sys.modules.pop(name, None)
            else:
                sys.modules[name] = module


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
                "extra_body": {
                    "top_k": -1,
                    "min_p": 0.0,
                    "return_token_ids": True,
                    "cache_salt": "0",
                },
            }
        ),
    )


def inspect_trace(raw, gold, native_rows, censored=False):
    traces = raw.get("traces") or []
    trace = traces[0] if len(traces) == 1 else {}
    trace_errors = [
        *raw.get("errors", []),
        *(error for item in traces for error in item.get("errors", [])),
    ]
    trace_id = trace.get("id")
    audits = [row for row in native_rows if row.get("session_id") == trace_id]
    returned = [row for row in audits if row.get("status") == "returned"]
    audit_errors = [row for row in audits if row.get("status") == "error"]
    calls = trace.get("calls") or []
    committed = [call for call in calls if call.get("node") is not None]
    ambiguous_calls = [call for call in calls if call.get("node") is None]
    child = int((trace.get("metrics") or {}).get("sub_rlm_num_calls") or 0)
    root = max(0, len(returned) - child)
    total_cap_respected = len(returned) <= 6
    mapping_complete = bool(
        trace_id
        and len(returned) == len(committed)
        and not audit_errors
        and not ambiguous_calls
        and all(row.get("turn", {}).get("trace_id") == trace_id for row in returned)
        and total_cap_respected
    )
    stopped = "deadline_censored" if censored else trace.get("stop_condition")
    classified = study.classify_outcome(
        root_reply=trace.get("root_reply"),
        answer=gold["answer"],
        marker=gold["random_string_to_prepend"],
        stop_condition=stopped,
        trace_ok=bool(raw.get("ok") and len(traces) == 1),
        trace_errors=trace_errors,
        returned_root_actions=root,
        returned_child_actions=child,
        native_mapping_complete=mapping_complete,
    )
    nodes = trace.get("nodes") or []
    tool_results = [
        str((node.get("message") or {}).get("content") or "")
        for node in nodes
        if (node.get("message") or {}).get("role") == "tool"
    ]
    usage = [call.get("usage") or {} for call in committed]
    return {
        **classified,
        "terminal_status": stopped,
        "root_reply": trace.get("root_reply"),
        "root_reply_sha256": study.digest(trace.get("root_reply"))
        if trace.get("root_reply") is not None
        else None,
        "trace_id": trace_id,
        "error_types": [error.get("type") for error in trace_errors],
        "native_attempts": len(audits),
        "native_returned": len(returned),
        "native_errors": len(audit_errors),
        "trace_call_entries": len(calls),
        "trace_committed_calls": len(committed),
        "trace_ambiguous_calls": len(ambiguous_calls),
        "native_mapping_complete": mapping_complete,
        "root_actions_returned": root,
        "child_actions_returned": child,
        "total_actions_returned": len(returned),
        "six_total_root_child_cap_respected": total_cap_respected,
        "delegated": child > 0,
        "action_tokens": sum(row["evidence"]["action_tokens"] for row in returned),
        "prompt_tokens": sum(item.get("prompt_tokens", 0) for item in usage),
        "completion_tokens": sum(item.get("completion_tokens", 0) for item in usage),
        "context_json_mentions_in_tools": sum("context.json" in value for value in tool_results),
    }


def summarize(records):
    groups = []
    for source in study.selected():
        rows = [row for row in records if row["coordinate"]["record_id"] == source["id"]]
        rewards = [
            row["derived"]["reward"]
            for row in rows
            if row["derived"]["scientifically_available"]
        ]
        groups.append(
            {
                "record_id": source["id"],
                "recorded": len(rows),
                "scientifically_available": len(rewards),
                "rewards": rewards,
                "mixed": len({round(value, 12) for value in rewards}) >= 2,
                "reward_range": max(rewards) - min(rewards) if rewards else None,
            }
        )
    available = [
        row["derived"]
        for row in records
        if row["derived"]["scientifically_available"]
    ]
    rewards = [row["reward"] for row in available]
    infrastructure = sum(
        row["derived"]["failure_class"] == "infrastructure_unavailable" for row in records
    )
    mixed = sum(group["mixed"] for group in groups)
    mean = sum(rewards) / len(rewards) if rewards else None
    complete = len(records) == 32
    eligible = bool(
        complete
        and len(available) == 32
        and infrastructure == 0
        and mixed >= 2
        and mean is not None
        and mean < 0.90
        and all(row["derived"]["six_total_root_child_cap_respected"] for row in records)
    )
    delegated = [row for row in available if row["delegated"]]
    root_only = [row for row in available if not row["delegated"]]
    return {
        "schema": "openai-mrcr-short32-base-calibration-result-v1",
        "complete": complete,
        "planned": 32,
        "recorded": len(records),
        "scientifically_available": len(available),
        "infrastructure_unavailable": infrastructure,
        "model_finite_horizon": sum(
            row["derived"]["failure_class"] == "model_finite_horizon" for row in records
        ),
        "model_invalid_terminal": sum(
            row["derived"]["failure_class"] == "model_invalid_terminal" for row in records
        ),
        "mean_reward_available": mean,
        "mixed_groups": mixed,
        "groups": groups,
        "native_accounting": {
            "attempted_audit_boundaries": sum(row["derived"]["native_attempts"] for row in records),
            "confirmed_returned_responses": sum(row["derived"]["native_returned"] for row in records),
            "error_results": sum(row["derived"]["native_errors"] for row in records),
            "ambiguous_trace_entries": sum(
                row["derived"]["trace_ambiguous_calls"] for row in records
            ),
            "root_actions_returned": sum(row["derived"]["root_actions_returned"] for row in records),
            "child_actions_returned": sum(row["derived"]["child_actions_returned"] for row in records),
            "action_tokens": sum(row["derived"]["action_tokens"] for row in records),
            "wrapper_retries": 0,
            "harness_retry_configuration": 0,
            "harness_max_completed_turns_cumulative_root_child_per_episode": 6,
        },
        "delegation_observation": {
            "not_a_causal_arm_comparison": True,
            "delegated_trajectories": len(delegated),
            "nondelegated_trajectories": len(root_only),
            "mean_reward_delegated": sum(row["reward"] for row in delegated) / len(delegated)
            if delegated
            else None,
            "mean_reward_nondelegated": sum(row["reward"] for row in root_only) / len(root_only)
            if root_only
            else None,
        },
        "future_root_rl_gate": {
            "eligible": eligible,
            "requirements": {
                "exact_inventory": 32,
                "all_scientifically_available": True,
                "infrastructure_unavailable": 0,
                "mixed_groups_at_least": 2,
                "mean_reward_below": 0.90,
                "six_total_root_child_cap_respected": True,
                "clean_owner_release_required_externally": True,
            },
        },
        "claim_boundary": (
            "Eight frozen training contexts only; heldout16 untouched. Delegation subgroup is "
            "observational and base-pretraining exposure is unknown."
        ),
    }


async def run(spec_path, endpoint_path, output, deadline):
    from verifiers.v1.env import RunSlot
    from verifiers.v1.episode import EvalRunInfo, GroupInfo

    spec = study.read(spec_path)
    if spec != study.read(study.SPEC) or study.sha(spec_path) != study.sha(study.SPEC):
        raise ValueError("actual specification differs from sealed source")
    endpoint = study.read(endpoint_path)
    if endpoint.get("model_alias") != study.MODEL_ALIAS or endpoint.get("adapter") is not None:
        raise ValueError("actual endpoint is not the base no-adapter model")
    if Path(endpoint["base_model"]["path"]).resolve() != study.MODEL.resolve():
        raise ValueError("actual endpoint base path changed")
    if not os.environ.get(endpoint["api_key_env"]):
        raise ValueError("private endpoint credential missing")
    output.mkdir(parents=True, exist_ok=False)
    study.write_x(output / "SPEC.json", spec)
    os.environ["PATH"] = str(study.RUNTIME_BIN) + os.pathsep + os.environ.get("PATH", "")
    os.environ.setdefault("VERIFIERS_CACHE_DIR", "/project/alex_phd/cache/verifiers-prime")
    env = study.environment(study.INPUTS)
    tasks = {task.data.name: task for task in env.taskset}
    gold = study.read(study.INPUTS / "HOST_GOLD.json")
    records = []
    lock = asyncio.Lock()
    queue = asyncio.Queue()
    for coordinate in study.plan():
        queue.put_nowait(coordinate)
    run_id = str(uuid4())
    recorder = v7_recorder()
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
            raw = {
                "ok": False,
                "errors": [{"type": "TimeoutError", "message": "coordinate deadline censored"}],
                "traces": [trace.to_record() for trace in slot.traces],
            }
        except BaseException as error:
            raw = {
                "ok": False,
                "errors": [{"type": type(error).__name__, "message": str(error)}],
                "traces": [trace.to_record() for trace in slot.traces],
            }
        record = {
            "schema": "openai-mrcr-short32-base-episode-v1",
            "coordinate": coordinate,
            "episode": raw,
            "episode_sha256": study.digest(raw),
            "derived": inspect_trace(
                raw, gold[coordinate["record_id"]], native_rows, censored=censored
            ),
            "timing": {"started": started, "ended": time.time()},
        }
        study.write_x(output / "episodes" / (coordinate["id"] + ".json"), record)
        async with lock:
            records.append(record)
            study.write_x(output / "progress" / f"{len(records):03d}.json", summarize(records))

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

    with recorder.native_checkpoints(output / "native-calls", study.MODEL_ALIAS) as rows:
        native_rows = rows
        async with env.serving():
            workers = [asyncio.create_task(worker()) for _ in range(4)]
            try:
                await asyncio.wait_for(
                    asyncio.gather(*workers), max(0.001, deadline - time.time())
                )
            except TimeoutError:
                for task in workers:
                    task.cancel()
                await asyncio.gather(*workers, return_exceptions=True)
    missing = [
        row["id"]
        for row in study.plan()
        if row["id"] not in {record["coordinate"]["id"] for record in records}
    ]
    result = {
        **summarize(records),
        "missing_coordinates": missing,
        "native_start_files": len(list((output / "native-calls").glob("*-start.json"))),
        "native_result_files": len(list((output / "native-calls").glob("*-result.json"))),
    }
    study.write_x(output / "RESULT.json", result)
    return 0 if result["complete"] else 3


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--spec", type=Path, required=True)
    parser.add_argument("--endpoint", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--deadline", type=float, required=True)
    args = parser.parse_args()
    raise SystemExit(asyncio.run(run(args.spec, args.endpoint, args.output, args.deadline)))
