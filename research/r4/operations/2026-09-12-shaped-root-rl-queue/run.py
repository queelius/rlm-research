"""MAIN-reviewed saved-trajectory root-RL dose probe; external flock required."""

import hashlib
import importlib.util
from pathlib import Path

ROOT = Path(__file__).resolve().parent
SOURCE = ROOT.parent / "2026-09-12-rl-perturbation-chain/run.py"
if hashlib.sha256(SOURCE.read_bytes()).hexdigest() != "a10a6b7c6960c8e4a717c40da642389ddea8da03dc81b88d6d304457c5e68347":
    raise ValueError("reviewed driver changed")
spec = importlib.util.spec_from_file_location("shaped_root_rl_driver", SOURCE)
driver = importlib.util.module_from_spec(spec)
spec.loader.exec_module(driver)
driver.ROOT = ROOT
SIDE = driver.SIDES / "openai-mrcr-short-root-shaped-rl-v1"
driver.STAGES = [
    ("shaped_root_rl_step1", SIDE.name, "RUN_READY.json",
     "0ff060b68b78753b3d44c7acc239955efb3b6c77f5c202cb16d5e59c06c8e1e5", 1000, False),
]

if __name__ == "__main__":
    if (SIDE / "outputs/attempt-001").exists():
        raise ValueError("preserve existing shaped-root training output")
    driver.write_once("ADMISSION.json", {
        "authority": "MAIN", "decision": "APPROVE_ONE_SAVED_BATCH_ROOT_RL_UPDATE",
        "epoch": driver.time.time(), "wrapper_sha256": driver.sha(__file__),
        "review": "Full new input extractor/facade/tests/seal and original HF trainer/math read; actual24-episode CPU mapping and streamed-gradient test read; own248-pin actual trainer input verification passed.",
        "question": "Can a root-only update use correct-retrieval near-success rather than arbitrary wrong-passage overlap?",
        "reward": "0.5*I(raw official similarity>=0.90)+0.5*I(raw exact)",
        "episodes": 24, "complete_groups": 6, "mixed_groups": 2,
        "excluded": "Two whole G4 groups contain unavailable trajectories; retain exclusions and do not zero-fill. All complete groups stay in denominator24.",
        "training": "One fixed LR1e-5 rank8 AdamW step on authentic saved root actions, fixed base child; full-trajectory unclipped IS, finite-support/ESS/replay gates; adapter/Adam/RNG checkpoint.",
        "owner_seconds": 900, "external_seconds": 1000,
        "evaluation": "Separate conditional fixed base-vs-step1 held16x1 comparison is being CPU-prepared; no other checkpoint selection.",
        "interpretation": "A weak endpoint is not evidence the entire reward direction fails. Distinguish small update, poor procedure, and bad reward; this has zero child training and makes no recursion-learning claim.",
        "diagnostics_limit": "Current trainer measures prestep HF/native likelihood discrepancy, replay, gradient and adapter change; postupdate likelihood shift is not yet measured.",
    })
    driver.main()
