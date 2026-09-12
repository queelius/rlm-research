"""One-shot CPU-only raw audit of the paired four-needle ordinal-transfer evaluation.

Generated model programs are parsed or inspected as inert text and are never executed.
"""

from __future__ import annotations

import argparse
import ast
from collections import Counter
from difflib import SequenceMatcher
import hashlib
import json
import math
from pathlib import Path
import re
import time


ROOT = Path(__file__).resolve().parent
STORE = ROOT.parents[1]
SIDE = STORE / "sidecars/openai-mrcr-fourneedle-ordinal-transfer-eval-v1"
DATA = STORE / "sidecars/openai-mrcr-fourneedle-ordinal-transfer-data-v1"
READY = SIDE / "READY.json"
READY_SHA = "02e90c8e7c30a3fc6070a94d03b93b43a14fac3db675d297b84d4b4b8a56324c"
ATTEMPTS = {"base": SIDE / "outputs/base-001", "checkpoint32": SIDE / "outputs/checkpoint32-001"}
SOURCE_SHA256: dict[str, str] = {}


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
    return float(
        SequenceMatcher(None, response.removeprefix(marker), answer.removeprefix(marker)).ratio()
    )


def _literal_request(program: str) -> str | None:
    try:
        tree = ast.parse(program)
    except SyntaxError:
        return None
    for node in ast.walk(tree):
        if not isinstance(node, (ast.Assign, ast.AnnAssign)):
            continue
        targets = node.targets if isinstance(node, ast.Assign) else [node.target]
        value = node.value
        if not isinstance(value, ast.Constant) or not isinstance(value.value, str):
            continue
        if any(isinstance(target, ast.Name) and target.id in {"request", "request_text", "query"}
               for target in targets):
            return value.value
    return None


def _mentions_ordinal(program: str, target_occurrence: int) -> bool:
    word = {3: "third", 4: "fourth"}[target_occurrence]
    patterns = (
        rf"\b{word}\b",
        rf"\b(?:occurrence|ordinal|nth|n)\s*=\s*{target_occurrence}\b",
        rf"\b(?:index|idx)\s*=\s*{target_occurrence - 1}\b",
        rf"\[\s*{target_occurrence - 1}\s*\]",
    )
    return any(re.search(pattern, program, flags=re.IGNORECASE) for pattern in patterns)


def mechanism(observations, reply, answer, marker, first_program, target_occurrence):
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
    literal = _literal_request(first_program)
    return {
        "category": category,
        "clean_target_observed": clean,
        "tool_observation_count": len(observations),
        "tool_observation_utf8_bytes": sum(len(value.encode()) for value in observations),
        "traceback_observations": sum("Traceback" in value for value in observations),
        "truncated_observations": sum(value.startswith("Warning: truncated output") for value in observations),
        "broad_observation": any(len(value.encode()) > max(4096, 2 * len(answer.encode())) for value in observations),
        "first_program_ast_parseable": bool(first_program) and _ast_parseable(first_program),
        "literal_request_present": literal is not None,
        "literal_request_sha256": hashlib.sha256(literal.encode()).hexdigest() if literal else None,
        "program_mentions_requested_ordinal": _mentions_ordinal(first_program, target_occurrence),
        "ordinal_unavailable_observation": any(
            "requested ordinal is unavailable" in value.casefold() for value in observations
        ),
    }


def _ast_parseable(program: str) -> bool:
    try:
        ast.parse(program)
        return True
    except SyntaxError:
        return False


def role_cost(returned, mapping):
    result = {
        role: {"calls": 0, "prompt_tokens": 0, "completion_tokens": 0}
        for role in ("root", "child")
    }
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
        raise ValueError("authoritative four-needle READY changed")
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
    root_alias = (
        base_alias if arm == "base" else "Qwen3-4B-Instruct-2507-mrcr-procedural-sft-step32"
    )
    models = {
        base_alias: {
            "path": zero["path"],
            "adapter_sha256": zero["adapter_model_sha256"],
            "config_sha256": zero["adapter_config_sha256"],
        }
    }
    if arm == "checkpoint32":
        train = receipt["training"]
        models[root_alias] = {
            "path": train["checkpoint"],
            "adapter_sha256": train["adapter_model_sha256"],
            "config_sha256": train["adapter_config_sha256"],
        }
    return root_alias, models


def _first_program(trace):
    for node in trace.get("nodes") or []:
        for call in (node.get("message") or {}).get("tool_calls") or []:
            if call.get("name") != "ipython":
                continue
            arguments = call.get("arguments", "")
            try:
                parsed = json.loads(arguments)
            except (json.JSONDecodeError, TypeError):
                return ""
            return parsed.get("code", "") if isinstance(parsed, dict) else ""
    return ""


def stage(arm, plan, rows_by_id, gold, prefixes, receipt):
    directory = ATTEMPTS[arm]
    terminal = read(directory / "OWNER_TERMINAL.json")
    result_path = directory / "science/RESULT.json"
    result = read(result_path) if result_path.exists() else None
    binding_path = directory / "owned-service/BINDING.json"
    binding = read(binding_path) if binding_path.exists() else None
    root_alias, models = expected_binding(arm, receipt)
    integrity: list[str] = []
    if binding is None:
        integrity.append("missing owned-service binding")
    else:
        expected_roles = {
            "root": root_alias,
            "children": ["Qwen3-4B-Instruct-2507-procedural-eval-zero"],
        }
        if binding.get("role_map") != expected_roles:
            integrity.append("role map differs")
        if binding.get("models") != models:
            integrity.append("model binding differs")
    contract_path = directory / "science/TERMINAL_STRIP_CONTRACT.json"
    contract = read(contract_path) if contract_path.exists() else None
    if contract is None or contract.get("condition") != "terminal-strip-disabled":
        integrity.append("missing or wrong terminal condition")

    native = [read(path) for path in sorted((directory / "science/native-calls").glob("*-result.json"))]
    starts = [read(path) for path in sorted((directory / "science/native-calls").glob("*-start.json"))]
    provider_ids: list[str] = []
    records = {}
    for path in sorted((directory / "science/episodes").glob("*.json")):
        item = read(path)
        coordinate = item["coordinate"]
        ident = coordinate["id"]
        if ident not in plan or coordinate != plan[ident] or path.stem != ident:
            raise ValueError("episode is outside fixed schedule: " + str(path))
        if digest(item["episode"]) != item["episode_sha256"]:
            raise ValueError("episode bytes/digest differ: " + str(path))
        source_row = rows_by_id[coordinate["record_id"]]
        target_occurrence = source_row["target_occurrence_one_indexed"]
        truth = gold[coordinate["record_id"]]
        traces = item["episode"].get("traces") or []
        trace = traces[0] if len(traces) == 1 else {}
        reply = trace.get("root_reply")
        derived = item.get("derived") or {}
        available = bool(derived.get("scientifically_available"))
        raw_exact = isinstance(reply, str) and reply == truth["answer"]
        score = official_grade(reply, truth["answer"], truth["random_string_to_prepend"])
        if available and (
            derived.get("raw_exact") != raw_exact
            or not math.isclose(derived.get("reward"), score, abs_tol=1e-12)
        ):
            integrity.append(f"collector score differs:{ident}")
        session = sorted(
            (
                row
                for row in native
                if row.get("session_id") == trace.get("id") and row.get("status") == "returned"
            ),
            key=lambda row: row["index"],
        )
        for row in session:
            response = row.get("response") or {}
            provider = response.get("id")
            if provider:
                provider_ids.append(provider)
            tokens = response.get("tokens") or {}
            if len(tokens.get("completion_ids") or []) != len(
                tokens.get("completion_logprobs") or []
            ):
                integrity.append(f"native action/logprob length differs:{ident}:{row.get('index')}")
        mapping = derived.get("causal_mapping") or {}
        costs = role_cost(session, mapping)
        first_root = next(
            (match for match in mapping.get("matches") or [] if match.get("role") == "root"), None
        )
        physical_prefix = None
        if first_root is not None and first_root["audit_index"] < len(session):
            physical_prefix = (
                (session[first_root["audit_index"]].get("response") or {}).get("tokens") or {}
            ).get("prompt_ids")
        prefix_exact = (
            physical_prefix == prefixes[ident]["token_ids"] if physical_prefix is not None else None
        )
        if prefix_exact is False:
            integrity.append(f"physical initial prefix differs:{ident}")
        observations = [
            (node.get("message") or {}).get("content", "")
            for node in trace.get("nodes") or []
            if (node.get("message") or {}).get("role") == "tool"
            and isinstance((node.get("message") or {}).get("content"), str)
        ]
        first_program = _first_program(trace)
        details = mechanism(
            observations,
            reply,
            truth["answer"],
            truth["random_string_to_prepend"],
            first_program,
            target_occurrence,
        )
        # Match any literal request variable against public user-message content without persisting text.
        literal = _literal_request(first_program)
        public_context = json.loads(Path(source_row["prompt_json_path"]).read_text())
        details["literal_request_exact_context_matches"] = sum(
            entry.get("role") == "user"
            and isinstance(entry.get("content"), str)
            and entry["content"].strip().casefold() == literal.strip().casefold()
            for entry in public_context[:-1]
        ) if literal is not None else 0
        records[ident] = {
            "coordinate": coordinate,
            "target_occurrence": target_occurrence,
            "source_ordinal": source_row["source_ordinal"],
            "available": available,
            "raw_exact": raw_exact,
            "official_marker_gated_sequence_matcher_similarity": score if available else None,
            "terminal_status": derived.get("terminal_status"),
            "failure_class": derived.get("failure_class"),
            "initial_prefix_exact": prefix_exact,
            "neural_initial_prefix_tokens": len(prefixes[ident]["token_ids"]),
            "source_prompt_json_bytes": source_row["prompt_json_bytes"],
            "source_prompt_plus_answer_o200k_tokens": source_row["o200k_prompt_plus_answer"],
            "cost": costs,
            "mechanism": details,
            "root_reply_sha256": hashlib.sha256(reply.encode()).hexdigest()
            if isinstance(reply, str)
            else None,
            "answer_sha256": hashlib.sha256(truth["answer"].encode()).hexdigest(),
            "first_program_sha256": hashlib.sha256(first_program.encode()).hexdigest()
            if first_program
            else None,
            "episode_path": str(path),
            "episode_file_sha256": SOURCE_SHA256[str(path)],
            "native_returned": len(session),
        }
    if len(provider_ids) != len(set(provider_ids)):
        integrity.append("duplicate native provider response ID")
    returned = [row for row in native if row.get("status") == "returned"]
    physical = {
        "started": len(starts),
        "result_records": len(native),
        "returned": len(returned),
        "errors": len(native) - len(returned),
        "start_only": len(starts) - len(native),
        "prompt_tokens": sum(
            len(((row.get("response") or {}).get("tokens") or {}).get("prompt_ids") or [])
            for row in returned
        ),
        "completion_tokens": sum(
            len(((row.get("response") or {}).get("tokens") or {}).get("completion_ids") or [])
            for row in returned
        ),
    }
    for role in ("root", "child"):
        physical[role] = {
            field: sum(row["cost"][role][field] for row in records.values())
            for field in ("calls", "prompt_tokens", "completion_tokens")
        }
    by_ordinal = {}
    for ordinal in (3, 4):
        subset = [row for row in records.values() if row["target_occurrence"] == ordinal]
        by_ordinal[str(ordinal)] = {
            "planned": 8,
            "recorded": len(subset),
            "available": sum(row["available"] for row in subset),
            "raw_exact": sum(row["available"] and row["raw_exact"] for row in subset),
            "mechanisms": dict(Counter(row["mechanism"]["category"] for row in subset)),
        }
    return {
        "arm": arm,
        "terminal": terminal,
        "collector_result": result,
        "binding": binding,
        "terminal_contract": contract,
        "records": records,
        "integrity_errors": integrity,
        "summary": {
            "planned": 16,
            "recorded": len(records),
            "available": sum(row["available"] for row in records.values()),
            "raw_exact": sum(row["available"] and row["raw_exact"] for row in records.values()),
            "mechanisms": dict(Counter(row["mechanism"]["category"] for row in records.values())),
            "by_target_occurrence": by_ordinal,
        },
        "physical": physical,
    }


def pair_rows(left, right):
    pairs = []
    for ident in sorted(set(left) | set(right)):
        base, checkpoint = left.get(ident), right.get(ident)
        if base and checkpoint and base["coordinate"] != checkpoint["coordinate"]:
            raise ValueError("paired coordinate differs: " + ident)
        source = base or checkpoint
        both = bool(base and checkpoint and base["available"] and checkpoint["available"])
        pairs.append(
            {
                "coordinate_id": ident,
                "record_id": source["coordinate"]["record_id"],
                "target_occurrence": source["target_occurrence"],
                "paired_available": both,
                "base_exact": base["raw_exact"] if both else None,
                "checkpoint32_exact": checkpoint["raw_exact"] if both else None,
                "base_mechanism": (base.get("mechanism") or {}).get("category") if base else None,
                "checkpoint32_mechanism": (checkpoint.get("mechanism") or {}).get("category")
                if checkpoint
                else None,
            }
        )

    def summary(values):
        return {
            "coordinates": len(values),
            "paired_available": sum(row["paired_available"] for row in values),
            "wins": sum(
                row["checkpoint32_exact"] is True and row["base_exact"] is False for row in values
            ),
            "losses": sum(
                row["base_exact"] is True and row["checkpoint32_exact"] is False for row in values
            ),
            "unknown_pairs": sum(not row["paired_available"] for row in values),
        }

    overall = summary(pairs)
    return {
        "matched_coordinates": len(pairs),
        "paired_available": overall["paired_available"],
        "checkpoint32_wins": overall["wins"],
        "checkpoint32_losses": overall["losses"],
        "unknown_pairs": overall["unknown_pairs"],
        "by_target_occurrence": {
            str(ordinal): summary([row for row in pairs if row["target_occurrence"] == ordinal])
            for ordinal in (3, 4)
        },
        "pairs": pairs,
    }


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
    rows_by_id = {row["id"]: row for row in inputs}
    receipt = read(Path(ready["checkpoint"]["receipt"]))
    stages = {
        arm: stage(arm, plan, rows_by_id, gold, prefixes, receipt) for arm in ATTEMPTS
    }
    pairing = pair_rows(stages["base"]["records"], stages["checkpoint32"]["records"])
    manifest = read(DATA / "MANIFEST.json")
    selection = read(DATA / "SELECTION.json")
    errors = [item for value in stages.values() for item in value["integrity_errors"]]
    return {
        "schema": "openai-mrcr-fourneedle-ordinal-transfer-independent-analysis-v1",
        "status": "COMPLETE_RAW_AUDIT" if not errors else "HOLD_INTEGRITY_ERRORS",
        "created_epoch": time.time(),
        "ready_identity": ready["identity"],
        "ready_sha256": READY_SHA,
        "context_units": 16,
        "episodes_per_arm": 16,
        "stages": stages,
        "pairing": pairing,
        "source_qualification": {
            "data_ready_sha256": sha(DATA / "DATA_READY.json"),
            "dataset": manifest["dataset"],
            "source_revision": manifest["revision"],
            "records": manifest["records"],
            "third_occurrence": manifest["third_occurrence"],
            "fourth_occurrence": manifest["fourth_occurrence"],
            "excluded_prior_rows": manifest["excluded_prior_rows"],
            "pairwise_and_exposure_conflicts": manifest["pairwise_and_exposure_conflicts"],
            "selection_uses_model_answers": selection["selection_uses_model_answers"],
            "selection_uses_previous_outcomes": selection["selection_uses_previous_outcomes"],
            "eligible_counts": selection["eligible_counts"],
            "unknown_base_pretraining_exposure": manifest["unknown_base_pretraining_exposure"],
            "claim_boundary": manifest["claim_boundary"],
        },
        "integrity_errors": errors,
        "source_sha256": dict(SOURCE_SHA256),
        "generated_programs_executed": False,
        "GPU_calls": 0,
        "limits": [
            "Sixteen paired context units are grouped by requested third versus fourth occurrence; 32 arm outputs are not 32 independent contexts.",
            "The official secondary score is marker-gated SequenceMatcher similarity, not rfind or normalized exact.",
            "Literal-request and ordinal-selection fields are inert static program indicators, not proof that the program selected the right object.",
            "Clean-target observation is exact stdout evidence; its absence does not prove retrieval did not occur internally.",
            "A fixed zero-LoRA child is available in both arms; actual child calls and cost are measured rather than assumed zero.",
            "This is same-task ordinal transfer with common framing and unknown base pretraining exposure, not a new benchmark or learned-routing test.",
        ],
    }


def markdown(report):
    if report["status"].startswith("PENDING"):
        return "# Four-needle ordinal-transfer independent audit\n\nBoth owner terminals are not yet present; no partial results were scored.\n"
    base = report["stages"]["base"]
    checkpoint = report["stages"]["checkpoint32"]
    pairing = report["pairing"]
    rows = []
    for ordinal in (3, 4):
        base_o = base["summary"]["by_target_occurrence"][str(ordinal)]
        cp_o = checkpoint["summary"]["by_target_occurrence"][str(ordinal)]
        pair_o = pairing["by_target_occurrence"][str(ordinal)]
        rows.append(
            f"| {ordinal} | {base_o['raw_exact']}/{base_o['available']} | "
            f"{cp_o['raw_exact']}/{cp_o['available']} | {pair_o['wins']}/{pair_o['losses']} | "
            f"{pair_o['unknown_pairs']} |"
        )
    return f"""---
schema: openai-mrcr-fourneedle-ordinal-transfer-independent-report-v1
status: {report['status']}
---

# Four-needle ordinal-transfer readout

Base returned {base['summary']['raw_exact']}/{base['summary']['available']}/16 raw-exact;
checkpoint 32 returned {checkpoint['summary']['raw_exact']}/{checkpoint['summary']['available']}/16.
Across {pairing['paired_available']} jointly available context units, checkpoint 32 had
{pairing['checkpoint32_wins']} wins and {pairing['checkpoint32_losses']} losses; 
{pairing['unknown_pairs']} pairs remain unknown.

| Requested occurrence | Base exact/available | Checkpoint 32 exact/available | cp32 wins/losses | Unknown pairs |
| ---: | ---: | ---: | ---: | ---: |
{chr(10).join(rows)}

## Physical evidence

| Arm | Native returned/errors | Root calls (prompt/completion tokens) | Child calls (prompt/completion tokens) |
| --- | ---: | ---: | ---: |
| base | {base['physical']['returned']}/{base['physical']['errors']} | {base['physical']['root']['calls']} ({base['physical']['root']['prompt_tokens']}/{base['physical']['root']['completion_tokens']}) | {base['physical']['child']['calls']} ({base['physical']['child']['prompt_tokens']}/{base['physical']['child']['completion_tokens']}) |
| checkpoint32 | {checkpoint['physical']['returned']}/{checkpoint['physical']['errors']} | {checkpoint['physical']['root']['calls']} ({checkpoint['physical']['root']['prompt_tokens']}/{checkpoint['physical']['root']['completion_tokens']}) | {checkpoint['physical']['child']['calls']} ({checkpoint['physical']['child']['prompt_tokens']}/{checkpoint['physical']['child']['completion_tokens']}) |

Mechanism fields separately record exact clean-target stdout, terminal copy success/failure,
first-program literal-request matching, and a conservative ordinal-mention heuristic. They are
descriptive trace evidence, not proof of internal retrieval or correct ordinal selection. Generated
programs were parsed as inert text and never executed. The secondary metric is the official
marker-gated SequenceMatcher similarity. This is same-task ordinal transfer, not a new benchmark.
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
        print(
            json.dumps(
                {key: value[key] for key in ("status", "context_units", "pairing")},
                sort_keys=True,
            )
        )
