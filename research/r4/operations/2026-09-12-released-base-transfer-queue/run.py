"""MAIN-reviewed original-model reference; external shared GPU flock required."""

import hashlib
import importlib.util
from pathlib import Path

ROOT = Path(__file__).resolve().parent
SOURCE = ROOT.parent / "2026-09-12-rl-perturbation-chain/run.py"
if hashlib.sha256(SOURCE.read_bytes()).hexdigest() != "a10a6b7c6960c8e4a717c40da642389ddea8da03dc81b88d6d304457c5e68347":
    raise ValueError("reviewed driver changed")
spec = importlib.util.spec_from_file_location("released_base_transfer_driver", SOURCE)
driver = importlib.util.module_from_spec(spec)
spec.loader.exec_module(driver)
driver.ROOT = ROOT
SIDE = driver.SIDES / "helper-base4b-ag512-dbpedia224-eval-v1"
driver.STAGES = [
    ("base_two_panels", SIDE.name, "READY.json",
     "81075bceabca9224bfe14aa9cbeea2742cb3daa10ab1e4abb91b63f675b48742", 1000, True),
]

if __name__ == "__main__":
    if (SIDE / "outputs/attempt-001").exists():
        raise ValueError("preserve existing base-control output")
    driver.write_once("ADMISSION.json", {
        "authority": "MAIN", "decision": "APPROVE_RELEASED_BASE_ADDITIVE_REFERENCE",
        "epoch": driver.time.time(), "wrapper_sha256": driver.sha(__file__),
        "review": "All957lines of new source, design/runbook and actual4test CPUreceipt read; own closure verification passed before queueing.",
        "question": "Do the learned helper gains exceed the original model, or recover a cost of prior specialization?",
        "panels": {"official_AG_test": 512, "DBpedia_test": 224},
        "fixed_calls": 184, "temperature": 0, "batch": 4,
        "owner_seconds": 900, "external_seconds": 1000,
        "claim_boundary": "Original released base has no LoRA and no prefix caching. Exact prompts, request settings and paired seeds otherwise match frozen panels; runtime is not a bitwise or matched-cost comparison.",
        "selection": "This supplements all four previously fixed trained endpoints and replaces none. No original-model query on either new panel preceded this decision.",
        "followup": "Retain raw predictions, each dataset separately, paired wins/losses and class-specific differences; do not pool distinct tasks or report only a winning arm.",
    })
    driver.main()
