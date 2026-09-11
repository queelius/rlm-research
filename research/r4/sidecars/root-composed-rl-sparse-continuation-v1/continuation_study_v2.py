"""Additive runtime correction for the frozen continuation package."""
from pathlib import Path

import continuation_study as base

ROOT = Path(__file__).resolve().parent
ATTEMPT = ROOT / "outputs/attempt-002"
READOUT_ATTEMPT = ROOT / "outputs/readout-attempt-002"
TRAIN = Path("/project/alex_phd/repos/rlm-bootstrap/.worktrees/a100-lora-roundtrip/gpu/training/.venv/bin/python")


def __getattr__(name):
    return getattr(base, name)


def verify_prepared():
    campaign = base.read(ROOT / "CAMPAIGN_V2.json")
    if base.digest({key: value for key, value in campaign.items() if key != "identity"}) != campaign["identity"]:
        raise ValueError("campaign V2 identity")
    for path, pin in {**campaign["source_sha256"], **campaign["input_sha256"]}.items():
        base.check(path, pin)
    ready = base.read(ROOT / "READY_V2.json")
    if ready["identity"] != campaign["identity"] or ready["campaign_sha256"] != base.sha(ROOT / "CAMPAIGN_V2.json"):
        raise ValueError("READY V2 identity")
    gate = base.readout_gate()
    if not gate["run"] or ready["readout_gate"] != gate:
        raise ValueError("checkpoint2 readout gate differs")
    if ready["checkpoint2_policy"] != base.checkpoint2_policy():
        raise ValueError("checkpoint2 policy differs")
    return campaign


def final_policy():
    terminal_path = ATTEMPT / "OWNER_TERMINAL.json"
    if not terminal_path.exists():
        return {"run": False, "reason": "continuation V2 terminal absent"}
    terminal = base.read(terminal_path)
    if not terminal.get("complete") or not terminal.get("released") or terminal.get("completed_windows") != 8:
        return {"run": False, "reason": "continuation V2 did not consume through window8"}
    policy = terminal["policy"]
    base.common.c.authenticate_policy(policy)
    return {"run": True, "reason": None, "policy": policy,
            "owner_terminal_sha256": base.sha(terminal_path)}
