"""Official TREC-test child-only base/c32 granularity study."""
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
PRIOR = SIDE / "leaf-adapter-by-granularity-v1"
SOURCE = Path("/project/alex_phd/research-cache/2026-09-08-literature/trec-leaf-splits.4HU2Tz/TREC_10.label")
SPLIT = SIDE / "trec-leaf-split-provenance-v1/PROPOSED_SPLIT.json"
TRAIN_PREPARED = SIDE / "trec-leaf-sft-v1/prepared-v1"
BASE_MODEL = "/project/alex_phd/research-cache/models/Qwen--Qwen3-4B-Instruct-2507--cdbee75f17c01a7cc42f958dc650907174af0554"
SEEDS = (991902701, 991902702)


def read(path):
    return json.loads(Path(path).read_text())


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def digest(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(",", ":")).encode()).hexdigest()


def write(path, value):
    path = Path(path); path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(path.name + ".partial")
    temporary.write_text(json.dumps(value, sort_keys=True, indent=2, allow_nan=False) + "\n")
    os.replace(temporary, path)


def load(name, path, pin):
    if sha(path) != pin:
        raise ValueError("qualified source changed")
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec); spec.loader.exec_module(module)
    return module


QUALIFIED_READY_SHA = "96fbd27f17b8a979ddc52016459dfced7f3a8f9aaa7389f1bc80de72c5828435"
if sha(PRIOR / "READY.json") != QUALIFIED_READY_SHA:
    raise ValueError("qualified READY changed")
qualified_ready = read(PRIOR / "READY.json")
qualified = load("trec_test_qualified_study", PRIOR / "bg_study.py", qualified_ready["source_sha256"][str(PRIOR / "bg_study.py")])
NATIVE = qualified.NATIVE


def dependencies():
    return qualified.dependencies()


def binding():
    value = qualified.binding()
    value["study"] = ROOT.name; value["campaign_id"] = ROOT.name
    value["batch_granularity"] = {"scientific_role": "official_trec_test_base_vs_c32", "frozen_child": "c32", "root_calls": 0, "planned": 148}
    return value


@functools.lru_cache(maxsize=1)
def renderer():
    return qualified.renderer()


def verify():
    ready = read(ROOT / "READY.json")
    if digest({key: value for key, value in ready.items() if key != "identity"}) != ready["identity"]:
        raise ValueError("READY identity")
    for path, pin in {**ready["source_sha256"], **ready["input_sha256"]}.items():
        if sha(path) != pin:
            raise ValueError("frozen source changed " + path)
    return ready
