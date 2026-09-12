"""Call-free three-arm reinspection; preserve unknowns and original completion flags."""

import hashlib
import importlib.util
import json
import math
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
STORE = HERE.parents[1]
SIDE = STORE / "sidecars/openai-mrcr-short-root-token-tis-held-eval-v1"
READY_SHA = "fb703d787841976e04a016e69e95841e1aa1ab4003840b0d4afb2cd0f8a0c65d"
ARMS = ("base", "lr1e-5", "lr1e-4")


def read(path):
    return json.loads(path.read_text())


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def execute():
    assert sha(SIDE / "CPU_READY_V4.json") == READY_SHA
    sys.path.insert(0, str(SIDE))
    import owner_v4
    import collect_v4
    study = owner_v4.study
    owner_v4.verify("base")
    inspector = collect_v4.source_module()
    previous = STORE / "analyses/openai-mrcr-shaped-root-update-2026-09-12/analyze.py"
    spec = importlib.util.spec_from_file_location("held_procedure_diagnostics", previous)
    helpers = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(helpers)
    plan = {row["id"]: row for row in study.schedule("held")}
    gold = read(study.input_dir("held") / "HOST_GOLD.json")
    prefixes = read(study.input_dir("held") / "PREFIXES.json")
    arms = {}
    sources = {str(SIDE / "CPU_READY_V4.json"): READY_SHA, str(previous): sha(previous)}
    for arm in ARMS:
        output = SIDE / "outputs-v4" / (arm + "-001")
        terminal = read(output / "OWNER_TERMINAL.json")
        assert terminal["released"]
        science = output / "science"
        original = read(science / "RESULT.json")
        native_paths = sorted((science / "native-calls").glob("*-result.json"))
        native = [read(path) for path in native_paths]
        assert len({row["index"] for row in native}) == len(native)
        wrappers, rows = [], []
        for path in sorted((science / "episodes").glob("*.json")):
            value = read(path)
            coordinate, raw = value["coordinate"], value["episode"]
            assert coordinate == plan[coordinate["id"]]
            assert study.digest(raw) == value["episode_sha256"]
            derived = inspector.inspect_trace(raw, gold[coordinate["record_id"]], native,
                prefixes[coordinate["id"]]["token_ids"],
                value["derived"]["terminal_status"] == "deadline_censored")
            assert derived == value["derived"], (arm, coordinate["id"], "saved derivation mismatch")
            trace = raw["traces"][0] if len(raw.get("traces", [])) == 1 else {}
            reply = derived["root_reply"]
            available = derived["scientifically_available"]
            rows.append({
                "coordinate_id": coordinate["id"], "record_id": coordinate["record_id"],
                "available": available, "raw_exact": derived["raw_exact"] if available else None,
                "official_score": derived["reward"] if available else None,
                "root_reply_sha256": study.digest(reply), "failure_class": derived["failure_class"],
                "error_types": derived["error_types"], "terminal_status": derived["terminal_status"],
                "root_actions": derived["root_actions_returned"], "child_actions": derived["child_actions_returned"],
                "native_mapping_complete": derived["native_mapping_complete"],
                "initial_root_prefix_verified": derived["initial_root_prefix_verified"],
                "newline_only_would_match": bool(isinstance(reply, str) and reply != derived["answer"]
                                                   and reply.replace("\\n", "\n") == derived["answer"]),
                **helpers.procedure(trace),
            })
            wrappers.append(value)
            sources[str(path)] = sha(path)
        assert {row["coordinate_id"] for row in rows} == set(plan) and len(rows) == 16
        rescored = inspector.summarize(wrappers, "held", arm)
        for key, value in rescored.items():
            assert value == original[key], (arm, key)
        for path in [output / "OWNER_TERMINAL.json", science / "RESULT.json", *native_paths]:
            sources[str(path)] = sha(path)
        known = [row for row in rows if row["available"]]
        arms[arm] = {
            "owner_complete": terminal["complete"], "science_inventory_complete": original["complete"],
            "elapsed_owner_seconds": terminal["elapsed_seconds"], "recorded": len(rows),
            "available": len(known), "unavailable": len(rows) - len(known),
            "raw_exact": sum(row["raw_exact"] for row in known),
            "near_exact": sum(row["official_score"] >= .9 for row in known),
            "official_score_sum": math.fsum(row["official_score"] for row in known),
            "physical_returned": sum(row["status"] == "returned" for row in native),
            "physical_errors": sum(row["status"] == "error" for row in native),
            "root_actions": sum(row["root_actions"] for row in rows),
            "child_actions": sum(row["child_actions"] for row in rows),
            "tool_tracebacks": sum(row["tool_tracebacks"] for row in rows),
            "observation_characters": sum(row["tool_observation_characters"] for row in rows),
            "broad_observations": sum(row["broad_observations_at_least_18000_chars"] for row in rows),
            "rows": rows,
        }
    comparisons = {}
    for left, right in (("base", "lr1e-5"), ("base", "lr1e-4"), ("lr1e-5", "lr1e-4")):
        before = {row["coordinate_id"]: row for row in arms[left]["rows"]}
        pairs = [(before[row["coordinate_id"]], row) for row in arms[right]["rows"]]
        known = [(a, b) for a, b in pairs if a["available"] and b["available"]]
        comparisons[left + "_to_" + right] = {
            "planned": 16, "both_available": len(known), "unavailable_either": 16 - len(known),
            "exact_wins": sum(not a["raw_exact"] and b["raw_exact"] for a, b in known),
            "exact_losses": sum(a["raw_exact"] and not b["raw_exact"] for a, b in known),
            "changed_known_replies": sum(a["root_reply_sha256"] != b["root_reply_sha256"] for a, b in known),
            "near_exact_wins": sum(a["official_score"] < .9 <= b["official_score"] for a, b in known),
            "near_exact_losses": sum(b["official_score"] < .9 <= a["official_score"] for a, b in known),
            "official_score_delta_sum_both_available": math.fsum(b["official_score"] - a["official_score"] for a, b in known),
        }
    return {"schema": "mrcr-token-tis-fixed-three-arm-held-reinspection-v1", "new_model_calls": 0,
            "all48_saved_derivations_reproduced": True, "arms": arms, "paired": comparisons,
            "source_sha256": sources, "derivation_sha256": sha(Path(__file__)),
            "scope": "Reuses frozen mapper/classifier/scorer to recheck native inventories, prefixes and saved episodes; not an independently implemented full wire audit. Missing outcomes remain null. Both fixed doses retained; no checkpoint selection."}


if __name__ == "__main__":
    value = execute()
    with (HERE / "RESULT.json").open("x") as stream:
        json.dump(value, stream, indent=2, sort_keys=True)
        stream.write("\n")
    print(json.dumps({"arms": {arm: {k: v for k, v in data.items() if k != "rows"}
                                for arm, data in value["arms"].items()}, "paired": value["paired"]}, indent=2))
