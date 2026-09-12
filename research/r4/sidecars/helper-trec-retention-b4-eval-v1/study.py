"""Exact historically exposed TREC B4 retention schedule and endpoint arms."""

import copy
import importlib.util
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent
SIDE = ROOT.parent
PANEL = SIDE / "helper-trec-retention-b4-panel-v1"
SOURCE_EVAL = SIDE / "helper-agnews-fresh512-eval-v1"
DATA = SIDE / "helper-agnews-broader-data-v1"  # Endpoint training lineage only.
RL = SIDE / "helper-agnews-native-hf-eightstep-v1"
spec = importlib.util.spec_from_file_location("trec_retention_rl_core", RL / "core.py")
rl = importlib.util.module_from_spec(spec)
spec.loader.exec_module(rl)
read, sha, digest, write_x = rl.read, rl.sha, rl.digest, rl.write_x
MODEL, CHILD_ALIAS, NATIVE = rl.original.BASE_MODEL, rl.original.CHILD_ALIAS, rl.original.NATIVE
CAP, OUTER_CAP = 600, 700
ARMS = ("c32", "rl_step8", "sft_step8")
SEED2_EXCLUSION = {
    "arm": "ag_rl_step8_seed2",
    "source": str(SIDE / "helper-agnews-native-hf-eightstep-seed2-v1"),
    "reason": "conditional replica was not a completed, qualified step8 endpoint at seal time",
    "status": "deferred_to_additive_evaluation_after_exact_step8_qualification",
}


def gold():
    return read(PANEL / "HOST_GOLD.json")


def schedule():
    records = read(PANEL / "PUBLIC.json")["records"]
    rows = []
    for index, raw in enumerate(read(PANEL / "REQUESTS.json")):
        schema = json.loads(raw["schema_ordered_json"])
        ids = raw["ids"]
        body = copy.deepcopy(raw["body_template"])
        body["model"] = CHILD_ALIAS
        body["sampling_params"]["structured_outputs"]["json"] = schema
        if (
            raw["dataset"] != "trec"
            or list(schema["properties"]) != ids
            or schema["required"] != ids
            or body["sampling_params"]["temperature"] != 0
            or body["sampling_params"]["seed"] != 202609121800 + index
            or len(body["token_ids"]) + 1024 > 8192
        ):
            raise ValueError("frozen TREC retention request differs")
        rows.append(
            {
                "call_id": raw["request_id"],
                "dataset": "trec",
                "start": raw["start"],
                "ids": ids,
                "schema_ordered_json": raw["schema_ordered_json"],
                "body": body,
            }
        )
    ids = [identifier for row in rows for identifier in row["ids"]]
    if (
        len(rows) != 32
        or len(ids) != 128
        or len(set(ids)) != 128
        or ids != [row["id"] for row in records]
        or set(ids) != set(gold()["labels"])
    ):
        raise ValueError("exact 32-call/128-record retention inventory differs")
    return rows


def attempt(arm):
    if arm not in ARMS:
        raise ValueError("unknown endpoint arm")
    return ROOT / "outputs" / (arm + "-001")


def ready_path(arm):
    return ROOT / ("READY_" + arm.upper() + ".json")


def plan(arm):
    return {
        "schema": "helper-trec-retention-b4-eval-plan-v1",
        "arm": arm,
        "output": str(attempt(arm)),
        "owner_seconds": CAP,
        "external_seconds": OUTER_CAP,
        "planned_calls": 32,
        "planned_records": 128,
        "batch": 4,
        "temperature": 0,
        "schedule_sha256": digest(schedule()),
        "panel_manifest_sha256": sha(PANEL / "MANIFEST.json"),
        "evaluator_amendment_sha256": sha(ROOT / "EVALUATOR_AMENDMENT.json"),
        "endpoint_selection": "fixed c32 or fixed completed step8; no checkpoint selection",
        "seed2_exclusion": SEED2_EXCLUSION,
        "claim_boundary": "retention on an historically evaluated TREC source partition",
        "command": [
            str(NATIVE),
            str(ROOT / "owner.py"),
            "run",
            "--arm",
            arm,
            "--outer-seconds",
            str(CAP),
        ],
    }


def verify(arm):
    ready = read(ready_path(arm))
    if digest({key: value for key, value in ready.items() if key != "identity"}) != ready["identity"]:
        raise ValueError("endpoint READY identity differs")
    for key, value in plan(arm).items():
        if ready.get(key) != value:
            raise ValueError("endpoint plan differs: " + key)
    for path, expected in ready["closure_sha256"].items():
        if sha(path) != expected:
            raise ValueError("endpoint closure changed: " + path)
    return ready


def lifecycle():
    view = rl.step_view(1)
    view.ROOT = ROOT
    native = rl.native_module(view)
    owner = native.lifecycle()
    with rl.original.aliases({"study": view}):
        suite = owner.dependencies()
    return owner, suite


def sanitized_runtime(config):
    value = copy.deepcopy(config)
    value.pop("output_dir", None)
    value.get("vllm", {}).pop("api_key", None)
    return value
