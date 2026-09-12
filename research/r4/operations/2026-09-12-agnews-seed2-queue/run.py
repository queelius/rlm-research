"""Prespecified fresh-seed replication, followed by its exact endpoint readout."""

import hashlib
import importlib.util
from pathlib import Path

ROOT = Path(__file__).resolve().parent
SOURCE = ROOT.parent / "2026-09-12-rl-perturbation-chain/run.py"
SOURCE_SHA = "a10a6b7c6960c8e4a717c40da642389ddea8da03dc81b88d6d304457c5e68347"
if hashlib.sha256(SOURCE.read_bytes()).hexdigest() != SOURCE_SHA:
    raise ValueError("reviewed driver changed")
spec = importlib.util.spec_from_file_location("reviewed_ag_seed2_queue", SOURCE)
driver = importlib.util.module_from_spec(spec)
spec.loader.exec_module(driver)
driver.ROOT = ROOT
driver.STAGES = [
    ("ag_seed2_train", "helper-agnews-native-hf-onestep-seed2-v1", "READY.json",
     "22e1eb0408b855d79d5dac768f4aac93f810263512363d5f918492cc037b7bdf", 1200, True),
    ("ag_seed2_eval", "helper-agnews-native-hf-onestep-seed2-v1", "EVAL_READY.json",
     "a263853837cd00e12d047192b5bcb1a5bb6e5177760badda7423744d17fafca1", 700, True),
]

if __name__ == "__main__":
    side = driver.SIDES / "helper-agnews-native-hf-onestep-seed2-v1"
    for name in ("outputs/attempt-001", "eval/outputs/attempt-001"):
        if (side / name).exists():
            raise ValueError("preserve existing output: " + name)
    driver.write_once("WRAPPER_START.json", {
        "wrapper_sha256": driver.sha(__file__), "driver_sha256": SOURCE_SHA,
        "started_epoch": driver.time.time(),
        "purpose": "Replicate one-win AG result with new training-sampling seeds",
        "same_data": "128 articles, 32 four-item prompts, four responses each",
        "starting_weights": "fresh c32, fresh Adam; not continued seed1 checkpoint",
        "evaluation": "fixed AG256; reuse qualified c32 only after runtime comparison",
        "preflight": "MAIN reviewed source diff, seed-only schedule fixture, exact closures",
    })
    driver.main()
