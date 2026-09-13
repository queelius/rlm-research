"""Response-joint G4 credit bindings over the identical fixed native vector batch."""

import importlib.util
from pathlib import Path


ROOT = Path(__file__).resolve().parent
LOCAL = ROOT.parent / "b05-vector-credit-local-v1/study.py"
spec = importlib.util.spec_from_file_location("vector_joint_local_study", LOCAL)
local = importlib.util.module_from_spec(spec); spec.loader.exec_module(local)
for name, value in vars(local).items():
    if not name.startswith("__"): globals()[name] = value
ROOT = Path(__file__).resolve().parent
READY = ROOT / "READY.json"; OUTPUT = ROOT / "outputs/attempt-001"
CREDIT_MODE = "joint"
REWARD_DESCRIPTION = "mean candidate correctness per response; response-joint G4 RLOO"
ALIAS = "Qwen3-4B-Instruct-2507-b05-vector-credit-joint-step1"


def validate_inputs(data):
    rows = local.validate_inputs(data)
    assert any(any(value != 0 for value in row["joint_advantages"]) for row in rows)
    return rows


def verify():
    ready = read(READY)
    assert ready["identity"] == digest({key: value for key, value in ready.items() if key != "identity"})
    for path, expected in ready["closure_sha256"].items(): assert sha(path) == expected, path
    validate_inputs(read(INPUTS)); return ready
