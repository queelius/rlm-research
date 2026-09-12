"""Independent source-to-native audit of the paired B05 eligible-IDs interface screen."""

from __future__ import annotations

import argparse
from collections import Counter
import hashlib
import importlib.util
import json
import math
from pathlib import Path
import sys
from typing import Any


HERE = Path(__file__).resolve().parent
STORE = HERE.parents[1]
SIDE = STORE / "sidecars/b05-eligible-ids-interface-v1"
SOURCE = STORE / "sidecars/b05-recombination-feasibility-v1"
ATTEMPT = SIDE / "outputs/attempt-001"
READY = SIDE / "READY_RUN.json"
READY_SHA256 = "3fe8fff0d3d177f54171a54544998a2de8568b01743896254b1347afa97b9aa3"
BASELINE = SOURCE / "outputs/attempt-003"
BASELINE_READY = SOURCE / "READY_RUN_V3.json"
BASELINE_READY_SHA256 = "b534d80731de70cc250ec4138204a177629cfb19ded6b5a1b637345d964acee8"


def read(path: Path) -> Any:
    return json.loads(Path(path).read_text())


def sha(path: Path) -> str:
    with Path(path).open("rb") as stream:
        return hashlib.file_digest(stream, "sha256").hexdigest()


def write_x(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("x") as stream:
        json.dump(value, stream, sort_keys=True, indent=2, ensure_ascii=False, allow_nan=False)
        stream.write("\n")


def modules():
    if str(SIDE) not in sys.path:
        sys.path.insert(0, str(SIDE))
    import interface
    import study

    return study, interface


def strict_json_parser():
    study, interface = modules()
    interface.reference()
    return sys.modules["b05_native_runner_etl_catalog.grading"]._parse_json_object


def project_ids(text: str, arm: str) -> dict[str, Any]:
    try:
        value = strict_json_parser()(text)
        if arm == "ids_only":
            ids = value.get("eligible_ids")
            if not isinstance(ids, list) or not all(isinstance(item, str) for item in ids):
                raise ValueError("eligible_ids is not a string list")
            return {"ids": ids, "metadata_rows": [], "projection_error": None}
        rows = value.get("rows")
        if not isinstance(rows, list) or not all(isinstance(row, dict) for row in rows):
            raise ValueError("rows is not an object list")
        ids = [row.get("implementation_id") for row in rows]
        if not all(isinstance(item, str) for item in ids):
            raise ValueError("implementation_id missing")
        return {"ids": ids, "metadata_rows": rows, "projection_error": None}
    except Exception as error:
        return {
            "ids": [],
            "metadata_rows": [],
            "projection_error": f"{type(error).__name__}: {error}",
        }


def id_metric(ids: list[str], target: set[str]) -> dict[str, Any]:
    predicted = set(ids)
    duplicate_ids = len(ids) - len(predicted)
    true_positive = len(predicted & target)
    return {
        "predicted_ids": sorted(predicted),
        "eligible_ids": sorted(target),
        "true_positive": true_positive,
        "false_positive": len(predicted - target),
        "false_negative": len(target - predicted),
        "duplicate_ids": duplicate_ids,
        "id_set_exact": duplicate_ids == 0 and predicted == target,
        "precision": true_positive / len(predicted) if predicted else None,
        "recall": true_positive / len(target) if target else None,
    }


def response_integrity(path: Path, recorded_digest: str, study) -> dict[str, Any]:
    raw = path.read_bytes()
    response = json.loads(raw)
    return {
        "response": response,
        "raw_bytes_sha256": hashlib.sha256(raw).hexdigest(),
        "canonical_content_sha256": study.digest(response),
        "canonical_content_matches_recorded": study.digest(response) == recorded_digest,
        "recorded_field_is_canonical_content_not_raw_bytes": True,
    }


def validate_physical(call, record, prompt, study) -> tuple[list[str], dict[str, Any]]:
    issues = []
    prompt_path = Path(record["prompt_path"])
    request_path = Path(record["request_path"])
    response_path = Path(record["response_path"])
    saved_prompt = read(prompt_path)["messages"][0]["content"]
    if saved_prompt != prompt:
        issues.append("saved_prompt")
    if record.get("prompt_sha256") != sha(prompt_path):
        issues.append("prompt_sha")
    body = read(request_path)
    expected = study.request_body(prompt, call["seed"], call["max_tokens"])
    if body != expected:
        issues.append("request_body_or_prefix")
    if record.get("request_sha256") != sha(request_path):
        issues.append("request_sha")
    if record.get("prefix_token_ids_sha256") != study.digest(body["token_ids"]):
        issues.append("prefix_token_ids_sha")
    response_info = response_integrity(response_path, record["response_sha256"], study)
    response = response_info.pop("response")
    if not response_info["canonical_content_matches_recorded"]:
        issues.append("response_canonical_content")
    decoded = study.decode_response(body, response)
    for key in (
        "transport_valid",
        "text",
        "finish_reason",
        "completion_ids",
        "completion_logprobs",
        "request_id",
        "usage",
    ):
        if decoded.get(key) != record.get(key):
            issues.append("decoded_" + key)
    if response.get("model") != study.MODEL_ALIAS:
        issues.append("model_alias")
    if not all(math.isfinite(float(value)) for value in record.get("completion_logprobs", [])):
        issues.append("nonfinite_logprob")
    return issues, {
        "request_sha256": sha(request_path),
        "response_raw_bytes_sha256": response_info["raw_bytes_sha256"],
        "response_canonical_content_sha256": response_info["canonical_content_sha256"],
        "prefix_token_ids_sha256": study.digest(body["token_ids"]),
        "prefix_tokens": len(body["token_ids"]),
        "completion_tokens": len(record.get("completion_ids", [])),
        "usage": response.get("usage"),
        "finish_reason": record.get("finish_reason"),
        "provider_id": record.get("request_id"),
    }


def runtime_attestation(attempt: Path, study) -> dict[str, Any]:
    terminal = read(attempt / "OWNER_TERMINAL.json")
    result = read(attempt / "RESULT.json")
    if not (
        terminal.get("complete")
        and terminal.get("released")
        and terminal.get("runtime_qualified")
        and result.get("complete")
        and result.get("released")
        and result.get("runtime_qualified")
    ):
        raise RuntimeError(f"owner is not complete/released/runtime-qualified: {attempt}")
    if terminal["result_sha256"] != sha(attempt / "RESULT.json"):
        raise ValueError("terminal/result link differs")
    service = attempt / "service/service"
    log_path = service / "inference.log"
    log = log_path.read_text()
    expected = "Injected <class 'report_worker.ReportWorker'>"
    default = (
        "Injected <class "
        "'prime_rl.inference.vllm.worker.filesystem.FileSystemWeightUpdateWorker'>"
    )
    dispatch = read(service / "ACTUAL_DISPATCH.json")
    owner = read(attempt / "ENGINE_ATTESTATION.json")
    issues = []
    if expected not in log or default in log:
        issues.append("actual_worker_marker")
    if dispatch.get("instrumentation_sha256") != study.sha(study.MUSIQUE / "report_worker.py"):
        issues.append("dispatch_instrumentation")
    if dispatch.get("installed_batch_invariant_mode") is not True:
        issues.append("dispatch_mode")
    if dispatch.get("original_function_returned") is not True:
        issues.append("dispatch_return")
    if owner.get("dispatch_receipt_sha256") != sha(service / "ACTUAL_DISPATCH.json"):
        issues.append("owner_dispatch_link")
    return {
        "issues": issues,
        "actual_report_worker_marker": expected in log,
        "default_worker_marker_absent": default not in log,
        "dispatch_sha256": sha(service / "ACTUAL_DISPATCH.json"),
        "inference_log_sha256": sha(log_path),
        "owner_attestation_sha256": sha(attempt / "ENGINE_ATTESTATION.json"),
        "terminal_sha256": sha(attempt / "OWNER_TERMINAL.json"),
        "result_sha256": sha(attempt / "RESULT.json"),
        "config_is_not_runtime_proof": True,
    }


def arm_records(arm: str, attempt: Path, study, interface) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    source_roots = {root["root_id"]: root for root in study.active_roots()}
    contract = study.load("b05_ids_audit_contract_v3", study.SOURCE / "contract_v3.py")
    issues = []
    rows = []
    records = {path.stem: read(path) for path in (attempt / "calls").glob("*.json")}
    for call in study.calls():
        call_id = study.call_id(call)
        record = records.get(call_id)
        if record is None:
            issues.append({"arm": arm, "call_id": call_id, "issue": "missing_record"})
            continue
        root = source_roots[call["root_id"]]
        child = root["safe_children"][call["child_index"]]
        original = root["child_prompts"][call["child_index"]]
        prompt = interface.render(original) if arm == "ids_only" else contract.clarify(call, original)
        local, physical = validate_physical(call, record, prompt, study)
        issues.extend({"arm": arm, "call_id": call_id, "issue": item} for item in local)
        strict = (
            interface.grade(record["text"], child)
            if arm == "ids_only"
            else study.source.b05().grade_child_response(record["text"], child)
        )
        if strict != record.get("child_grade"):
            issues.append({"arm": arm, "call_id": call_id, "issue": "strict_grade"})
        projection = project_ids(record["text"], arm)
        known = {
            row["implementation_id"]
            for row in child["stage"]["tables"]["implementations"]
        }
        target_rows = interface.reference().solve_child_reference(child)["rows"]
        target_by_id = {row["implementation_id"]: row for row in target_rows}
        receipt = interface.reference().child_reference_receipt(child)
        effective_by_id = {
            row["implementation_id"]: row["effective_row"]
            for row in receipt["derivations"]
        }
        metric = id_metric(projection["ids"], set(target_by_id))
        valid_ids_for_lookup = (
            projection["projection_error"] is None
            and len(projection["ids"]) == len(set(projection["ids"]))
            and set(projection["ids"]) <= known
        )
        lookup = interface.lookup(projection["ids"], child) if valid_ids_for_lookup else None
        looked_up = {row["implementation_id"]: row for row in (lookup or {}).get("rows", [])}
        metadata_rows = {
            row["implementation_id"]: row
            for row in projection["metadata_rows"]
            if isinstance(row.get("implementation_id"), str)
        }
        matched = set(metric["predicted_ids"]) & set(metric["eligible_ids"])
        rows.append(
            {
                "arm": arm,
                "call_id": call_id,
                "root_id": call["root_id"],
                "child_index": call["child_index"],
                "alternative": call["alternative"],
                "seed": call["seed"],
                "strict_grade_status": strict.get("status"),
                "strict_claim_valid": strict.get("parsed") is not None,
                "inert_projection": projection,
                "id_metric": metric,
                "model_metadata_claimed": arm == "full_report",
                "model_metadata_exact_for_matched_ids": sum(
                    metadata_rows.get(key) == target_by_id[key] for key in matched
                ),
                "model_metadata_wrong_for_matched_ids": sum(
                    metadata_rows.get(key) != target_by_id[key] for key in matched
                ) if arm == "full_report" else None,
                "host_lookup_applied": lookup is not None,
                "host_lookup_ids_unchanged": set(looked_up) == set(projection["ids"])
                if lookup is not None else None,
                "host_lookup_metadata_matches_source_effective_rows": all(
                    looked_up[key] == effective_by_id[key]
                    for key in looked_up
                ) if lookup is not None else None,
                "host_lookup_retained_claimed_ineligible_ids": (
                    (set(projection["ids"]) - set(target_by_id)) <= set(looked_up)
                    if lookup is not None else None
                ),
                "lookup_all_known_ids_count": len(interface.lookup(sorted(known), child)["rows"]),
                "source_known_ids_count": len(known),
                "host_lookup_does_not_establish_eligibility": True,
                "physical": physical,
            }
        )
        saved = rows[-1]
        if saved["lookup_all_known_ids_count"] != saved["source_known_ids_count"]:
            issues.append({"arm": arm, "call_id": call_id, "issue": "lookup_filtered_known_id"})
        if lookup is not None and not saved["host_lookup_ids_unchanged"]:
            issues.append({"arm": arm, "call_id": call_id, "issue": "lookup_changed_id_set"})
        if lookup is not None and not saved["host_lookup_metadata_matches_source_effective_rows"]:
            issues.append({"arm": arm, "call_id": call_id, "issue": "lookup_metadata"})
    return rows, issues


def aggregate(rows: list[dict[str, Any]], *, strict_only: bool) -> dict[str, Any]:
    selected = [row for row in rows if row["strict_claim_valid"]] if strict_only else rows
    totals = Counter()
    for row in selected:
        metric = row["id_metric"]
        totals["true_positive"] += metric["true_positive"]
        totals["false_positive"] += metric["false_positive"]
        totals["false_negative"] += metric["false_negative"]
        totals["exact_sets"] += metric["id_set_exact"]
    tp, fp, fn = totals["true_positive"], totals["false_positive"], totals["false_negative"]
    return {
        "denominator_records": len(selected),
        "true_positive": tp,
        "false_positive": fp,
        "false_negative": fn,
        "exact_sets": totals["exact_sets"],
        "micro_precision": tp / (tp + fp) if tp + fp else None,
        "micro_recall": tp / (tp + fn) if tp + fn else None,
        "conditional_on_strict_validity": strict_only,
    }


def run() -> dict[str, Any]:
    study, interface = modules()
    if sha(READY) != READY_SHA256 or sha(BASELINE_READY) != BASELINE_READY_SHA256:
        raise ValueError("source READY changed")
    study.verify()
    runtime = {
        "full_report": runtime_attestation(BASELINE, study),
        "ids_only": runtime_attestation(ATTEMPT, study),
    }
    arms = {}
    issues = []
    for arm, attempt in (("full_report", BASELINE), ("ids_only", ATTEMPT)):
        rows, local = arm_records(arm, attempt, study, interface)
        issues.extend(local)
        all24 = aggregate(rows, strict_only=False)
        valid = aggregate(rows, strict_only=True)
        if len(rows) != 24 or all24["true_positive"] + all24["false_negative"] != 64:
            issues.append({"arm": arm, "issue": "fixed_24_record_64_eligible_denominator"})
        usage = Counter()
        for row in rows:
            for key in ("prompt_tokens", "completion_tokens", "total_tokens"):
                value = (row["physical"].get("usage") or {}).get(key)
                if isinstance(value, int):
                    usage[key] += value
        arms[arm] = {
            "records": rows,
            "strict_valid": sum(row["strict_claim_valid"] for row in rows),
            "all_24_inert_id_projection": all24,
            "strict_valid_conditional_id_metrics": valid,
            "usage": dict(usage),
            "host_lookup_deterministic_metadata_not_model_learning": True,
        }
        issues.extend(
            {"arm": arm, "issue": value}
            for value in runtime[arm]["issues"]
        )
    baseline = {row["call_id"]: row for row in arms["full_report"]["records"]}
    ids = {row["call_id"]: row for row in arms["ids_only"]["records"]}
    paired = []
    for call_id in sorted(baseline):
        first, second = baseline[call_id], ids[call_id]
        paired.append(
            {
                "call_id": call_id,
                "root_id": first["root_id"],
                "child_index": first["child_index"],
                "alternative": first["alternative"],
                "same_seed": first["seed"] == second["seed"],
                "full_report_exact": first["id_metric"]["id_set_exact"],
                "ids_only_exact": second["id_metric"]["id_set_exact"],
            }
        )
    output = {
        "schema": "b05-eligible-ids-interface-independent-native-audit-v1",
        "status": "COMPLETE_RAW_AUDIT" if not issues else "AUDIT_WITH_INTEGRITY_ISSUES",
        "source_ready_sha256": sha(READY),
        "baseline_ready_sha256": sha(BASELINE_READY),
        "runtime": runtime,
        "arms": arms,
        "paired": {
            "records": paired,
            "known": len(paired),
            "ids_only_exact_wins": sum(
                not row["full_report_exact"] and row["ids_only_exact"] for row in paired
            ),
            "ids_only_exact_losses": sum(
                row["full_report_exact"] and not row["ids_only_exact"] for row in paired
            ),
        },
        "integrity_issues": issues,
        "interpretation": {
            "root_lookup_filters_ineligible": False,
            "root_lookup_uses_every_claimed_known_id": True,
            "root_lookup_is_host_arithmetic_not_model_learning": True,
            "all_24_projection_is_inert_not_strict_answer_repair": True,
            "only_four_root_context_units": True,
            "no_root_model_calls": True,
        },
        "gpu_calls_in_analysis": 0,
        "model_calls_in_analysis": 0,
    }
    write_x(HERE / "RESULTS.json", output)
    a, b = arms["full_report"], arms["ids_only"]
    report = f"""---
title: B05 eligible-IDs interface independent native audit
date: 2026-09-12
status: {output['status']}
---

# B05 eligible-IDs interface independent native audit

Both arms contain 24/24 paired child coordinates over four root contexts. The all-record
inert projection uses the fixed 64 eligible-ID denominator. Full-report precision/recall
is {a['all_24_inert_id_projection']['micro_precision']} /
{a['all_24_inert_id_projection']['micro_recall']}; IDs-only precision/recall is
{b['all_24_inert_id_projection']['micro_precision']} /
{b['all_24_inert_id_projection']['micro_recall']}. The IDs-only arm has
{output['paired']['ids_only_exact_wins']} exact-set wins and
{output['paired']['ids_only_exact_losses']} losses relative to the paired full-report arm.

Strict-valid-only metrics are separately labeled and use denominators
{a['strict_valid_conditional_id_metrics']['denominator_records']} and
{b['strict_valid_conditional_id_metrics']['denominator_records']}; invalid outputs are not
silently credited as valid answers. Every saved prompt was independently re-rendered to
the exact native request, and response token IDs, chosen-token logprobs, usage, model,
provider ID, canonical response-content digest, and actual `ReportWorker` runtime marker
were checked. Integrity issues: {len(issues)}.

The host lookup retains every claimed known ID, including ineligible IDs, and only supplies
deterministic effective metadata. It does not infer eligibility, repair the model's ID set,
or demonstrate model learning. The 32 downstream combinations are CPU host arithmetic,
not additional model calls or independent root problems.
"""
    (HERE / "REPORT.md").write_text(report)
    return output


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("command", choices=("run", "check"))
    args = parser.parse_args()
    if args.command == "check":
        print("terminal" if (ATTEMPT / "OWNER_TERMINAL.json").exists() else "pending")
    else:
        print(json.dumps(run()["status"]))
