"""V4 runtime-only repair for the exact V3 MRCR calibration."""

import copy
import importlib.util
from pathlib import Path
import sys

import study as base
import study_v3 as v3


ROOT = base.ROOT
INPUTS = v3.INPUTS
SPEC = v3.SPEC
ATTEMPT = ROOT / "outputs/attempt-004"
RUNTIME = base.SIDE / "runtime-an22-5801-v1"
RUNTIME_BIN = RUNTIME / "bin"
IMAGE = "8cfe5976b347e0201e52035256537a7cc90fca5004a0bf48cbd42b282498838c"

plan = base.plan
full_rows = v3.full_rows
patch_task_setup = v3.patch_task_setup
prepare_inputs = v3.prepare_inputs


def environment_config(directory):
    value = copy.deepcopy(v3.environment_config(directory))
    value["agent"]["runtime"] = {
        "type": "docker",
        "image": IMAGE,
        "workdir": "/app",
    }
    return value


def verify_allocation_runtime():
    name = "mrcr_v4_allocation_study_wrapper"
    spec = importlib.util.spec_from_file_location(name, RUNTIME / "study_wrapper.py")
    module = importlib.util.module_from_spec(spec)
    old_path = list(sys.path)
    try:
        sys.path.insert(0, str(RUNTIME))
        assert spec.loader is not None
        spec.loader.exec_module(module)
        receipt = module.verify_runtime()
    finally:
        sys.path[:] = old_path
    if receipt["image_id"] != IMAGE or Path(receipt["private_wrapper"]) != RUNTIME_BIN / "docker":
        raise ValueError("allocation runtime receipt changed")
    return receipt


def verify():
    v3.verify()
    ready = base.read(ROOT / "READY_V4.json")
    if ready["identity"] != base.digest({k: value for k, value in ready.items() if k != "identity"}):
        raise ValueError("READY_V4 identity changed")
    for path, expected in ready["closure_sha256"].items():
        if base.sha(path) != expected:
            raise ValueError("READY_V4 closure changed: " + path)
    verify_allocation_runtime()
    return ready

