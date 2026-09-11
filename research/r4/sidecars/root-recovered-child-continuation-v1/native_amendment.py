"""Narrow, authenticated unsampled-child-overflow exclusion; original checks retained."""

import argparse
import asyncio
import copy
import json
import re
from collections import Counter
from pathlib import Path

import common as a

c = a.c
import campaign_native as old
import campaign_lifecycle_v2 as lifecycle

BASE_BINDING = lifecycle.binding_for
BASE_PREPARE = lifecycle.prepare_spec
REJECTION = re.compile(r"The decoder prompt \(length (\d+)\) is longer than the maximum model length of (\d+)\. Make sure that `max_model_len` is no smaller than the number of text tokens\.")


def verify_failed_call(call, audit, binding, seed):
    """Accept no generated tokens: this recognizes one exact failure family only."""
    request_id = (call.get("acp") or {}).get("request_id")
    alias = binding["fixed_child"]
    error = call.get("error") or {}
    wire = audit.get("native_wire_request", {}).get("body", {})
    response = audit.get("native_wire_response", {})
    if not request_id or request_id != audit.get("request_id"):
        raise ValueError("missing or mismatched failed request identity")
    if (audit.get("status") != "error" or audit.get("depth") != 1
            or audit.get("actual_alias") != alias or call.get("model") != alias or wire.get("model") != alias
            or audit.get("model_sha256") != binding["models"][alias]["adapter_sha256"]
            or audit.get("model_sha256") != c.CHILD_SHA
            or audit.get("role_map_sha256") != c.digest(binding["role_map"])):
        raise ValueError("failed child role/model/hash binding mismatch")
    if (error.get("type") != "ProviderError" or audit.get("error_type") != "ProviderError"
            or error.get("status_code") != 400 or response.get("http_status") != 400):
        raise ValueError("unknown provider failure family")
    if call.get("node") is not None or call.get("usage") is not None or audit.get("native_response") is not None:
        raise ValueError("failed request may contain sampled or ambiguous completion evidence")
    payload = json.loads(response["body"])
    if set(payload) != {"error"} or not isinstance(payload["error"], dict):
        raise ValueError("failed raw response contains ambiguous output")
    details = payload["error"]
    match = REJECTION.fullmatch(details.get("message", ""))
    if not match or details.get("type") != "BadRequestError" or details.get("code") != 400:
        raise ValueError("not the explicit decoder-context overflow rejection")
    ids = wire.get("token_ids")
    if not isinstance(ids, list) or any(type(token) is not int or token < 0 for token in ids):
        raise ValueError("invalid failed prompt token IDs")
    if int(match[2]) != 8192 or int(match[1]) != len(ids) or len(ids) <= 8192:
        raise ValueError("failed prompt length/model limit mismatch")
    sampler = dict(wire.get("sampling_params", {}))
    offset = sampler.pop("routed_experts_prompt_start", None)
    expected = {"logprobs": 1, "max_tokens": 2048, "min_p": 0.0, "return_token_ids": True,
                "seed": seed, "skip_special_tokens": False, "stop_token_ids": [151645, 151643],
                "temperature": .5, "top_k": -1, "top_p": 1.0}
    if sampler != expected or (offset is not None and (type(offset) is not int or not 0 <= offset <= len(ids))):
        raise ValueError("failed request sampling contract changed")
    if audit.get("kind") not in ("ordinary", "checkpoint") or not audit.get("invocation"):
        raise ValueError("unbound failed invocation kind")
    return {"request_id": request_id, "depth": 1, "alias": alias, "model_sha256": c.CHILD_SHA,
            "http_status": 400, "prompt_tokens": len(ids), "model_context_limit": 8192,
            "sampled_node": None, "training_admission": False}


def recovered_failure_proof(record, attempt, binding):
    if not record["derived"]["execution_completed"] or not record["derived"]["terminal_observable"]:
        raise ValueError("failed episode is not completed and observable")
    episode = record["episode"]
    traces = episode.get("traces") or []
    if not traces or any(t.get("root_reply") is None or not t.get("ok") or not t.get("is_completed") or t.get("errors") for t in traces):
        raise ValueError("completed root terminal identity missing")
    calls = [call for trace in traces for call in trace["calls"]]
    requested = [(call.get("acp") or {}).get("request_id") for call in calls]
    if None in requested or len(set(requested)) != len(requested):
        raise ValueError("missing/duplicate ACP request identity")
    audit_dir = attempt.with_name(attempt.name + "-routing")
    audits = {}
    for path in (audit_dir / "role-audit").glob("*-result.json"):
        value = c.read(path)
        if value.get("request_id") in requested:
            if value["request_id"] in audits:
                raise ValueError("duplicate request-local audit result")
            audits[value["request_id"]] = (value, path)
    if set(audits) != set(requested):
        raise ValueError("failed episode has missing request-local audit evidence")
    failed = []
    for call in calls:
        if call.get("error"):
            value, path = audits[call["acp"]["request_id"]]
            certificate = verify_failed_call(call, value, binding, record["coordinate"]["seed"])
            certificate.update(source_audit_path=str(path), source_audit_sha256=c.file_hash(path))
            failed.append(certificate)
    if not failed:
        raise ValueError("integrity failure has no authenticated unsampled child rejection")
    projected = copy.deepcopy(episode)
    for trace in projected["traces"]:
        trace["calls"] = [call for call in trace["calls"] if not call.get("error")]
    # All graph nodes, sample masks, physical prefixes, success wire responses,
    # aliases, hashes and semantic depth links still pass the untouched exporter.
    roots, evidence = old.exporter.episode_turns(projected, audit_dir, binding)
    if len(evidence) + len(failed) != len(calls) or any(t["sampling"]["seed"] != record["coordinate"]["seed"] for t in evidence):
        raise ValueError("successful/unsampled-failed call partition incomplete")
    return {"classification": "excluded_authenticated_unsampled_child_context_overflow",
        "failed_calls": failed, "all_request_ids_accounted": len(calls),
        "successful_calls_original_exporter_verified": len(evidence),
        "root_turns_diagnostic_only": len(roots),
        "root_action_tokens_diagnostic_only": sum(len(t["old_logprobs"]) for t in roots),
        "graph_nodes_removed": 0, "recovered_root_actions_admitted": False}


def rebuild_export(attempt, *, amendment_id=None):
    """Explicit ID permits CPU pre-freeze diagnosis; public export always authenticates it."""
    if amendment_id is None:
        amendment_id = a.verify_amendment()["amendment_id"]
    attempt = Path(attempt)
    if attempt.resolve() != a.OLD_ROUND04.resolve() and c.read(attempt / "SPEC.json").get("continuation_amendment_id") != amendment_id:
        raise ValueError("new collection is not from this continuation")
    rows, unused_group, manifest = old.rebuild_export(attempt)
    if attempt.resolve() == a.OLD_ROUND04.resolve():
        frozen = attempt.parent / "export"
        old_manifest = c.read(frozen / "MANIFEST.json")
        if rows != c.read(frozen / "EPISODES.json") or manifest != {k: v for k, v in old_manifest.items() if k != "artifact_sha256"}:
            raise ValueError("round04 evidence differs from the original frozen export")
    before = copy.deepcopy(rows)
    base_manifest_sha = c.digest(manifest)
    old_failures = {entry["episode_id"]: entry for entry in manifest["integrity_failures"]}
    recovered = []
    for row in rows:
        metadata = {"amendment_id": amendment_id, "endpoint_reward": row["strict_reward"],
                    "training_reward": row["reward"], "previous_training_admission_preserved": True,
                    "classification": "unchanged_admitted" if row["reward"] is not None else "unchanged_excluded"}
        if row["episode_id"] in old_failures:
            if row["reward"] is not None:
                raise ValueError("cannot reclassify an already admitted integrity failure")
            record = c.read(attempt / "episodes" / (row["episode_id"] + ".json"))
            proof = recovered_failure_proof(record, attempt, manifest["role_binding"])
            metadata.update(proof)
            recovered.append({"episode_id": row["episode_id"], "original_integrity_entry": old_failures[row["episode_id"]], "proof": proof})
        row["admission_metadata"] = metadata
    if [{k: v for k, v in row.items() if k != "admission_metadata"} for row in rows] != before:
        raise ValueError("amendment altered existing admission/outcome/action fields")
    # Unknown failed-call families raise above; no catch-and-forgive path exists.
    manifest["integrity_failures"] = []
    group, reason = None, None
    if manifest["generation"] is not None:
        try:
            group = old.capture.recursive.exporter.trainer_module().training_group(rows)
            group.update(dataset_id=manifest["dataset_id"], role_binding=manifest["role_binding"],
                         generation=manifest["generation"], credit_policy=c.read(attempt / "SPEC.json")["credit_policy"])
            group["group_id"] = c.digest({k: v for k, v in group.items() if k != "group_id"})
        except ValueError as error:
            if str(error) != "no fresh within-prompt mixed reward group":
                raise
            reason = str(error)
    manifest.update(training_group_episodes=len(group["episodes"]) if group else 0,
        training_group_unavailable_reason=reason,
        continuation_amendment_id=amendment_id, original_export_semantics_sha256=base_manifest_sha,
        reclassified_exclusions=recovered,
        endpoint_outcomes=dict(Counter("unobservable" if r["strict_reward"] is None else str(r["strict_reward"]) for r in rows)),
        admission_categories=dict(Counter(r["admission_metadata"]["classification"] for r in rows)),
        old_fields_by_episode_sha256={r["episode_id"]: c.digest(r) for r in before},
        recovered_episodes_newly_admitted=0)
    return rows, group, manifest


def export(attempt, output):
    amendment = a.verify_amendment()
    rows, group, manifest = rebuild_export(attempt, amendment_id=amendment["amendment_id"])
    output = Path(output)
    if output.exists():
        raise ValueError("new export path required; existing artifacts are immutable")
    output.mkdir(parents=True)
    c.write_once(output / "EPISODES.json", rows)
    if group:
        c.write_once(output / "GROUP.json", group)
    manifest["artifact_sha256"] = {path.name: c.file_hash(path) for path in output.iterdir()}
    c.write_once(output / "MANIFEST.json", manifest)
    return manifest


def authenticate_export(output):
    a.verify_amendment()
    output = Path(output)
    manifest = c.read(output / "MANIFEST.json")
    c.authenticate({output / name: sha for name, sha in manifest["artifact_sha256"].items()})
    rows, group, rebuilt = rebuild_export(Path(manifest["source_attempt"]))
    if rows != c.read(output / "EPISODES.json") or rebuilt != {k: v for k, v in manifest.items() if k != "artifact_sha256"}:
        raise ValueError("amended export differs from actual raw evidence")
    if (group is None) != (not (output / "GROUP.json").exists()) or group is not None and group != c.read(output / "GROUP.json"):
        raise ValueError("amended mixed group differs from exact admitted rows")
    return {"manifest_sha256": c.file_hash(output / "MANIFEST.json"),
        "group_sha256": c.file_hash(output / "GROUP.json") if group else None,
        "replayed": len(rows), "selected": len(group["episodes"]) if group else 0,
        "amendment_id": manifest["continuation_amendment_id"], "verifier_source_sha256": c.file_hash(Path(__file__))}


def binding_for(policy):
    amendment = a.verify_amendment()
    binding = BASE_BINDING(policy)
    binding["continuation_amendment"] = {"id": amendment["amendment_id"], "path": str(a.ROOT / "AMENDMENT.json"), "sha256": c.file_hash(a.ROOT / "AMENDMENT.json")}
    return binding


def prepare_spec(phase, binding, endpoint, destination, cap, generation=None):
    amendment = a.verify_amendment()
    spec = BASE_PREPARE(phase, binding, endpoint, destination.with_name("CAPTURE_SPEC_V2_BASE.json"), cap, generation)
    spec["source_file_sha256"].update(amendment["source_sha256"])
    spec["source_file_sha256"].update(amendment["input_sha256"])
    spec["source_file_sha256"][str(a.ROOT / "AMENDMENT.json")] = c.file_hash(a.ROOT / "AMENDMENT.json")
    spec["continuation_amendment_id"] = amendment["amendment_id"]
    c.write_once(destination, spec)
    return spec


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("command", choices=("collect", "export", "verify-export"))
    parser.add_argument("--spec", type=Path)
    parser.add_argument("--attempt", type=Path)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    if args.command == "collect":
        amendment = a.verify_amendment()
        spec = old.verify_spec(args.spec)
        if spec.get("continuation_amendment_id") != amendment["amendment_id"]:
            raise ValueError("collection is not bound to this continuation")
        result = asyncio.run(old.collect(args.spec, args.output))
    elif args.command == "export":
        result = export(args.attempt, args.output)
    else:
        result = authenticate_export(args.output)
    print(json.dumps(result, sort_keys=True, allow_nan=False))
