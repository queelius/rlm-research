"""MAIN-reviewed frozen-root live-helper transfer; requires external shared flock."""

import hashlib
import importlib.util
from pathlib import Path

ROOT = Path(__file__).resolve().parent
SOURCE = ROOT.parent / "2026-09-12-rl-perturbation-chain/run.py"
if hashlib.sha256(SOURCE.read_bytes()).hexdigest() != "a10a6b7c6960c8e4a717c40da642389ddea8da03dc81b88d6d304457c5e68347":
    raise ValueError("reviewed driver changed")
spec = importlib.util.spec_from_file_location("whole_rlm_transfer_driver", SOURCE)
driver = importlib.util.module_from_spec(spec)
spec.loader.exec_module(driver)
driver.ROOT = ROOT
SIDE = driver.SIDES / "root-qs6-ag-live-helper-transfer-v1"
driver.STAGES = [
    ("whole_rlm48", SIDE.name, "READY.json",
     "f99deb3e8813641b7d02e283a98a98f5a7d4dfc4944b7f7c0edb829c5dfb47c1", 1900, True),
]
original_read = driver.read


def read(path):
    value = original_read(path)
    if Path(path) == SIDE / "READY.json":
        value = {**value, "command": value["argv"]}
    return value


driver.read = read

if __name__ == "__main__":
    if (SIDE / "outputs/attempt-001").exists():
        raise ValueError("preserve prior live-helper attempt")
    driver.write_once("ADMISSION.json", {
        "authority": "MAIN", "decision": "APPROVE_FROZEN_ROOT_LIVE_HELPER_TRANSFER",
        "epoch": driver.time.time(), "wrapper_sha256": driver.sha(__file__),
        "question": "Does the fixed RL-trained helper improve final answers under an unchanged root on fresh news contexts?",
        "review": "All new source/PLAN/RUNBOOK and actual three-case container/physical-map receipts read; own871-pin owner verify passed.",
        "arms": ["no-child/Python RLM control", "fixed QS6 root plus c32 helper", "fixed QS6 root plus original RL8 helper"],
        "contexts": 8, "queries_per_context": 2, "episodes": 48,
        "caps": {"owner_seconds": 1800, "external_seconds": 1900, "physical_calls": 416},
        "primary": "16 paired final-answer outcomes RL8 versus c32, clustered in8 contexts",
        "diagnostics": ["actual local label accuracy", "root agreement with helper-implied aggregate", "unknown outcomes", "all physical root/helper calls and costs"],
        "limits": "Familiar operators on fresh articles; prescribed B4 acquisition, not learned grouping/depth. Two service phases and different cache histories. No-child control is not strongest conventional direct baseline. No seed/checkpoint selection.",
        "followup": "Promising final gains across contexts justify fresh-context replication. Better maps without better final answers motivate root aggregation diagnostics, not a helper failure claim.",
    })
    driver.main()
