"""MAIN-approved evidence-selection interface screen after the existing owners."""

import hashlib
import importlib.util
from pathlib import Path

ROOT = Path(__file__).resolve().parent
SOURCE = ROOT.parent / "2026-09-12-rl-perturbation-chain/run.py"
SOURCE_SHA = "a10a6b7c6960c8e4a717c40da642389ddea8da03dc81b88d6d304457c5e68347"
if hashlib.sha256(SOURCE.read_bytes()).hexdigest() != SOURCE_SHA:
    raise ValueError("reviewed driver changed")
spec = importlib.util.spec_from_file_location("budgeted_evidence_queue_driver", SOURCE)
driver = importlib.util.module_from_spec(spec)
spec.loader.exec_module(driver)
driver.ROOT = ROOT
driver.STAGES = [
    ("budgeted_evidence", "root-qs6-budgeted-evidence-stop-v1", "READY.json",
     "27f4676a7e245459df2d24d62975e189060fd56a971a142281e2e6f227883360", 1130, True),
]
SIDE = driver.SIDES / "root-qs6-budgeted-evidence-stop-v1"
original_read = driver.read


def read(path):
    value = original_read(path)
    if Path(path) == SIDE / "READY.json":
        value = {**value, "command": value["argv"]}
    return value


driver.read = read

if __name__ == "__main__":
    if (SIDE / "outputs/attempt-001").exists():
        raise ValueError("preserve existing attempt001")
    driver.write_once("ADMISSION.json", {
        "authority": "MAIN", "decision": "APPROVE_PAIRED_INTERFACE_SCREEN",
        "started_epoch": driver.time.time(), "wrapper_sha256": driver.sha(__file__),
        "driver_sha256": SOURCE_SHA,
        "review": "MAIN read complete protocol, study, collector, owner, preparation and tests; own closure verify passed. Both actual container/fake-provider paths passed in CPU receipt.",
        "science": "48 paired root episodes, two familiar contexts, fixed authentic helper maps; arbitrary subset versus all16 classification interface, zero optimizer updates",
        "caps": {"owner_seconds": 1000, "owner_outer_argument": 1100, "external_seconds": 1130},
        "limits": "Logical evidence requests are not measured child compute savings. Direct-access flags disqualify faithfulness/savings promotion; unflagged is not proof of sandboxing. Missing finalization is not zero evidence cost.",
    })
    driver.main()
