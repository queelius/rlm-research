"""Response-joint V2 bindings over the exact same fixed native batch."""

import hashlib
import importlib.util
from pathlib import Path


ROOT = Path(__file__).resolve().parent
LOCAL = ROOT.parent / "b05-vector-credit-local-v2/study.py"
assert hashlib.sha256(LOCAL.read_bytes()).hexdigest() == "d9eadbde5f43c103df9cd36cf0eda1801a98bc10195fc2f91d5754fa9a6bf5dd"
spec = importlib.util.spec_from_file_location("vector_joint_v2_local_study", LOCAL)
local = importlib.util.module_from_spec(spec); spec.loader.exec_module(local)
for name, value in vars(local).items():
    if not name.startswith("__"): globals()[name] = value
ROOT = Path(__file__).resolve().parent
READY = ROOT / "READY.json"; OUTPUT = ROOT / "outputs/attempt-001"
CREDIT_MODE = "joint"
REWARD_DESCRIPTION = "mean candidate correctness per response; response-joint G4 RLOO"
ALIAS = "Qwen3-4B-Instruct-2507-b05-vector-credit-joint-step1-v2"


def validate_inputs(data):
    # The joint reward is a response scalar, while the inherited diagnostic row is
    # explicitly vector-valued. Broadcast only in a temporary validation view and
    # restore the scientific scalar before returning it to the loss implementation.
    source_rewards = {row["episode_id"]: row["joint_reward"] for row in data["episodes"]}
    patched = dict(data); patched["episodes"] = []
    for source_row in data["episodes"]:
        row = dict(source_row)
        row["joint_reward"] = [row["joint_reward"]] * row["candidate_count"]
        patched["episodes"].append(row)
    rows = local.validate_for_mode(patched, CREDIT_MODE)
    for row in rows: row["joint_reward"] = source_rewards[row["episode_id"]]
    return rows
def load_sealed_inputs(): return validate_inputs(read(INPUTS))


def verify():
    ready = read(READY)
    assert ready["identity"] == digest({key: value for key, value in ready.items() if key != "identity"})
    for path, expected in ready["closure_sha256"].items(): assert sha(path) == expected, path
    validate_inputs(read(INPUTS)); return ready
