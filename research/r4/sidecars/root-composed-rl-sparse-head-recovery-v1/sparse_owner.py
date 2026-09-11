"""MAIN-only bounded owner for qualification followed by exact update-2 recovery."""
import argparse
import json
import os
from pathlib import Path
import signal
import subprocess
import time
import traceback

import sparse_study as study


def budget(start):
    return {"started": start, "qualification_end": start + 900,
            "work_end": start + 2700, "owned_end": start + 2970,
            "outer_end": start + 3000}


def stage_deadline(stage, now, limits):
    if stage == "qualification":
        return min(limits["qualification_end"], limits["work_end"])
    if stage == "training":
        return min(now + 1800, limits["work_end"])
    raise ValueError("unknown stage")


def check_output(output):
    if Path(output).resolve() != study.ATTEMPT.resolve():
        raise ValueError("exact additive attempt-001 namespace only")
    if Path(output).exists():
        raise FileExistsError("attempt retained; no implicit overwrite")


def qualification_argv(output, deadline):
    return [str(study.TRAIN), str(study.ROOT / "sparse_qualify.py"),
            "--group", str(study.GROUP), "--generation", str(study.GENERATION),
            "--checkpoint", str(study.CHECKPOINT), "--output", str(output / "qualification"),
            "--deadline", str(float(deadline))]


def training_argv(output, deadline):
    return [str(study.TRAIN), str(study.ROOT / "sparse_train.py"),
            "--group", str(study.GROUP), "--generation", str(study.GENERATION),
            "--checkpoint", str(study.CHECKPOINT), "--output", str(output / "training"),
            "--deadline", str(float(deadline))]


def require_qualification(output):
    path = Path(output) / "QUALIFICATION_RESULT.json"
    if not path.exists():
        raise ValueError("qualification result absent")
    value = study.read(path)
    expected = {
        "schema": "root-composed-rl-sparse-head-qualification-v1",
        "passed": True,
        "optimizer_steps": 0,
        "checkpoint1_state_sha256": study.PINS[study.CHECKPOINT / "state.json"],
        "group_sha256": study.PINS[study.GROUP],
    }
    if any(value.get(key) != expected_value for key, expected_value in expected.items()):
        raise ValueError("qualification gate failed or foreign")
    if not value.get("short_equivalence", {}).get("passed") or not value.get("longest_sparse", {}).get("passed"):
        raise ValueError("qualification subgate failed")
    return value


def _error(error):
    return {"type": type(error).__name__, "message": str(error), "traceback": traceback.format_exc()}


def _stop(process, seconds):
    if process.poll() is not None:
        return True
    for sig, allowance in ((signal.SIGINT, 30), (signal.SIGTERM, 30), (signal.SIGKILL, 30)):
        try:
            os.killpg(process.pid, sig)
        except ProcessLookupError:
            return True
        try:
            process.wait(timeout=min(allowance, max(.001, seconds)))
            return True
        except subprocess.TimeoutExpired:
            seconds -= allowance
            if seconds <= 0:
                break
    return process.poll() is not None


def _run_stage(name, argv, output, deadline):
    stage = output / (name + "-stage")
    stage.mkdir()
    study.write(stage / "COMMAND.json", {"argv": argv, "started_epoch": time.time(),
        "deadline_epoch": deadline, "cuda_visible_devices": os.environ.get("CUDA_VISIBLE_DEVICES"),
        "start_new_session": True})
    with (stage / "process.log").open("x") as log:
        process = subprocess.Popen(argv, stdout=log, stderr=subprocess.STDOUT,
            start_new_session=True, env={**os.environ, "PYTHONDONTWRITEBYTECODE": "1"})
        study.write(stage / "PROCESS.json", {"pid": process.pid, "pgid": os.getpgid(process.pid),
            "started_epoch": time.time()})
        try:
            returncode = process.wait(timeout=max(.001, deadline - time.time()))
        except subprocess.TimeoutExpired:
            _stop(process, 90)
            raise TimeoutError(name + " stage cap")
        except BaseException:
            _stop(process, 90)
            raise
        finally:
            study.write(stage / "EXIT.json", {"returncode": process.returncode,
                "ended_epoch": time.time(), "released": process.poll() is not None})
    if returncode:
        raise RuntimeError(name + " subprocess failed")


def _checkpoint2(output):
    checkpoint = output / "training/checkpoint-2"
    state = study.read(checkpoint / "state.json")
    if state["optimizer_steps"] != 2 or state["generation"] != study.read(study.GENERATION):
        raise ValueError("checkpoint2 cursor/generation mismatch")
    metrics = state["metrics"]
    if metrics["episodes"] != 11 or metrics["root_turns"] != 154 or metrics["root_action_tokens"] != 18517:
        raise ValueError("checkpoint2 changed frozen group")
    required = {"adapter_model.safetensors", "adapter_config.json", "optimizer.pt", "rng_state.pt"}
    if not required <= set(state["files_sha256"]):
        raise ValueError("checkpoint2 missing persisted state")
    for name, pin in state["files_sha256"].items():
        study.check(checkpoint / name, pin)
    result = study.read(output / "training/RESULT.json")
    if result["optimizer_steps"] != 2 or result["policy"]["state_sha256"] != study.sha(checkpoint / "state.json"):
        raise ValueError("training result does not select update2")
    return result["policy"]


def execute(output):
    output = Path(output)
    check_output(output)
    if not os.environ.get("CUDA_VISIBLE_DEVICES") or "," in os.environ["CUDA_VISIBLE_DEVICES"]:
        raise ValueError("MAIN must assign exactly one GPU")
    campaign = study.verify_prepared()
    inputs = campaign["frozen_inventory"]
    started = time.time()
    limits = budget(started)
    output.mkdir(parents=True, exist_ok=False)
    study.write(output / "OWNER_RUN.json", {"schema": "root-composed-rl-sparse-head-owner-v1",
        "started_epoch": started, "budget": limits, "identity": campaign["identity"], "inputs": inputs,
        "qualification_cap_seconds": 900, "training_cap_seconds": 1800,
        "cleanup_reserve_seconds": 270, "outer_margin_seconds": 30})
    errors = []
    policy = None
    qualification = None
    try:
        q_deadline = stage_deadline("qualification", time.time(), limits)
        _run_stage("qualification", qualification_argv(output, q_deadline), output, q_deadline)
        qualification = require_qualification(output / "qualification")
        t_deadline = stage_deadline("training", time.time(), limits)
        if t_deadline <= time.time():
            raise TimeoutError("no training allowance remains")
        _run_stage("training", training_argv(output, t_deadline), output, t_deadline)
        policy = _checkpoint2(output)
    except BaseException as error:
        errors.append(_error(error))
    result = {"schema": "root-composed-rl-sparse-head-owner-terminal-v1",
        "complete": not errors and policy is not None, "errors": errors,
        "qualification": qualification, "policy": policy,
        "previous_optimizer_step": 1, "target_optimizer_step": 2,
        "no_recollection": True, "elapsed_seconds": time.time() - started,
        "released": all(not p.exists() or study.read(p).get("released") for p in
            (output / "qualification-stage/EXIT.json", output / "training-stage/EXIT.json"))}
    study.write(output / "OWNER_TERMINAL.json", result)
    return result


def parse_args(argv=None):
    parser = argparse.ArgumentParser()
    parser.add_argument("command", choices=("verify", "run"))
    parser.add_argument("--output", type=Path, default=study.ATTEMPT)
    return parser.parse_args(argv)


if __name__ == "__main__":
    args = parse_args()
    if args.command == "verify":
        print(study.verify_prepared()["identity"])
    else:
        value = execute(args.output)
        print(json.dumps(value, sort_keys=True, allow_nan=False))
        raise SystemExit(0 if value["complete"] else 1)
