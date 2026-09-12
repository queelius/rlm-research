"""One-shot CPU-only raw audit of the paired long-transfer evaluation."""

from __future__ import annotations

import argparse
from collections import Counter
from difflib import SequenceMatcher
import hashlib
import json
import math
from pathlib import Path
import time


ROOT = Path(__file__).resolve().parent
STORE = ROOT.parents[1]
SIDE = STORE / "sidecars/openai-mrcr-long-transfer-eval-v1"
DATA = STORE / "sidecars/openai-mrcr-long-transfer-data-v1"
READY = SIDE / "READY_V2.json"
READY_SHA = "d896540268ec2ced54414415de07db2e30c0d7c756a741487cd2165194efbd62"
ATTEMPTS = {"base": SIDE / "outputs/base-002", "checkpoint32": SIDE / "outputs/checkpoint32-002"}
SOURCE_SHA256 = {}


def sha(path: Path) -> str:
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def digest(value) -> str:
    return hashlib.sha256(
        json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False).encode()
    ).hexdigest()


def read(path: Path):
    path = Path(path)
    SOURCE_SHA256[str(path)] = sha(path)
    return json.loads(path.read_text())


def write_x(path: Path, value) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("x") as stream:
        if isinstance(value, str):
            stream.write(value)
        else:
            json.dump(value, stream, indent=2, sort_keys=True, allow_nan=False)
            stream.write("\n")


def official_grade(response, answer, marker):
    if not isinstance(response, str) or not response.startswith(marker):
        return 0.0
    return float(SequenceMatcher(None, response.removeprefix(marker), answer.removeprefix(marker)).ratio())


def mechanism(observations, reply, answer, marker):
    target = answer.removeprefix(marker)
    acceptable = {answer, answer + "\n", target, target + "\n"}
    clean = any(value in acceptable for value in observations)
    exact = isinstance(reply, str) and reply == answer
    if clean and exact:
        category = "exact_after_clean_target"
    elif clean:
        category = "clean_target_copy_failure"
    elif exact:
        category = "exact_without_clean_target_observation"
    else:
        category = "no_clean_target_and_wrong_final"
    return {
        "category": category,
        "clean_target_observed": clean,
        "tool_observation_count": len(observations),
        "tool_observation_utf8_bytes": sum(len(value.encode()) for value in observations),
        "traceback_observations": sum("Traceback" in value for value in observations),
        "truncated_observations": sum(value.startswith("Warning: truncated output") for value in observations),
        "broad_observation": any(len(value.encode()) > max(4096, 2 * len(answer.encode())) for value in observations),
    }


def role_cost(returned, mapping):
    result = {role: {"calls": 0, "prompt_tokens": 0, "completion_tokens": 0} for role in ("root", "child")}
    for match in mapping.get("matches") or []:
        index = match.get("audit_index")
        role = match.get("role")
        if role not in result or not isinstance(index, int) or index >= len(returned):
            continue
        tokens = (returned[index].get("response") or {}).get("tokens") or {}
        result[role]["calls"] += 1
        result[role]["prompt_tokens"] += len(tokens.get("prompt_ids") or [])
        result[role]["completion_tokens"] += len(tokens.get("completion_ids") or [])
    return result


def verify_ready():
    if sha(READY) != READY_SHA:
        raise ValueError("authoritative long-transfer READY V2 changed")
    ready = read(READY)
    if ready["identity"] != digest({key: value for key, value in ready.items() if key != "identity"}):
        raise ValueError("READY identity changed")
    for raw, expected in ready["closure_sha256"].items():
        if sha(Path(raw)) != expected:
            raise ValueError("sealed input/source changed: " + raw)
    return ready


def expected_binding(arm, receipt):
    zero = receipt["zero_adapter"]
    base_alias = "Qwen3-4B-Instruct-2507-procedural-eval-zero"
    root_alias = base_alias if arm == "base" else "Qwen3-4B-Instruct-2507-mrcr-procedural-sft-step32"
    models = {base_alias: {"path": zero["path"], "adapter_sha256": zero["adapter_model_sha256"],
                           "config_sha256": zero["adapter_config_sha256"]}}
    if arm == "checkpoint32":
        train = receipt["training"]
        models[root_alias] = {"path": train["checkpoint"], "adapter_sha256": train["adapter_model_sha256"],
                              "config_sha256": train["adapter_config_sha256"]}
    return root_alias, models


def stage(arm, plan, rows_by_id, gold, prefixes, receipt):
    directory = ATTEMPTS[arm]
    terminal = read(directory / "OWNER_TERMINAL.json")
    result_path = directory / "science/RESULT.json"
    result = read(result_path) if result_path.exists() else None
    binding_path = directory / "owned-service/BINDING.json"
    binding = read(binding_path) if binding_path.exists() else None
    root_alias, models = expected_binding(arm, receipt)
    integrity = []
    if binding is not None:
        if binding.get("role_map") != {"root": root_alias, "children": ["Qwen3-4B-Instruct-2507-procedural-eval-zero"]}:
            integrity.append("role map differs")
        if binding.get("models") != models:
            integrity.append("model binding differs")
    contract_path = directory / "science/TERMINAL_STRIP_CONTRACT.json"
    contract = read(contract_path) if contract_path.exists() else None
    if contract is not None and contract.get("condition") != "terminal-strip-disabled":
        integrity.append("wrong terminal condition")
    native = [read(path) for path in sorted((directory / "science/native-calls").glob("*-result.json"))]
    starts = [read(path) for path in sorted((directory / "science/native-calls").glob("*-start.json"))]
    provider_ids = []
    records = {}
    for path in sorted((directory / "science/episodes").glob("*.json")):
        item = read(path)
        coordinate = item["coordinate"]
        ident = coordinate["id"]
        if ident not in plan or coordinate != plan[ident] or path.stem != ident:
            raise ValueError("episode is outside fixed schedule: " + str(path))
        if digest(item["episode"]) != item["episode_sha256"]:
            raise ValueError("episode bytes/digest differ: " + str(path))
        truth = gold[coordinate["record_id"]]
        traces = item["episode"].get("traces") or []
        trace = traces[0] if len(traces) == 1 else {}
        reply = trace.get("root_reply")
        derived = item.get("derived") or {}
        available = bool(derived.get("scientifically_available"))
        raw_exact = isinstance(reply, str) and reply == truth["answer"]
        score = official_grade(reply, truth["answer"], truth["random_string_to_prepend"])
        if available and (derived.get("raw_exact") != raw_exact or not math.isclose(derived.get("reward"), score, abs_tol=1e-12)):
            integrity.append(f"collector score differs:{ident}")
        session = sorted((row for row in native if row.get("session_id") == trace.get("id") and row.get("status") == "returned"), key=lambda row: row["index"])
        for row in session:
            response = row.get("response") or {}
            provider = response.get("id")
            if provider:
                provider_ids.append(provider)
            tokens = response.get("tokens") or {}
            if len(tokens.get("completion_ids") or []) != len(tokens.get("completion_logprobs") or []):
                integrity.append(f"native action/logprob length differs:{ident}:{row.get('index')}")
        mapping = derived.get("causal_mapping") or {}
        costs = role_cost(session, mapping)
        first_root = next((m for m in mapping.get("matches") or [] if m.get("role") == "root"), None)
        physical_prefix = None
        if first_root is not None and first_root["audit_index"] < len(session):
            physical_prefix = ((session[first_root["audit_index"]].get("response") or {}).get("tokens") or {}).get("prompt_ids")
        prefix_exact = physical_prefix == prefixes[ident]["token_ids"] if physical_prefix is not None else None
        if prefix_exact is False:
            integrity.append(f"physical initial prefix differs:{ident}")
        observations = [(node.get("message") or {}).get("content", "") for node in trace.get("nodes") or []
                        if (node.get("message") or {}).get("role") == "tool" and isinstance((node.get("message") or {}).get("content"), str)]
        programs = [call.get("arguments") for node in trace.get("nodes") or [] for call in ((node.get("message") or {}).get("tool_calls") or []) if call.get("name") == "ipython"]
        records[ident] = {
            "coordinate": coordinate, "available": available, "raw_exact": raw_exact,
            "official_score": score if available else None, "terminal_status": derived.get("terminal_status"),
            "failure_class": derived.get("failure_class"), "initial_prefix_exact": prefix_exact,
            "neural_initial_prefix_tokens": len(prefixes[ident]["token_ids"]), "cost": costs,
            "mechanism": mechanism(observations, reply, truth["answer"], truth["random_string_to_prepend"]),
            "root_reply_sha256": hashlib.sha256(reply.encode()).hexdigest() if isinstance(reply, str) else None,
            "answer_sha256": hashlib.sha256(truth["answer"].encode()).hexdigest(),
            "first_program_sha256": hashlib.sha256(str(programs[0]).encode()).hexdigest() if programs else None,
            "episode_path": str(path), "episode_file_sha256": SOURCE_SHA256[str(path)],
            "native_returned": len(session),
        }
    if len(provider_ids) != len(set(provider_ids)):
        integrity.append("duplicate native provider response ID")
    returned = [row for row in native if row.get("status") == "returned"]
    physical = {"started": len(starts), "result_records": len(native), "returned": len(returned),
                "errors": len(native) - len(returned), "start_only": len(starts) - len(native),
                "prompt_tokens": sum(len(((row.get("response") or {}).get("tokens") or {}).get("prompt_ids") or []) for row in returned),
                "completion_tokens": sum(len(((row.get("response") or {}).get("tokens") or {}).get("completion_ids") or []) for row in returned)}
    for role in ("root", "child"):
        physical[role] = {field: sum(row["cost"][role][field] for row in records.values())
                          for field in ("calls", "prompt_tokens", "completion_tokens")}
    return {"arm": arm, "terminal": terminal, "collector_result": result, "binding": binding,
            "terminal_contract": contract, "records": records, "integrity_errors": integrity,
            "summary": {"planned": 16, "recorded": len(records),
                        "available": sum(row["available"] for row in records.values()),
                        "raw_exact": sum(row["available"] and row["raw_exact"] for row in records.values()),
                        "mechanisms": dict(Counter(row["mechanism"]["category"] for row in records.values()))},
            "physical": physical}


def pair_rows(left, right):
    pairs = []
    for ident in sorted(set(left) | set(right)):
        a, b = left.get(ident), right.get(ident)
        if a and b and a["coordinate"] != b["coordinate"]:
            raise ValueError("paired coordinate differs: " + ident)
        both = bool(a and b and a["available"] and b["available"])
        pairs.append({"coordinate_id": ident, "record_id": (a or b)["coordinate"]["record_id"],
                      "paired_available": both, "base_exact": a["raw_exact"] if both else None,
                      "checkpoint32_exact": b["raw_exact"] if both else None,
                      "base_mechanism": (a.get("mechanism") or {}).get("category") if a else None,
                      "checkpoint32_mechanism": (b.get("mechanism") or {}).get("category") if b else None})
    return {"matched_coordinates": len(pairs), "paired_available": sum(row["paired_available"] for row in pairs),
            "checkpoint32_wins": sum(row["checkpoint32_exact"] is True and row["base_exact"] is False for row in pairs),
            "checkpoint32_losses": sum(row["base_exact"] is True and row["checkpoint32_exact"] is False for row in pairs),
            "unknown_pairs": sum(not row["paired_available"] for row in pairs), "pairs": pairs}


def build():
    SOURCE_SHA256.clear()
    ready = verify_ready()
    if not all((path / "OWNER_TERMINAL.json").exists() for path in ATTEMPTS.values()):
        return {"status": "PENDING_BOTH_OWNER_TERMINALS", "polling": False}
    public = read(SIDE / "inputs/PUBLIC.json")
    plan = {row["id"]: row for row in public["plan"]}
    gold = read(SIDE / "inputs/HOST_GOLD.json")
    prefixes = read(SIDE / "inputs/PREFIXES.json")
    inputs = read(DATA / "MODEL_INPUTS.json")["records"]
    receipt = read(SIDE.parent / "openai-mrcr-procedural-sft-continue32-eval-v1/checkpoint-artifacts/CHECKPOINT_READY.json")
    stages = {arm: stage(arm, plan, inputs, gold, prefixes, receipt) for arm in ATTEMPTS}
    pairing = pair_rows(stages["base"]["records"], stages["checkpoint32"]["records"])
    manifest = read(DATA / "MANIFEST.json")
    ranking = read(DATA / "RANKING.json")
    context_sizes = [{"record_id": row["id"], "source_ordinal": row["source_ordinal"],
                      "context_utf8_bytes": Path(row["prompt_json_path"]).stat().st_size,
                      "context_o200k_tokens": row["prompt_content_o200k_tokens"],
                      "prompt_plus_answer_o200k_tokens": row["prompt_plus_answer_o200k_tokens"],
                      "neural_initial_prefix_tokens": len(prefixes[next(c["id"] for c in plan.values() if c["record_id"] == row["id"])]["token_ids"])}
                     for row in inputs]
    errors = [item for value in stages.values() for item in value["integrity_errors"]]
    return {"schema": "openai-mrcr-long-transfer-independent-analysis-v1",
            "status": "COMPLETE_RAW_AUDIT" if not errors else "HOLD_INTEGRITY_ERRORS",
            "created_epoch": time.time(), "ready_identity": ready["identity"], "ready_sha256": READY_SHA,
            "context_units": 16, "episodes_per_arm": 16, "stages": stages, "pairing": pairing,
            "context_sizes": context_sizes,
            "source_qualification": {"data_ready_sha256": sha(DATA / "DATA_READY.json"),
                "source_revision": manifest["source_revision"], "source_rows": manifest["source_rows"],
                "previously_queried_short_rows_excluded": manifest["previously_queried_short_rows_excluded"],
                "pairwise_exact_core_pair_overlap": manifest["pairwise_exact_core_pair_overlap"],
                "pairwise_target_answer_to_other_core_overlap_both_directions": manifest["pairwise_target_answer_to_other_core_overlap_both_directions"],
                "selection_uses_model_answers": ranking["selection_uses_model_answers"],
                "selection_uses_previous_outcomes": ranking["selection_uses_previous_outcomes"],
                "unknown_base_pretraining_exposure": manifest["unknown_base_pretraining_exposure"],
                "claim_boundary": manifest["claim_boundary"]},
            "integrity_errors": errors, "source_sha256": dict(SOURCE_SHA256),
            "generated_programs_executed": False, "GPU_calls": 0,
            "limits": ["One sample per context; 16 context units, not 32 IID observations.",
                       "External-file size is not neural prompt length or a neural-context-extension test.",
                       "Clean-target observation is exact stdout evidence; absence does not prove retrieval did not occur internally.",
                       "A fixed zero-LoRA child is available in both arms; actual child calls and cost are reported, not assumed zero.",
                       "Same-task length transfer does not establish broad generalization or exclude pretraining exposure."]}


def markdown(report):
    if report["status"].startswith("PENDING"):
        return "# Long-transfer independent audit\n\nBoth owner terminals are not yet present; no partial results were scored.\n"
    base, cp = report["stages"]["base"], report["stages"]["checkpoint32"]
    p = report["pairing"]
    return f"""---
schema: openai-mrcr-long-transfer-independent-report-v1
status: {report['status']}
---

# Procedural-SFT long-input transfer

Base returned {base['summary']['raw_exact']}/{base['summary']['available']}/16 raw-exact; checkpoint32 returned {cp['summary']['raw_exact']}/{cp['summary']['available']}/16. Across {p['paired_available']} jointly available coordinates, checkpoint32 had {p['checkpoint32_wins']} wins and {p['checkpoint32_losses']} losses; {p['unknown_pairs']} pairs remain unknown.

This is a fixed one-shot comparison over 16 context units. The source selection excluded 48 prior short rows and has zero exact core-pair or bidirectional target-to-other-core overlap within the selected cohort. Base pretraining exposure remains unknown.

## Physical evidence

| Arm | Native returned/errors | Root calls (prompt/completion tokens) | Child calls (prompt/completion tokens) |
| --- | ---: | ---: | ---: |
| base | {base['physical']['returned']}/{base['physical']['errors']} | {base['physical']['root']['calls']} ({base['physical']['root']['prompt_tokens']}/{base['physical']['root']['completion_tokens']}) | {base['physical']['child']['calls']} ({base['physical']['child']['prompt_tokens']}/{base['physical']['child']['completion_tokens']}) |
| checkpoint32 | {cp['physical']['returned']}/{cp['physical']['errors']} | {cp['physical']['root']['calls']} ({cp['physical']['root']['prompt_tokens']}/{cp['physical']['root']['completion_tokens']}) | {cp['physical']['child']['calls']} ({cp['physical']['child']['prompt_tokens']}/{cp['physical']['child']['completion_tokens']}) |

Mechanism categories distinguish exact clean target observations, clean-target copy failures, exact answers without an exact target stdout, and wrong finals without exact target stdout. They are trace descriptions, not causal proof of internal retrieval. Generated programs were never executed by this analyzer.
"""


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("command", choices=("verify", "check"))
    parser.add_argument("--output-dir", type=Path, default=ROOT / "outcome")
    args = parser.parse_args()
    if args.command == "verify":
        value = verify_ready()
        print(json.dumps({"identity": value["identity"], "ready_sha256": READY_SHA}, sort_keys=True))
    else:
        value = build()
        if value["status"].startswith("PENDING"):
            print(json.dumps(value, sort_keys=True))
            raise SystemExit(2)
        write_x(args.output_dir / "RESULTS.json", value)
        write_x(args.output_dir / "REPORT.md", markdown(value))
        print(json.dumps({key: value[key] for key in ("status", "context_units", "pairing")}, sort_keys=True))
