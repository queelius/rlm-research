"""CPU-only first-stage dispatch qualification against the real inherited state machine."""

import argparse
import json
import os
import tempfile
import time
from pathlib import Path

import common as a
import driver

c = a.c


def main():
    if os.environ.get("CUDA_VISIBLE_DEVICES") != "":
        raise ValueError("qualification must start with CUDA hidden")
    amendment = a.verify_amendment()
    before = a.prior_policies()
    directory = a.ROOT / "qualification"
    directory.mkdir(exist_ok=True)
    output = Path(tempfile.mkdtemp(prefix="first-stage-cpu-", dir=directory))
    c.write_once(output / "RUN.json", driver.run_envelope(time.time(), "CPU_ONLY_NO_GPU", amendment["amendment_id"]))
    driver.stage_inherited(output)
    calls = []
    class ExpectedCPUStop(RuntimeError):
        pass
    def stop_before_external_command(command, log_path, timeout, *, gpu=False):
        calls.append({"command": command, "gpu_flag": gpu, "timeout": timeout})
        raise ExpectedCPUStop("CPU-only interception before subprocess/model load")
    def no_service(*args, **kwargs):
        raise AssertionError("first stage must train preserved round04, not start a rollout service")
    saved_command, saved_start = driver.BASE_OWNED_COMMAND, driver.coordinator.start_service
    driver.install()
    driver.BASE_OWNED_COMMAND = stop_before_external_command
    driver.coordinator.start_service = no_service
    os.environ["CUDA_VISIBLE_DEVICES"] = "CPU_ONLY_NO_GPU"
    try:
        try:
            driver.coordinator.run_campaign(argparse.Namespace(output=output, resume=True))
        except ExpectedCPUStop:
            pass
        else:
            raise AssertionError("expected interception did not occur")
    finally:
        os.environ["CUDA_VISIBLE_DEVICES"] = ""
        driver.BASE_OWNED_COMMAND, driver.coordinator.start_service = saved_command, saved_start
    if len(calls) != 1 or calls[0]["command"][:2] != [str(c.TRAIN_PYTHON), str(a.ROOT / "train.py")] or not calls[0]["gpu_flag"]:
        raise AssertionError("actual coordinator did not dispatch the amended step4 trainer first")
    command = calls[0]["command"]
    if Path(command[command.index("--group") + 1]) != output / "round-04/collection/export/GROUP.json":
        raise AssertionError("trainer is not using copied immutable round04 group")
    if a.prior_policies() != before or any(output.glob("services/*")):
        raise AssertionError("prior states changed or service was started")
    result = {"amendment_id": amendment["amendment_id"], "actual_original_coordinator_invoked": True,
        "first_actual_dispatched_command": calls[0], "first_stage": "train4_from_exact_step3_and_preserved_round04",
        "old_inputs_reverified_after": True, "service_starts": 0, "subprocesses_launched": 0,
        "gpu_calls": 0, "cpu_fixture_output": str(output),
        "step3_policy": before[3], "new_budget_seconds": a.CAP_SECONDS}
    c.write_once(a.ROOT / "FIRST_STAGE_PROOF.json", result)
    print(json.dumps(result, sort_keys=True))


if __name__ == "__main__":
    main()
