"""Qualified four-worker collector rebound to the official-test study."""
import argparse
import asyncio
import importlib.util
import sys

import protocol
import study

ready = study.read(study.PRIOR / "READY.json")
path = study.PRIOR / "bg_collect.py"
if study.sha(path) != ready["source_sha256"][str(path)]:
    raise ValueError("qualified collector changed")
sys.modules["bg_study"] = study
sys.modules["bg_protocol"] = protocol
spec = importlib.util.spec_from_file_location("trec_test_qualified_collect", path)
qualified = importlib.util.module_from_spec(spec); spec.loader.exec_module(qualified)
run = qualified.run
harvest = qualified.harvest


def summarize(rows, gold):
    cells = {}
    for row in rows:
        coordinate = row["coordinate"]
        key = (coordinate["repeat"], coordinate["model_policy"], coordinate["arm"])
        cells.setdefault(key, []).append(row)
    result = []
    labels = gold["official-trec-test-500"]["labels"]
    for (repeat, policy, arm), values in sorted(cells.items()):
        by_class = {name: {"correct": 0, "planned": 0, "null": 0} for name in protocol.CATEGORIES}
        correct = null = 0
        for row in values:
            available = row["score"]["available"]
            correct += row["score"]["strict_correct"] or 0
            null += row["coordinate"]["n"] if not available else 0
            returned = row["score"].get("labels") or {}
            for rid in row["coordinate"]["ids"]:
                name = labels[rid]; by_class[name]["planned"] += 1
                if not available: by_class[name]["null"] += 1
                elif row["score"]["complete_map"] and returned[rid] == name: by_class[name]["correct"] += 1
        result.append({"repeat": repeat, "model_policy": policy, "arm": arm, "planned_labels": 500, "strict_correct": correct, "null_labels": null, "strict_bounds": [correct, correct + null], "complete_maps": sum(row["score"]["complete_map"] for row in values), "planned_maps": len(values), "by_class": by_class})
    return result


def main():
    parser = argparse.ArgumentParser(); parser.add_argument("--endpoint", required=True); parser.add_argument("--output", required=True); parser.add_argument("--deadline", type=float, required=True)
    args = parser.parse_args(); asyncio.run(run(args.endpoint, args.output, args.deadline))


if __name__ == "__main__":
    main()
