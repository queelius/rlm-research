"""Fixed broader-data RL endpoint; no pilot-positive or heldout-based escalation."""

import hashlib
import importlib.util
from pathlib import Path

ROOT = Path(__file__).resolve().parent
SOURCE = ROOT.parent / "2026-09-12-rl-perturbation-chain/run.py"
SOURCE_SHA = "a10a6b7c6960c8e4a717c40da642389ddea8da03dc81b88d6d304457c5e68347"
if hashlib.sha256(SOURCE.read_bytes()).hexdigest() != SOURCE_SHA:
    raise ValueError("reviewed driver changed")
spec = importlib.util.spec_from_file_location("reviewed_ag_broader_queue", SOURCE)
driver = importlib.util.module_from_spec(spec)
spec.loader.exec_module(driver)
driver.ROOT = ROOT
driver.STAGES = [
    ("ag_eightstep_train", "helper-agnews-native-hf-eightstep-v1", "READY.json",
     "053b0c06c9124d9c3d8f9a1210bc91319a3d316afea751fe0f8ad2e6a42e970b", 5200, True),
]

if __name__ == "__main__":
    side = driver.SIDES / "helper-agnews-native-hf-eightstep-v1"
    if (side / "outputs/attempt-001").exists():
        raise ValueError("preserve previous run; explicit authenticated resume only")
    driver.write_once("WRAPPER_START.json", {
        "wrapper_sha256": driver.sha(__file__), "driver_sha256": SOURCE_SHA,
        "started_epoch": driver.time.time(),
        "admission_sha256": driver.sha(side / "ADMISSION.json"),
        "purpose": "Eight fresh training blocks, persistent Adam; compare fixed cp8 with c32 and separately prepared SFT on fresh512",
        "decision": "Seed2 null retires one-win pilot signal; broader study was independently frozen before seed2",
        "heldout512_model_calls_before_launch": 0,
        "preflight": "MAIN reviewed actual continuation/replay/parent-binding sources and focused fixtures; exact538-pin owner verify passed",
    })
    driver.main()
