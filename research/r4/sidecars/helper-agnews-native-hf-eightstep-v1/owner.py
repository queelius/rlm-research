"""Conditional fixed-dose owner; native release precedes every single-load HF step."""

import argparse
import json
import os
import signal
import threading
import time
from pathlib import Path

import core


def check_admission(path, ready):
    admission = core.read(path)
    if (
        admission.get("authority") != "MAIN"
        or admission.get("training_ready_sha256") != core.sha(core.ROOT / "READY.json")
        or admission.get("decision") != "APPROVE_FIXED_EIGHTSTEP_DOSE"
        or admission.get("endpoint") != "fixed-step8-versus-c32-on-fresh512"
        or admission.get("start") != "fresh-original-c32-not-one-step-continuation"
        or not admission.get("reason")
        or admission.get("heldout512_consulted") is not False
    ):
        raise ValueError("explicit MAIN fixed-dose admission is absent or inconsistent")
    evidence = admission.get("reviewed_evidence_sha256", {})
    if not evidence:
        raise ValueError("MAIN admission must pin reviewed pilot/replica evidence")
    for raw, expected in evidence.items():
        if core.sha(raw) != expected:
            raise ValueError("reviewed admission evidence changed: " + raw)
    initial = core.load_bound(
        "ag_eight_initial_pilot_eligibility",
        core.SOURCE / "eval_owner.py",
        {"ag_study": core.original},
    )
    initial.qualify()  # Full qualified UPDATED, actual optimizer/masks/raw/replay receipts.
    result = core.read(core.SOURCE / "outputs/attempt-001/RESULT.json")
    if result.get("mixed_reward_groups", 0) <= 0:
        raise ValueError("initial AG step has no verified mixed reward groups")
    return {
        "path": str(path),
        "sha256": core.sha(path),
        "receipt": admission,
        "initial_qualified_result_sha256": core.sha(
            core.SOURCE / "outputs/attempt-001/RESULT.json"
        ),
        "ready_identity": ready["identity"],
    }


def execute(cap, admission_path, resume_after):
    started = time.time()
    ready = core.verify()
    runtime = core.read(core.ROOT / "RUNTIME.json")
    if cap != runtime["owner_seconds"] or cap > 10600 or runtime["external_seconds"] > 10800:
        raise ValueError("exact measured owner cap and at most3h external required")
    if not os.environ.get("CUDA_VISIBLE_DEVICES") or "," in os.environ["CUDA_VISIBLE_DEVICES"]:
        raise ValueError("MAIN must assign one GPU under the shared lock")
    admission = check_admission(admission_path, ready)
    if not 0 <= resume_after <= 7:
        raise ValueError("resume_after must be0..7")
    if resume_after == 0:
        if core.ATTEMPT.exists():
            raise ValueError("fresh original-c32 run requires unused output")
        core.ATTEMPT.mkdir(parents=True)
    else:
        core.parent_for(resume_after + 1)
    if (core.ATTEMPT / f"step-{resume_after + 1:03d}").exists():
        raise ValueError(
            "an incomplete existing next step cannot be recollected/resumed automatically"
        )
    segment = f"segment-after-{resume_after:03d}"
    core.write_x(
        core.ATTEMPT / f"{segment}-START.json",
        {
            "started_epoch": started,
            "owner_seconds": cap,
            "runtime": runtime,
            "admission": admission,
            "resume_after": resume_after,
            "planned_final_step": 8,
            "data_manifest_sha256": ready["data_manifest_sha256"],
        },
    )
    errors, committed = [], resume_after

    def stop(_number, _frame):
        raise TimeoutError("eight-step owner wall cap or termination")

    previous = {number: signal.signal(number, stop) for number in (signal.SIGTERM, signal.SIGINT)}
    timer = threading.Timer(
        max(1, cap - (time.time() - started)), os.kill, args=(os.getpid(), signal.SIGTERM)
    )
    timer.daemon = True
    timer.start()
    try:
        for step in range(resume_after + 1, 9):
            if time.time() - started + runtime["step_owner_seconds"] + 30 > cap:
                raise TimeoutError("insufficient remaining budget for a complete capped step")
            parent = core.parent_for(step)
            core.write_x(
                core.ATTEMPT / f"parent-inputs/step-{step:03d}.json",
                {
                    "parent_policy": parent,
                    "before_collection_epoch": time.time(),
                    "ready_identity": ready["identity"],
                    "schedule_sha256": core.sha(
                        core.DATA / f"inputs/step-{step:03d}/REQUESTS.json"
                    ),
                },
            )
            view = core.step_view(step, parent=parent)
            stage = core.step_owner(view)
            previous_step = os.environ.get("RLM_AG_EIGHT_STEP")
            os.environ["RLM_AG_EIGHT_STEP"] = str(step)
            try:
                terminal = stage.execute(view.CAP)
            finally:
                if previous_step is None:
                    os.environ.pop("RLM_AG_EIGHT_STEP", None)
                else:
                    os.environ["RLM_AG_EIGHT_STEP"] = previous_step
            if not terminal["complete"] or terminal["optimizer_steps"] != step:
                raise RuntimeError("step did not fully qualify/update/release: " + str(step))
            core.verify_commit(step)
            committed = step
    except BaseException as error:
        errors.append({"type": type(error).__name__, "message": str(error)})
    finally:
        timer.cancel()
        for number, handler in previous.items():
            signal.signal(number, handler)
    result = {
        "status": "UPDATED_STEP8" if committed == 8 and not errors else "STOPPED_PARTIAL_DOSE",
        "completed_steps": committed,
        "fixed_primary_step": 8,
        "primary_endpoint_eligible": committed == 8 and not errors,
        "errors": errors,
        "elapsed_seconds": time.time() - started,
        "ready_identity": ready["identity"],
        "admission_sha256": admission["sha256"],
        "resume_after": resume_after,
        "heldout_model_calls": 0,
    }
    if result["primary_endpoint_eligible"]:
        result["endpoint"] = core.parent_for(9)
        core.write_x(core.ATTEMPT / "FINAL_RESULT.json", result)
    core.write_x(core.ATTEMPT / f"{segment}-RESULT.json", result)
    return result


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("command", choices=("verify", "run", "endpoint"))
    parser.add_argument("--owner-seconds", type=int, default=5000)
    parser.add_argument("--admission-json", type=Path, default=core.ROOT / "ADMISSION.json")
    parser.add_argument("--resume-after", type=int, default=0)
    args = parser.parse_args()
    if args.command == "verify":
        print(core.verify()["identity"])
    elif args.command == "endpoint":
        core.verify()
        final = core.read(core.ATTEMPT / "FINAL_RESULT.json")
        if final["status"] != "UPDATED_STEP8" or not final["primary_endpoint_eligible"]:
            raise ValueError("complete predeclared step8 endpoint unavailable")
        print(json.dumps(core.parent_for(9), sort_keys=True))
    else:
        result = execute(args.owner_seconds, args.admission_json, args.resume_after)
        print(json.dumps(result, sort_keys=True))
        raise SystemExit(0 if result["primary_endpoint_eligible"] else 1)
