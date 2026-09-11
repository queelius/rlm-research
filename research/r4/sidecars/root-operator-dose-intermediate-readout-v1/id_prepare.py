"""Prepare immutable intermediate-dose inputs."""
import copy
import hashlib
import json
from collections import Counter
from pathlib import Path

import id_study as s

POLICIES = ["sft18", "sft24", "sft12", "sft6"]
MASTER = 981681001


def build_inputs():
    source = source_inputs()
    selected, receipt = s.select_panel(source["FREE_PLAN.json"], source["HOST_GOLD.json"])
    free, prompts = [], {}
    for index, old in enumerate(selected):
        seed = 981681101 + index
        new = copy.deepcopy(old)
        new.update(source_coordinate_id=old["id"], seed=seed,
                   namespace="operator-dose-intermediate-readout-v1")
        new["id"] = hashlib.sha256(f"operator-dose-intermediate-readout-v1|{old['id']}|{seed}".encode()).hexdigest()
        prompts[new["id"]] = copy.deepcopy(source["PROMPTS_ACCURATE.json"][old["id"]])
        free.append(new)
    old_probes = source["TEACHER_DIAGNOSTIC_PLAN.json"]
    probes, first_requests = [], {}
    for index, old in enumerate(old_probes):
        seed = 981681201 + index
        new = copy.deepcopy(old)
        new.update(source_coordinate_id=old["id"], seed=seed,
                   namespace="operator-dose-intermediate-probe-v1")
        new["id"] = hashlib.sha256(f"operator-dose-intermediate-probe-v1|{old['id']}|{seed}".encode()).hexdigest()
        probes.append(new)
        first_requests[new["id"]] = copy.deepcopy(source["TEACHER_FIRST_REQUESTS.json"][old["id"]])
    full_inventory = [{"policy": policy, "coordinate": row, "available": False}
                      for policy in POLICIES for row in free]
    probe_inventory = [{"policy": policy, "coordinate": row, "available": False}
                       for policy in POLICIES for row in probes]
    receipt.update({
        "label_use": "gold_is_zero only; explicit 13 nonzero/3 zero design stratification",
        "source_plan_path": str(s.SOURCE / "inputs/FREE_PLAN.json"),
        "selected_source_ids": [row["source_coordinate_id"] for row in free],
        "new_coordinate_ids": [row["id"] for row in free],
        "selection_after_prior_results_existed": True,
        "selection_uses_prior_results": False,
    })
    counts = Counter(row["context_id"] for row in free)
    excluded = {"FREE_PLAN.json", "PROMPTS_ACCURATE.json", "TEACHER_DIAGNOSTIC_PLAN.json",
                "TEACHER_FIRST_REQUESTS.json", "EVALUATION_PLAN.json", "BASELINES.json",
                "PROVENANCE.json"}
    values = {name: copy.deepcopy(value) for name, value in source.items() if name not in excluded}
    def summarize(rows):
        answers = [source["HOST_GOLD.json"][row["context_id"]]["answers"][row["family"]]
                   for row in rows]
        histogram = Counter(answers)
        best = max(histogram.values())
        return {"n": len(rows), "zero_correct": histogram.get(0, 0),
                "answer_histogram": {str(key): histogram[key] for key in sorted(histogram)},
                "best_constant_correct": best,
                "best_constants": [key for key in sorted(histogram) if histogram[key] == best]}
    strata = {name: summarize([row for row in free if row["stratum"] == name])
              for name in sorted({row["stratum"] for row in free})}
    contexts = {name: summarize([row for row in free if row["context_id"] == name])
                for name in sorted(counts)}
    values.update({
        "FREE_PLAN.json": free,
        "PROMPTS_ACCURATE.json": prompts,
        "TEACHER_DIAGNOSTIC_PLAN.json": probes,
        "TEACHER_FIRST_REQUESTS.json": first_requests,
        "EVALUATION_PLAN.json": {"policy_order": POLICIES, "full": full_inventory,
                                 "first_action": probe_inventory, "planned_full": 64,
                                 "planned_first_action": 48},
        "SELECTION_RECEIPT.json": receipt,
        "BASELINES.json": {"planned": 16, "source_strata": strata,
                           "context_clusters": contexts, "overall": summarize(free)},
        "SOURCE_PROVENANCE.json": copy.deepcopy(source["PROVENANCE.json"]),
        "PROVENANCE.json": {
            "authoritative_new_selection": "SELECTION_RECEIPT.json",
            "historical_source_provenance": "SOURCE_PROVENANCE.json",
            "source_ready_sha256": s.SOURCE_READY_SHA,
            "selection_after_prior_results_existed": True,
            "selection_uses_model_outcomes": False,
            "scope": "named source inventories and frozen source plan; not globally unseen",
        },
        "ANALYSIS_PLAN.json": {
            "primary_planned_coordinate_denominator": 16,
            "descriptive_equal_context_denominator": 12,
            "context_coordinate_counts": dict(sorted(counts.items())),
            "source_strata_reported_separately": True,
            "equal_context_means_are_descriptive_not_equivalence_tests": True,
            "single_paired_seed_no_abrupt_transition_or_equivalence_claim": True,
        },
    })
    for index, policy in enumerate(POLICIES):
        offset = index * 4
        values[f"FREE_PLAN_{policy}.json"] = free[offset:] + free[:offset]
    return values


def source_inputs():
    return {path.name: json.loads(path.read_text()) for path in (s.SOURCE / "inputs").glob("*.json")}


def seed_collisions(candidates, catalog):
    found = set()
    def visit(value):
        if isinstance(value, dict):
            for key, child in value.items():
                if key in {"seed", "master_seed"} and type(child) is int and child in candidates:
                    found.add(child)
                visit(child)
        elif isinstance(value, list):
            for child in value: visit(child)
    visit(catalog)
    return sorted(found)


def write_inputs(target):
    target = Path(target); target.mkdir(parents=True, exist_ok=False)
    values = build_inputs()
    for name, value in values.items():
        with (target / name).open("x") as handle:
            json.dump(value, handle, sort_keys=True, indent=2, allow_nan=False); handle.write("\n")
    return {"files": len(values), "path": str(target)}
