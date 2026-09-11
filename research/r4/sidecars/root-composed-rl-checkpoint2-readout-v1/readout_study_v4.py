"""Additive attempt-002 binding after attempt-001 used the wrong Python environment."""
from pathlib import Path

import readout_study as base

ROOT = Path(__file__).resolve().parent
ATTEMPT = ROOT / "outputs/attempt-002"


def __getattr__(name):
    return getattr(base, name)


def verify_prepared():
    campaign = base.read(ROOT / "CAMPAIGN_V4.json")
    if base.digest({key: value for key, value in campaign.items() if key != "identity"}) != campaign["identity"]:
        raise ValueError("campaign identity")
    for path, pin in {**campaign["source_sha256"], **campaign["input_sha256"]}.items():
        base.check(path, pin)
    ready = base.read(ROOT / "READY_V4.json")
    if ready["identity"] != campaign["identity"] or ready["campaign_sha256"] != base.sha(ROOT / "CAMPAIGN_V4.json"):
        raise ValueError("READY V4 identity")
    if ready["attempt"] != str(ATTEMPT) or campaign["attempt"] != str(ATTEMPT):
        raise ValueError("attempt-002 binding")
    decision = base.checkpoint2_decision()
    expected = {"policy": decision.get("policy"),
                "owner_terminal_sha256": decision.get("owner_terminal_sha256"),
                "state_sha256": decision.get("state_sha256")}
    if not decision["run"] or ready.get("checkpoint2") != expected:
        raise ValueError("READY checkpoint2 receipt is stale or foreign")
    return campaign
