"""MAIN admission of exact engine ownership repair; external shared flock required."""

import hashlib
import importlib.util
from pathlib import Path

ROOT = Path(__file__).resolve().parent
SOURCE = ROOT.parent / "2026-09-12-rl-perturbation-chain/run.py"
assert hashlib.sha256(SOURCE.read_bytes()).hexdigest() == "a10a6b7c6960c8e4a717c40da642389ddea8da03dc81b88d6d304457c5e68347"
spec = importlib.util.spec_from_file_location("musique_exact_owner_driver", SOURCE)
driver = importlib.util.module_from_spec(spec)
spec.loader.exec_module(driver)
driver.ROOT = ROOT
SIDE = driver.SIDES / "musique-task-directed-followup-v1"
driver.STAGES = [("report132_v3", SIDE.name, "READY_V3.json",
                  "c799becad8d574d6785dbd4292e00b6bb27536175adb8b6b71f1df4c469dd1c1", 1800, True)]


if __name__ == "__main__":
    assert not (SIDE / "outputs/attempt-003").exists()
    driver.write_once("ADMISSION.json", {
        "authority": "MAIN", "epoch": driver.time.time(),
        "decision": "ADMIT_UNCHANGED_SCIENCE_EXACT_ENGINE_OWNERSHIP_REPAIR",
        "wrapper_sha256": driver.sha(__file__),
        "review": "MAIN read all V3 runtime changes and actual start/claim/release test; own 1592-pin verify passed identity 11e50d7a751b42b7f877c8faa51798c8f3d0650214b759b843439772e98b73f3.",
        "question": "Do task-specific follow-up requests outperform equally long broad reports, sharing the same first helper reports?",
        "inputs": "12 fixed new training-split MuSiQue questions; four arms; 132 physical calls and 48 final slots; no checkpoint or answer selection.",
        "seed_schedule": "202609180000 + 32*question_index + fixed offset; unchanged sealed schedule",
        "metric": "Fixed raw final-answer and support-index grading; paired 12 question units; missing recorded separately.",
        "science_seconds": 1320, "owner_seconds": 1700, "external_seconds": 1800,
        "checkpoint_policy": "Immutable per-call native requests/responses and outcomes; no model-answer retries.",
        "prior_failure": "Attempt002 made zero scientific queries. MAIN authenticated and terminated its detached group577193; cleanup receipt preserved and all exited.",
        "claim_boundary": "Fixed graph and partition; this tests information requests, not learned recursive routing.",
    })
    driver.main()
    terminal = driver.read(SIDE / "outputs/attempt-003/OWNER_TERMINAL.json")
    if not terminal.get("released"):
        raise RuntimeError("Owner did not authenticate release; inspect saved owned identities before another launch")
    driver.write_once("RELEASE_CONFIRMED.json", {"epoch": driver.time.time(), "released": True,
                                              "owner_terminal_sha256": driver.sha(SIDE / "outputs/attempt-003/OWNER_TERMINAL.json")})
