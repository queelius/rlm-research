"""Query-conditioned TREC child-interface study bindings."""

import functools
import hashlib
import importlib.util
import json
import os
from pathlib import Path


ROOT = Path(__file__).resolve().parent
SIDE = ROOT.parent
STORE = SIDE.parent
ATTEMPT = ROOT / "outputs/attempt-001"
PRIOR = SIDE / "leaf-trec-test-adapter-granularity-v1"
BASE_MODEL = "/project/alex_phd/research-cache/models/Qwen--Qwen3-4B-Instruct-2507--cdbee75f17c01a7cc42f958dc650907174af0554"
SEEDS = tuple(range(993110001, 993110049))


def read(path):
    return json.loads(Path(path).read_text())


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def digest(value):
    payload = json.dumps(value, sort_keys=True, separators=(",", ":")).encode()
    return hashlib.sha256(payload).hexdigest()


def write(path, value):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(path.name + ".partial")
    temporary.write_text(json.dumps(value, sort_keys=True, indent=2, allow_nan=False) + "\n")
    os.replace(temporary, path)


def load(name, path, pin):
    if sha(path) != pin:
        raise ValueError("qualified source changed")
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


QUALIFIED_READY_SHA = "584d54accec7fb8234cf745dab2f65f6d80c2f839ea3253af9b4f9b10b0559b5"
if sha(PRIOR / "READY.json") != QUALIFIED_READY_SHA:
    raise ValueError("qualified TREC READY changed")
qualified_ready = read(PRIOR / "READY.json")
qualified = load(
    "query_conditioned_qualified_trec_study",
    PRIOR / "study.py",
    qualified_ready["source_sha256"][str(PRIOR / "study.py")],
)
NATIVE = qualified.NATIVE


def dependencies():
    return qualified.dependencies()


def binding():
    value = qualified.binding()
    value["study"] = ROOT.name
    value["campaign_id"] = ROOT.name
    value["batch_granularity"] = {
        "scientific_role": "trec_query_conditioned_child_interface",
        "frozen_child": "c32",
        "root_calls": 0,
        "planned": 192,
    }
    return value


@functools.lru_cache(maxsize=1)
def renderer():
    return qualified.renderer()


def verify():
    qualified.verify()
    ready = read(ROOT / "READY.json")
    if digest({key: value for key, value in ready.items() if key != "identity"}) != ready["identity"]:
        raise ValueError("READY identity")
    for path, pin in {**ready["source_sha256"], **ready["input_sha256"]}.items():
        if sha(path) != pin:
            raise ValueError("frozen source changed " + path)
    return ready
