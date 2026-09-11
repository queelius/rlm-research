"""Single-endpoint, paired EvalClient/TrainClient qualification; never launches a GPU."""

from __future__ import annotations

import argparse
import asyncio
import hashlib
import importlib.metadata
import json
import math
import os
import platform
import subprocess
import sys
import tempfile
import time
import traceback
import urllib.request
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any
from uuid import NAMESPACE_URL, uuid5

ROOT = Path(__file__).resolve().parent
SIDECARS = ROOT.parent
OLD = SIDECARS / "strict-rlm-temperature-adherence-v1"
STRICT = SIDECARS / "prime-rlm-strict-pilot-v1"
OFFICIAL = SIDECARS / "official-rlm-prime-pilot-v1"
OFFICIAL_RLM = Path("/project/alex_phd/research-cache/repos/rlm")
ROOTLESS = SIDECARS / "rootless-runtime-feasibility-v1"
PRIME = Path("/project/alex_phd/research-cache/repos/prime-rl")

for source in reversed(
    [
        OLD / "src",
        STRICT / "src",
        OFFICIAL / "src",
        OFFICIAL_RLM,
        OFFICIAL_RLM / "training/src",
        OFFICIAL_RLM / "training/environments/oolong",
    ]
):
    sys.path.insert(0, str(source))

from strict_rlm_temperature_adherence_v1.checkpoint import CheckpointStore  # noqa: E402
from strict_rlm_temperature_adherence_v1.metrics import derive_metrics  # noqa: E402


def digest(value: Any) -> str:
    return hashlib.sha256(
        json.dumps(value, sort_keys=True, separators=(",", ":")).encode()
    ).hexdigest()


def file_hash(path: Path) -> str:
    with path.open("rb") as handle:
        return hashlib.file_digest(handle, "sha256").hexdigest()


def atomic_json(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, name = tempfile.mkstemp(prefix=f".{path.name}.", dir=path.parent)
    temporary = Path(name)
    try:
        with os.fdopen(fd, "w") as handle:
            json.dump(value, handle, indent=2, sort_keys=True, allow_nan=False)
            handle.write("\n")
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temporary, path)
    finally:
        temporary.unlink(missing_ok=True)


def build_plan(task_names: list[str], repeats: int = 2) -> list[dict[str, Any]]:
    if len(task_names) != 16 or len(set(task_names)) != 16 or repeats not in (1, 2):
        raise ValueError("qualification requires 16 frozen source tasks and one or two repeats")
    plan = []
    for task_index, position in enumerate((0, 1, 7, 13)):
        task_name = task_names[position]
        for repeat in range(repeats):
            seed = int(
                digest(["strict-rlm-client-qualification-v2", task_name, repeat])[:8], 16
            ) % (2**31 - 1)
            temperatures = (0.0, 0.5, 1.0) if (task_index + repeat) % 2 == 0 else (1.0, 0.5, 0.0)
            for temperature in temperatures:
                pair = {
                    "task_name": task_name,
                    "temperature": temperature,
                    "repeat": repeat,
                    "seed": seed,
                }
                pair_id = digest(pair)
                client_order = (
                    ("eval", "train")
                    if (task_index + repeat + int(temperature * 2)) % 2 == 0
                    else ("train", "eval")
                )
                for pair_order, client_path in enumerate(client_order):
                    identity = {
                        **pair,
                        "client_path": client_path,
                        "study": "strict-rlm-client-qualification-v2",
                    }
                    plan.append(
                        {
                            **identity,
                            "id": digest(identity),
                            "pair_id": pair_id,
                            "group_id": digest([task_name, temperature, client_path]),
                            "pair_order": pair_order,
                            "dispatch_order": len(plan),
                            "task_position": position,
                        }
                    )
    return plan


def make_context(endpoint: dict[str, Any], row: dict[str, Any]) -> Any:
    from renderers import Qwen3RendererConfig
    from verifiers.v1.clients import ModelContext
    from verifiers.v1.configs.client import EvalClientConfig, TrainClientConfig
    from verifiers.v1.types import SamplingConfig

    common = {"base_url": endpoint["url"], "api_key_var": endpoint["api_key_env"]}
    if row["client_path"] == "train":
        client = TrainClientConfig(
            **common,
            renderer=Qwen3RendererConfig(enable_thinking=False),
            renderer_model_name=endpoint["renderer_model"],
            multiplex=256,
        )
    elif row["client_path"] == "eval":
        client = EvalClientConfig(**common)
    else:
        raise ValueError("unknown client path")
    return ModelContext(
        model=endpoint["model"],
        client=client,
        sampling=SamplingConfig.model_validate(
            {
                "temperature": row["temperature"],
                "top_p": 1.0,
                "seed": row["seed"],
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


def request_metadata(endpoint: dict[str, Any], row: dict[str, Any]) -> dict[str, Any]:
    train = row["client_path"] == "train"
    return {
        "client": row["client_path"],
        "endpoint_url": endpoint["url"],
        "model": endpoint["model"],
        "temperature": row["temperature"],
        "seed": row["seed"],
        "top_p": 1.0,
        "top_k": -1,
        "min_p": 0.0,
        "return_token_ids": True,
        "cache_salt": "0",
        "max_tokens": 2048,
        "parallel_tool_calls": False,
        "renderer": {"name": "qwen3", "enable_thinking": False} if train else None,
        "route": "/inference/v1/generate" if train else "/v1/chat/completions",
        "client_added_options": {
            "logprobs": 1,
            "skip_special_tokens": False,
            "stop_token_ids": "renderer-derived",
        }
        if train
        else {},
        "effective_call_settings": (
            "Retained verbatim in episode.traces[].calls[].sampling and endpoint."
        ),
    }


def episode_metrics(episode: dict[str, Any], wall_seconds: float | None = None) -> dict[str, Any]:
    result = derive_metrics(episode, wall_seconds)
    traces = episode.get("traces") or []
    nodes = [node for trace in traces for node in trace.get("nodes", [])]
    sampled = [node for node in nodes if node.get("sampled") is True]
    capture_valid = bool(sampled)
    sampled_tokens = 0
    sampled_logprobs = 0
    for node in nodes:
        ids, mask, logs = (node.get(key) or [] for key in ("token_ids", "mask", "logprobs"))
        valid = (
            len(ids) == len(mask)
            and all(type(token) is int and token >= 0 for token in ids)
            and all(type(flag) is bool for flag in mask)
            and len(logs) == sum(mask)
            and all(type(value) in (int, float) and math.isfinite(value) for value in logs)
        )
        if node.get("sampled"):
            valid = valid and sum(mask) > 0
            sampled_tokens += sum(mask)
            sampled_logprobs += len(logs)
        elif any(mask):
            valid = False
        capture_valid = capture_valid and valid
    calls = [call for trace in traces for call in trace.get("calls", [])]
    for trace in traces:
        local_nodes = trace.get("nodes", [])
        for call in trace.get("calls", []):
            index = call.get("node")
            if not call.get("error") and (
                type(index) is not int
                or not 0 <= index < len(local_nodes)
                or local_nodes[index].get("sampled") is not True
            ):
                capture_valid = False
    python_ids = set()
    structured = 0
    executed = 0
    for trace in traces:
        for node in trace.get("nodes", []):
            message = node.get("message") or {}
            for call in message.get("tool_calls") or []:
                name = call.get("name") or (call.get("function") or {}).get("name")
                if name == "ipython":
                    structured += 1
                    if call.get("id"):
                        python_ids.add(call["id"])
            if message.get("role") == "tool" and (
                message.get("name") == "ipython" or message.get("tool_call_id") in python_ids
            ):
                executed += 1
    scored = bool(traces) and "score" in (traces[-1].get("rewards", {}).get("correctness") or {})
    observable = (
        result["execution_completed"] and result["strict_terminal_valid"] is not None and scored
    )
    reward = int(result["strict_correct"]) if observable else None
    result.update(
        {
            "trace_trainable": bool(capture_valid),
            "terminal_observable": bool(observable),
            "strict_reward": reward,
            "update_eligible": bool(observable and capture_valid),
            "structured_ipython_calls": structured,
            "executed_ipython_calls": executed,
            "python_used": executed > 0,
            "sampled_nodes": len(sampled),
            "sampled_tokens": sampled_tokens,
            "selected_token_logprobs": sampled_logprobs,
            "model_calls": len(calls),
            "trace_count": len(traces),
            "actual_call_endpoints": dict(Counter(str(call.get("endpoint")) for call in calls)),
            "truncated_calls": sum(call.get("finish_reason") == "length" for call in calls),
        }
    )
    return result


def load_inputs(
    args: argparse.Namespace,
) -> tuple[dict[str, Any], list[dict[str, Any]], dict[str, Any]]:
    from oolong_prime_rlm_strict_v1.taskset import StrictOolongConfig, StrictOolongTaskset

    source_spec = json.loads((OLD / "data/SPEC.json").read_text())
    for row in source_spec["required_files"]:
        if Path(row["path"]) == ROOTLESS / "MANIFEST.json":
            continue  # A newly inspected runtime image replaces the vanished September 2 image.
        if file_hash(Path(row["path"])) != row["sha256"]:
            raise ValueError(f"frozen source hash mismatch: {row['path']}")
    tasks = list(StrictOolongTaskset(StrictOolongConfig(split="train")).load())
    actual = [{"name": task.data.name, "key": task.key, "hash": task.hash} for task in tasks]
    expected = [{key: row[key] for key in ("name", "key", "hash")} for row in source_spec["tasks"]]
    if actual != expected:
        raise ValueError("strict task identities changed")
    descriptor = json.loads(args.endpoint_descriptor.read_text())
    endpoint = {
        "url": (
            args.endpoint_url
            or descriptor.get("url")
            or f"http://{descriptor.get('host', '127.0.0.1')}:{descriptor['port']}/v1"
        ).rstrip("/"),
        "model": args.model or descriptor["model_alias"],
        "api_key_env": args.api_key_env,
        "renderer_model": args.renderer_model or descriptor["base_model"]["path"],
    }
    if (
        endpoint["model"] != descriptor["model_alias"]
        or endpoint["renderer_model"] != descriptor["base_model"]["path"]
    ):
        raise ValueError("model override must agree with supplied frozen descriptor")
    if not endpoint["url"].startswith(("http://127.0.0.1:", "http://localhost:")):
        raise ValueError("qualification endpoint must be local to this allocated runtime")
    plan = build_plan([task.data.name for task in tasks], args.repeats)
    sources = [
        ROOT / "driver.py",
        ROOT / "SPEC.json",
        OLD / "data/SPEC.json",
        args.endpoint_descriptor,
        OLD / "src/strict_rlm_temperature_adherence_v1/metrics.py",
        OLD / "src/strict_rlm_temperature_adherence_v1/checkpoint.py",
        ROOTLESS / "bin/docker",
        PRIME / "deps/verifiers/verifiers/v1/clients/train.py",
        PRIME / "deps/verifiers/verifiers/v1/clients/eval.py",
    ]
    hashes = {str(path): file_hash(path) for path in sources if path.is_file()}
    versions = {
        name: importlib.metadata.version(name)
        for name in ("verifiers", "renderers", "prime-rl", "vllm", "torch")
    }
    frozen = {
        "schema": "strict-rlm-client-qualification-attempt-v2",
        "design": json.loads((ROOT / "SPEC.json").read_text()),
        "endpoint": endpoint,
        "source_endpoint_descriptor": descriptor,
        "actual_topology": "single endpoint on one operator-owned GPU",
        "source_file_sha256": hashes,
        "frozen_dependencies": source_spec["required_files"],
        "runtime_image": args.image,
        "expected_runtime_image_id": args.image_id,
        "harness": {"id": "rlm", "version": "4ef3438", "max_depth": 1},
        "plan": plan,
        "coordinate_plan_sha256": digest(plan),
        "tasks": [row for row in actual if row["name"] in {item["task_name"] for item in plan}],
        "python": platform.python_version(),
        "versions": versions,
        "max_concurrent_pairs": args.max_concurrent_pairs,
        "wall_time_cap_seconds": args.wall_time_cap_seconds,
        "stop_rule": (
            "Stop above 50% execution errors after 8 attempted episodes, or at wall cap. "
            "Completed malformed policy output is not an execution error."
        ),
    }
    return frozen, plan, {task.data.name: task for task in tasks}


def summarize(records: list[dict[str, Any]], planned: int) -> dict[str, Any]:
    groups: dict[tuple[str, float], list[dict[str, Any]]] = defaultdict(list)
    pairs: dict[str, dict[str, dict[str, Any]]] = defaultdict(dict)
    for row in records:
        coordinate = row["coordinate"]
        groups[(coordinate["client_path"], coordinate["temperature"])].append(row["derived"])
        pairs[coordinate["pair_id"]][coordinate["client_path"]] = row["derived"]
    cells = []
    for (client, temperature), rows in sorted(groups.items()):
        cells.append(
            {
                "client_path": client,
                "temperature": temperature,
                "episodes": len(rows),
                **{
                    key: sum(bool(row.get(key)) for row in rows)
                    for key in (
                        "execution_completed",
                        "trace_trainable",
                        "update_eligible",
                        "python_used",
                        "ipython_intent_in_content",
                        "strict_terminal_valid",
                        "strict_correct",
                    )
                },
                "strict_rewards": dict(Counter(str(row["strict_reward"]) for row in rows)),
                "error_types": dict(Counter(kind for row in rows for kind in row["error_types"])),
                "completion_tokens": sum(row["completion_tokens"] for row in rows),
                "prompt_tokens": sum(row["prompt_tokens"] for row in rows),
            }
        )
    comparisons = []
    for pair_id, pair in sorted(pairs.items()):
        if set(pair) == {"train", "eval"}:
            comparisons.append(
                {
                    "pair_id": pair_id,
                    "both_execution_completed": all(
                        row["execution_completed"] for row in pair.values()
                    ),
                    **{
                        f"{key}_train_minus_eval": int(bool(pair["train"][key]))
                        - int(bool(pair["eval"][key]))
                        for key in ("python_used", "strict_terminal_valid", "strict_correct")
                    },
                }
            )
    return {"planned": planned, "recorded": len(records), "cells": cells, "paired": comparisons}


async def run(
    args: argparse.Namespace,
    frozen: dict[str, Any],
    plan: list[dict[str, Any]],
    tasks: dict[str, Any],
) -> int:
    from verifiers.v1.env import RunSlot
    from verifiers.v1.envs.single_agent import SingleAgentEnv, SingleAgentEnvConfig
    from verifiers.v1.episode import EvalRunInfo, GroupInfo

    endpoint = frozen["endpoint"]
    if not os.environ.get(endpoint["api_key_env"]):
        raise ValueError(f"missing API key environment variable: {endpoint['api_key_env']}")
    image_id = subprocess.run(
        [str(ROOTLESS / "bin/docker"), "image", "inspect", args.image, "--format", "{{.Id}}"],
        capture_output=True,
        text=True,
        check=True,
        timeout=30,
    ).stdout.strip()
    if image_id != args.image_id:
        raise ValueError(f"runtime image identity differs: {image_id}")
    frozen["observed_runtime_image_id"] = image_id
    request = urllib.request.Request(
        endpoint["url"] + "/models",
        headers={"Authorization": f"Bearer {os.environ[endpoint['api_key_env']]}"},
    )
    with urllib.request.urlopen(request, timeout=10) as response:
        advertised = json.load(response)
    if endpoint["model"] not in {row.get("id") for row in advertised.get("data", [])}:
        raise ValueError("endpoint does not advertise the frozen adapter")
    frozen["advertised_models"] = sorted(row.get("id") for row in advertised["data"])
    specification = args.output_dir / "SPEC.json"
    if args.resume:
        if not specification.is_file() or json.loads(specification.read_text()) != frozen:
            raise ValueError("resume requires byte-equivalent inputs and runtime identity")
    elif args.output_dir.exists():
        raise ValueError("output directory already exists; use a new attempt or --resume")
    else:
        atomic_json(specification, frozen)
    store = CheckpointStore(args.output_dir)
    records = store.records()
    completed = {row["coordinate"]["id"] for row in records}
    if completed - {row["id"] for row in plan}:
        raise ValueError("output contains coordinates outside this plan")
    environment = SingleAgentEnv(
        SingleAgentEnvConfig.model_validate(
            {
                "taskset": {"id": "oolong-prime-rlm-strict-v1", "split": "train"},
                "timeout": {"episode": 1020, "finalize": 60},
                "interception": {"type": "server"},
                "agent": {
                    "harness": {"id": "rlm", "version": "4ef3438", "max_depth": 1},
                    "runtime": {"type": "docker", "image": args.image, "workdir": "/app"},
                    "timeout": {"setup": 300, "rollout": 900, "finalize": 60, "scoring": 60},
                    "retries": {"max_retries": 0},
                },
                "retries": {"max_retries": 0},
            }
        )
    )
    grouped: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in plan:
        grouped[row["pair_id"]].append(row)
    queue: asyncio.Queue[list[dict[str, Any]]] = asyncio.Queue()
    for pair in grouped.values():
        queue.put_nowait(pair)
    started = time.monotonic()
    stop_reason = None
    run_id = str(uuid5(NAMESPACE_URL, str(args.output_dir.resolve())))

    async def one(row: dict[str, Any]) -> None:
        nonlocal stop_reason
        begin = time.time()
        task = tasks[row["task_name"]]
        try:
            episode = await environment.run_slot(RunSlot(task), make_context(endpoint, row))
            episode.group = GroupInfo(id=row["group_id"])
            episode.record_run(EvalRunInfo(id=run_id, name="strict-rlm-client-qualification-v2"))
            raw = episode.to_record()
        except Exception as error:
            raw = {
                "ok": False,
                "errors": [
                    {
                        "type": type(error).__name__,
                        "message": str(error),
                        "traceback": traceback.format_exc(),
                    }
                ],
                "traces": [],
            }
        ended = time.time()
        record = {
            "schema": "strict-rlm-client-qualification-episode-v2",
            "coordinate": row,
            "request": request_metadata(endpoint, row),
            "episode": raw,
            "episode_sha256": digest(raw),
            "task_identity": {"key": task.key, "hash": task.hash, "name": task.data.name},
            "timing": {"started": begin, "ended": ended, "wall_seconds": ended - begin},
            "derived": episode_metrics(raw, ended - begin),
        }
        store.write(record)
        records.append(record)
        completed.add(row["id"])
        failures = sum(not item["derived"]["execution_completed"] for item in records)
        if len(records) >= 8 and failures / len(records) > 0.5:
            stop_reason = "execution_error_rate_above_50pct_after_8"
        atomic_json(args.output_dir / "analysis.json", summarize(records, len(plan)))
        print(
            json.dumps(
                {
                    "completed": len(records),
                    "planned": len(plan),
                    "coordinate": row,
                    "derived": record["derived"],
                },
                sort_keys=True,
            ),
            flush=True,
        )

    async def worker() -> None:
        nonlocal stop_reason
        while not queue.empty() and stop_reason is None:
            if time.monotonic() - started >= args.wall_time_cap_seconds:
                stop_reason = "wall_time_cap"
                return
            try:
                pair = queue.get_nowait()
            except asyncio.QueueEmpty:
                return
            for row in pair:
                if row["id"] not in completed and stop_reason is None:
                    await one(row)
            queue.task_done()

    try:
        async with environment.serving():
            await asyncio.wait_for(
                asyncio.gather(*(worker() for _ in range(args.max_concurrent_pairs))),
                timeout=args.wall_time_cap_seconds,
            )
    except TimeoutError:
        stop_reason = "wall_time_cap"
    finally:
        status = {
            "planned": len(plan),
            "completed": len(records),
            "stop_reason": stop_reason,
            "wall_seconds": time.monotonic() - started,
        }
        atomic_json(args.output_dir / "STATUS.json", status)
        atomic_json(args.output_dir / "analysis.json", summarize(records, len(plan)))
    print(json.dumps(status, sort_keys=True), flush=True)
    return 0 if len(records) == len(plan) else 3


def main() -> int:
    design = json.loads((ROOT / "SPEC.json").read_text())
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--endpoint-url")
    parser.add_argument(
        "--endpoint-descriptor", type=Path, default=OLD / "configs/endpoint-replica0.json"
    )
    parser.add_argument("--model")
    parser.add_argument("--renderer-model")
    parser.add_argument("--api-key-env", default="STRICT_RLM_CALIBRATION_API_KEY")
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--repeats", type=int, choices=(1, 2), default=2)
    parser.add_argument("--max-concurrent-pairs", type=int, choices=(1, 2, 4), default=2)
    parser.add_argument("--wall-time-cap-seconds", type=float, default=5400)
    parser.add_argument("--image", default=design["container_image"])
    parser.add_argument("--image-id", default=design["container_image_id"])
    parser.add_argument("--resume", action="store_true")
    parser.add_argument(
        "--preflight",
        action="store_true",
        help="Authenticate inputs; no endpoint or container contact and no writes",
    )
    args = parser.parse_args()
    if args.wall_time_cap_seconds <= 0:
        parser.error("wall cap must be positive")
    os.environ["PATH"] = str(ROOTLESS / "bin") + os.pathsep + os.environ.get("PATH", "")
    os.environ.setdefault("VERIFIERS_CACHE_DIR", "/project/alex_phd/cache/verifiers-prime")
    frozen, plan, tasks = load_inputs(args)
    if args.preflight:
        print(
            json.dumps(
                {
                    "ok": True,
                    "episodes": len(plan),
                    "plan_sha256": digest(plan),
                    "endpoint": frozen["endpoint"],
                    "image_id": args.image_id,
                    "versions": frozen["versions"],
                },
                indent=2,
            )
        )
        return 0
    return asyncio.run(run(args, frozen, plan, tasks))


if __name__ == "__main__":
    raise SystemExit(main())
