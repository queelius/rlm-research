"""Bindings for the supplied-plan child-only J1 ceiling."""
import functools
import hashlib
import importlib.util
import json
import os
from pathlib import Path

ROOT = Path(__file__).resolve().parent
SIDE = ROOT.parent
ATTEMPT = ROOT / "outputs/attempt-001"
PRIOR = SIDE / "leaf-trec-test-adapter-granularity-v1"
SCALE = SIDE / "root-qs-scale-harness-factorial-v1"
QUERY = SIDE / "leaf-trec-query-conditioned-interface-v1"


def read(path): return json.loads(Path(path).read_text())
def sha(path): return hashlib.sha256(Path(path).read_bytes()).hexdigest()
def digest(value): return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(",", ":")).encode()).hexdigest()
def write(path, value):
    path = Path(path); path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(path.name + ".partial")
    temporary.write_text(json.dumps(value, sort_keys=True, indent=2, allow_nan=False) + "\n")
    os.replace(temporary, path)


def load(name, path, pin, aliases=None):
    if sha(path) != pin: raise ValueError("qualified source changed: " + str(path))
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    old = {}
    if aliases:
        import sys
        old = {key: sys.modules.get(key) for key in aliases}; sys.modules.update(aliases)
    try: spec.loader.exec_module(module)
    finally:
        if aliases:
            import sys
            for key, value in old.items():
                if value is None: sys.modules.pop(key, None)
                else: sys.modules[key] = value
    return module


if sha(PRIOR / "READY.json") != "584d54accec7fb8234cf745dab2f65f6d80c2f839ea3253af9b4f9b10b0559b5":
    raise ValueError("qualified TREC service READY changed")
qualified = load("supplied_plan_qualified_trec", PRIOR / "study.py",
                 "e11611a387806cf8dc0213875583a0014a0b7b2fefcd35358ef605db3942a808")
NATIVE = qualified.NATIVE


def dependencies(): return qualified.dependencies()


def binding():
    value = qualified.binding()
    value["study"] = ROOT.name; value["campaign_id"] = ROOT.name
    value["batch_granularity"] = {
        "scientific_role": "supplied_public_j1_plan_ceiling", "frozen_child": "c32",
        "root_calls": 0, "planned": 40,
    }
    return value


@functools.lru_cache(maxsize=1)
def renderer(): return qualified.renderer()


def verify():
    qualified.verify()
    ready = read(ROOT / "READY.json")
    if digest({key: value for key, value in ready.items() if key != "identity"}) != ready["identity"]:
        raise ValueError("READY identity")
    for path, pin in {**ready["source_sha256"], **ready["input_sha256"]}.items():
        if sha(path) != pin: raise ValueError("frozen closure changed: " + path)
    return ready
