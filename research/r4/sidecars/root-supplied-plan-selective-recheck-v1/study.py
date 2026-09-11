"""Pinned bindings for the selective recheck sidecar."""
import functools
import hashlib
import importlib.util
import json
import os
from pathlib import Path

ROOT = Path(__file__).resolve().parent
SIDE = ROOT.parent
ATTEMPT = ROOT / "outputs/attempt-001"
CEILING = SIDE / "root-lambda-supplied-plan-ceiling-v1"
CEILING_ANALYSIS = SIDE.parent / "analyses/root-lambda-supplied-plan-ceiling-live-2026-09-10"
NATIVE = Path("/project/alex_phd/envs/prime-rl-5990b1b/bin/python")


def read(path): return json.loads(Path(path).read_text())
def sha(path): return hashlib.sha256(Path(path).read_bytes()).hexdigest()
def digest(value): return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(",", ":")).encode()).hexdigest()
def write(path, value):
    path = Path(path); path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(path.name + ".partial")
    temporary.write_text(json.dumps(value, sort_keys=True, indent=2, allow_nan=False) + "\n")
    os.replace(temporary, path)


@functools.lru_cache(maxsize=1)
def ceiling_study():
    path = CEILING / "study.py"
    spec = importlib.util.spec_from_file_location("selective_recheck_ceiling_study", path)
    module = importlib.util.module_from_spec(spec); spec.loader.exec_module(module)
    return module


def dependencies(): return ceiling_study().dependencies()
def renderer(): return ceiling_study().renderer()


def binding():
    value = ceiling_study().binding()
    value["study"] = ROOT.name; value["campaign_id"] = ROOT.name
    value["batch_granularity"] = {"scientific_role": "confidence_vs_uniform_recheck",
                                  "frozen_child": "c32", "root_calls": 0, "planned": 24}
    return value


def verify():
    ready = read(ROOT / "READY.json")
    if digest({k: v for k, v in ready.items() if k != "identity"}) != ready["identity"]:
        raise ValueError("READY identity")
    for path, pin in {**ready["source_sha256"], **ready["input_sha256"]}.items():
        if sha(path) != pin: raise ValueError("frozen closure changed: " + path)
    return ready
