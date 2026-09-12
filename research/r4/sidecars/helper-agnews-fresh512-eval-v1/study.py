"""One frozen512 schedule and separately qualified endpoint arms."""

import copy
import importlib.util
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent
SIDE = ROOT.parent
DATA = SIDE / "helper-agnews-broader-data-v1"
RL = SIDE / "helper-agnews-native-hf-eightstep-v1"
spec = importlib.util.spec_from_file_location("fresh512_rl_core", RL / "core.py")
rl = importlib.util.module_from_spec(spec)
spec.loader.exec_module(rl)
read, sha, digest, write_x = rl.read, rl.sha, rl.digest, rl.write_x
MODEL, CHILD_ALIAS, NATIVE = rl.original.BASE_MODEL, rl.original.CHILD_ALIAS, rl.original.NATIVE
CAP, OUTER_CAP = 900, 1000
ARMS = ("c32", "rl_step8", "sft_step8")


def gold():
    return read(DATA / "inputs/HELDOUT_GOLD.json")


def schedule():
    records = read(DATA / "inputs/HELDOUT_PUBLIC.json")["records"]
    rows = []
    for index, raw in enumerate(read(DATA / "inputs/HELDOUT_REQUESTS.json")):
        schema = json.loads(raw["schema_ordered_json"])
        ids = raw["requested_ids"]
        body = copy.deepcopy(raw["body"])
        body["sampling_params"]["structured_outputs"]["json"] = schema
        if (
            list(schema["properties"]) != ids
            or schema["required"] != ids
            or body["sampling_params"]["temperature"] != 0
            or body["sampling_params"]["seed"] != 202609126000 + index
            or len(body["token_ids"]) + 1024 > 8192
        ):
            raise ValueError("frozen512 ordered schema/seed/context differs")
        rows.append(
            {
                "call_id": raw["coordinate_id"],
                "dataset": "ag_news",
                "start": index * 4,
                "ids": ids,
                "schema_ordered_json": raw["schema_ordered_json"],
                "body": body,
            }
        )
    ids = [identifier for row in rows for identifier in row["ids"]]
    if (
        len(rows) != 128
        or len(ids) != 512
        or len(set(ids)) != 512
        or ids != [row["id"] for row in records]
    ):
        raise ValueError("exact128call/512record source order differs")
    return rows


def attempt(arm):
    if arm not in ARMS:
        raise ValueError("unknown endpoint arm")
    return ROOT / "outputs" / (arm + "-001")


def ready_path(arm):
    return ROOT / ("READY_" + arm.upper() + ".json")


def plan(arm):
    return {
        "schema": "agnews-fresh512-eval-plan-v1",
        "arm": arm,
        "output": str(attempt(arm)),
        "owner_seconds": CAP,
        "external_seconds": OUTER_CAP,
        "planned_calls": 128,
        "planned_records": 512,
        "batch": 4,
        "temperature": 0,
        "schedule_sha256": digest(schedule()),
        "endpoint_selection": "fixed final step8",
        "endpoints_fixed_receipt_required": True,
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
    if (
        digest({key: value for key, value in ready.items() if key != "identity"})
        != ready["identity"]
    ):
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
