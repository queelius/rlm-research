"""Export exact causal controller turns through the official Verifiers Trace branches."""

from __future__ import annotations

import argparse
import importlib.util
import json
import math
import re
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

import analyze_comparison as analysis
from verifiers.v1.trace import WireTrace

base = analysis.base
ROOT = Path(__file__).resolve().parent
TRAINER = ROOT.parent / "single-gpu-rlvr-v2/source/single_gpu_rlvr.py"
CREDIT_POLICY = (
    "All captured sampled policy actions across all physical trace branches, deduplicated "
    "by trace/node identity. One causal sequence per call. Only the current action is "
    "unmasked; previous actions, scaffolding, prompts, and observations are context. "
    "Every credited call must use the declared policy model and group temperature."
)
INFERENCE_LOG = Path(
    "/project/alex_phd/runs/rlm-research-r4/operations/2026-09-08-resume/"
    "inference-attempt-002/inference.log"
)


def observed_logprob_contract() -> dict[str, Any]:
    """Extract only the safe sampler setting; never serialize the server's API arguments."""
    for number, line in enumerate(INFERENCE_LOG.read_text().splitlines(), 1):
        match = re.search(r"'logprobs_mode': '([^']+)'", line)
        if match:
            mode = match.group(1)
            if mode != "processed_logprobs":
                raise ValueError("rollout logprobs must match the processed sampler distribution")
            return {
                "logprobs_mode": mode,
                "evidence_path": str(INFERENCE_LOG),
                "evidence_line": number,
                "interpretation": (
                    "Selected action logprobs after temperature/top-k/top-p processing"
                ),
            }
    raise ValueError("server logprob distribution mode has not been verified")


def trainer_module() -> Any:
    spec = importlib.util.spec_from_file_location("_export_generic_trainer", TRAINER)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def causal_turns(
    trace: WireTrace, *, expected_model: str, temperature: float
) -> list[dict[str, Any]]:
    """Use the official physical graph, never reconstructed message-text tokenization."""
    if not math.isfinite(temperature) or temperature <= 0:
        raise ValueError("sampled policy-gradient export needs a positive temperature")
    node_indices = {id(node): index for index, node in enumerate(trace.nodes)}
    calls = {}
    for call_index, call in enumerate(trace.calls):
        if call.error or call.node is None or not 0 <= call.node < len(trace.nodes):
            raise ValueError("failed or unpreserved model call")
        if call.node in calls:
            raise ValueError("multiple model calls share a sampled node")
        if call.model != expected_model or call.sampling is None:
            raise ValueError("credited model identity or sampling metadata mismatch")
        if call.sampling.temperature != temperature:
            raise ValueError("credited call temperature differs from sampler group")
        if call.sampling.top_p != 1.0 or call.sampling.top_k != -1 or call.sampling.min_p != 0.0:
            raise ValueError("credited sampler support differs from full-softmax trainer")
        calls[call.node] = (call_index, call)
    sampled = {index for index, node in enumerate(trace.nodes) if node.sampled}
    if not sampled or set(calls) != sampled:
        raise ValueError("model calls and sampled graph nodes are not one-to-one")

    exported: dict[int, dict[str, Any]] = {}
    for branch in trace.branches:
        prefix: list[int] = []
        for node in branch.nodes:
            index = node_indices[id(node)]
            ids, mask, logs = node.token_ids, node.mask, node.logprobs
            if len(ids) != len(mask) or any(type(token) is not int or token < 0 for token in ids):
                raise ValueError("invalid exact-prefix graph token capture")
            count = sum(mask)
            if len(logs) != count or any(
                isinstance(value, bool) or not math.isfinite(value) or value > 0 for value in logs
            ):
                raise ValueError("missing, invalid, or misaligned compact action logprobs")
            if not node.sampled and count:
                raise ValueError("unsampled observation has a nonzero action mask")
            if node.sampled:
                if not count or mask != [False] * (len(ids) - count) + [True] * count:
                    raise ValueError("current action must be a nonempty sampled suffix")
                call_index, call = calls[index]
                sequence = prefix + ids
                prompt_length = len(sequence) - count
                if not prompt_length or call.usage is None:
                    raise ValueError("missing prompt prefix or per-call usage audit")
                if call.usage.input_tokens != prompt_length:
                    raise ValueError("official branch prefix differs from call input token count")
                if call.usage.completion_tokens != count:
                    raise ValueError("official graph action differs from call completion count")
                action = sequence[prompt_length:]
                candidate = {
                    "input_ids": sequence,
                    "labels": [-100] * prompt_length + action,
                    "loss_mask": [0] * prompt_length + [1] * count,
                    "old_logprobs": list(logs),
                    "prompt_length": prompt_length,
                    "source_trace_id": trace.id,
                    "source_node_index": index,
                    "source_call_index": call_index,
                    "sampling": call.sampling.model_dump(mode="json", exclude_none=True),
                    "call_model": call.model,
                    "call_finish_reason": call.finish_reason,
                    "usage_input_tokens": call.usage.input_tokens,
                    "usage_completion_tokens": call.usage.completion_tokens,
                }
                if index in exported and exported[index] != candidate:
                    raise ValueError("shared sampled node has inconsistent causal branch prefix")
                exported[index] = candidate
            prefix.extend(ids)
        if prefix != branch.token_ids:
            raise ValueError("official branch token flattening mismatch")
    if set(exported) != sampled:
        raise ValueError("not every sampled action is reachable from an official graph branch")
    return [exported[index] for index in sorted(exported)]


def export_record(
    record: dict[str, Any], source_spec: dict[str, Any], *, dataset_id: str
) -> dict[str, Any]:
    coordinate, metrics = record["coordinate"], record["derived"]
    descriptor = source_spec["source_endpoint_descriptor"]
    row = {
        "episode_id": coordinate["id"],
        "task_id": coordinate["task_name"],
        "cell_id": f"native-prefill-temperature-{coordinate['temperature']}",
        "split": coordinate.get("split", "calibration"),
        "sample_seed": coordinate["seed"],
        "temperature": coordinate["temperature"],
        "dataset_id": dataset_id,
        "trace_trainable": False,
        "reward": None,
        "strict_reward": metrics["strict_reward"],
        "execution_completed": metrics["execution_completed"],
        "terminal_observable": metrics["terminal_observable"],
        "terminal_schema_valid": metrics["strict_terminal_valid"],
        "terminal_correct": metrics["strict_correct"],
        "turns": [],
        "invalid_reason": None,
        "provenance": {
            "raw_episode_sha256": record["episode_sha256"],
            "source_record_sha256": record["source_sha256"],
            "task_identity": record["task_identity"],
            "endpoint": source_spec["endpoint"],
            "base_model": descriptor["base_model"],
            "adapter": descriptor["adapter"],
            "renderer": {"name": "qwen3", "enable_thinking": True},
            "runtime_image_id": source_spec["observed_runtime_image_id"],
            "credit_policy": CREDIT_POLICY,
            "rollout_logprobs_mode": "processed_logprobs",
        },
    }
    if coordinate["client_path"] != "train" or coordinate["temperature"] <= 0:
        row["invalid_reason"] = "not_positive_temperature_train_client"
        return row
    if not metrics["execution_completed"] or not metrics["terminal_observable"]:
        row["invalid_reason"] = "execution_failure_or_unobservable_terminal"
        return row
    if not metrics["trace_trainable"]:
        row["invalid_reason"] = "incomplete_raw_token_or_logprob_capture"
        return row
    try:
        trace_ids = set()
        for raw_trace in record["episode"]["traces"]:
            renderer = raw_trace["agent"]["config"]["client"].get("renderer")
            if renderer != {"name": "qwen3", "enable_thinking": True}:
                raise ValueError("raw trace renderer differs from declared native prefill")
            trace = WireTrace.model_validate(raw_trace)
            if trace.id in trace_ids or trace.errors or not trace.ok or not trace.is_completed:
                raise ValueError("duplicate or failed incomplete trace")
            trace_ids.add(trace.id)
            row["turns"].extend(
                causal_turns(
                    trace,
                    expected_model=source_spec["endpoint"]["model"],
                    temperature=coordinate["temperature"],
                )
            )
        if len(row["turns"]) != metrics["model_calls"]:
            raise ValueError("episode model call count differs from exported causal turn count")
        if not row["turns"] or type(metrics["strict_reward"]) is not int:
            raise ValueError("missing exact turns or binary observable strict reward")
        validator = trainer_module().validate_turn
        row["action_tokens"] = sum(validator(turn) for turn in row["turns"])
    except (ValueError, TypeError, KeyError, AttributeError) as error:
        row["invalid_reason"] = f"causal_capture_rejected: {error}"
        row["turns"] = []
        return row
    row["trace_trainable"] = True
    row["reward"] = metrics["strict_reward"]
    row["turn_count"] = len(row["turns"])
    return row


def export_attempt(path: Path, *, allow_partial: bool = False) -> tuple[Any, Any, Any]:
    spec, records = analysis.load_attempt(path)
    complete = len(records) == len(spec["plan"])
    if not complete and not allow_partial:
        raise ValueError(
            "collection is incomplete; final dataset export requires all planned records"
        )
    provenance = {
        "source_attempt": str(path),
        "source_spec_sha256": base.file_hash(path / "SPEC.json"),
        "source_record_sha256": {
            record["coordinate"]["id"]: record["source_sha256"] for record in records
        },
        "planned": len(spec["plan"]),
        "recorded": len(records),
        "complete": complete,
        "coordinate_plan_sha256": spec["coordinate_plan_sha256"],
        "rollout_logprob_contract": observed_logprob_contract(),
    }
    dataset_id = base.digest(provenance)
    rows = [export_record(record, spec, dataset_id=dataset_id) for record in records]
    grouped = defaultdict(list)
    for row in rows:
        grouped[row["task_id"]].append(row)
    task_summaries = []
    for task, episodes in sorted(grouped.items()):
        valid = [row for row in episodes if row["trace_trainable"]]
        task_summaries.append(
            {
                "task": task,
                "episodes": len(episodes),
                "trainable": len(valid),
                "rewards": [row["reward"] for row in valid],
                "mixed": {row["reward"] for row in valid} == {0, 1},
            }
        )
    group = None
    group_reason = "not a complete fresh training split"
    if complete and rows and all(row["split"] == "training" for row in rows):
        try:
            group = trainer_module().training_group(rows)
            group_reason = None
        except ValueError as error:
            if str(error) != "no fresh within-prompt mixed reward group":
                raise
            group_reason = str(error)
    from verifiers.v1 import graph, trace

    manifest = {
        "schema": "strict-rlm-causal-export-v1",
        "dataset_id": dataset_id,
        **provenance,
        "credit_policy": CREDIT_POLICY,
        "reward_contract": (
            "Completed observable malformed or wrong policy outputs keep reward zero "
            "when their exact actions are captured. Infrastructure/capture failures have "
            "trace_trainable=false, reward=null; their diagnostic strict_reward is preserved."
        ),
        "tasks": task_summaries,
        "trainable_episodes": sum(row["trace_trainable"] for row in rows),
        "verified_successes": sum(row["reward"] == 1 for row in rows),
        "controller_turns": sum(len(row["turns"]) for row in rows),
        "action_tokens": sum(row.get("action_tokens", 0) for row in rows),
        "invalid_reasons": dict(
            Counter(row["invalid_reason"] for row in rows if row["invalid_reason"])
        ),
        "training_group_id": group["group_id"] if group else None,
        "training_group_episodes": len(group["episodes"]) if group else 0,
        "training_group_unavailable_reason": group_reason,
        "source_file_sha256": {
            str(source): base.file_hash(source)
            for source in (
                Path(__file__).resolve(),
                ROOT / "tests/test_trace_export.py",
                Path(analysis.__file__),
                Path(analysis.native.__file__),
                Path(base.__file__),
                Path(graph.__file__),
                Path(trace.__file__),
                TRAINER,
            )
        },
    }
    return rows, group, manifest


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--attempt", required=True, type=Path)
    parser.add_argument("--output-dir", type=Path)
    parser.add_argument(
        "--allow-partial", action="store_true", help="Inspection only; no update group"
    )
    args = parser.parse_args()
    source = args.attempt.resolve()
    rows, group, manifest = export_attempt(source, allow_partial=args.allow_partial)
    if args.output_dir:
        output = args.output_dir.resolve()
        if output.exists() or output.is_relative_to(source):
            raise ValueError("export requires a new directory outside the immutable source attempt")
        output.mkdir(parents=True)
        with (output / "episodes.jsonl").open("x") as stream:
            for row in rows:
                stream.write(json.dumps(row, sort_keys=True, allow_nan=False) + "\n")
        if group:
            base.atomic_json(output / "training-group.json", group)
        manifest["artifact_sha256"] = {
            file.name: base.file_hash(file) for file in sorted(output.iterdir())
        }
        base.atomic_json(output / "MANIFEST.json", manifest)
    print(json.dumps(manifest, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
