"""Fresh native TrainClient recursive episodes over the frozen executable-example harness."""

from __future__ import annotations

import argparse
import asyncio
import hashlib
import importlib.util
import json
import re
import sys
from collections import defaultdict
from copy import deepcopy
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parent
STUDY = ROOT.name
QUAL = ROOT.parent / "strict-rlm-client-qualification-v2"
EXAMPLE = ROOT.parent / "recursive-call-example-v1"
EXAMPLE_SHA256 = "45a839de6790f0ee710fcc171af768b7e2b19b160bad7ef9aba524aee6ec31b3"
if hashlib.sha256((EXAMPLE / "driver.py").read_bytes()).hexdigest() != EXAMPLE_SHA256:
    raise ValueError("frozen executable-example driver changed")
sys.path.insert(0, str(QUAL))
import export_causal_turns as exporter  # noqa: E402
import native_prefill_arm as native  # noqa: E402

_loader = importlib.util.spec_from_file_location(
    "example_for_native_capture", EXAMPLE / "driver.py"
)
example = importlib.util.module_from_spec(_loader)
_loader.loader.exec_module(example)
base, q = example.base, example.q


def load_tasks() -> dict[str, Any]:
    from oolong_prime_rlm_strict_v1.taskset import StrictOolongConfig, StrictOolongTaskset

    selected = {
        task.data.name: task
        for task in StrictOolongTaskset(StrictOolongConfig(split="train")).load()
        if task.data.source_id in example.SOURCE_IDS
    }
    if len(selected) != 3 or {task.data.context_window_id for task in selected.values()} != {8}:
        raise ValueError("declared three reused development questions changed")
    return dict(sorted(selected.items()))


def build_plan(tasks: dict[str, Any]) -> list[dict[str, Any]]:
    plan = []
    for repeat in range(4):
        for index, (name, task) in enumerate(tasks.items()):
            row = {
                "study": STUDY,
                "task_name": name,
                "source_id": task.data.source_id,
                "analysis_split": "reused_development_fresh_onpolicy",
                "split": "training",
                "context_window_id": 8,
                "context_sha256": hashlib.sha256(task.data.context.encode()).hexdigest(),
                "repeat": repeat,
                "seed": 950260900 + index * 4 + repeat,
                "temperature": 0.5,
                "client_path": "train",
                "arm": "example",
                "group_id": q.digest([STUDY, name, "example", 0.5]),
                "task_hash": example.with_prompt(task, "example").hash,
            }
            plan.append(
                {
                    **row,
                    "id": q.digest(row),
                    "pair_id": q.digest([row, "unpaired"]),
                    "pair_order": 0,
                    "dispatch_order": len(plan),
                }
            )
    return plan


def serving_evidence(log: Path) -> dict[str, Any]:
    """Seal an append-only log prefix without copying credential-bearing startup text."""
    payload = log.read_bytes()
    matches = []
    for number, line in enumerate(payload.decode(errors="replace").splitlines(), 1):
        match = re.search(r"['\"]logprobs_mode['\"]\s*:\s*['\"]([^'\"]+)['\"]", line)
        if match:
            matches.append((number, match.group(1), hashlib.sha256(line.encode()).hexdigest()))
    if not matches or {mode for _, mode, _ in matches} != {"processed_logprobs"}:
        raise ValueError("current service has not established processed sampler logprobs")
    return {
        "source_log": str(log.resolve()),
        "prefix_bytes": len(payload),
        "prefix_sha256": hashlib.sha256(payload).hexdigest(),
        "logprobs_mode": "processed_logprobs",
        "evidence_line": matches[-1][0],
        "evidence_line_sha256": matches[-1][2],
        "interpretation": "Selected action logprobs after temperature/top-k/top-p processing",
        "snapshot_policy": (
            "Original bytes must remain an identical prefix; append-only traffic allowed"
        ),
    }


def validate_serving_evidence(evidence: dict[str, Any]) -> None:
    with Path(evidence["source_log"]).open("rb") as stream:
        prefix = stream.read(evidence["prefix_bytes"])
    if hashlib.sha256(prefix).hexdigest() != evidence["prefix_sha256"]:
        raise ValueError("current serving log prefix changed")
    if evidence["logprobs_mode"] != "processed_logprobs":
        raise ValueError("current processed sampling distribution is required")


def capture_metrics(episode: dict[str, Any], seconds: float | None, endpoint: dict) -> dict:
    metrics = {
        **example.example_metrics(episode, seconds),
        **native.episode_metrics(episode, seconds),
    }
    metrics["causal_capture_audit_error"] = None
    metrics["exact_credited_turns"] = 0
    metrics["exact_credited_action_tokens"] = 0
    if metrics["trace_trainable"]:
        try:
            for raw in episode["traces"]:
                if raw["agent"]["config"]["client"]["renderer"] != {
                    "name": "qwen3",
                    "enable_thinking": True,
                }:
                    raise ValueError("actual renderer differs from native-prefill contract")
                trace = exporter.WireTrace.model_validate(raw)
                if trace.errors or not trace.ok or not trace.is_completed:
                    raise ValueError("failed or incomplete trace")
                turns = exporter.causal_turns(
                    trace, expected_model=endpoint["model"], temperature=0.5
                )
                metrics["exact_credited_turns"] += len(turns)
                metrics["exact_credited_action_tokens"] += sum(
                    len(t["old_logprobs"]) for t in turns
                )
            if metrics["exact_credited_turns"] != metrics["model_calls"]:
                raise ValueError("all-call causal capture count differs from actual model calls")
        except (ValueError, TypeError, KeyError, AttributeError) as error:
            metrics["trace_trainable"] = False
            metrics["causal_capture_audit_error"] = str(error)
    metrics["update_eligible"] = bool(
        metrics["trace_trainable"]
        and metrics["execution_completed"]
        and metrics["terminal_observable"]
        and type(metrics["strict_reward"]) is int
    )
    return metrics


def summarize(records: list[dict], plan: list[dict]) -> dict:
    groups = defaultdict(list)
    for record in records:
        groups[record["coordinate"]["task_name"]].append(record["derived"])
    tasks = []
    for name, rows in sorted(groups.items()):
        rewards = [row["strict_reward"] for row in rows if row["update_eligible"]]
        tasks.append(
            {
                "task": name,
                "episodes": len(rows),
                "trainable_rewards": rewards,
                "mixed": set(rewards) == {0, 1},
            }
        )
    return {
        "study": STUDY,
        "planned": len(plan),
        "recorded": len(records),
        "tasks": tasks,
        "mixed_tasks": sum(row["mixed"] for row in tasks),
        **{
            key: sum(int(record["derived"].get(key) or 0) for record in records)
            for key in (
                "execution_completed",
                "trace_trainable",
                "strict_correct",
                "python_used",
                "actual_recursive_model_call",
                "committed_subagent_call_edges",
                "committed_subagent_return_edges",
                "exact_credited_turns",
                "exact_credited_action_tokens",
            )
        },
        "caution": (
            "Three reused development questions, fresh samples; inspect mixed groups and "
            "child semantic quality before any further update"
        ),
    }


def make_spec(descriptor: Path, evidence_path: Path) -> tuple[dict, dict]:
    # Process-local substitution avoids loading the heldout task split in the inherited builder.
    base.load_tasks = load_tasks
    frozen, tasks = base.make_spec(descriptor, "post_update")
    plan = build_plan(tasks)
    evidence = json.loads(evidence_path.read_text())
    validate_serving_evidence(evidence)
    for task_spec in frozen["tasks"]:
        task = tasks[task_spec["name"]]
        prompted = example.with_prompt(task, "example")
        task_spec["arms"] = {
            "example": {"prompt": prompted.data.prompt, "task_hash": prompted.hash}
        }
    frozen.update(
        {
            "schema": STUDY,
            "plan": plan,
            "plan_sha256": q.digest(plan),
            "coordinate_plan_sha256": q.digest(plan),
            "wall_time_cap_seconds": 1800,
            "observed_runtime_image_id": frozen["image_id"].removeprefix("sha256:"),
            "request_template": native.request_metadata(frozen["endpoint"], plan[0]),
            "serving_evidence": evidence,
            "example_code": example.EXAMPLE_CODE,
            "credit_policy": exporter.CREDIT_POLICY,
            "split_provenance": {
                "source_ids": list(example.SOURCE_IDS),
                "context_window_id": 8,
                "questions_reused_from_development": True,
                "samples_fresh": True,
                "heldout_outcomes_used": False,
            },
            "interpretation": (
                "On-policy native TrainClient parent+child capture after one TIS update; "
                "no additional update authorized by this collection"
            ),
            "primary_outcome": (
                "Complete aligned all-call traces and within-question mixed terminal rewards"
            ),
            "exclusions": "Every heldout question and every development question outside IDs8/9/25",
            "scheduler": (
                "Inherited four workers, each consumes two independent episodes sequentially; "
                "not a paired treatment study"
            ),
        }
    )
    sources = [
        Path(__file__).resolve(),
        ROOT / "export.py",
        ROOT / "tests/test_capture_driver.py",
        evidence_path,
        EXAMPLE / "driver.py",
        Path(native.__file__),
        Path(exporter.__file__),
        q.PRIME / "deps/verifiers/verifiers/v1/clients/train.py",
        q.PRIME / "deps/verifiers/verifiers/v1/interception/server.py",
        q.PRIME / "deps/verifiers/verifiers/v1/trace.py",
        q.PRIME / "deps/verifiers/verifiers/v1/graph.py",
    ]
    config = frozen["source_endpoint_descriptor"].get("prime_inference_config")
    if config:
        sources.append(Path(config))  # Hash only; never copy credentials from serving config.
    frozen["source_file_sha256"].update({str(path): q.file_hash(path) for path in sources})
    return frozen, tasks


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument("--prepare", action="store_true")
    mode.add_argument("--preflight", action="store_true")
    parser.add_argument("--endpoint-descriptor", type=Path, required=True)
    parser.add_argument("--server-log", type=Path)
    parser.add_argument("--serving-evidence", type=Path, default=ROOT / "SERVER_EVIDENCE.json")
    parser.add_argument("--spec-path", type=Path, default=ROOT / "SPEC.json")
    parser.add_argument("--output-dir", type=Path)
    parser.add_argument("--endpoint-url")
    parser.add_argument("--resume", action="store_true")
    args = parser.parse_args()
    if args.prepare:
        if args.spec_path.exists() or args.serving_evidence.exists() or args.server_log is None:
            raise ValueError(
                "prepare needs new spec/evidence paths and an explicit current server log"
            )
        q.atomic_json(args.serving_evidence, serving_evidence(args.server_log))
    frozen, tasks = make_spec(args.endpoint_descriptor.resolve(), args.serving_evidence.resolve())
    from verifiers.v1.envs.single_agent import SingleAgentEnvConfig

    SingleAgentEnvConfig.model_validate(deepcopy(frozen["environment"]))
    for row in frozen["plan"]:
        context = native.make_context(frozen["endpoint"], row)
        if context.client.type != "train" or not context.client.renderer.enable_thinking:
            raise ValueError("native TrainClient required")
    if args.prepare:
        q.atomic_json(args.spec_path, frozen)
    elif json.loads(args.spec_path.read_text()) != frozen:
        raise ValueError("frozen collection inputs changed")
    if args.prepare or args.preflight:
        print(
            json.dumps(
                {
                    "ok": True,
                    "episodes": 12,
                    "spec_sha256": q.file_hash(args.spec_path),
                    "plan_sha256": frozen["plan_sha256"],
                    "client": "native_train",
                    "model": frozen["endpoint"]["model"],
                },
                indent=2,
            )
        )
        return 0
    if args.output_dir is None:
        parser.error("--output-dir is required for collection")
    base.STUDY = STUDY
    base.with_prompt = example.with_prompt
    base.crossover_metrics = lambda episode, seconds: capture_metrics(
        episode, seconds, frozen["endpoint"]
    )
    base.summarize = summarize
    q.make_context = native.make_context
    q.request_metadata = native.request_metadata
    return asyncio.run(base.run(args, frozen, tasks))


if __name__ == "__main__":
    raise SystemExit(main())
