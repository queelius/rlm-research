"""MAIN-approved same-data SFT control, fixed checkpoint8 only."""

import hashlib
import importlib.util
from pathlib import Path

ROOT = Path(__file__).resolve().parent
SOURCE = ROOT.parent / "2026-09-12-rl-perturbation-chain/run.py"
SOURCE_SHA = "a10a6b7c6960c8e4a717c40da642389ddea8da03dc81b88d6d304457c5e68347"
if hashlib.sha256(SOURCE.read_bytes()).hexdigest() != SOURCE_SHA:
    raise ValueError("reviewed driver changed")
spec = importlib.util.spec_from_file_location("reviewed_ag_sft_broader_queue", SOURCE)
driver = importlib.util.module_from_spec(spec)
spec.loader.exec_module(driver)
driver.ROOT = ROOT
driver.STAGES = [
    ("ag_sft_eightstep", "helper-agnews-sft-eightstep-v1", "READY_V2.json",
     "088f4b7e366582365f62d226fac9e3677957e0f32c54e534f5d000ea3bce9753", 1000, False),
]

if __name__ == "__main__":
    side = driver.SIDES / "helper-agnews-sft-eightstep-v1"
    if (side / "outputs/attempt-001").exists():
        raise ValueError("preserve previous SFT attempt")
    driver.write_once("ADMISSION.json", {
        "authority": "MAIN", "decision": "APPROVE_FIXED_EIGHTSTEP_SFT",
        "ready_sha256": driver.sha(side / "READY_V2.json"),
        "created_epoch": driver.time.time(),
        "wrapper_sha256": driver.sha(__file__), "driver_sha256": SOURCE_SHA,
        "reason": "Frozen broader1024 data-signal control after one-step RL gain failed seed replication; fixed cp8 versus c32 and RL8 on separate fresh512. Launch first while RL nested import is repaired.",
        "preflight": "MAIN read V1/V2 actual trainer, masking, optimizer, owner, endpoint and focused fixtures; verify passed; V2 trainer byte-identical to V1 and label diagnostic only changes",
        "limits": "Same articles/groups/eight Adam updates, not same objective, sampled answers, token count or answer support; 1536/20591 target tokens overlap label content",
        "checkpoint_policy": "save adapter/Adam/RNG/metrics and commit every update; no intermediate test selection",
        "heldout512_model_calls_before_launch": 0,
    })
    driver.main()
