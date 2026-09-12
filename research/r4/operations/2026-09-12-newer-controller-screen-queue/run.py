"""MAIN-reviewed cached-model comparison; invoke under external coordinator flock."""

import hashlib
import importlib.util
import os
from pathlib import Path
import subprocess
import time

ROOT = Path(__file__).resolve().parent
SOURCE = ROOT.parent / "2026-09-12-rl-perturbation-chain/run.py"
assert hashlib.sha256(SOURCE.read_bytes()).hexdigest() == "a10a6b7c6960c8e4a717c40da642389ddea8da03dc81b88d6d304457c5e68347"
spec = importlib.util.spec_from_file_location("cached_controller_helpers", SOURCE)
driver = importlib.util.module_from_spec(spec)
spec.loader.exec_module(driver)
driver.ROOT = ROOT
SIDE = driver.SIDES / "openai-mrcr-newer-controller-screen-v1"
READY = SIDE / "READY.json"
EXPECTED = "7c86dbdfa4fe125563cc0e642e7241455fda872469339c5ecb1f63bf46c51b5e"


def execute():
    assert driver.sha(READY) == EXPECTED
    ready = driver.read(READY)
    driver.verify_closure(ready)
    assert ready["arm_order"] == ["qwen3", "qwen35"]
    assert not (SIDE / "outputs/attempt-001").exists()
    driver.empty_gpu()
    driver.write_once("ADMISSION.json", {
        "authority": "MAIN", "epoch": time.time(), "ready_sha256": EXPECTED,
        "ready_identity": ready["identity"], "wrapper_sha256": driver.sha(__file__),
        "review": "Full source, native-template fixtures and inherited lifecycle reviewed. MAIN actual owner verify passed 5820 source pins and model stat receipts; CPU-only native two-turn qualification passed both model packages.",
        "question": "Does a newer cached 4B released model more readily inspect the conversation schema and return the requested text within two turns?",
        "paired_contexts": 8, "max_physical_calls": 32, "optimizer_steps": 0,
        "seed_base": 202609190000, "owner_seconds": 1800, "external_seconds": 1900,
        "metric": "Original returned-text exact; raw-token/native/returned fidelity diagnostics separate.",
        "limitations": "Exposed train cases, short two-turn cap, different native model/template/parser packages; not held-out transfer, a weights-only comparison or cost-matched capability ranking.",
        "checkpoint_policy": "Persist every native call and episode; no retries or case selection; authenticate owner release.",
    })
    env = {**os.environ, "CUDA_VISIBLE_DEVICES": driver.GPU, "OMP_NUM_THREADS": "4",
           "PYTHONDONTWRITEBYTECODE": "1"}
    private = driver.read(driver.SIDES / "leaf-output-cue-order-v1/owned/attempt-001/service/inference.json")
    env["STRICT_RLM_CALIBRATION_API_KEY"] = private["vllm"]["api_key"][0]
    started = time.time()
    driver.write_once("START.json", {"epoch": started, "argv": ready["fixed_argv"], "external_seconds": 1900})
    with (ROOT / "owner.log").open("x") as log:
        result = subprocess.run(["timeout", "--signal=TERM", "--kill-after=30", "1900", *ready["fixed_argv"]],
                                cwd=SIDE, env=env, stdout=log, stderr=subprocess.STDOUT)
    driver.write_once("EXIT.json", {"epoch": time.time(), "returncode": result.returncode,
                                   "elapsed_seconds": time.time() - started})
    terminal = SIDE / "outputs/attempt-001/OWNER_TERMINAL.json"
    if not terminal.exists() or not driver.read(terminal).get("released"):
        raise RuntimeError("Cannot authenticate owner release")
    driver.empty_gpu()
    driver.write_once("QUEUE_TERMINAL.json", {"epoch": time.time(), "returncode": result.returncode,
                                            "owner_terminal_sha256": driver.sha(terminal)})


if __name__ == "__main__":
    execute()
