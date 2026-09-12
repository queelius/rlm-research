"""One MAIN-approved fixed-checkpoint return-path ablation; external flock required."""

import hashlib
import importlib.util
import os
from pathlib import Path
import subprocess
import time

ROOT = Path(__file__).resolve().parent
SOURCE = ROOT.parent / "2026-09-12-rl-perturbation-chain/run.py"
assert hashlib.sha256(SOURCE.read_bytes()).hexdigest() == "a10a6b7c6960c8e4a717c40da642389ddea8da03dc81b88d6d304457c5e68347"
spec = importlib.util.spec_from_file_location("terminal_strip_queue_helpers", SOURCE)
driver = importlib.util.module_from_spec(spec)
spec.loader.exec_module(driver)
driver.ROOT = ROOT
SIDE = driver.SIDES / "openai-mrcr-procedural-sft-terminal-strip-disabled-v1"
READY = SIDE / "CPU_READY.json"
EXPECTED = "686e484b6ffa0338b6b699537b10e4ea84f436a29d76baa0ec704f895a629d91"
REVIEW = driver.STORE / "analyses/openai-mrcr-procedural-sft-dose32-independent-review-2026-09-12/TERMINAL_HOOK_REVIEW.json"


def execute():
    assert driver.sha(READY) == EXPECTED
    assert driver.sha(REVIEW) == "7240ffed617605d3b49c2889fb074bd221b654ef12187c473cdf7d9e08244ac7"
    ready = driver.read(READY)
    driver.verify_closure(ready)
    assert ready["caps"] == {"science": 600, "owner": 900, "external": 1000}
    assert not (SIDE / "outputs/held-checkpoint32-001").exists()
    driver.empty_gpu()
    driver.write_once("ADMISSION.json", {
        "authority": "MAIN", "epoch": time.time(), "ready_sha256": EXPECTED,
        "ready_identity": ready["identity"], "wrapper_sha256": driver.sha(__file__),
        "review_sha256": driver.sha(REVIEW),
        "review": "MAIN read all seven source/test files and RUNBOOK; actual owner verified324 source pins/currentcp32. Independent review passed all66 archived parser actions and full-native fixture receipts. Six focused regressions passed before sealing.",
        "question": "Does disabling two terminal whitespace clamps preserve exact model outputs through unchanged grading?",
        "condition": "terminal-strip-disabled", "contexts": 16, "episodes": 32,
        "seed_range": [2026091700, 2026091731], "fixed_checkpoint": 32, "optimizer_steps": 0,
        "metric": "Original exact string equality on returned root; compare all actual token paths before attributing changes to trimming.",
        "limits": "Same exposed heldpanel, two seeds/context; not general lossless parsing. Reasoning newline and tool parsing unchanged. Old17score unchanged; no automatic25 forecast.",
        "checkpoint_policy": "Every native call/episode/contract saved, unknowns retained, no retry or gold-dependent repair.",
    })
    env = {**os.environ, "CUDA_VISIBLE_DEVICES": driver.GPU, "OMP_NUM_THREADS": "4",
           "PYTHONDONTWRITEBYTECODE": "1"}
    private = driver.read(driver.SIDES / "leaf-output-cue-order-v1/owned/attempt-001/service/inference.json")
    env["STRICT_RLM_CALIBRATION_API_KEY"] = private["vllm"]["api_key"][0]
    began = time.time()
    driver.write_once("START.json", {"epoch": began, "argv": ready["stage_argv"], "external_seconds": 1000})
    with (ROOT / "owner.log").open("x") as log:
        outcome = subprocess.run(["timeout", "--signal=TERM", "--kill-after=30", "1000", *ready["stage_argv"]],
                                 cwd=SIDE, env=env, stdout=log, stderr=subprocess.STDOUT)
    driver.write_once("EXIT.json", {"epoch": time.time(), "returncode": outcome.returncode,
                                   "elapsed_seconds": time.time() - began})
    terminal = SIDE / "outputs/held-checkpoint32-001/OWNER_TERMINAL.json"
    if not terminal.exists() or not driver.read(terminal).get("released"):
        raise RuntimeError("Cannot authenticate owner release")
    driver.empty_gpu()
    driver.write_once("QUEUE_TERMINAL.json", {"epoch": time.time(), "returncode": outcome.returncode,
                                            "owner_terminal_sha256": driver.sha(terminal)})


if __name__ == "__main__":
    execute()
