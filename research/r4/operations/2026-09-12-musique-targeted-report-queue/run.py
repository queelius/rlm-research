"""MAIN-admitted fixed report-channel comparison; external shared GPU flock required."""

import hashlib
import importlib.util
from pathlib import Path

ROOT = Path(__file__).resolve().parent
SOURCE = ROOT.parent / "2026-09-12-rl-perturbation-chain/run.py"
if hashlib.sha256(SOURCE.read_bytes()).hexdigest() != "a10a6b7c6960c8e4a717c40da642389ddea8da03dc81b88d6d304457c5e68347":
    raise ValueError("reviewed driver changed")
spec = importlib.util.spec_from_file_location("musique_targeted_report_driver", SOURCE)
driver = importlib.util.module_from_spec(spec)
spec.loader.exec_module(driver)
driver.ROOT = ROOT
SIDE = driver.SIDES / "musique-task-directed-followup-v1"
driver.STAGES = [
    ("report132", SIDE.name, "READY.json",
     "3fbee4fcd369fa439c3b1f1b1a463a407624bcdd4fd29653989714c2db897832", 1800, True),
]

if __name__ == "__main__":
    if (SIDE / "outputs/attempt-001").exists():
        raise ValueError("preserve existing report-channel output")
    driver.write_once("ADMISSION.json", {
        "authority": "MAIN", "epoch": driver.time.time(),
        "decision": "APPROVE_FIXED_REPORT_CHANNEL_EXPLORATORY_SCREEN",
        "wrapper_sha256": driver.sha(__file__),
        "question": "Does asking a focused follow-up recover more useful information than asking for more information generally?",
        "reason": "The completed depth-permission pilot never called helpers; separate information targeting from Python access and voluntary delegation.",
        "review": "MAIN read all nine new Python files, PLAN/RUNBOOK, actual graph and service fixture; own owner verify passed all1555 source/input pins.",
        "conditions": ["shared first reports then stop", "broad additional reports", "targeted additional reports", "all original source text"],
        "paired_questions": 12, "physical_calls": 132, "terminal_slots": 48,
        "owner_seconds": 1700, "external_seconds": 1800,
        "seed_policy": "Frozen per-question and role seeds; broad/targeted helper seeds and final seeds paired.",
        "checkpoint_policy": "Every physical start, native request/response and derived outcome persisted; no retry or result-selected continuation.",
        "claim_boundary": "Fixed partition and call graph, not learned routing, autonomous depth, architecture novelty, or long-context necessity. Four-question concurrency means call-time sums are not elapsed time.",
    })
    driver.main()
