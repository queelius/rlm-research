"""Small descriptive paired analysis; saved AST inspection only, never run generated code."""

import argparse
import ast
import json
from collections import Counter
from pathlib import Path

import study as s

c = s.c
CELLS = [(w, a) for w in s.WEIGHTS for a in s.ARMS]


def static_markers(code):
    try:
        tree = ast.parse(code)
    except (SyntaxError, TypeError):
        return {"direct_answer_extend": None, "json_loads": None, "python_ast_parsed": False}
    calls = [node for node in ast.walk(tree) if isinstance(node, ast.Call)]
    return {"direct_answer_extend": sum(isinstance(n.func, ast.Attribute) and n.func.attr == "extend"
        and len(n.args) == 1 and isinstance(n.args[0], ast.Attribute) and n.args[0].attr == "answer" for n in calls),
        "json_loads": sum(isinstance(n.func, ast.Attribute) and n.func.attr == "loads"
            and isinstance(n.func.value, ast.Name) and n.func.value.id == "json" for n in calls),
        "python_ast_parsed": True}


def code_markers(episode):
    codes, observations = [], []
    for trace in episode.get("traces") or []:
        if not trace.get("is_completed") or trace.get("root_reply") is None:
            continue
        nodes = trace.get("nodes") or []
        index, seen = len(nodes) - 1, set()
        while type(index) is int and 0 <= index < len(nodes) and index not in seen:
            seen.add(index)
            node = nodes[index]
            message = node.get("message") or {}
            if message.get("role") == "tool":
                observations.append(str(message.get("content") or ""))
            for call in message.get("tool_calls") or []:
                function = call.get("function") or call
                if function.get("name") != "ipython":
                    continue
                args = function.get("arguments") or {}
                try:
                    args = json.loads(args) if isinstance(args, str) else args
                except json.JSONDecodeError:
                    continue
                if isinstance(args, dict) and isinstance(args.get("code"), str):
                    codes.append(args["code"])
            index = node.get("parent")
    parsed = [static_markers(code) for code in codes]
    return {"root_code_cells_observed": len(codes), "root_tool_observations": len(observations),
        "direct_answer_extend": sum(p["direct_answer_extend"] or 0 for p in parsed) if codes else None,
        "json_loads": sum(p["json_loads"] or 0 for p in parsed) if codes else None,
        "unparsed_root_cells": sum(not p["python_ast_parsed"] for p in parsed),
        "observed_tool_TypeError_marker": any("TypeError" in text for text in observations) if observations else None,
        "observed_tool_JSONDecodeError_marker": any("JSONDecodeError" in text for text in observations) if observations else None,
        "interpretation": "narrow code/observation markers, not hidden-state or executed-dataflow proof; no observation means null"}


def episode_metrics(episode, seconds):
    result = s.native.capture.native.episode_metrics(episode, seconds)
    result["return_type_diagnostics"] = code_markers(episode)
    result["first_root"] = None
    for trace in episode.get("traces") or []:
        sampled = [(i, node) for i, node in enumerate(trace.get("nodes") or []) if node.get("sampled")]
        if not sampled:
            continue
        index, node = sampled[0]
        call = next((r for r in trace.get("calls") or [] if r.get("node") == index), None)
        if call is None:
            continue
        message = node.get("message") or {}
        tools = message.get("tool_calls") or []
        result["first_root"] = {"node": index, "finish_reason": call.get("finish_reason"),
            "action_tokens": sum(node.get("mask") or []), "completion_tokens": (call.get("usage") or {}).get("completion_tokens"),
            "structured_tool_present": bool(tools),
            "structured_ipython_present": any((t.get("name") or (t.get("function") or {}).get("name")) == "ipython" for t in tools),
            "message_content_characters": len(message["content"]) if isinstance(message.get("content"), str) else None}
        break
    return result


def summarize(records, plan):
    by_id = {r["coordinate"]["id"]: r for r in records}
    planned = {r["id"]: r for r in plan}
    if len(by_id) != len(records) or not by_id.keys() <= planned.keys():
        raise ValueError("duplicate or unplanned episode")
    if any(r["coordinate"] != planned[r["coordinate"]["id"]] for r in records):
        raise ValueError("raw coordinate differs from frozen plan")
    cells = []
    for weight, arm in CELLS:
        rows = [r["derived"] for r in records if (r["coordinate"]["weight"], r["coordinate"]["arm"]) == (weight, arm)]
        cells.append({"weight": weight, "arm": arm,
            "planned": sum((r["weight"], r["arm"]) == (weight, arm) for r in plan),
            "recorded": len(rows), "observable": sum(r.get("strict_reward") is not None for r in rows),
            "strict_successes": sum(r.get("strict_reward") == 1 for r in rows),
            "execution_failures": sum(not r.get("execution_completed", False) for r in rows),
            "usage": {key: sum(r.get(key, 0) or 0 for r in rows) for key in
                ("model_calls", "completion_tokens", "logical_input_tokens", "wall_seconds", "recursive_subcalls", "truncated_calls", "calls_without_cache_measurement")}})
    matches = {}
    for row in plan:
        match = matches.setdefault(row["matched_id"], {"matched_id": row["matched_id"],
            "task_name": row["task_name"], "seed": row["seed"], "context_sha256": row["context_sha256"],
            "outcomes": {w + "/" + a: None for w, a in CELLS}})
        match["outcomes"][row["weight"] + "/" + row["arm"]] = by_id.get(row["id"], {}).get("derived", {}).get("strict_reward")
    def delta(a, b):
        return a - b if a is not None and b is not None else None
    for match in matches.values():
        outcomes = match["outcomes"]
        for weight in s.WEIGHTS:
            match[weight + "_contract_minus_unchanged"] = delta(outcomes[weight + "/contract"], outcomes[weight + "/unchanged"])
        for arm in s.ARMS:
            match[arm + "_step8_minus_original"] = delta(outcomes["step8/" + arm], outcomes["original/" + arm])
        match["interaction"] = delta(match["step8_contract_minus_unchanged"], match["original_contract_minus_unchanged"])
    contrasts = [w + "_contract_minus_unchanged" for w in s.WEIGHTS] + [a + "_step8_minus_original" for a in s.ARMS] + ["interaction"]
    def summary(rows):
        return {key: {"observable_matches": sum(row[key] is not None for row in rows),
            "sum": sum(row[key] or 0 for row in rows),
            "mean": (sum(row[key] or 0 for row in rows) / sum(row[key] is not None for row in rows)) if any(row[key] is not None for row in rows) else None,
            "positive": sum(row[key] is not None and row[key] > 0 for row in rows),
            "negative": sum(row[key] is not None and row[key] < 0 for row in rows)} for key in contrasts}
    contexts = [{"context_sha256": sha, "planned_matches": len(rows), "contrasts": summary(rows)}
        for sha in sorted({r["context_sha256"] for r in plan})
        for rows in [[m for m in matches.values() if m["context_sha256"] == sha]]]
    return {"planned": len(plan), "recorded": len(records), "cells": cells,
        "matched": list(matches.values()), "contrasts": summary(list(matches.values())), "contexts": contexts,
        "unrun_coordinates": [r["id"] for r in plan if r["id"] not in by_id],
        "caution": "96 planned episodes nest within24 task/seed coordinates and6 exposed contexts; two service phases confound weight with time/order"}


def analyze(output):
    spec = s.verify()
    files = sorted(Path(output).glob("phase-*/rollout/episodes/*.json"))
    records = [c.read(path) for path in files]
    report = summarize(records, spec["plan"])
    evidence = []
    for path, record in zip(files, records, strict=True):
        if c.digest(record["episode"]) != record["episode_sha256"]:
            raise ValueError("raw episode content hash changed")
        attempt = path.parent.parent
        phase = s.verify_phase(attempt / "SPEC.json")
        proof = {"episode_id": path.stem, "source_path": str(path), "source_sha256": c.file_hash(path),
            "markers": code_markers(record["episode"]), "exact_native_capture_verified": None}
        try:
            roots, calls = s.native.exporter.episode_turns(record["episode"], attempt.with_name("rollout-routing"), phase["role_binding"])
            if any(call["sampling"]["seed"] != record["coordinate"]["seed"] for call in calls):
                raise ValueError("actual call seed differs from frozen matched coordinate")
            proof.update(exact_native_capture_verified=True, root_calls=len(roots),
                child_calls=len(calls)-len(roots), root_action_tokens=sum(len(t["old_logprobs"]) for t in roots))
        except (ValueError, KeyError, TypeError, AttributeError) as error:
            proof.update(exact_native_capture_verified=False, capture_error=str(error))
        evidence.append(proof)
    costs = []
    for path in sorted(Path(output).glob("phase-*/rollout-routing/role-audit/*-result.json")):
        audit = c.read(path)
        wire = audit.get("native_wire_request", {}).get("body", {})
        response = audit.get("native_wire_response", {})
        try:
            payload = json.loads(response.get("body", "null"))
            choices = payload.get("choices", []) if isinstance(payload, dict) else []
        except json.JSONDecodeError:
            choices = []
        action = sum(len(choice.get("token_ids") or []) for choice in choices) if choices else None
        costs.append({"audit_path": str(path), "audit_sha256": c.file_hash(path),
            "request_id": audit.get("request_id"), "alias": audit.get("actual_alias"), "depth": audit.get("depth"),
            "status": audit["status"], "http_status": response.get("http_status"),
            "physical_prompt_tokens": len(wire["token_ids"]) if "token_ids" in wire else None,
            "physical_action_tokens": action, "cached_tokens": None,
            "wall_seconds": audit["ended"] - audit["started"]})
    report.update(episode_evidence=evidence, physical_calls=costs,
        physical_cost_totals={"retained_attempts": len(costs),
            "physical_prompt_tokens": sum(r["physical_prompt_tokens"] or 0 for r in costs),
            "physical_action_tokens": sum(r["physical_action_tokens"] or 0 for r in costs),
            "missing_prompt_counts": sum(r["physical_prompt_tokens"] is None for r in costs),
            "missing_action_counts": sum(r["physical_action_tokens"] is None for r in costs), "cached_tokens": None},
        source_manifest={str(p): c.file_hash(p) for p in [s.ROOT / "SPEC.json", *files]},
        source_spec_path=str(s.ROOT / "SPEC.json"), phase_status={p.parent.parent.name: c.read(p) for p in Path(output).glob("phase-*/rollout/STATUS.json")})
    c.write_once(Path(output) / "ANALYSIS.json", report)
    return report


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    print(json.dumps({"recorded": analyze(args.output)["recorded"]}))
