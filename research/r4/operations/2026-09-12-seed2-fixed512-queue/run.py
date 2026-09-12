"""MAIN-approved fixed replica endpoint; run under the shared external flock."""

import hashlib
import importlib.util
import json
import os
from pathlib import Path
import subprocess

ROOT = Path(__file__).resolve().parent
SOURCE = ROOT.parent / "2026-09-12-rl-perturbation-chain/run.py"
SOURCE_SHA = "a10a6b7c6960c8e4a717c40da642389ddea8da03dc81b88d6d304457c5e68347"
if hashlib.sha256(SOURCE.read_bytes()).hexdigest() != SOURCE_SHA:
    raise ValueError("reviewed driver changed")
spec = importlib.util.spec_from_file_location("seed2_fixed512_driver", SOURCE)
driver = importlib.util.module_from_spec(spec)
spec.loader.exec_module(driver)
driver.ROOT = ROOT
SIDE = driver.SIDES / "helper-agnews-eightstep-seed2-eval-v1"
TRAIN = driver.SIDES / "helper-agnews-native-hf-eightstep-seed2-v1"
READY = "41e4d69d9d191d28b89acdb5358f63ddeb420a8a239184d22549ae0885cbcf9a"
TRAIN_READY = "abafc45c35a038aee97ccb7a4dce4dee8c2ce03b111a9430bd2c17022ac20853"
ARM = "rl_seed2_step8"
NATIVE = "/project/alex_phd/envs/prime-rl-5990b1b/bin/python"
driver.STAGES = [("seed2_fixed512", SIDE.name, "READY_RL_SEED2_STEP8.json", READY, 1000, True)]


if __name__ == "__main__":
    driver.empty_gpu()
    if (SIDE / "ENDPOINTS_FIXED.json").exists() or (SIDE / "outputs").exists():
        raise ValueError("preserve existing endpoint receipt and outputs")
    if driver.sha(SIDE / "READY_RL_SEED2_STEP8.json") != READY:
        raise ValueError("evaluation readiness changed")
    driver.verify_closure(driver.read(SIDE / "READY_RL_SEED2_STEP8.json"))
    driver.write_once("MAIN_START.json", {
        "authority": "MAIN", "started_epoch": driver.time.time(),
        "wrapper_sha256": driver.sha(__file__), "driver_sha256": SOURCE_SHA,
        "decision": "Fixed completed step8 only; same exposed512, no checkpoint selection",
        "review": "Complete source, exact raw decoder and full inherited eligibility reviewed; own closure verification passed; actual replica step1 gate and focused fixtures passed",
        "caps": {"owner_seconds": 900, "external_seconds": 1000},
    })
    if not (TRAIN / "outputs/attempt-001/FINAL_RESULT.json").exists():
        driver.write_once("NO_ENDPOINT.json", {
            "reason": "Replica did not produce its predeclared complete eight-update endpoint",
            "accuracy_result": None, "no_earlier_checkpoint_replacement": True,
            "checked_epoch": driver.time.time(),
        })
        raise SystemExit(0)
    result = subprocess.run(
        [NATIVE, str(SIDE / "owner.py"), "qualify", "--arm", ARM],
        cwd=SIDE, env={**os.environ, "CUDA_VISIBLE_DEVICES": "", "PYTHONDONTWRITEBYTECODE": "1"},
        capture_output=True, text=True, timeout=300,
    )
    if result.returncode:
        driver.write_once("QUALIFICATION_ERROR.json", {
            "returncode": result.returncode, "stdout": result.stdout,
            "stderr": result.stderr, "no_endpoint_queries": True,
        })
        raise ValueError("replica endpoint qualification failed")
    qualified = json.loads(result.stdout)
    if not qualified.get("eligible"):
        raise ValueError("replica endpoint ineligible")
    driver.write_once("QUALIFIED.json", qualified)
    fixed = {
        "authority": "MAIN", "fixed_step": 8, "created_epoch": driver.time.time(),
        "prior_seed1_panel_consulted": True,
        "replica_checkpoint_consulted_before_fix": False,
        "training_ready_sha256": TRAIN_READY,
        "data_manifest_sha256": "b5e9cc22161959fc09f5e1f15afd03e722a32818bca692a01f9e265fd6c81c2d",
        "trained_endpoints": {ARM: {key: qualified[key] for key in (
            "checkpoint", "state_sha256", "step_commit_sha256", "binding_sha256"
        )}},
        "wrapper_sha256": driver.sha(__file__),
        "interpretation": "Training-seed replication on the same research-exposed panel, not new-data confirmation",
    }
    with (SIDE / "ENDPOINTS_FIXED.json").open("x") as stream:
        json.dump(fixed, stream, indent=2, sort_keys=True)
        stream.write("\n")
    driver.main()
