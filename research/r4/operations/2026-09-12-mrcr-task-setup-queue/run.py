"""Canonical MRCR task setup repair; unchanged32 questions and policies."""

import hashlib
import importlib.util
from pathlib import Path

ROOT = Path(__file__).resolve().parent
SOURCE = ROOT.parent / "2026-09-12-rl-perturbation-chain/run.py"
SOURCE_SHA = "a10a6b7c6960c8e4a717c40da642389ddea8da03dc81b88d6d304457c5e68347"
if hashlib.sha256(SOURCE.read_bytes()).hexdigest() != SOURCE_SHA:
    raise ValueError("reviewed driver changed")
spec = importlib.util.spec_from_file_location("reviewed_mrcr_task_setup_queue", SOURCE)
driver = importlib.util.module_from_spec(spec)
spec.loader.exec_module(driver)
driver.ROOT = ROOT
driver.STAGES = [
    ("mrcr_task_setup_repair", "mrcr-v3-root-procedure-calibration-v1", "READY_V5.json",
     "8562394d48d316aa2bfdbd378e8a9cbdf89709388775f3e8afbebae464635795", 1000, True),
]
SIDE = driver.SIDES / "mrcr-v3-root-procedure-calibration-v1"
RECEIPT = SIDE / "READY_V5.json"
original_read = driver.read


def read(path):
    result = original_read(path)
    if Path(path) == RECEIPT:
        for name in ("READY.json", "READY_V2.json", "READY_V3.json", "READY_V4.json"):
            driver.verify_closure(original_read(SIDE / name))
        result = {**result, "command": result["fixed_argv"]}
    return result


driver.read = read

if __name__ == "__main__":
    if (SIDE / "outputs/attempt-005").exists():
        raise ValueError("preserve existing attempt005")
    driver.write_once("ADMISSION.json", {
        "authority": "MAIN", "decision": "APPROVE_CANONICAL_TASK_SETUP_REPAIR",
        "wrapper_sha256": driver.sha(__file__), "driver_sha256": SOURCE_SHA,
        "started_epoch": driver.time.time(), "owner_seconds": 900, "external_seconds": 1000,
        "delta": "Patch actual registry-instantiated task class instead of unused alias class",
        "preflight": "MAIN read all V5 sources/fixtures, own verify passed; actual task.setup(None,runtime) plus in-container frozen full-query read passed CPU allocation smoke",
        "science": "Same32 tasks/seeds/model/prompt/score/gate as V3/V4; zero optimizer steps, one underlying context",
        "claim_boundary": "V3/V4 had zero model calls; no model or learning conclusion from them",
    })
    driver.main()
