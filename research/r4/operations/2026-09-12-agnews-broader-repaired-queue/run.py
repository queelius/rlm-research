"""Same fixed broader RL study after CPU-qualified nested import repair."""

import hashlib
import importlib.util
from pathlib import Path

ROOT = Path(__file__).resolve().parent
SOURCE = ROOT.parent / "2026-09-12-rl-perturbation-chain/run.py"
SOURCE_SHA = "a10a6b7c6960c8e4a717c40da642389ddea8da03dc81b88d6d304457c5e68347"
if hashlib.sha256(SOURCE.read_bytes()).hexdigest() != SOURCE_SHA:
    raise ValueError("reviewed driver changed")
spec = importlib.util.spec_from_file_location("reviewed_ag_broader_repaired_queue", SOURCE)
driver = importlib.util.module_from_spec(spec)
spec.loader.exec_module(driver)
driver.ROOT = ROOT
driver.STAGES = [
    ("ag_eightstep_train_repaired", "helper-agnews-native-hf-eightstep-v1", "READY_V2.json",
     "e9dcccfdcb45a092d5ad85d4a161266f85c3f8f3cbe2f3a494aaec46edeaabb5", 5200, True),
]

if __name__ == "__main__":
    side = driver.SIDES / "helper-agnews-native-hf-eightstep-v1"
    if (side / "outputs/attempt-001").exists():
        raise ValueError("preserve existing attempt; authenticated resume only")
    driver.write_once("WRAPPER_START.json", {
        "authority": "MAIN", "wrapper_sha256": driver.sha(__file__),
        "driver_sha256": SOURCE_SHA, "started_epoch": driver.time.time(),
        "admission_sha256": driver.sha(side / "ADMISSION.json"),
        "cpu_actual_admission_sha256": driver.sha(side / "ADMISSION_V2_CPU.json"),
        "purpose": "Unchanged prospective broader8 RL/SFT study; fixed step8 endpoint, no test selection",
        "repair": "Keep exact original AG module bound throughout full pilot eligibility call",
        "preflight": "MAIN read additive owner+seal and successful actual CPU qualification; own V2 verify passed",
        "previous_launch": "operations/2026-09-12-agnews-broader-queue; failed before model loading/output creation",
        "heldout512_model_calls_before_launch": 0,
    })
    driver.main()
