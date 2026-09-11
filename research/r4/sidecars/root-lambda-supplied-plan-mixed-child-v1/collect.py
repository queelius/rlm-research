"""Qualified four-worker collection plus deterministic episode reduction."""
import argparse
import asyncio
import importlib.util
from pathlib import Path
import sys

import protocol as p
import study as s


def implementation():
    path = s.SIDE / "leaf-adapter-by-granularity-v1/bg_collect.py"
    if s.sha(path) != "c9e1da5a697e6315ef20118d2afb2d70ad2f242bbcb0fc9b2cb89193d9c1bcd5":
        raise ValueError("qualified collector changed")
    old = {name: sys.modules.get(name) for name in ("bg_study", "bg_protocol")}
    sys.modules.update({"bg_study": s, "bg_protocol": p})
    try:
        spec = importlib.util.spec_from_file_location("supplied_plan_qualified_collect", path)
        module = importlib.util.module_from_spec(spec); spec.loader.exec_module(module)
    finally:
        for name, value in old.items():
            if value is None: sys.modules.pop(name, None)
            else: sys.modules[name] = value
    return module


def summarize(rows, public, host):
    episodes = []
    by_context = {}
    for row in rows: by_context.setdefault(row["coordinate"]["context_id"], []).append(row)
    for context in public:
        values = sorted(by_context[context["id"]], key=lambda row: row["coordinate"]["batch"])
        spec = values[0]["coordinate"]; gold = host[context["id"]]
        unavailable = [row for row in values if not row["score"]["available"]]
        invalid = [row for row in values if row["score"]["available"] and not row["score"]["complete_map"]]
        predicted = {}
        for row in values:
            if row["score"]["complete_map"]: predicted.update(row["score"]["labels"])
        result = {
            "context_id": context["id"], "cluster": context["cluster"], "size": context["size"],
            "planned_batches": len(values), "available_batches": len(values) - len(unavailable),
            "complete_batches": sum(row["score"]["complete_map"] for row in values),
            "predicted_map_coverage": len(predicted), "planned_records": context["size"],
            "leaf_correct": sum(row["score"]["strict_correct"] or 0 for row in values),
            "canonical_id_matches": sum(row["score"]["canonical_id_matches"] or 0 for row in values),
            "final_available": not unavailable,
            "final_valid": not unavailable and not invalid and len(predicted) == context["size"],
            "predicted_answer": None, "gold_answer": gold["answers"]["J1"],
            "strict": None if unavailable else False, "absolute_error": None,
            "reason": "native unavailable" if unavailable else "malformed batch" if invalid
                      else "incomplete batch inventory" if len(predicted) != context["size"]
                      else "complete",
        }
        gold_reduction = p.reduce_j1(context["records"], gold["labels"], spec)
        result["cpu_gold_reducer_answer"] = gold_reduction["answer"]
        result["cpu_gold_reducer_matches_host"] = gold_reduction["answer"] == result["gold_answer"]
        if result["final_valid"]:
            reduction = p.reduce_j1(context["records"], predicted, spec)
            result.update(predicted_answer=reduction["answer"],
                          strict=reduction["answer"] == result["gold_answer"],
                          absolute_error=abs(reduction["answer"] - result["gold_answer"]),
                          predicted_qualifying_users=reduction["qualifying_users"],
                          gold_qualifying_users=gold_reduction["qualifying_users"],
                          contribution_errors={key: reduction["contributions"][key] - value
                                               for key, value in gold_reduction["contributions"].items()})
        episodes.append(result)
    return {"episodes": episodes, "planned": 8,
            "available": sum(row["final_available"] for row in episodes),
            "valid": sum(row["final_valid"] for row in episodes),
            "strict": sum(row["strict"] is True for row in episodes),
            "null": sum(row["strict"] is None for row in episodes),
            "cpu_gold_reducer_matches": sum(row["cpu_gold_reducer_matches_host"] for row in episodes),
            "root_model_calls": 0, "supplied_reducer": True}


async def run(endpoint, output, deadline, transport=None):
    module = implementation()
    result = await module.run(endpoint, output, deadline, transport)
    summary = summarize(result["rows"], s.read(s.ROOT / "inputs/PUBLIC.json"),
                        s.read(s.ROOT / "inputs/HOST_GOLD.json"))
    s.write(Path(output) / "EPISODES.json", summary["episodes"])
    s.write(Path(output) / "SUMMARY.json", {key: value for key, value in summary.items()
                                             if key != "episodes"})
    return {**result, "episode_summary": summary}


def main():
    parser = argparse.ArgumentParser(); parser.add_argument("--endpoint", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--deadline", type=float, required=True); args = parser.parse_args()
    asyncio.run(run(args.endpoint, args.output, args.deadline))


if __name__ == "__main__": main()
