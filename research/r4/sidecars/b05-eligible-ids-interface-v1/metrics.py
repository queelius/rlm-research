"""Host-only fixed-denominator selection and same-lookup comparison, after release."""
import collections
import json
import sys
import interface
import study

with study.aliases({"runner_study": study}, study.SOURCE):
    inherited = study.load("ids_only_cost_metrics", study.SOURCE / "runner_metrics.py")


def summarize(output, runtime_qualified):
    schedule = study.calls()
    expected = {study.call_id(call): call for call in schedule}
    records = {path.stem: study.read(path) for path in (output / "calls").glob("*.json")}
    starts = {path.stem: study.read(path) for path in (output / "starts").glob("*.json")}
    assert set(records) <= set(expected) and set(starts) <= set(expected)
    start_only = set(starts)-set(records)
    for key in start_only:
        records[key] = {**starts[key], "status": "start_only_provider_unknown", "usage": {}, "transport_valid": False}
    roots = {root["root_id"]: root for root in study.active_roots()}
    api = study.source.b05()
    parser = sys.modules["b05_native_runner_etl_catalog.grading"]._parse_json_object
    arms = {}
    all_rows = {}
    for arm in ("v3_full_report", "ids_only"):
        rows, resolved = [], {}
        for call_id, call in expected.items():
            record = study.read(study.BASELINE / "calls" / (call_id+".json")) if arm == "v3_full_report" else records.get(call_id, {})
            child = roots[call["root_id"]]["safe_children"][call["child_index"]]
            target = {row["implementation_id"] for row in interface.reference().solve_child_reference(child)["rows"]}
            value = {"call_id": call_id, "root_id": call["root_id"], "child_index": call["child_index"],
                     "alternative": call["alternative"], "seed": call["seed"], "available": bool(record.get("transport_valid")),
                     "strict_claim_valid": False, "id_set_exact": False, "precision": None, "recall": None,
                     "original_status": record.get("status"), "original_grade_status": (record.get("child_grade") or {}).get("status"),
                     "diagnostic_id_projection": None}
            if record.get("transport_valid"):
                if arm == "ids_only":
                    grade = interface.grade(record["text"], child)
                    assert grade == record["child_grade"]
                    ids = grade["parsed"]["eligible_ids"] if grade["parsed"] is not None else None
                else:
                    grade = api.grade_child_response(record["text"], child)
                    assert grade == record["child_grade"]
                    ids = [row["implementation_id"] for row in grade["parsed"]["rows"]] if grade["parsed"] is not None else None
                    try:
                        raw = parser(record["text"])
                        projected = [row["implementation_id"] for row in raw["rows"]]
                        known = {row["implementation_id"] for row in child["stage"]["tables"]["implementations"]}
                        assert len(projected) == len(set(projected)) and set(projected) <= known
                        value["diagnostic_id_projection"] = selection_metrics(projected, target)
                    except Exception:
                        pass
                if ids is not None:
                    value.update(strict_claim_valid=True, ids=ids, **selection_metrics(ids, target))
                    resolved[call_id] = interface.lookup(ids, child)
            rows.append(value)
        recombinations = []
        for call in study.source.calls():
            if call["kind"] != "recombined_synthesis":
                continue
            dependency = [next(key for key, item in expected.items() if item["root_id"] == call["root_id"]
                               and item["child_index"] == index and item["alternative"] == alternative)
                          for index, alternative in enumerate(call["alternatives"])]
            value = {"call_id": study.call_id(call), "root_id": call["root_id"], "alternatives": call["alternatives"],
                     "dependency_call_ids": dependency, "status": "dependency_unsupported"}
            if all(key in resolved for key in dependency):
                reports = [resolved[key] for key in dependency]
                root = roots[call["root_id"]]["safe_root"]
                answer = api.combine_reports(root, reports)
                grade = api.grade_root_response(json.dumps(answer), root)
                value.update(status="host_combined", answer=answer, source_grade=grade,
                             report_implied_feasible=answer["status"] == "selected",
                             selected_ids_never_eligibility_filtered=True)
            recombinations.append(value)
        valid = [row for row in rows if row["strict_claim_valid"]]
        tp = sum(row["true_positive"] for row in valid)
        fp = sum(row["false_positive"] for row in valid)
        fn = sum(row["false_negative"] for row in valid)
        arms[arm] = {"planned_children": 24, "available": sum(row["available"] for row in rows),
                     "strict_valid": len(valid), "invalid_known": sum(row["available"] and not row["strict_claim_valid"] for row in rows),
                     "unknown": sum(not row["available"] for row in rows), "id_set_exact": sum(row["id_set_exact"] for row in rows),
                     "micro_true_positive": tp, "micro_false_positive": fp, "micro_false_negative": fn,
                     "precision_valid_only": tp/(tp+fp) if tp+fp else None,
                     "recall_valid_only": tp/(tp+fn) if tp+fn else None,
                     "precision_recall_valid_denominator": len(valid), "children": rows, "recombinations": recombinations,
                     "host_source_correct": sum((row.get("source_grade") or {}).get("status") == "correct" for row in recombinations),
                     "host_unsupported": sum(row["status"] == "dependency_unsupported" for row in recombinations)}
        all_rows[arm] = rows
    return {"schema": "b05-eligible-ids-interface-result-v1", "runtime_qualified": runtime_qualified,
            "complete": bool(runtime_qualified and set(records) == set(expected) and not start_only and all(row.get("transport_valid") for row in records.values())),
            "planned_coordinates": 24, "active_roots": 4, "arms": arms,
            "physical_cost": inherited.costs(list(records.values()), 24), "root_model_calls": 0,
            "natural_model_calls_per_host_plan": 3, "CPU_recombined_coordinates_per_arm": 32,
            "same_lookup_both_arms": True, "lookup_is_host_arithmetic_not_model_skill": True,
            "missing_call_ids": sorted(set(expected)-set(records)), "start_only_call_ids": sorted(start_only),
            "paired_known": sum(a["available"] and b["available"] for a,b in zip(all_rows["v3_full_report"], all_rows["ids_only"], strict=True)),
            "paired_exact_wins": sum(a["available"] and b["available"] and not a["id_set_exact"] and b["id_set_exact"] for a,b in zip(all_rows["v3_full_report"], all_rows["ids_only"], strict=True)),
            "paired_exact_losses": sum(a["available"] and b["available"] and a["id_set_exact"] and not b["id_set_exact"] for a,b in zip(all_rows["v3_full_report"], all_rows["ids_only"], strict=True)),
            "benchmark_admission_or_novelty_claim": False}


def selection_metrics(ids, target):
    chosen = set(ids)
    tp = len(chosen & target)
    return {"id_set_exact": chosen == target, "true_positive": tp, "false_positive": len(chosen-target),
            "false_negative": len(target-chosen), "precision": tp/len(chosen) if chosen else None,
            "recall": tp/len(target) if target else None}
