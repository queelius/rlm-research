"""Conditional fixed readout after the accepted trainer; external GPU flock required."""

import hashlib
import importlib.util
import json
import os
from pathlib import Path
import subprocess
import time

ROOT = Path(__file__).resolve().parent
SOURCE = ROOT.parent / "2026-09-12-rl-perturbation-chain/run.py"
if hashlib.sha256(SOURCE.read_bytes()).hexdigest() != "a10a6b7c6960c8e4a717c40da642389ddea8da03dc81b88d6d304457c5e68347":
    raise ValueError("reviewed driver changed")
spec = importlib.util.spec_from_file_location("continue32_readout_helpers", SOURCE)
driver = importlib.util.module_from_spec(spec)
spec.loader.exec_module(driver)
driver.ROOT = ROOT
SIDE = driver.SIDES / "openai-mrcr-procedural-sft-continue32-eval-v1"
READY = SIDE / "CPU_READY.json"
EXPECTED = "d2a1bd1638c837483c1c56db2551642c251816ddfd385240ce92caa7f49457b9"
TRAIN = driver.SIDES / "openai-mrcr-procedural-sft-continue32-v1/outputs/attempt-001"


def run_stage(name, argv, cap, uses_gpu):
    driver.empty_gpu()
    env = {**os.environ, "CUDA_VISIBLE_DEVICES": driver.GPU if uses_gpu else "",
           "OMP_NUM_THREADS": "4", "PYTHONDONTWRITEBYTECODE": "1"}
    if uses_gpu:
        private = driver.read(driver.SIDES / "leaf-output-cue-order-v1/owned/attempt-001/service/inference.json")
        env["STRICT_RLM_CALIBRATION_API_KEY"] = private["vllm"]["api_key"][0]
    start = time.time()
    driver.write_once(name + "_START.json", {"epoch": start, "argv": argv, "cap_seconds": cap})
    with (ROOT / (name + ".log")).open("x") as log:
        result = subprocess.run(["timeout", "--signal=TERM", "--kill-after=30", str(cap), *argv],
                                cwd=SIDE, env=env, stdout=log, stderr=subprocess.STDOUT)
    driver.write_once(name + "_EXIT.json", {"epoch": time.time(), "returncode": result.returncode,
                                           "elapsed_seconds": time.time() - start})
    driver.empty_gpu()
    return result.returncode


def execute():
    if driver.sha(READY) != EXPECTED:
        raise ValueError("reviewed evaluator READY changed")
    ready = driver.read(READY)
    driver.verify_closure(ready)
    assert ready["stage_order"] == ["train32", "held-base", "held-checkpoint32"]
    driver.write_once("ADMISSION.json", {
        "authority": "MAIN", "epoch": time.time(), "ready_sha256": EXPECTED,
        "ready_identity": ready["identity"], "wrapper_sha256": driver.sha(__file__),
        "decision": "ADMIT_FIXED_CP32_TRAIN_THEN_CONDITIONAL_HELD_READOUT",
        "review": "MAIN read full additive evaluator, original owner/collector seams and tests; own169-pin collector verification passed; independent review recorded before launch.",
        "question": "Did the same procedure become usable after more training, and if so does it work on separate conversations?",
        "no_checkpoint_selection": True, "original_cp4_failure_preserved": True,
        "fixed_gate": {"available": 32, "raw_exact_at_least": 8, "exact_contexts_at_least": 4},
        "held_panel_prior_exposure": "Token-TIS used one seed per each of these16 contexts; cp4 SFT held stages never ran. This remains exploratory.",
    })
    result_path = TRAIN / "RESULT.json"
    if not result_path.exists() or driver.read(result_path).get("status") != "COMPLETED_32_TOTAL_UPDATES":
        return {"state": "SKIPPED_NO_COMPLETED_CP32", "GPU_queries": 0}
    code = run_stage("checkpoint_seal", ready["checkpoint_seal_argv"], 180, False)
    if code:
        return {"state": "STOPPED_CHECKPOINT_QUALIFICATION", "returncode": code, "GPU_queries": 0}
    outcomes = {}
    for name in ready["stage_order"]:
        if name != "train32":
            terminal = outcomes["train32"]
            science = driver.read(SIDE / "outputs/train32-001/science/RESULT.json")
            gate = science.get("manipulation_gate") or {}
            if not (terminal["complete"] and not terminal.get("errors") and science["complete"]
                    and gate.get("eligible") and gate.get("available") == 32
                    and gate.get("raw_exact", 0) >= 8 and gate.get("exact_contexts", 0) >= 4):
                return {"state": "STOPPED_TRAIN_MANIPULATION_GATE", "gate": gate, "held_queries": 0}
        code = run_stage(name, ready["stage_argv"][name], 1000, True)
        path = SIDE / "outputs" / (name + "-001") / "OWNER_TERMINAL.json"
        if not path.exists():
            raise RuntimeError("owner terminal absent; cannot assume cleanup: " + name)
        terminal = driver.read(path)
        if not terminal.get("released"):
            raise RuntimeError("owner did not authenticate release: " + name)
        outcomes[name] = terminal
        print(json.dumps({"stage": name, "returncode": code,
                          "available": terminal.get("scientifically_available"),
                          "complete": terminal.get("complete")}), flush=True)
    return {"state": "ALL_FIXED_STAGES_ATTEMPTED", "stages": outcomes}


if __name__ == "__main__":
    try:
        value = execute()
    except BaseException as error:
        driver.write_once("QUEUE_FAILURE.json", {"epoch": time.time(), "type": type(error).__name__, "message": str(error)})
        raise
    driver.write_once("QUEUE_TERMINAL.json", {"epoch": time.time(), **value})
    print(json.dumps({"state": value["state"]}), flush=True)
