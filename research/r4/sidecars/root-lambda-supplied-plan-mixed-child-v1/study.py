"""Exact mixed-child binding over the frozen supplied-plan40 harness."""

import functools
import hashlib
import importlib.util
import json
import os
from pathlib import Path

ROOT = Path(__file__).resolve().parent
SIDE = ROOT.parent
ATTEMPT = ROOT / "outputs/attempt-001"
PRIOR_CEILING = SIDE / "root-lambda-supplied-plan-ceiling-v1"
MIXED_ROOT = SIDE / "trec-child-interface-mixed-sft-followup-v1"
MIXED = MIXED_ROOT / "outputs/attempt-001/training/mixed/checkpoint-0024"
MIXED_SHA = "0fd1c50319b9bd33fb5ee01de373873348f0d07a956928268fd9be5e65472701"
MIXED_ALIAS = "trec-mixed-sft24"
NATIVE = Path("/project/alex_phd/envs/prime-rl-5990b1b/bin/python")


def read(path): return json.loads(Path(path).read_text())
def sha(path): return hashlib.sha256(Path(path).read_bytes()).hexdigest()
def digest(value): return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(",", ":")).encode()).hexdigest()
def write(path, value):
    path = Path(path); path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(path.name + ".partial")
    temporary.write_text(json.dumps(value, sort_keys=True, indent=2, allow_nan=False) + "\n")
    os.replace(temporary, path)


def load(name, path, pin):
    if sha(path) != pin: raise ValueError("qualified source changed: " + str(path))
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec); spec.loader.exec_module(module)
    return module


qualified = load("mixed_supplied_plan_qualified", PRIOR_CEILING / "study.py",
                 "45dc503a23888ee88f19355fea0c017b8aea813e6b9c3c641af212d89d801455")


def dependencies(): return qualified.dependencies()


def binding():
    value = qualified.binding()
    old_alias = value["fixed_child"]
    value["models"].pop(old_alias)
    value["models"][MIXED_ALIAS] = {
        "path": str(MIXED), "adapter_sha256": MIXED_SHA,
        "config_sha256": sha(MIXED / "adapter_config.json"),
    }
    value["fixed_child"] = MIXED_ALIAS
    value["role_map"]["children"] = [MIXED_ALIAS]
    value["study"] = ROOT.name; value["campaign_id"] = ROOT.name
    value["batch_granularity"] = {
        "scientific_role": "supplied_public_j1_plan_mixed_child_bridge",
        "frozen_child": "mixed_sft24", "root_calls": 0, "planned": 40,
    }
    value["child_selection"] = {
        "rule": "fixed true completed mixed update24; no outcome selection",
        "selection_sha256": sha(MIXED.parent / "SELECTION.json"),
        "state_sha256": sha(MIXED / "state.json"),
        "adapter_sha256": MIXED_SHA,
    }
    return value


@functools.lru_cache(maxsize=1)
def renderer(): return qualified.renderer()


def verify():
    qualified.verify()
    if sha(MIXED / "adapter_model.safetensors") != MIXED_SHA:
        raise ValueError("mixed checkpoint changed")
    ready = read(ROOT / "READY.json")
    if digest({key: value for key, value in ready.items() if key != "identity"}) != ready["identity"]:
        raise ValueError("READY identity")
    for path, pin in {**ready["source_sha256"], **ready["input_sha256"]}.items():
        if sha(path) != pin: raise ValueError("frozen closure changed: " + path)
    return ready
