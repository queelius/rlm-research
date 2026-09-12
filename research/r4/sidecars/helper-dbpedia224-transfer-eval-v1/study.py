"""Frozen DBpedia-224 schedule and four predeclared completed helper endpoints."""

import copy
import importlib.util
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parent
SIDE = ROOT.parent
EVAL_DATA = SIDE / "helper-dbpedia224-transfer-data-v1"
DATA = SIDE / "helper-agnews-broader-data-v1"
RL = SIDE / "helper-agnews-native-hf-eightstep-v1"
SOURCE = SIDE / "helper-agnews-fresh512-eval-v1"
OFFICIAL_SOURCE = SIDE / "helper-agnews-official-test-fresh512-eval-v1"
SEED2_EVAL = SIDE / "helper-agnews-eightstep-seed2-eval-v1"
spec = importlib.util.spec_from_file_location("dbpedia_transfer_rl_core", RL / "core.py")
rl = importlib.util.module_from_spec(spec)
spec.loader.exec_module(rl)
read, sha, digest, write_x = rl.read, rl.sha, rl.digest, rl.write_x
MODEL, CHILD_ALIAS, NATIVE = rl.original.BASE_MODEL, rl.original.CHILD_ALIAS, rl.original.NATIVE
CAP, OUTER_CAP = 700, 800
ARMS = ("c32", "rl_step8", "sft_step8", "rl_seed2_step8")
LABELS = (
    "Company",
    "EducationalInstitution",
    "Artist",
    "Athlete",
    "OfficeHolder",
    "MeanOfTransportation",
    "Building",
    "NaturalPlace",
    "Village",
    "Animal",
    "Plant",
    "Album",
    "Film",
    "WrittenWork",
)


def gold():
    return read(EVAL_DATA / "inputs/HOST_GOLD.json")


def schedule():
    records = read(EVAL_DATA / "inputs/PUBLIC.json")["records"]
    rows = []
    for index, raw in enumerate(read(EVAL_DATA / "inputs/REQUESTS.json")):
        schema = json.loads(raw["schema_ordered_json"])
        ids = raw["ids"]
        body = copy.deepcopy(raw["body_template"])
        body["model"] = CHILD_ALIAS
        body["sampling_params"]["structured_outputs"]["json"] = schema
        enums = [value["enum"] for value in schema["properties"].values()]
        if (
            list(schema["properties"]) != ids
            or schema["required"] != ids
            or any(value != list(LABELS) for value in enums)
            or body["sampling_params"]["temperature"] != 0
            or body["sampling_params"]["seed"] != 202609123500 + index
            or len(body["token_ids"]) + 1024 > 8192
        ):
            raise ValueError("DBpedia frozen ordered request differs")
        rows.append(
            {
                "call_id": raw["request_id"],
                "dataset": "dbpedia14",
                "start": raw["start"],
                "ids": ids,
                "schema_ordered_json": raw["schema_ordered_json"],
                "body": body,
            }
        )
    ids = [key for row in rows for key in row["ids"]]
    if len(rows) != 56 or len(ids) != 224 or len(set(ids)) != 224 or ids != [row["id"] for row in records]:
        raise ValueError("exact DBpedia 56-call/224-record order differs")
    return rows


def attempt(arm):
    if arm not in ARMS:
        raise ValueError("unknown endpoint arm")
    return ROOT / "outputs" / (arm + "-001")


def ready_path(arm):
    return ROOT / ("READY_" + arm.upper() + ".json")


def plan(arm):
    return {
        "schema": "helper-dbpedia224-transfer-eval-plan-v1",
        "arm": arm,
        "output": str(attempt(arm)),
        "owner_seconds": CAP,
        "external_seconds": OUTER_CAP,
        "planned_calls": 56,
        "planned_records": 224,
        "batch": 4,
        "temperature": 0,
        "schedule_sha256": digest(schedule()),
        "evaluation_data_ready_sha256": sha(EVAL_DATA / "DATA_READY.json"),
        "endpoint_selection": "none; four named completed checkpoints fixed before DBpedia query",
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
        raise ValueError("READY identity differs")
    for key, value in plan(arm).items():
        if ready.get(key) != value:
            raise ValueError("plan differs: " + key)
    for path, expected in ready["closure_sha256"].items():
        if sha(path) != expected:
            raise ValueError("closure changed: " + path)
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

