"""Frozen singleton schedule and authenticated c32/reference-step4 bindings."""

from __future__ import annotations

import copy
import functools
import hashlib
import importlib.util
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parent
SIDE = ROOT.parent
SIZE_SOURCE = SIDE / "helper-unseen-size-comparison-v1"
REFERENCE_EVAL = SIDE / "helper-hf-fourstep-unseen-eval-v1"
C32 = SIDE / "helper-unseen-generalization-c32-baseline-v1"
ARMS = ("c32", "reference_step4")
ATTEMPTS = {arm: ROOT / "outputs" / arm / "attempt-001" for arm in ARMS}
CAP = 900
CALLS = 256
PREDICTIONS = 256


def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec); spec.loader.exec_module(module); return module


@functools.lru_cache(maxsize=1)
def size(): return load("singleton_comparison_size_source", SIZE_SOURCE / "size_study.py")


@functools.lru_cache(maxsize=1)
def reference(): return load("singleton_comparison_reference_eval", REFERENCE_EVAL / "fourstep_panel_study.py")


read = size().read
write = size().write
digest = size().digest
sha = size().sha
NATIVE = size().NATIVE
MODEL = size().MODEL
CHILD_ALIAS = size().CHILD_ALIAS
validator = size().validator
dependencies = size().dependencies
attest = size().attest


def schedule():
    rows = [copy.deepcopy(row) for row in size().schedule() if row["batch_size"] == 1]
    if len(rows) != CALLS or sum(len(row["ids"]) for row in rows) != PREDICTIONS:
        raise ValueError("singleton schedule is not exact256/256")
    if len({row["call_id"] for row in rows}) != CALLS or len({row["ids"][0] for row in rows}) != 256:
        raise ValueError("singleton coordinate/record inventory differs")
    return rows


def binding(arm):
    if arm == "c32":
        source = size().source(); source.verify(); value = source.binding()
        expected = "c32de1293c01bba5104eb1f123867649c71dd38e5194661ace4b17dcbbe66ba3"
    elif arm == "reference_step4":
        receipt = reference().qualify_fourstep(); value = receipt["binding"]
        expected = sha(Path(receipt["checkpoint"]) / "adapter_model.safetensors")
        if receipt.get("primary_step") != 4 or not receipt.get("eligible"):
            raise ValueError("reference binding is not authenticated step4 primary")
    else: raise ValueError("unknown arm")
    alias = value["role_map"]["children"][0]
    if alias != CHILD_ALIAS or value["fixed_child"] != CHILD_ALIAS or value["models"][alias]["adapter_sha256"] != expected:
        raise ValueError("child binding differs")
    return value


def verify(arm):
    if arm not in ARMS: raise ValueError("unknown arm")
    ready = read(ROOT / ("READY_C32.json" if arm == "c32" else "READY_REFERENCE_STEP4.json"))
    if ready.get("arm") != arm or ready.get("status") != "CPU_READY_MAIN_GPU_LAUNCH_ONLY":
        raise ValueError("wrong singleton arm READY")
    if digest({k: v for k, v in ready.items() if k != "identity"}) != ready.get("identity"):
        raise ValueError("READY identity differs")
    for path, expected in ready["closure_sha256"].items():
        if sha(path) != expected: raise ValueError("singleton closure changed: " + path)
    if digest(schedule()) != ready["schedule_sha256"]: raise ValueError("singleton schedule changed")
    if digest(binding(arm)) != ready["binding_sha256"]: raise ValueError("authenticated binding changed")
    return ready
