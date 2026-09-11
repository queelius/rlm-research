"""Unchanged stable-anchor scorer."""
import protocol as p
import study as s

module = s.load("qwen8b_stable_scoring", s.PRIOR / "scoring.py",
    "7f24a53c62544a48881b880a982497c00bccf9e4b78014654121ceb3dc7311eb",
    {"study": s, "protocol": p})
score, missing, verified_response = module.score, module.missing, module.verified_response


def summarize(rows):
    cells = {}
    for arm in p.ARMS:
        selected = [row for row in rows if row["coordinate"]["arm"] == arm]
        available = [row for row in selected if row["score"]["available"]]
        cells[arm] = {"planned": len(selected), "available": len(available),
                      "null": len(selected) - len(available),
                      "strict_correct": sum(row["score"]["strict_correct"] for row in available),
                      "contract_valid": sum(bool(row["score"]["contract_valid"]) for row in available)}
    differences = {}
    for anchor in p.ANCHORS[1:]:
        differences[anchor] = {}
        for index in range(16):
            delta = known = 0
            for relation in p.RELATIONS:
                left = next((row for row in rows if row["coordinate"]["context_index"] == index and row["coordinate"]["arm"] == f"{relation}_{anchor}"), None)
                right = next((row for row in rows if row["coordinate"]["context_index"] == index and row["coordinate"]["arm"] == f"{relation}_labels_only"), None)
                if left and right and left["score"]["available"] and right["score"]["available"]:
                    delta += left["score"]["strict_correct"] - right["score"]["strict_correct"]
                    known += 48
            differences[anchor][str(index)] = {"difference": delta, "known_labels": known}
    return {"cells": cells, "context_differences": differences,
            "cluster_unit": "16 paired exposed contexts; calls and labels are dependent"}
