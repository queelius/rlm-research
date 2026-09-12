"""All three fixed doses on a second seed block; external GPU flock required."""

import hashlib
import importlib.util
import os
from pathlib import Path
import subprocess
import time

ROOT = Path(__file__).resolve().parent
SOURCE = ROOT.parent / "2026-09-12-rl-perturbation-chain/run.py"
assert hashlib.sha256(SOURCE.read_bytes()).hexdigest() == "a10a6b7c6960c8e4a717c40da642389ddea8da03dc81b88d6d304457c5e68347"
spec = importlib.util.spec_from_file_location("token_tis_seed2_helpers", SOURCE)
driver = importlib.util.module_from_spec(spec)
spec.loader.exec_module(driver)
driver.ROOT = ROOT
SIDE = driver.SIDES / "openai-mrcr-short-root-token-tis-held-seed2-v1"
READY = SIDE / "CPU_READY.json"
EXPECTED = "25e43f052f9339cc80efe456911ce3b07c3db1a60d05b596b23c85fce919ae07"


def execute():
    assert driver.sha(READY) == EXPECTED
    ready = driver.read(READY)
    driver.verify_closure(ready)
    assert ready["stage_order"] == ["base", "lr1e-5", "lr1e-4"]
    assert not any((SIDE / "outputs" / (stage + "-001")).exists() for stage in ready["stage_order"])
    driver.write_once("ADMISSION.json", {
        "authority": "MAIN", "epoch": time.time(), "ready_sha256": EXPECTED,
        "ready_identity": ready["identity"], "wrapper_sha256": driver.sha(__file__),
        "question": "Does the single high-dose exact answer survive another paired random decoding block, and how do both fixed doses compare?",
        "review": "MAIN read all six source/test files and reused qualified runtime seams; own actual high-arm verify passed all401 pins and fixed checkpoint qualification. Agent tested all3 arms and actual fake full run_slot.",
        "primary": "Paired raw exact; unavailable separate, both blocks and all fixed doses retained.",
        "seeds": "2026091900..2026091915; identical16 tasks and rendered initial prefixes to first block",
        "episodes_per_arm": 16, "owner_seconds_each": 650, "external_seconds_each": 700,
        "checkpoint_policy": "Save every native call, episode and terminal; no retries, training, dose or case selection.",
        "limitation": "Exploratory decoding repeat on already-exposed contexts, not transfer or a training-seed replication; prior one exact was broad-dump/copy.",
    })
    outcomes = {}
    for stage in ready["stage_order"]:
        driver.empty_gpu()
        env = {**os.environ, "CUDA_VISIBLE_DEVICES": driver.GPU, "OMP_NUM_THREADS": "4",
               "PYTHONDONTWRITEBYTECODE": "1"}
        private = driver.read(driver.SIDES / "leaf-output-cue-order-v1/owned/attempt-001/service/inference.json")
        env["STRICT_RLM_CALIBRATION_API_KEY"] = private["vllm"]["api_key"][0]
        started = time.time()
        driver.write_once(stage + "_START.json", {"epoch": started, "argv": ready["stage_argv"][stage], "external_seconds": 700})
        with (ROOT / (stage + ".log")).open("x") as log:
            result = subprocess.run(["timeout", "--signal=TERM", "--kill-after=30", "700", *ready["stage_argv"][stage]],
                                    cwd=SIDE, env=env, stdout=log, stderr=subprocess.STDOUT)
        driver.write_once(stage + "_EXIT.json", {"epoch": time.time(), "returncode": result.returncode,
                                                 "elapsed_seconds": time.time() - started})
        terminal_path = SIDE / "outputs" / (stage + "-001") / "OWNER_TERMINAL.json"
        if not terminal_path.exists() or not driver.read(terminal_path).get("released"):
            raise RuntimeError("Cannot authenticate owner release: " + stage)
        driver.empty_gpu()
        outcomes[stage] = {"returncode": result.returncode, "terminal_sha256": driver.sha(terminal_path)}
    return outcomes


if __name__ == "__main__":
    outcomes = execute()
    driver.write_once("QUEUE_TERMINAL.json", {"epoch": time.time(), "state": "ALL_FIXED_ARMS_ATTEMPTED", "outcomes": outcomes})
