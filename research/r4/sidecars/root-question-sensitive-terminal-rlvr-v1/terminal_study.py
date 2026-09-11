"""Exact QS6 start and isolated terminal-RLVR study identity."""
import hashlib
import importlib.util
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
SIDE = ROOT.parent
QS = SIDE / "root-question-sensitive-sft-v1"
RECOVERY = SIDE / "root-question-sensitive-sft-recovery-v1"
WARM = SIDE / "root-sft24-terminal-rlvr-v1"
QSR = SIDE / "root-query-sensitive-rl-v1"
ATTEMPT = ROOT / "outputs/attempt-001"
CHECKPOINT = RECOVERY / "outputs/attempt-003/training/checkpoint-0006"
SELECTION = RECOVERY / "outputs/attempt-003/training/SELECTION.json"
ROOT_START_SHA = "4d8287537a9ff3d8e33bc0314f64315dee06e71b801257b389dab8b667e27aca"
CHILD_SHA = "c32de1293c01bba5104eb1f123867649c71dd38e5194661ace4b17dcbbe66ba3"
CAMPAIGN_ID = hashlib.sha256(b"root-question-sensitive-terminal-rlvr-v1|composed48x4|fixed8").hexdigest()
SEED = 990731000

sys.path.insert(0, str(QS))
import qs_study as qs  # noqa: E402
sys.path.insert(0, str(WARM))
import warm_study as warm  # noqa: E402

read, write, sha, digest, aliases, load = qs.read, qs.write, qs.sha, qs.digest, qs.aliases, qs.load
check = warm.check
NATIVE, TRAIN = qs.NATIVE, qs.TRAIN
for _name in ("OLD", "OLD_MANIFEST", "PRIOR", "LOCAL", "CAMPAIGN", "RUNTIME", "PINS",
              "private", "prior_study"):
    globals()[_name] = getattr(warm, _name)


def fixed_start():
    selected = read(SELECTION)
    if selected != {
        "adapter_sha256": ROOT_START_SHA,
        "checkpoint": str(CHECKPOINT),
        "config_sha256": "5bb10e33566ed74c56438c465a8c26fd6a5bd8f41f221ab0bf28517375607a76",
        "rule": "fixed final6; no validation selection or partial substitute",
        "state_sha256": "4c2fab6360030ee446e681f76e61591ac2892aad9c509332a244a12a05ddb68a",
        "step": 6,
    }:
        raise ValueError("exact recovery SELECTION changed")
    for name, pin in {
        "adapter_model.safetensors": selected["adapter_sha256"],
        "adapter_config.json": selected["config_sha256"],
        "state.json": selected["state_sha256"],
    }.items():
        if sha(CHECKPOINT / name) != pin:
            raise ValueError("selected QS6 checkpoint changed: " + name)
    if read(CHECKPOINT / "state.json")["step"] != 6:
        raise ValueError("selected source is not SFT step6")
    return {
        "path": str(CHECKPOINT),
        "adapter_sha256": selected["adapter_sha256"],
        "config_sha256": selected["config_sha256"],
        "source_state_sha256": selected["state_sha256"],
        "state_sha256": selected["state_sha256"],
        "step": 0,
        "rl_step": 0,
        "source_sft_step": 6,
        "optimizer_sha256": None,
        "rng_sha256": None,
        "optimizer": "fresh AdamW; no SFT optimizer state loaded",
    }


def data():
    return read(ROOT / "inputs/PUBLIC.json"), read(ROOT / "inputs/HOST_GOLD.json")


def candidate_plan(window):
    if not 1 <= window <= 8:
        raise ValueError("fixed eight windows only")
    return read(ROOT / "inputs/PLANS.json")["training"][str(window)]


def endpoint_reward(reply, gold, completed, available):
    if not completed or not available or not isinstance(reply, str):
        return None
    match = re.fullmatch(r"Answer: ([0-9]+)", reply.strip())
    return int(bool(match and int(match[1]) == gold))


def runtime():
    return qs.runtime()


def verify_campaign():
    ready = read(ROOT / "CAMPAIGN.json")
    if digest({k: v for k, v in ready.items() if k != "identity"}) != ready["identity"]:
        raise ValueError("campaign identity")
    for path, pin in {**ready["source_sha256"], **ready["input_sha256"]}.items():
        if sha(path) != pin:
            raise ValueError("campaign source changed " + path)
    fixed_start()
    return ready


def verify_prepared():
    ready = read(ROOT / "READY.json")
    campaign = verify_campaign()
    if ready["campaign_identity"] != campaign["identity"] or ready["campaign_sha256"] != sha(ROOT / "CAMPAIGN.json"):
        raise ValueError("READY does not bind current campaign")
    return campaign


def final_order():
    return ("start", "rl_last")
