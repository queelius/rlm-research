"""Exact/BA metrics with explicit denominators for three public views."""

import json
import study


with study.aliases({"runner_study": study}, study.SOURCE):
    costs = study.load("b05_state_repr_native_costs", study.SOURCE / "runner_metrics.py").costs


def unique(items):
    result = {}
    for key, value in items:
        if key in result:
            raise ValueError("duplicate key")
        result[key] = value
    return result


def grade(call, record, known, gold):
    row = {**call, "call_id": study.call_id(call), "available": bool(record.get("transport_valid")),
        "semantic_valid": False, "strict_valid": False, "exact": False, "strict_exact": False,
        "balanced_accuracy": None, "ids": None}
    if not row["available"]:
        return row
    try:
        obj = json.loads(record["text"], object_pairs_hook=unique)
        assert type(obj) is dict and set(obj) == {"eligible_ids"}
        ids = obj["eligible_ids"]
        assert type(ids) is list and all(type(value) is str for value in ids)
        assert len(ids) == len(set(ids)) and set(ids) <= known
        predicted = set(ids); tp = len(predicted & gold); fp = len(predicted-gold)
        fn = len(gold-predicted); tn = len(known-gold-predicted)
        recalls = ([tp/len(gold)] if gold else []) + ([tn/len(known-gold)] if known-gold else [])
        row.update(semantic_valid=True, strict_valid=ids == sorted(ids), exact=predicted == gold,
            strict_exact=predicted == gold and ids == sorted(ids), ids=ids, tp=tp, fp=fp, fn=fn, tn=tn,
            balanced_accuracy=sum(recalls)/len(recalls),
            precision=tp/len(predicted) if predicted else None,
            recall=tp/len(gold) if gold else None)
    except (ValueError, TypeError, AssertionError, KeyError) as error:
        row["error"] = f"{type(error).__name__}: {error}"
    return row


def summarize(output, qualified):
    plan = study.read(study.INPUTS)
    gold = {row["root_id"]: set(row["gold_ids"]) for row in study.read(study.HOST)["rows"]}
    tasks = {row["root_id"]: row for row in plan["tasks"]}
    records = {path.stem: study.read(path) for path in (output/"calls").glob("*.json")}
    starts = {path.stem: study.read(path) for path in (output/"starts").glob("*.json")}
    expected = {study.call_id(call) for call in plan["calls"]}
    assert set(records) <= expected and set(starts) <= expected
    start_only = set(starts)-set(records)
    for key in start_only:
        records[key] = {**starts[key], "transport_valid": False, "usage": {},
                        "status": "start_only_provider_unknown"}
    rows = [grade(call, records.get(study.call_id(call), {}),
                  set(tasks[call["root_id"]]["known_ids"]), gold[call["root_id"]])
            for call in plan["calls"]]
    arms = {}
    for arm in ("raw", "unresolved", "resolved"):
        selected = [row for row in rows if row["arm"] == arm]
        valid = [row for row in selected if row["semantic_valid"]]
        confusion = {key: sum(row[key] for row in valid) for key in ("tp","fp","fn","tn")}
        tp, fp, fn = confusion["tp"], confusion["fp"], confusion["fn"]
        arms[arm] = {"planned": 24, "available": sum(row["available"] for row in selected),
            "unknown": sum(not row["available"] for row in selected),
            "unordered_exact": sum(row["exact"] for row in selected), "semantic_valid": len(valid),
            "strict_valid": sum(row["strict_valid"] for row in selected),
            "strict_exact": sum(row["strict_exact"] for row in selected), "confusion": confusion,
            "BA_valid_set_mean": sum(row["balanced_accuracy"] for row in valid)/len(valid) if valid else None,
            "BA_valid_set_denominator": len(valid),
            "micro_precision_valid_sets": tp/(tp+fp) if tp+fp else None,
            "micro_recall_valid_sets": tp/(tp+fn) if tp+fn else None,
            "cost": costs([records.get(row["call_id"], {}) for row in selected], 24)}
    available = sum(row["available"] for row in rows)
    return {"schema": "b05-state-representation72-result-v1",
        "complete": bool(qualified and available == 72 and not start_only),
        "runtime_qualified": qualified, "planned": 72, "available": available,
        "unknown": 72-available, "context_units": 12, "paired_seed_units": 24,
        "arms": arms, "rows": rows, "cost": costs(list(records.values()), 72),
        "start_only": sorted(start_only), "unattempted": sorted(expected-set(records)),
        "primary": "unordered known unique-ID exact; explicit valid-set denominators",
        "strict_sorted_format_separate": True, "unknown_is_not_wrong": True,
        "unresolved_groups_only_public_rows": True, "no_eligibility_computation": True,
        "token_costs_not_matched": True, "not_learned_decomposition": True}

