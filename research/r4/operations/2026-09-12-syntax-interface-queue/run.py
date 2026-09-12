"""MAIN-reviewed syntax-only interface comparison under the shared GPU lock."""

import hashlib
import importlib.util
from pathlib import Path

ROOT = Path(__file__).resolve().parent
SOURCE = ROOT.parent / "2026-09-12-rl-perturbation-chain/run.py"
if hashlib.sha256(SOURCE.read_bytes()).hexdigest() != "a10a6b7c6960c8e4a717c40da642389ddea8da03dc81b88d6d304457c5e68347":
    raise ValueError("reviewed driver changed")
spec = importlib.util.spec_from_file_location("syntax_interface_driver", SOURCE)
driver = importlib.util.module_from_spec(spec)
spec.loader.exec_module(driver)
driver.ROOT = ROOT
SIDE = driver.SIDES / "root-qs6-budgeted-evidence-syntax-v1"
driver.STAGES = [
    ("syntax48", SIDE.name, "READY.json",
     "c2af923cd014642eea1884861570f25a54f245bae99df02e44a0d66fe92ee960", 1100, True),
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
        raise ValueError("preserve existing syntax attempt")
    driver.write_once("ADMISSION.json", {
        "authority": "MAIN", "decision": "APPROVE_SYNTAX_ONLY_INTERFACE_SCREEN",
        "epoch": driver.time.time(), "wrapper_sha256": driver.sha(__file__),
        "question": "Does one syntax-only example improve reliable use of classify/finish?",
        "review": "Full new source, fixed prompt, two actual collector fixtures, inherited accepted V2 source and boundary reviewed; own source closure verify passed.",
        "episodes": 48, "paired_tasks": 24, "physical_child_calls": 0,
        "primary": ["finish-consistent strict finals", "rejected API actions"],
        "secondary": ["correct/wrong/unknown", "logical acquired IDs", "root calls/tokens"],
        "caps": {"owner_seconds": 1000, "external_seconds": 1100, "arm_seconds": 420},
        "limits": "Two familiar contexts; saved helper predictions. Interface screen only, not new-data transfer, helper cost reduction, or architecture promotion.",
        "decision": "If syntax improves protocol use, inspect remaining errors before ledger/depth variants. No repeat of unchanged failing interface.",
    })
    driver.main()
