"""MAIN-approved fixed first-block repetition; independent of replica outcome."""

import hashlib
import importlib.util
from pathlib import Path

ROOT = Path(__file__).resolve().parent
SOURCE = ROOT.parent / "2026-09-12-rl-perturbation-chain/run.py"
SOURCE_SHA = "a10a6b7c6960c8e4a717c40da642389ddea8da03dc81b88d6d304457c5e68347"
if hashlib.sha256(SOURCE.read_bytes()).hexdigest() != SOURCE_SHA:
    raise ValueError("reviewed driver changed")
spec = importlib.util.spec_from_file_location("repeat128_mechanism_driver", SOURCE)
driver = importlib.util.module_from_spec(spec)
spec.loader.exec_module(driver)
driver.ROOT = ROOT
SIDE = driver.SIDES / "helper-agnews-repeat-first128-eightstep-v1"
driver.STAGES = [
    ("repeat128_eightstep", SIDE.name, "READY.json",
     "1ebe94d3339e1e742c4f984ffa3f00f9cb9813e239747b7a390f70c70e5b7119", 5200, True),
]

if __name__ == "__main__":
    if (SIDE / "outputs/attempt-001").exists():
        raise ValueError("preserve existing repeated-data attempt")
    driver.write_once("MAIN_START.json", {
        "authority": "MAIN", "started_epoch": driver.time.time(),
        "wrapper_sha256": driver.sha(__file__), "driver_sha256": SOURCE_SHA,
        "admission_sha256": driver.sha(SIDE / "ADMISSION.json"),
        "question": "Does the original broader-data gain require distinct examples, beyond repeated updates?",
        "unique_articles": 128, "planned_optimizer_updates": 8,
        "owner_seconds": 5000, "external_seconds": 5200,
        "checkpoint": "Every qualified adapter, full Adam, RNG and parent-linked update",
        "claim_boundary": "Paired seed1 randomization; first fixed block only; no early-stop endpoint rescue or inference beyond exposed512",
    })
    driver.main()
