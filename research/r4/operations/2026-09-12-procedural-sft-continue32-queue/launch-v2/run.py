"""Map the trainer's sealed fixed_argv onto the existing launcher command field."""

import hashlib
import importlib.util
from pathlib import Path

ROOT = Path(__file__).resolve().parent
SOURCE = ROOT.parents[1] / "2026-09-12-rl-perturbation-chain/run.py"
if hashlib.sha256(SOURCE.read_bytes()).hexdigest() != "a10a6b7c6960c8e4a717c40da642389ddea8da03dc81b88d6d304457c5e68347":
    raise ValueError("reviewed driver changed")
spec = importlib.util.spec_from_file_location("continue32_fixed_argv_driver", SOURCE)
driver = importlib.util.module_from_spec(spec)
spec.loader.exec_module(driver)
driver.ROOT = ROOT
SIDE = driver.SIDES / "openai-mrcr-procedural-sft-continue32-v1"
READY = SIDE / "READY_TRAINING.json"
original_read = driver.read


def read_with_command(path):
    value = original_read(path)
    if Path(path) == READY:
        assert "command" not in value
        value = {**value, "command": value["fixed_argv"]}
    return value


driver.read = read_with_command
driver.STAGES = [("continue32", SIDE.name, READY.name,
                  "d482834e4584db70fb8f405440ac146af427bb4f4174018a0a1f0b9fa459f1be", 1600, False)]

if __name__ == "__main__":
    assert not (SIDE / "outputs/attempt-001").exists()
    driver.write_once("ADMISSION.json", {
        "authority": "MAIN", "epoch": driver.time.time(),
        "decision": "REPAIR_LAUNCHER_FIELD_ONLY_SAME_ADMITTED_TRAINING",
        "prior_admission": str(ROOT.parent / "ADMISSION.json"),
        "prior_zero_training_calls": True,
        "repair": "Common driver expects command, while authenticated trainer READY uses fixed_argv; map exactly that field in memory without editing any sealed file.",
        "wrapper_sha256": driver.sha(__file__), "checkpoint_selection": False,
    })
    driver.main()
