"""CPU-prepared task-procedure crossover; connects to ONE existing local server only."""

from __future__ import annotations

import argparse
import ast
import asyncio
import hashlib
import importlib.metadata
import importlib.util
import json
import os
import platform
import random
import subprocess
import time
import traceback
import urllib.request
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any
from uuid import NAMESPACE_URL, uuid5

ROOT = Path(__file__).resolve().parent
STUDY = ROOT.name
QUAL = ROOT.parent / "strict-rlm-client-qualification-v2"
SNAPSHOT = Path("/project/alex_phd/research-cache/2026-09-08-literature/plan-hint-prompt.HoZuFs")
NANO_REVISION = "4ef3438d55fdd39b18d34035833c73e13b006733"
IMAGE = "localhost/verifiers-rlm-python:3.11-slim-single-id-v1"
IMAGE_ID = "sha256:53a70288e91a75c9bc8cbc9a75da4c3d156227266fd8c6c997deb8ef7f921552"
QUAL_SHA256 = "757d98441666769785e30fac39a18fe46bf83e8ee3ca73b13a31d09bf79534a7"
if hashlib.sha256((QUAL / "driver.py").read_bytes()).hexdigest() != QUAL_SHA256:
    raise ValueError("qualification helper source changed; review before a new freeze")
_loader = importlib.util.spec_from_file_location("qualification_for_hint", QUAL / "driver.py")
q = importlib.util.module_from_spec(_loader)
_loader.loader.exec_module(q)

SELECTED = {
    "train": (12000008, 12000009, 12000010, 12000023, 12000024, 12000025, 12000029),
    "eval": (12000006, 12000007, 12000037, 12000044, 12000045, 12000046, 12000050),
}
EXCLUDED = {
    "answer_revealing_single_allowed_label": [12000030, 12000031, 12000052],
    "development_task_type_balance_not_outcome_selection": [
        12000014,
        12000017,
        12000020,
        12000022,
        12000026,
        12000027,
        12000028,
    ],
}
MINIMAL_FILE = (
    "The full context is stored in context.txt in your current working directory. "
    "Do not guess from the question alone. Return the requested final answer format."
)
PROCEDURE = (
    "Suggested procedure: First inspect context.txt and parse each Date/User/Instance record. "
    "Read the aggregate question to decide which records and fields are relevant. If the answer "
    "needs only user IDs, count them directly in Python. If semantic labels are needed, "
    "partition the relevant records into batches, use recursive rlm calls to assign exactly "
    "one of the six labels to each record, store the assignments with record indices, then "
    "use Python to compute the requested exact aggregate. Check that every relevant record "
    "has one assignment before giving the final answer. Do not replace classification "
    "with keyword guessing."
)


def load_tasks() -> dict[str, Any]:
    from oolong_prime_rlm_strict_v1.taskset import StrictOolongConfig, StrictOolongTaskset

    result = {}
    contexts = {}
    for split, ids in SELECTED.items():
        tasks = {
            task.data.source_id: task
            for task in StrictOolongTaskset(StrictOolongConfig(split=split)).load()
        }
        contexts[split] = set()
        for source_id in ids:
            task = tasks[source_id]
            if task.data.system_prompt is not None:
                raise ValueError("unexpected task-level system prompt")
            result[task.data.name] = task
            contexts[split].add(hashlib.sha256(task.data.context.encode()).hexdigest())
    if contexts["train"] & contexts["eval"] or any(len(x) != 1 for x in contexts.values()):
        raise ValueError("expected exactly two disjoint source context windows")
    return result


def with_prompt(task: Any, arm: str) -> Any:
    from oolong_prime_v1.taskset import _RLM_FILE_INSTRUCTION

    if arm not in ("minimal", "procedure"):
        raise ValueError("unknown prompt arm")
    if task.data.prompt.count(_RLM_FILE_INSTRUCTION) != 1:
        raise ValueError("original task instruction no longer matches audited text")
    replacement = MINIMAL_FILE + ("\n\n" + PROCEDURE if arm == "procedure" else "")
    prompt = task.data.prompt.replace(_RLM_FILE_INSTRUCTION, replacement, 1)
    return type(task)(task.data.model_copy(update={"prompt": prompt}), task.config)


def build_plan(tasks: dict[str, Any]) -> list[dict[str, Any]]:
    pairs = []
    for index, (name, task) in enumerate(tasks.items()):
        for repeat in range(2):
            pair = {
                "study": STUDY,
                "task_name": name,
                "source_id": task.data.source_id,
                "analysis_split": "development" if ":train:" in name else "source_heldout",
                "context_window_id": task.data.context_window_id,
                "context_sha256": hashlib.sha256(task.data.context.encode()).hexdigest(),
                "repeat": repeat,
                "seed": int(q.digest([STUDY, name, repeat])[:8], 16) % (2**31 - 1),
                "temperature": 0.5,
                "client_path": "eval",
            }
            order = (
                ("minimal", "procedure") if (index + repeat) % 2 == 0 else ("procedure", "minimal")
            )
            pair_id = q.digest(pair)
            pairs.append(
                [
                    {
                        **pair,
                        "arm": arm,
                        "id": q.digest([pair, arm]),
                        "pair_id": pair_id,
                        "pair_order": position,
                        "group_id": q.digest([STUDY, name, arm]),
                        "task_hash": with_prompt(task, arm).hash,
                    }
                    for position, arm in enumerate(order)
                ]
            )
    random.Random(20260908).shuffle(pairs)
    plan = [row for pair in pairs for row in pair]
    return [{**row, "dispatch_order": index} for index, row in enumerate(plan)]


def crossover_metrics(episode: dict[str, Any], wall_seconds: float | None) -> dict[str, Any]:
    result = q.episode_metrics(episode, wall_seconds)
    traces = episode.get("traces") or []
    usages = [call.get("usage") or {} for trace in traces for call in trace.get("calls", [])]
    for key in ("prompt_tokens", "completion_tokens", "cached_input_tokens"):
        result[key] = sum(int(usage.get(key, 0) or 0) for usage in usages)
    result["logical_input_tokens"] = result["prompt_tokens"] + result["cached_input_tokens"]
    result["cost_scope"] = "all retained trace call records; prompt excludes cached input"
    inspected = recursive = False
    inspected_calls = recursive_calls = 0
    system_hashes = set()
    for trace in traces:
        pending = {}
        for node in trace.get("nodes", []):
            message = node.get("message") or {}
            if message.get("role") == "system":
                system_hashes.add(q.digest(message.get("content")))
            for call in message.get("tool_calls") or []:
                function = call.get("function") or call
                if function.get("name") == "ipython" and call.get("id"):
                    arguments = function.get("arguments") or {}
                    if isinstance(arguments, str):
                        try:
                            arguments = json.loads(arguments)
                        except json.JSONDecodeError:
                            arguments = {}
                    pending[call["id"]] = (
                        arguments.get("code", "") if isinstance(arguments, dict) else ""
                    )
            if message.get("role") != "tool":
                continue
            code = pending.pop(message.get("tool_call_id"), "")
            if not isinstance(code, str):
                continue
            # Executed-cell marker, not proof the read completed or informed the answer.
            read_marker = "context.txt" in code and any(
                marker in code
                for marker in ("open(", "read_text(", "read_csv(", "cat ", "head ", "readlines(")
            )
            recursive_marker = False
            try:
                tree = ast.parse(code, mode="exec")
                recursive_marker = any(
                    isinstance(item, ast.Call)
                    and isinstance(item.func, ast.Name)
                    and item.func.id == "rlm"
                    for item in ast.walk(tree)
                )
            except SyntaxError:
                pass  # IPython magics are not Python; do not infer recursion from prose.
            inspected |= read_marker
            recursive |= recursive_marker
            inspected_calls += int(read_marker)
            recursive_calls += int(recursive_marker)
    result.update(
        {
            "inspection_executed_proxy": inspected,
            "inspection_executed_cells": inspected_calls,
            "recursive_call_code_executed_proxy": recursive,
            "recursive_call_code_executed_cells": recursive_calls,
            "decomposition_observed": result["recursive_subcalls"] > 0,
            "observed_system_prompt_sha256": sorted(system_hashes),
        }
    )
    return result


def environment_config() -> dict[str, Any]:
    return {
        "taskset": {"id": "oolong-prime-rlm-strict-v1", "split": "train"},
        "timeout": {"episode": 1020, "finalize": 60},
        "interception": {"type": "server"},
        "agent": {
            "harness": {"id": "rlm", "version": "4ef3438", "max_depth": 1},
            "runtime": {"type": "docker", "image": IMAGE, "workdir": "/app"},
            "timeout": {"setup": 300, "rollout": 900, "finalize": 60, "scoring": 60},
            "retries": {"max_retries": 0},
        },
        "retries": {"max_retries": 0},
    }


def normalize_image_id(value: str) -> str:
    digest = value.strip().removeprefix("sha256:")
    if len(digest) != 64 or any(character not in "0123456789abcdef" for character in digest):
        raise ValueError("runtime image identity is not a SHA-256 digest")
    return "sha256:" + digest


def make_spec(
    descriptor_path: Path, weight_condition: str = "pre_update"
) -> tuple[dict[str, Any], dict[str, Any]]:
    from oolong_prime_rlm_strict_v1 import scoring as strict_scoring
    from oolong_prime_rlm_strict_v1 import taskset as strict_taskset
    from oolong_prime_v1 import scoring as source_scoring
    from oolong_prime_v1 import taskset as source_taskset

    tasks = load_tasks()
    plan = build_plan(tasks)
    descriptor = json.loads(descriptor_path.read_text())
    model = Path(descriptor["base_model"]["path"])
    adapter = Path(descriptor["adapter"]["path"])
    checks = {
        model / "local-research-manifest.json": descriptor["base_model"]["manifest_sha256"],
        adapter / "adapter_config.json": descriptor["adapter"]["config_sha256"],
        adapter / "adapter_model.safetensors": descriptor["adapter"]["model_sha256"],
    }
    for path, expected in checks.items():
        if q.file_hash(path) != expected:
            raise ValueError(f"model/adapter identity changed: {path}")
    sources = [
        ROOT / "driver.py",
        QUAL / "driver.py",
        descriptor_path,
        q.OFFICIAL / "data/tasks.jsonl",
        q.OFFICIAL / "data/selection.json",
        *(
            Path(module.__file__)
            for module in (strict_scoring, strict_taskset, source_scoring, source_taskset)
        ),
        q.OLD / "src/strict_rlm_temperature_adherence_v1/metrics.py",
        q.OLD / "src/strict_rlm_temperature_adherence_v1/checkpoint.py",
        q.ROOTLESS / "bin/docker",
        q.PRIME / "deps/verifiers/verifiers/v1/clients/eval.py",
        q.PRIME / "deps/verifiers/verifiers/v1/harnesses/rlm/harness.py",
        model / "tokenizer_config.json",
        model / "config.json",
        *checks,
        SNAPSHOT / "prompt.py",
        SNAPSHOT / "config.py",
        SNAPSHOT / "LICENSE",
    ]
    endpoint = {
        "url": f"http://{descriptor['host']}:{descriptor['port']}/v1",
        "model": descriptor["model_alias"],
        "api_key_env": descriptor["api_key_env"],
        "renderer_model": descriptor["base_model"]["path"],
    }
    task_specs = []
    for task in tasks.values():
        task_specs.append(
            {
                "name": task.data.name,
                "key": task.key,
                "source_hash": task.hash,
                "source_id": task.data.source_id,
                "source_split": task.data.source_split,
                "source_revision": task.data.source_revision,
                "context_window_id": task.data.context_window_id,
                "context_sha256": hashlib.sha256(task.data.context.encode()).hexdigest(),
                "answer_type": task.data.answer_type,
                "task_kind": task.data.task_kind,
                "gold_sha256": q.digest(task.data.answer),
                "original_prompt": task.data.prompt,
                "arms": {
                    arm: {
                        "prompt": with_prompt(task, arm).data.prompt,
                        "task_hash": with_prompt(task, arm).hash,
                    }
                    for arm in ("minimal", "procedure")
                },
            }
        )
    return {
        "schema": STUDY,
        "source_file_sha256": {str(path): q.file_hash(path) for path in sources},
        "endpoint": endpoint,
        "source_endpoint_descriptor": descriptor,
        "environment": environment_config(),
        "image_id": IMAGE_ID,
        "plan": plan,
        "plan_sha256": q.digest(plan),
        "tasks": task_specs,
        "request_template": q.request_metadata(endpoint, plan[0]),
        "max_concurrent_pairs": 4,
        "wall_time_cap_seconds": 5400,
        "exclusions": EXCLUDED,
        "split_provenance": {
            "dataset": "oolongbench/oolong-synth",
            "original_split": "validation",
            "development_context_window": 8,
            "source_heldout_context_window": 6,
            "heldout_is_fresh": False,
            "limitation": (
                "Source-heldout was evaluated September 2; two contexts only, exploratory reuse."
            ),
        },
        "interpretation": (
            "Task-level supplied procedure benefit under shared coding/recursion system guidance; "
            "not free planning."
        ),
        "weight_condition": weight_condition,
        "model_status": (
            "Operator-declared weight condition with frozen model/adapter bytes. Default pre_update "
            "step_0 LoRA has zero updates; post_update requires separate descriptor and SPEC."
        ),
        "nano_source": {
            "repository": "https://github.com/PrimeIntellect-ai/nano-rlm",
            "revision": NANO_REVISION,
        },
        "python": platform.python_version(),
        "versions": {
            name: importlib.metadata.version(name)
            for name in ("verifiers", "renderers", "prime-rl", "vllm", "torch")
        },
    }, tasks


def summarize(records: list[dict[str, Any]], plan: list[dict[str, Any]]) -> dict[str, Any]:
    groups = defaultdict(list)
    pairs = defaultdict(dict)
    for record in records:
        coordinate = record["coordinate"]
        groups[(coordinate["analysis_split"], coordinate["arm"])].append(record["derived"])
        pairs[coordinate["pair_id"]][coordinate["arm"]] = record["derived"]
    cells = []
    for (split, arm), rows in sorted(groups.items()):
        observable = sum(row["strict_reward"] is not None for row in rows)
        correct = sum(row["strict_reward"] == 1 for row in rows)
        cells.append(
            {
                "split": split,
                "arm": arm,
                "recorded": len(rows),
                "observable": observable,
                "strict_successes": correct,
                "success_per_attempt": correct / len(rows),
                "success_per_observable": correct / observable if observable else None,
                **{
                    key: sum(bool(row[key]) for row in rows)
                    for key in (
                        "execution_completed",
                        "python_used",
                        "inspection_executed_proxy",
                        "recursive_call_code_executed_proxy",
                        "decomposition_observed",
                        "strict_terminal_valid",
                    )
                },
                **{
                    key: sum(row[key] or 0 for row in rows)
                    for key in (
                        "completion_tokens",
                        "prompt_tokens",
                        "logical_input_tokens",
                        "wall_seconds",
                        "recursive_subcalls",
                    )
                },
                "error_types": dict(Counter(kind for row in rows for kind in row["error_types"])),
            }
        )
    compared = []
    for pair_id, pair in sorted(pairs.items()):
        if set(pair) == {"minimal", "procedure"}:
            observable = all(row["strict_reward"] is not None for row in pair.values())
            compared.append(
                {
                    "pair_id": pair_id,
                    "both_observable": observable,
                    "strict_success_procedure_minus_minimal": pair["procedure"]["strict_reward"]
                    - pair["minimal"]["strict_reward"]
                    if observable
                    else None,
                    **{
                        key + "_procedure_minus_minimal": pair["procedure"][key]
                        - pair["minimal"][key]
                        for key in ("completion_tokens", "logical_input_tokens", "wall_seconds")
                    },
                }
            )
    done = {record["coordinate"]["id"] for record in records}
    return {
        "planned": len(plan),
        "recorded": len(records),
        "cells": cells,
        "paired": compared,
        "unrun_coordinates": [row["id"] for row in plan if row["id"] not in done],
        "caution": (
            "Two independent context groups, not 56 independent tasks; "
            "execution errors are null rewards."
        ),
    }


async def run(args: argparse.Namespace, frozen: dict[str, Any], tasks: dict[str, Any]) -> int:
    from verifiers.v1.env import RunSlot
    from verifiers.v1.envs.single_agent import SingleAgentEnv, SingleAgentEnvConfig
    from verifiers.v1.episode import EvalRunInfo, GroupInfo

    endpoint = {
        **frozen["endpoint"],
        "url": (args.endpoint_url or frozen["endpoint"]["url"]).rstrip("/"),
    }
    if not endpoint["url"].startswith(("http://127.0.0.1:", "http://localhost:")):
        raise ValueError("one existing local inference endpoint is required")
    if not os.environ.get(endpoint["api_key_env"]):
        raise ValueError(f"missing API key environment variable: {endpoint['api_key_env']}")
    image_id = subprocess.run(
        [str(q.ROOTLESS / "bin/docker"), "image", "inspect", IMAGE, "--format", "{{.Id}}"],
        capture_output=True,
        text=True,
        check=True,
        timeout=30,
    ).stdout.strip()
    image_id = normalize_image_id(image_id)
    if image_id != IMAGE_ID:
        raise ValueError("runtime image differs from frozen September 8 image")
    request = urllib.request.Request(
        endpoint["url"] + "/models",
        headers={"Authorization": f"Bearer {os.environ[endpoint['api_key_env']]}"},
    )
    with urllib.request.urlopen(request, timeout=10) as response:
        advertised = json.load(response)
    if endpoint["model"] not in {row.get("id") for row in advertised.get("data", [])}:
        raise ValueError("endpoint does not advertise frozen model alias")
    attempt = {"design_sha256": q.digest(frozen), "endpoint": endpoint, "image_id": image_id}
    output = args.output_dir
    if args.resume:
        prior = json.loads((output / "ATTEMPT.json").read_text())
        if {key: prior[key] for key in attempt} != attempt:
            raise ValueError("resume inputs differ")
        attempt = prior
    elif output.exists():
        raise ValueError("output exists; choose a new attempt or --resume")
    else:
        attempt["started_epoch"] = time.time()
        q.atomic_json(output / "SPEC.json", frozen)
        q.atomic_json(output / "ATTEMPT.json", attempt)
    deadline = attempt["started_epoch"] + frozen["wall_time_cap_seconds"]
    store = q.CheckpointStore(output)
    records = store.records()
    plan = frozen["plan"]
    coordinates = {row["id"]: row for row in plan}
    for record in records:
        if record["coordinate"] != coordinates.get(record["coordinate"]["id"]):
            raise ValueError("checkpoint coordinate does not match frozen plan")
    done = {record["coordinate"]["id"] for record in records}
    queue = asyncio.Queue()
    for offset in range(0, len(plan), 2):
        queue.put_nowait(plan[offset : offset + 2])
    environment = SingleAgentEnv(SingleAgentEnvConfig.model_validate(frozen["environment"]))
    run_id = str(uuid5(NAMESPACE_URL, str(output.resolve())))
    stop_reason = None

    async def one(row: dict[str, Any]) -> None:
        nonlocal stop_reason
        task = with_prompt(tasks[row["task_name"]], row["arm"])
        begin = time.time()
        cancellation = False
        try:
            episode = await environment.run_slot(RunSlot(task), q.make_context(endpoint, row))
            episode.group = GroupInfo(id=row["group_id"])
            episode.record_run(EvalRunInfo(id=run_id, name=STUDY))
            raw = episode.to_record()
        except (Exception, asyncio.CancelledError) as error:
            cancellation = isinstance(error, asyncio.CancelledError)
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
            "schema": STUDY + "-episode",
            "coordinate": row,
            "request": q.request_metadata(endpoint, row),
            "episode": raw,
            "episode_sha256": q.digest(raw),
            "task_identity": {"name": task.data.name, "key": task.key, "hash": task.hash},
            "timing": {"started": begin, "ended": ended, "wall_seconds": ended - begin},
            "budget_censored": cancellation,
            "derived": crossover_metrics(raw, ended - begin),
        }
        store.write(record)
        records.append(record)
        done.add(row["id"])
        failures = sum(not item["derived"]["execution_completed"] for item in records)
        if len(records) >= 8 and failures / len(records) > 0.5:
            stop_reason = "execution_error_rate_above_50pct_after_8"
        q.atomic_json(output / "analysis.json", summarize(records, plan))
        print(
            json.dumps(
                {"recorded": len(records), "coordinate": row, "derived": record["derived"]},
                sort_keys=True,
            ),
            flush=True,
        )
        if cancellation:
            raise asyncio.CancelledError

    async def worker() -> None:
        nonlocal stop_reason
        while not queue.empty() and stop_reason is None:
            pair = queue.get_nowait()
            for row in pair:
                if time.time() >= deadline - 60:
                    stop_reason = "wall_time_cap"
                if row["id"] not in done and stop_reason is None:
                    await one(row)
            queue.task_done()

    try:
        remaining = deadline - time.time() - 60
        if remaining <= 0:
            stop_reason = "wall_time_cap"
        else:
            async with environment.serving():
                await asyncio.wait_for(
                    asyncio.gather(*(worker() for _ in range(frozen["max_concurrent_pairs"]))),
                    timeout=remaining,
                )
    except TimeoutError:
        stop_reason = "wall_time_cap"
    finally:
        status = {
            "planned": len(plan),
            "recorded": len(records),
            "stop_reason": stop_reason,
            "wall_seconds_since_attempt_start": time.time() - attempt["started_epoch"],
            "budget_censored": sum(row["budget_censored"] for row in records),
        }
        q.atomic_json(output / "STATUS.json", status)
        q.atomic_json(output / "analysis.json", summarize(records, plan))
    print(json.dumps(status, sort_keys=True), flush=True)
    return 0 if len(records) == len(plan) else 3


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument("--prepare", action="store_true", help="Freeze once, CPU only")
    mode.add_argument(
        "--preflight", action="store_true", help="Read-only, no endpoint/container contact"
    )
    parser.add_argument(
        "--endpoint-descriptor", type=Path, default=q.OLD / "configs/endpoint-replica0.json"
    )
    parser.add_argument("--spec-path", type=Path, default=ROOT / "SPEC.json")
    parser.add_argument(
        "--weight-condition", choices=("pre_update", "post_update"), default="pre_update"
    )
    parser.add_argument("--endpoint-url", help="Operational local URL override, saved in attempt")
    parser.add_argument("--output-dir", type=Path)
    parser.add_argument("--resume", action="store_true")
    args = parser.parse_args()
    frozen, tasks = make_spec(args.endpoint_descriptor.resolve(), args.weight_condition)
    spec_path = args.spec_path
    if args.prepare:
        if spec_path.exists():
            raise ValueError("immutable SPEC already exists; do not overwrite")
        q.atomic_json(spec_path, frozen)
    elif not spec_path.is_file() or json.loads(spec_path.read_text()) != frozen:
        raise ValueError("frozen SPEC or actual input hashes changed")
    if args.prepare or args.preflight:
        from verifiers.v1.envs.single_agent import SingleAgentEnvConfig

        SingleAgentEnvConfig.model_validate(frozen["environment"])
        context = q.make_context(frozen["endpoint"], frozen["plan"][0])
        if context.client.type != "eval":
            raise ValueError("client must remain eval")
        print(
            json.dumps(
                {
                    "ok": True,
                    "mode": "prepare" if args.prepare else "preflight",
                    "episodes": len(frozen["plan"]),
                    "plan_sha256": frozen["plan_sha256"],
                    "spec_sha256": q.file_hash(spec_path),
                    "client": "eval",
                    "wall_time_cap_seconds": frozen["wall_time_cap_seconds"],
                },
                indent=2,
            )
        )
        return 0
    if args.output_dir is None:
        parser.error("--output-dir is required for a live run")
    os.environ["PATH"] = str(q.ROOTLESS / "bin") + os.pathsep + os.environ.get("PATH", "")
    os.environ.setdefault("VERIFIERS_CACHE_DIR", "/project/alex_phd/cache/verifiers-prime")
    return asyncio.run(run(args, frozen, tasks))


if __name__ == "__main__":
    raise SystemExit(main())
