"""Development-only executable-recursion example probe; never launches an inference server."""

from __future__ import annotations

import argparse
import asyncio
import hashlib
import importlib.util
import json
import os
import random
import re
from collections import defaultdict
from copy import deepcopy
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parent
STUDY = ROOT.name
BASE = ROOT.parent / "plan-hint-crossover-v1"
SNAPSHOT = Path("/project/alex_phd/research-cache/2026-09-08-literature/recursive-example.6xBrmx")
BASE_DRIVER_SHA256 = "406a64ca59e4d77e6126c3fd97339c57cb5d7aef6808c998d7e18be7e6456832"
if hashlib.sha256((BASE / "driver.py").read_bytes()).hexdigest() != BASE_DRIVER_SHA256:
    raise ValueError("sealed baseline driver changed")
_loader = importlib.util.spec_from_file_location("hint_driver_for_example", BASE / "driver.py")
base = importlib.util.module_from_spec(_loader)
_loader.loader.exec_module(base)
q = base.q
original_prompt = base.with_prompt
original_metrics = base.crossover_metrics
original_summary = base.summarize

SOURCE_IDS = (12000008, 12000009, 12000025)
EXAMPLE_CODE = """import json
records = [line.split(" || Instance: ", 1)[1].strip()
           for line in open("context.txt") if " || Instance: " in line]
batch = records[:4]
child = await rlm(
    "Return only a JSON array of labels in input order. Allowed labels: "
    "human being, location, abbreviation, entity, description and abstract concept, "
    "numeric value.\\n" + json.dumps(batch)
)
print(child.answer)"""
EXAMPLE = (
    "Executable API example for the first four context records (a starting batch, "
    "not the final answer). You can run this in ipython:\n```python\n"
    + EXAMPLE_CODE
    + "\n```\nContinue covering the remaining relevant records and compute the aggregate "
    "requested by the question."
)


def load_tasks() -> dict[str, Any]:
    source = base.load_tasks()
    return {
        f"oolong:train:{source_id}": source[f"oolong:train:{source_id}"] for source_id in SOURCE_IDS
    }


def with_prompt(task: Any, arm: str) -> Any:
    abstract = original_prompt(task, "procedure")
    if arm == "abstract":
        return abstract
    if arm != "example":
        raise ValueError("unknown example-probe arm")
    marker = "\n\nQuestion: "
    if abstract.data.prompt.count(marker) != 1:
        raise ValueError("audited question boundary changed")
    prompt = abstract.data.prompt.replace(marker, "\n\n" + EXAMPLE + marker, 1)
    return type(task)(abstract.data.model_copy(update={"prompt": prompt}), task.config)


def build_plan(tasks: dict[str, Any]) -> list[dict[str, Any]]:
    pairs = []
    for index, (name, task) in enumerate(tasks.items()):
        for repeat in range(2):
            identity = {
                "study": STUDY,
                "task_name": name,
                "source_id": task.data.source_id,
                "analysis_split": "development",
                "context_window_id": 8,
                "context_sha256": hashlib.sha256(task.data.context.encode()).hexdigest(),
                "repeat": repeat,
                "seed": int(q.digest([STUDY, "fresh-development-v1", name, repeat])[:8], 16)
                % (2**31 - 1),
                "temperature": 0.5,
                "client_path": "eval",
            }
            order = (
                ("abstract", "example") if (index + repeat) % 2 == 0 else ("example", "abstract")
            )
            pairs.append(
                [
                    {
                        **identity,
                        "arm": arm,
                        "id": q.digest([identity, arm]),
                        "pair_id": q.digest(identity),
                        "pair_order": position,
                        "group_id": q.digest([STUDY, name, arm]),
                        "task_hash": with_prompt(task, arm).hash,
                    }
                    for position, arm in enumerate(order)
                ]
            )
    random.Random(2026090812).shuffle(pairs)
    plan = [
        {**row, "dispatch_order": index}
        for index, row in enumerate(row for pair in pairs for row in pair)
    ]
    baseline = json.loads((BASE / "SPEC.runtime-id-v2.json").read_text())
    if {row["seed"] for row in plan} & {row["seed"] for row in baseline["plan"]}:
        raise ValueError("probe seeds must be fresh relative to baseline")
    return plan


def example_metrics(episode: dict[str, Any], wall_seconds: float | None) -> dict[str, Any]:
    result = original_metrics(episode, wall_seconds)
    mentions = 0
    edges: dict[str, set[tuple[int, int, int]]] = defaultdict(set)
    traces = episode.get("traces") or []
    for trace_index, trace in enumerate(traces):
        nodes = trace.get("nodes", [])
        committed = {
            call["node"]
            for call in trace.get("calls", [])
            if type(call.get("node")) is int
            and not call.get("error")
            and (call.get("acp") or {}).get("request_id")
        }
        for index, node in enumerate(nodes):
            message = node.get("message") or {}
            if message.get("role") == "assistant":
                text = json.dumps(
                    {"content": message.get("content"), "tool_calls": message.get("tool_calls")}
                )
                mentions += len(re.findall(r"\brlm\s*\(", text))
            for link in node.get("semantic_parents") or []:
                parent = link.get("node")
                if (
                    link.get("type") in ("subagent_call", "subagent_return")
                    and index in committed
                    and parent in committed
                    and type(parent) is int
                    and 0 <= parent < len(nodes)
                    and node.get("sampled") is True
                    and nodes[parent].get("sampled") is True
                ):
                    edges[link["type"]].add((trace_index, parent, index))
    final_metrics = traces[-1].get("metrics", {}) if traces else {}
    observed = "sub_rlm_num_calls" in final_metrics
    result.update(
        {
            "assistant_rlm_mentions": mentions,
            "child_session_metric_observed": observed,
            "child_sessions_created": int(final_metrics["sub_rlm_num_calls"]) if observed else None,
            "committed_subagent_call_edges": len(edges["subagent_call"]),
            "committed_subagent_return_edges": len(edges["subagent_return"]),
            "actual_recursive_model_call": bool(edges["subagent_call"]),
            "recursive_model_return_observed": bool(edges["subagent_return"]),
        }
    )
    return result


def summarize(records: list[dict[str, Any]], plan: list[dict[str, Any]]) -> dict[str, Any]:
    result = original_summary(records, plan)
    pairs = defaultdict(dict)
    for record in records:
        pairs[record["coordinate"]["pair_id"]][record["coordinate"]["arm"]] = record["derived"]
    result["paired"] = []
    for pair_id, pair in sorted(pairs.items()):
        if set(pair) != {"abstract", "example"}:
            continue
        observable = all(row["strict_reward"] is not None for row in pair.values())
        result["paired"].append(
            {
                "pair_id": pair_id,
                "actual_recursion_example_minus_abstract": int(
                    pair["example"]["actual_recursive_model_call"]
                )
                - int(pair["abstract"]["actual_recursive_model_call"]),
                "strict_success_example_minus_abstract": pair["example"]["strict_reward"]
                - pair["abstract"]["strict_reward"]
                if observable
                else None,
                "completion_tokens_example_minus_abstract": pair["example"]["completion_tokens"]
                - pair["abstract"]["completion_tokens"],
            }
        )
    for cell in result["cells"]:
        rows = [r["derived"] for r in records if r["coordinate"]["arm"] == cell["arm"]]
        for key in (
            "actual_recursive_model_call",
            "recursive_model_return_observed",
            "child_session_metric_observed",
            "assistant_rlm_mentions",
            "committed_subagent_call_edges",
            "committed_subagent_return_edges",
        ):
            cell[key] = sum(row[key] for row in rows)
    result["caution"] = (
        "Selected development-only action-headroom probe: one reused context, three questions, "
        "six pairs. No free-planning, training, heldout, or transfer claim."
    )
    return result


def make_spec(descriptor: Path, weight_condition: str) -> tuple[dict[str, Any], dict[str, Any]]:
    frozen, _ = base.make_spec(descriptor, weight_condition)
    tasks = load_tasks()
    plan = build_plan(tasks)
    selected = {row["name"]: row for row in frozen["tasks"] if row["name"] in tasks}
    for name, task in tasks.items():
        selected[name]["arms"] = {
            arm: {
                "prompt": with_prompt(task, arm).data.prompt,
                "task_hash": with_prompt(task, arm).hash,
            }
            for arm in ("abstract", "example")
        }
    frozen.update(
        {
            "schema": STUDY,
            "tasks": list(selected.values()),
            "plan": plan,
            "plan_sha256": q.digest(plan),
            "wall_time_cap_seconds": 1800,
            "request_template": q.request_metadata(frozen["endpoint"], plan[0]),
            "exclusions": (
                "All heldout tasks and other development tasks excluded; selected failure probe."
            ),
            "split_provenance": {
                "analysis_split": "development",
                "context_window_id": 8,
                "source_ids": list(SOURCE_IDS),
                "heldout_used": False,
            },
            "interpretation": (
                "Does adding a compact executable example to the same verbal procedure induce "
                "committed child model calls? Selected development action-headroom probe only."
            ),
            "baseline_driver_sha256": BASE_DRIVER_SHA256,
            "example_code": EXAMPLE_CODE,
            "primary_outcome": "actual_recursive_model_call: committed subagent_call semantic edge",
            "metric_caveat": (
                "Child-session directory creation is separate from committed child inference; "
                "a returned model edge is separate from a semantically correct result."
            ),
        }
    )
    sources = [
        ROOT / "driver.py",
        BASE / "SPEC.runtime-id-v2.json",
        q.PRIME / "deps/verifiers/verifiers/v1/semantic.py",
        q.PRIME / "deps/verifiers/verifiers/v1/trace.py",
        *sorted(SNAPSHOT.glob("*.py")),
        SNAPSHOT / "LICENSE",
        SNAPSHOT / "PROVENANCE.json",
    ]
    frozen["source_file_sha256"].update({str(path): q.file_hash(path) for path in sources})
    return frozen, tasks


def validate_runtime_spec(frozen: dict[str, Any]) -> None:
    from verifiers.v1.envs.single_agent import SingleAgentEnvConfig

    # Its nested discriminated-union validators modify dictionaries in place.
    SingleAgentEnvConfig.model_validate(deepcopy(frozen["environment"]))
    if q.make_context(frozen["endpoint"], frozen["plan"][0]).client.type != "eval":
        raise ValueError("eval client required")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument("--prepare", action="store_true")
    mode.add_argument("--preflight", action="store_true")
    parser.add_argument(
        "--endpoint-descriptor", type=Path, default=q.OLD / "configs/endpoint-replica0.json"
    )
    parser.add_argument("--spec-path", type=Path, default=ROOT / "PREPARED_BASELINE_SPEC.json")
    parser.add_argument(
        "--weight-condition", choices=("pre_update", "post_update"), default="pre_update"
    )
    parser.add_argument("--endpoint-url")
    parser.add_argument("--output-dir", type=Path)
    parser.add_argument("--resume", action="store_true")
    args = parser.parse_args()
    frozen, tasks = make_spec(args.endpoint_descriptor.resolve(), args.weight_condition)
    validate_runtime_spec(frozen)
    if args.prepare:
        if args.spec_path.exists():
            raise ValueError("immutable spec already exists; select a new path")
        q.atomic_json(args.spec_path, frozen)
    elif not args.spec_path.is_file() or json.loads(args.spec_path.read_text()) != frozen:
        raise ValueError("frozen inputs changed")
    if args.prepare or args.preflight:
        print(
            json.dumps(
                {
                    "ok": True,
                    "episodes": len(frozen["plan"]),
                    "plan_sha256": frozen["plan_sha256"],
                    "spec_sha256": q.file_hash(args.spec_path),
                    "weight_condition": frozen["weight_condition"],
                },
                indent=2,
            )
        )
        return 0
    if args.output_dir is None:
        parser.error("--output-dir is required for a live run")
    os.environ["PATH"] = str(q.ROOTLESS / "bin") + os.pathsep + os.environ.get("PATH", "")
    os.environ.setdefault("VERIFIERS_CACHE_DIR", "/project/alex_phd/cache/verifiers-prime")
    # Process-local callbacks only: never modify the sealed baseline module on disk.
    base.STUDY = STUDY
    base.with_prompt = with_prompt
    base.crossover_metrics = example_metrics
    base.summarize = summarize
    return asyncio.run(base.run(args, frozen, tasks))


if __name__ == "__main__":
    raise SystemExit(main())
