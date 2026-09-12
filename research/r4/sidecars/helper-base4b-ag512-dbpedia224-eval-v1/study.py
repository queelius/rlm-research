"""Frozen true-base control over the exact AG512 and DBpedia224 schedules."""

import copy
import functools
import hashlib
import importlib.util
import json
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parent
SIDE = ROOT.parent
AG_SOURCE = SIDE / "helper-agnews-official-test-fresh512-eval-v1"
DB_SOURCE = SIDE / "helper-dbpedia224-transfer-eval-v1"
BASE_SOURCE = SIDE / "helper-unseen-generalization-base4b-v1"
MODEL = Path(
    "/project/alex_phd/research-cache/models/"
    "Qwen--Qwen3-4B-Instruct-2507--cdbee75f17c01a7cc42f958dc650907174af0554"
)
BASE_ALIAS = "Qwen3-4B-Instruct-2507-no-research-adapter"
PANELS = ("ag_news", "dbpedia14")
LABELS = {
    "ag_news": ("World", "Sports", "Business", "Sci/Tech"),
    "dbpedia14": (
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
    ),
}
NATIVE = Path("/project/alex_phd/envs/prime-rl-5990b1b/bin/python")
SERVICE_WRAPPER = (
    SIDE / "root-qs6-fixed-helper-top20-batch-invariant-v1/service_batch_invariant_v4.py"
)
ATTEMPT = ROOT / "outputs/attempt-001"
CAP, OUTER_CAP = 900, 1000
SOURCE_SHA = {
    AG_SOURCE / "study.py": "5222a743b5007f7389034f7b25adc148fe60df42f7825f21d0064815651b1041",
    DB_SOURCE / "study.py": "697c05d91be79c73d72499fbf1b888d60a1993a26cf7a5a91e0e7140b76852b2",
    BASE_SOURCE / "base_panel_study_v2.py": "ebd5bbfc912cb6ac51ee032d313704f1e7d5d1bb2fc20711161a6a6e2d4f86fc",
}


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def digest(value):
    return hashlib.sha256(
        json.dumps(value, sort_keys=True, separators=(",", ":")).encode()
    ).hexdigest()


def read(path):
    return json.loads(Path(path).read_text())


def write_x(path, value):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("x") as stream:
        json.dump(value, stream, indent=2, sort_keys=True, allow_nan=False)
        stream.write("\n")


def _load(name, path):
    if sha(path) != SOURCE_SHA[path]:
        raise ValueError("source study changed: " + str(path))
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


AG_STUDY = _load("base_control_ag_study", AG_SOURCE / "study.py")
DB_STUDY = _load("base_control_db_study", DB_SOURCE / "study.py")


def _load_base():
    path = BASE_SOURCE / "base_panel_study_v2.py"
    if sha(path) != SOURCE_SHA[path]:
        raise ValueError("released-base source study changed")
    sys.path.insert(0, str(BASE_SOURCE))
    try:
        spec = importlib.util.spec_from_file_location("base_control_released_study", path)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
    finally:
        sys.path.remove(str(BASE_SOURCE))
    return module


BASE_STUDY = _load_base()


@functools.lru_cache(maxsize=1)
def schedules():
    result = []
    for source in (AG_STUDY.schedule(), DB_STUDY.schedule()):
        rows = copy.deepcopy(source)
        for row in rows:
            row["body"]["model"] = BASE_ALIAS
        result.append(rows)
    calls = [row["call_id"] for rows in result for row in rows]
    if len(calls) != 184 or len(set(calls)) != 184:
        raise ValueError("combined exact schedule call inventory differs")
    return tuple(result)


def exact_source_request_match():
    for rows, source, child_alias in (
        (schedules()[0], AG_STUDY.schedule(), AG_STUDY.CHILD_ALIAS),
        (schedules()[1], DB_STUDY.schedule(), DB_STUDY.CHILD_ALIAS),
    ):
        restored = copy.deepcopy(rows)
        for row in restored:
            row["body"]["model"] = child_alias
        if restored != source:
            return False
    return True


def gold():
    return {
        "ag_news": AG_STUDY.gold()["labels"],
        "dbpedia14": DB_STUDY.gold()["labels"],
    }


def binding():
    value = BASE_STUDY.binding()
    if (
        value.get("adapter") is not None
        or value.get("checkpoint", {}).get("alias") != BASE_ALIAS
        or Path(value["checkpoint"]["path"]).resolve() != MODEL.resolve()
    ):
        raise ValueError("released-base binding is not exact no-adapter Qwen3-4B")
    return value


@functools.lru_cache(maxsize=1)
def dependencies():
    suite = BASE_STUDY.dependencies()
    suite.SERVE = SERVICE_WRAPPER
    suite.life.__dict__["ALLOCATION_SERVICE"] = SERVICE_WRAPPER
    return suite


def sanitized_runtime(config):
    value = copy.deepcopy(config)
    value.pop("output_dir", None)
    value.get("vllm", {}).pop("api_key", None)
    return value


def plan():
    ag, db = schedules()
    return {
        "schema": "helper-base4b-ag512-dbpedia224-eval-plan-v1",
        "output": str(ATTEMPT),
        "policy": "unadapted Qwen3-4B-Instruct-2507",
        "adapter": None,
        "owner_seconds": CAP,
        "external_seconds": OUTER_CAP,
        "planned_calls": {"ag_news": len(ag), "dbpedia14": len(db), "total": len(ag) + len(db)},
        "planned_records": {"ag_news": 512, "dbpedia14": 224, "total": 736},
        "batch": 4,
        "temperature": 0,
        "schedule_sha256": digest([ag, db]),
        "source_request_match_except_model_alias": True,
        "runtime_difference": (
            "True base service disables LoRA and prefix caching; trained arms enable LoRA/prefix "
            "caching. Batch-invariant kernel is required in both, but cost/bitwise matching is not claimed."
        ),
        "command": [str(NATIVE), str(ROOT / "owner.py"), "run", "--outer-seconds", str(CAP)],
    }


def verify():
    ready = read(ROOT / "READY.json")
    if ready["identity"] != digest({key: value for key, value in ready.items() if key != "identity"}):
        raise ValueError("READY identity changed")
    for key, value in plan().items():
        if ready.get(key) != value:
            raise ValueError("base-control plan changed: " + key)
    for path, expected in ready["closure_sha256"].items():
        if sha(path) != expected:
            raise ValueError("base-control closure changed: " + path)
    return ready
