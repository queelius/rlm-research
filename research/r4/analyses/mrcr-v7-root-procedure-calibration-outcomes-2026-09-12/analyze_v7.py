"""Independent V7 audit with returned-native and interceptor-failure accounting."""

from __future__ import annotations

import importlib.util
import json
from pathlib import Path
import sys
import time


ROOT = Path(__file__).resolve().parent
RUN = ROOT.parent.parent / "sidecars/mrcr-v3-root-procedure-calibration-v1"
ATTEMPT = RUN / "outputs/attempt-007"
READY = RUN / "READY_V7.json"
READY_SHA256 = "c79fa15c6463a89513b1c0aba65e7906efb708c97ab10d619ed925025af476b4"
V6_ANALYZER = ROOT.parent / "mrcr-v6-root-procedure-calibration-outcomes-2026-09-12/analyze_v6.py"
TWO_TURN_PROOF = ROOT.parent / "mrcr-v7-two-turn-wrapper-proof-2026-09-12/PROOF.json"


def _load():
    spec = importlib.util.spec_from_file_location("mrcr_v7_reused_v6_analyzer", V6_ANALYZER)
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


v6 = _load()
read, sha, digest, write_x = v6.read, v6.sha, v6.digest, v6.write_x


def verify_source():
    ready = v6.v5.core.base._verify_ready_file(READY, READY_SHA256)
    if ready.get("status") != "CPU_READY_FOR_MAIN_GPU_LAUNCH":
        raise ValueError("V7 READY status changed")
    expected = [
        "/project/alex_phd/envs/prime-rl-5990b1b/bin/python",
        str(RUN / "owner_v7.py"),
        "run",
        "--output",
        str(ATTEMPT),
        "--outer-seconds",
        "900",
    ]
    if ready.get("fixed_argv") != expected or ready.get("optimizer_steps") != 0:
        raise ValueError("V7 execution contract changed")
    if ready.get("planned_episodes") != 32:
        raise ValueError("V7 inventory changed")
    proof = read(TWO_TURN_PROOF)
    if not (
        proof.get("schema") == "mrcr-v7-two-turn-real-train-client-wrapper-proof-v1"
        and proof.get("passed") is True
        and proof.get("ready_v7_sha256") == READY_SHA256
        and proof.get("provider_requests") == proof.get("audit_results") == 2
        and proof.get("audit_statuses") == ["returned", "returned"]
        and proof.get("first_pending_turn_prefix_nodes") == 0
        and proof.get("second_pending_turn_prefix_nodes", 0) > 0
        and proof.get("second_pending_turn_path_len", 0) > 0
        and proof.get("second_prompt_has_tool_role") is True
        and proof.get("successful_context_read") is True
        and proof.get("real_train_client_and_renderer") is True
        and proof.get("weighted_model_calls") == proof.get("gpu_calls") == 0
    ):
        raise ValueError("V7 additive two-turn proof changed or failed")
    return {
        "ready_identity": ready["identity"],
        "planned_episodes": 32,
        "owner_cap_seconds": 900,
        "optimizer_steps": 0,
        "adapter": None,
        "one_underlying_context": True,
        "two_turn_proof": {
            "path": str(TWO_TURN_PROOF),
            "sha256": sha(TWO_TURN_PROOF),
            "provider_requests": 2,
            "second_pending_turn_prefix_nodes": proof["second_pending_turn_prefix_nodes"],
            "second_pending_turn_path_len": proof["second_pending_turn_path_len"],
        },
    }


def boundary_inventory(native_dir, episode_rows):
    starts = {path.name.removesuffix("-start.json"): path for path in native_dir.glob("*-start.json")}
    results = {
        path.name.removesuffix("-result.json"): read(path)
        for path in native_dir.glob("*-result.json")
    }
    returned = [row for row in results.values() if row.get("status") == "returned"]
    errors = [row for row in results.values() if row.get("status") == "error"]
    calls = [
        call
        for episode in episode_rows
        for trace in (episode.get("episode", {}).get("traces") or [])
        for call in (trace.get("calls") or [])
    ]
    pre_inference = [
        call
        for call in calls
        if call.get("node") is None and call.get("usage") is None and call.get("error")
    ]
    committed = [call for call in calls if call.get("node") is not None]
    return {
        "audit_start_records": len(starts),
        "audit_result_records": len(results),
        "audit_returned_native_responses": len(returned),
        "audit_error_results": len(errors),
        "orphan_start_without_result": len(set(starts) - set(results)),
        "trace_call_entries": len(calls),
        "trace_committed_native_responses": len(committed),
        "trace_pre_inference_failures": len(pre_inference),
        "unknown_trace_call_entries": len(calls) - len(committed) - len(pre_inference),
        "returned_action_tokens": sum(
            row.get("evidence", {}).get("action_tokens", 0) for row in returned
        ),
        "returned_prompt_tokens": sum(
            row.get("evidence", {}).get("prompt_tokens", 0) for row in returned
        ),
        "error_types": sorted(
            {
                (row.get("error") or {}).get("type")
                for row in errors
                if (row.get("error") or {}).get("type")
            }
        ),
    }


def analyze():
    source = verify_source()
    v6.ATTEMPT = ATTEMPT
    v6.READY = READY
    v6.READY_SHA256 = READY_SHA256
    v6.PARENT_READY = RUN / "READY_V6.json"
    v6.PARENT_SHA256 = sha(v6.PARENT_READY)
    v6.verify_source = verify_source
    report = v6.analyze()
    episodes = [read(path) for path in sorted((ATTEMPT / "science/episodes").glob("*.json"))]
    boundary = boundary_inventory(ATTEMPT / "science/native-calls", episodes)
    report["schema"] = "independent-mrcr-v7-root-procedure-calibration-audit-v1"
    report["source"]["attempt"] = str(ATTEMPT)
    report["source"]["ready_v7_sha256"] = READY_SHA256
    report["source"]["ready_v7_identity"] = read(READY)["identity"]
    report["source"]["transitive_source_verification"] = source
    report["native_boundary_accounting"] = boundary
    report["cost"]["model_calls_is_trace_entry_count_not_physical"] = True
    report["cost"]["confirmed_returned_native_responses"] = boundary[
        "audit_returned_native_responses"
    ]
    report["cost"]["pre_inference_failures"] = boundary["trace_pre_inference_failures"]
    report["created_epoch"] = time.time()
    write_x(ROOT / "REPORT.json", report)
    outcome = report["outcome"]
    supplement = report["supplementary_runtime_evidence"]
    gate = outcome["future_root_rl_gate"]["eligible"]
    (ROOT / "REPORT.md").write_text(
        "# Independent MRCR V7 calibration audit\n\n"
        f"Frozen gate eligible: **{gate}**. Decision: `{report['decision']}`. "
        "This is one-context calibration, not transfer.\n\n"
        f"- Planned/recorded/available: {outcome['planned']}/{outcome['recorded']}/"
        f"{outcome['available_scores']}\n"
        f"- Mixed groups / mean score: {outcome['mixed_groups']} / "
        f"{outcome['mean_official_score_available']}\n"
        f"- Successful/failed context reads: {supplement['successful_context_reads']}/"
        f"{supplement['failed_context_reads']}\n"
        f"- Confirmed returned native responses: {boundary['audit_returned_native_responses']}\n"
        f"- Pre-inference interceptor failures: {boundary['trace_pre_inference_failures']}\n"
        f"- Orphan audit starts: {boundary['orphan_start_without_result']}\n"
        f"- Clean release: {report['runtime_release']['clean']}\n\n"
        "Trace call entries are not reported as physical calls: only paired audit records with "
        "`status=returned` count as confirmed responses. Infrastructure failures remain unavailable, "
        "never reward zero. This audit authorizes no optimizer update by itself.\n"
    )
    return report


if __name__ == "__main__":
    value = analyze()
    print(json.dumps({"decision": value["decision"]}, sort_keys=True))
