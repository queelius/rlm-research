"""Exact checkpoint-2 continuation with all science kept in the source namespace."""
import hashlib
import importlib.util
import json
import os
import sys
import uuid
from pathlib import Path

ROOT = Path(__file__).resolve().parent
SIDE = ROOT.parent
SOURCE = SIDE / "root-question-sensitive-terminal-rlvr-recovery-v2"
SPARSE = SIDE / "root-composed-rl-sparse-head-recovery-v2"
READOUT = SIDE / "root-composed-rl-checkpoint2-readout-v1"
SPARSE_V1 = SIDE / "root-composed-rl-sparse-head-recovery-v1"
ATTEMPT = ROOT / "outputs/attempt-001"
READOUT_ATTEMPT = ROOT / "outputs/readout-attempt-001"
TRAIN = Path("/project/alex_phd/envs/bootstrap-training-v1/bin/python")
NATIVE = Path("/project/alex_phd/envs/prime-rl-5990b1b/bin/python")

sys.path.insert(0, str(SOURCE))
import terminal_study as source_study  # noqa: E402
import terminal_common as common  # noqa: E402
import terminal_native as native  # noqa: E402
import terminal_collect as collect  # noqa: E402
import terminal_export as export  # noqa: E402
import terminal_owner as source_owner  # noqa: E402
import terminal_train as source_train  # noqa: E402

read, sha, digest, check, load, aliases = (source_study.read, source_study.sha,
                                           source_study.digest, source_study.check,
                                           source_study.load, source_study.aliases)


def write(path, value):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(path.name + ".pending-" + uuid.uuid4().hex)
    try:
        with temporary.open("x") as stream:
            json.dump(value, stream, indent=2, sort_keys=True, allow_nan=False)
            stream.write("\n")
            stream.flush()
            os.fsync(stream.fileno())
        os.link(temporary, path)
    finally:
        temporary.unlink(missing_ok=True)


def checkpoint2_policy():
    terminal_path = SPARSE / "outputs/attempt-001/OWNER_TERMINAL.json"
    terminal = read(terminal_path)
    if not terminal.get("complete") or not terminal.get("released"):
        raise ValueError("checkpoint2 owner is not complete and released")
    policy = terminal["policy"]
    checkpoint = Path(policy["path"])
    state = read(checkpoint / "state.json")
    if state.get("optimizer_steps") != 2 or state.get("generation", {}).get("candidate_window") != 3:
        raise ValueError("not exact failed-window3 update2")
    for name, pin in state["files_sha256"].items():
        check(checkpoint / name, pin)
    if policy.get("state_sha256") != sha(checkpoint / "state.json"):
        raise ValueError("checkpoint2 policy state differs")
    common.c.authenticate_policy(policy)
    return policy


def readout_gate():
    terminal_path = READOUT / "outputs/attempt-003/OWNER_TERMINAL.json"
    cost_path = READOUT / "outputs/attempt-003/COST_LEDGER.json"
    if not terminal_path.exists() or not cost_path.exists():
        return {"run": False, "reason": "checkpoint2 readout terminal/cost absent"}
    terminal = read(terminal_path)
    if not terminal.get("complete") or not terminal.get("released"):
        return {"run": False, "reason": "checkpoint2 readout incomplete or unreleased"}
    if terminal.get("policy") != checkpoint2_policy():
        raise ValueError("checkpoint2 readout used another policy")
    return {"run": True, "reason": None, "terminal_sha256": sha(terminal_path),
            "cost_sha256": sha(cost_path)}


def verify_prepared():
    campaign = read(ROOT / "CAMPAIGN.json")
    if digest({key: value for key, value in campaign.items() if key != "identity"}) != campaign["identity"]:
        raise ValueError("campaign identity")
    for path, pin in {**campaign["source_sha256"], **campaign["input_sha256"]}.items():
        check(path, pin)
    ready = read(ROOT / "READY.json")
    if ready["identity"] != campaign["identity"] or ready["campaign_sha256"] != sha(ROOT / "CAMPAIGN.json"):
        raise ValueError("READY identity")
    if not readout_gate()["run"]:
        raise ValueError(readout_gate()["reason"])
    if ready["checkpoint2_policy"] != checkpoint2_policy() or ready["readout_gate"] != readout_gate():
        raise ValueError("live checkpoint2/readout gate differs")
    return campaign


def final_policy():
    terminal_path = ATTEMPT / "OWNER_TERMINAL.json"
    if not terminal_path.exists():
        return {"run": False, "reason": "continuation terminal absent"}
    terminal = read(terminal_path)
    if not terminal.get("complete") or not terminal.get("released") or terminal.get("completed_windows") != 8:
        return {"run": False, "reason": "continuation did not cleanly consume through window8"}
    policy = terminal["policy"]
    common.c.authenticate_policy(policy)
    return {"run": True, "reason": None, "policy": policy,
            "owner_terminal_sha256": sha(terminal_path)}
