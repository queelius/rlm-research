"""Isolated SFT24/fresh-RL namespace over the qualified QSR machinery."""
import hashlib
import importlib.util
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parent
SIDE = ROOT.parent
QSR = SIDE / "root-query-sensitive-rl-v1"
DOSE = SIDE / "root-operator-dose-continuation-v1"
COMPOSITION = SIDE / "root-operator-composition-transfer-v1"
ATTEMPT = ROOT / "outputs/attempt-001"
NATIVE = base.NATIVE if "base" in globals() else Path("/project/alex_phd/envs/prime-rl-5990b1b/bin/python")
SFT24 = DOSE / "outputs/attempt-001/training/checkpoint-0024"
CHILD_SHA = "c32de1293c01bba5104eb1f123867649c71dd38e5194661ace4b17dcbbe66ba3"
CAMPAIGN_ID = hashlib.sha256(b"root-sft24-terminal-rlvr-v1|fixed8|fresh-adam0").hexdigest()
SEED = 981731001


def _load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


base = _load("warm_qualified_qsr_study", QSR / "qsr_study.py")
NATIVE, TRAIN = base.NATIVE, base.TRAIN
read, write, sha, digest, check, aliases, load = (
    base.read, base.write, base.sha, base.digest, base.check, base.aliases, base.load)
for _name in ("OLD", "OLD_MANIFEST", "PRIOR", "LOCAL", "CAMPAIGN", "RUNTIME", "PINS",
              "private", "prior_study"):
    globals()[_name] = getattr(base, _name)


def fixed_start():
    pins = {
        "adapter_model.safetensors": "94022838a64a530e1abc8daf6cd43502d8aec7d549b6bfec10dd4928b0ca9006",
        "adapter_config.json": "9cab91502118f13b1a7d41118182a563285b23d2b1a77c8bd6e153ca38fe20bd",
        "state.json": "75b3138884cf526503bba311dae932158b7305a4958b478f73d286ad3a755171",
    }
    for name, pin in pins.items():
        check(SFT24 / name, pin)
    if read(SFT24 / "state.json")["step"] != 24:
        raise ValueError("exact source SFT step24 required")
    return {
        "path": str(SFT24), "adapter_sha256": pins["adapter_model.safetensors"],
        "config_sha256": pins["adapter_config.json"], "source_state_sha256": pins["state.json"],
        "state_sha256": pins["state.json"],
        "step": 0, "rl_step": 0, "source_sft_step": 24,
        "optimizer_sha256": None, "rng_sha256": None,
        "optimizer": "fresh AdamW; no SFT optimizer state loaded",
    }


def data():
    return read(ROOT / "inputs/PUBLIC.json"), read(ROOT / "inputs/HOST_GOLD.json")


def candidate_plan(window):
    if not 1 <= window <= 8:
        raise ValueError("fixed eight windows only")
    return read(ROOT / "inputs/PLANS.json")["training"][str(window)]


def endpoint_reward(reply, gold, completed, available):
    import re
    if not completed or not available or not isinstance(reply, str):
        return None
    match = re.fullmatch(r"Answer: ([0-9]+)", reply.strip())
    return int(bool(match and int(match[1]) == gold))


def runtime():
    return base.runtime()


def verify_prepared():
    campaign = read(ROOT / "CAMPAIGN.json")
    if campaign["campaign_id"] != CAMPAIGN_ID:
        raise ValueError("campaign identity")
    for path, pin in {**campaign["source_sha256"], **campaign["input_sha256"]}.items():
        check(path, pin)
    fixed_start()
    return campaign


def final_order():
    return ("unchanged", "trained")
