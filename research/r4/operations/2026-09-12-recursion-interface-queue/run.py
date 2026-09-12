"""MAIN-reviewed twelve-episode interface qualifier; no optimizer or fallback."""

import hashlib
import importlib.util
from pathlib import Path

ROOT = Path(__file__).resolve().parent
SOURCE = ROOT.parent / "2026-09-12-rl-perturbation-chain/run.py"
SOURCE_SHA = "a10a6b7c6960c8e4a717c40da642389ddea8da03dc81b88d6d304457c5e68347"
if hashlib.sha256(SOURCE.read_bytes()).hexdigest() != SOURCE_SHA:
    raise ValueError("reviewed driver changed")
spec = importlib.util.spec_from_file_location("reviewed_root_interface_queue", SOURCE)
driver = importlib.util.module_from_spec(spec)
spec.loader.exec_module(driver)
driver.ROOT = ROOT
driver.STAGES = [
    ("root_interface_qualifier", "root-qs6-recursion-interface-qualifier-v1", "READY.json",
     "e8fc4a74a3fe871bd132331126a706afe1bebc1bdd823a538a24a35f9fb0acca", 700, True),
]
RECEIPT = driver.SIDES / "root-qs6-recursion-interface-qualifier-v1/READY.json"
OUTPUT = driver.SIDES / "root-qs6-recursion-interface-qualifier-v1/outputs/attempt-001"
original_read = driver.read


def read(path):
    result = original_read(path)
    if Path(path) == RECEIPT:
        # Translate the receipt's command field for the unchanged queue driver.
        result = {**result, "command": result["fixed_argv"]}
    return result


driver.read = read

if __name__ == "__main__":
    if OUTPUT.exists():
        raise ValueError("preserve existing output: " + str(OUTPUT))
    driver.write_once("WRAPPER_START.json", {
        "wrapper_sha256": driver.sha(__file__), "driver_sha256": SOURCE_SHA,
        "started_epoch": driver.time.time(),
        "inventory": "six exposed contexts/families x two modes, one repeat; no-child then enabled",
        "command_translation": "fixed_argv copied exactly to driver command; READY bytes unchanged",
        "owned_seconds": 600, "external_seconds": 700,
        "request_trigger": 250, "trigger_is_not_hard_cap": True,
        "science_gate_separate_from_operational_completion": True,
    })
    driver.main()
