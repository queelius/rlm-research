"""Fix completed endpoints, then evaluate once; no checkpoint or heldout selection."""

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
spec = importlib.util.spec_from_file_location("reviewed_fresh512_endpoint_queue", SOURCE)
driver = importlib.util.module_from_spec(spec)
spec.loader.exec_module(driver)
driver.ROOT = ROOT
SIDE = driver.SIDES / "helper-agnews-fresh512-eval-v1"
RL_OUT = driver.SIDES / "helper-agnews-native-hf-eightstep-v1/outputs/attempt-001"
NATIVE = "/project/alex_phd/envs/prime-rl-5990b1b/bin/python"
PINS = {
    "c32": "2b00d61d4c03d7b9b60677715118f5f6a6d5f78fdf4632efa622282cf2af9df6",
    "rl_step8": "f76d0e1ace4b72f11d56959e8eb16ffc48e7be929f08ee3effcc7cc16e206b18",
    "sft_step8": "26e89aa78844333dc1d8913b08157bc45b20f9d272ce2e94c5df94a57cf3e299",
}


def qualify(arm):
    result = subprocess.run(
        [NATIVE, str(SIDE / "owner.py"), "qualify", "--arm", arm],
        cwd=SIDE, env={**os.environ, "CUDA_VISIBLE_DEVICES": "", "PYTHONDONTWRITEBYTECODE": "1"},
        capture_output=True, text=True, timeout=300,
    )
    if result.returncode:
        driver.write_once(arm + "_QUALIFICATION_ERROR.json", {
            "returncode": result.returncode, "stdout": result.stdout, "stderr": result.stderr,
            "source_verified": True, "no_endpoint_query": True,
        })
        raise ValueError("fixed endpoint qualification failed: " + arm)
    receipt = json.loads(result.stdout)
    if not receipt.get("eligible"):
        raise ValueError("unqualified endpoint: " + arm)
    driver.write_once(arm + "_QUALIFIED.json", receipt)
    return {key: receipt[key] for key in (
        "checkpoint", "state_sha256", "step_commit_sha256", "binding_sha256"
    )}


if __name__ == "__main__":
    driver.empty_gpu()
    if (SIDE / "ENDPOINTS_FIXED.json").exists() or (SIDE / "outputs").exists():
        raise ValueError("preserve existing endpoint receipt or queries")
    for arm, expected in PINS.items():
        path = SIDE / ("READY_" + arm.upper() + ".json")
        if driver.sha(path) != expected:
            raise ValueError("fixed evaluator source changed: " + arm)
        driver.verify_closure(driver.read(path))
    driver.write_once("WRAPPER_START.json", {
        "authority": "MAIN", "started_epoch": driver.time.time(),
        "wrapper_sha256": driver.sha(__file__), "driver_sha256": SOURCE_SHA,
        "decision": "Only completed predeclared cp8; if fixed RL dose failed, evaluate SFT/c32 and preserve RL failure separately",
        "preflight": "MAIN read all evaluator/collector/eligibility/metrics/fixture sources; own three READY verifies passed",
        "no_intermediate_checkpoint_selection": True,
    })
    endpoints = {"sft_step8": qualify("sft_step8")}
    if (RL_OUT / "FINAL_RESULT.json").exists():
        endpoints["rl_step8"] = qualify("rl_step8")
        rl_reason = "complete fixed RL checkpoint8"
    else:
        terminal_path = RL_OUT / "segment-after-000-RESULT.json"
        terminal = driver.read(terminal_path)
        if terminal.get("status") != "STOPPED_PARTIAL_DOSE" or terminal.get("primary_endpoint_eligible"):
            raise ValueError("RL is neither a qualified final endpoint nor a recorded failed fixed dose")
        rl_reason = "recorded partial dose; not promoted to checkpoint8"
        driver.write_once("RL_UNAVAILABLE.json", {
            "terminal": terminal, "terminal_sha256": driver.sha(terminal_path),
            "not_an_accuracy_failure": True,
        })
    fixed = {
        "authority": "MAIN", "fixed_step": 8,
        "created_epoch": driver.time.time(),
        "data_manifest_sha256": "b5e9cc22161959fc09f5e1f15afd03e722a32818bca692a01f9e265fd6c81c2d",
        "heldout512_consulted_before_fix": False,
        "trained_endpoints": endpoints,
        "rl_status_reason": rl_reason,
        "decision_source": "predeclared fixed endpoints; no heldout model calls yet",
        "wrapper_sha256": driver.sha(__file__),
    }
    with (SIDE / "ENDPOINTS_FIXED.json").open("x") as stream:
        json.dump(fixed, stream, indent=2, sort_keys=True)
        stream.write("\n")
    arms = ["c32"] + (["rl_step8"] if "rl_step8" in endpoints else []) + ["sft_step8"]
    driver.STAGES = [
        ("fresh512_" + arm, SIDE.name, "READY_" + arm.upper() + ".json", PINS[arm], 1000, True)
        for arm in arms
    ]
    driver.main()
