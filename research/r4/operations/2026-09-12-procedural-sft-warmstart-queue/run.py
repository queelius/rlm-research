"""Run the sealed procedural-SFT training and its fixed readouts exactly once.

MAIN is the only launch authority.  This wrapper waits for the shared GPU lease, runs
the five immutable stages in order, and stops without retry on any failed contract.
"""

from __future__ import annotations

import argparse
import fcntl
import hashlib
import json
import os
from pathlib import Path
import signal
import subprocess
import time
import traceback


ROOT = Path(__file__).resolve().parent
STORE = Path("/project/alex_phd/runs/rlm-research-r4")
TRAIN = STORE / "sidecars/openai-mrcr-procedural-sft-warmstart-v1"
EVAL = STORE / "sidecars/openai-mrcr-procedural-sft-eval-v1"
TRAIN_READY = TRAIN / "READY_TRAINING.json"
TRAIN_READY_SHA = "b8cfa1a9112c9147b97802d6999d4b05e9e94ccf00bec0690224e9a54635acfb"
TRAIN_READY_IDENTITY = "f7311b709192290e6b311749fd105ae0fe52adffa4dccb7789e00cfb072e72f9"
EVAL_READY = EVAL / "CPU_READY_V2.json"
EVAL_READY_SHA = "96369acf08a5fbff7e66f5a3df63023aed086ecbf6f54012d81925542bab95a0"
EVAL_READY_IDENTITY = "c2742716b7fcdc783d8b6809a8dd00193c4244d74b44546655062f8bfdb5deb7"
ENV_RECEIPT = EVAL / "TRAINING_ENVIRONMENT_V2.json"
ENV_RECEIPT_SHA = "b357afd67394a33293147978ff2ceec23b461886a93193ea6d9107966fc663db"
OUTPUT = ROOT / "outputs/attempt-001"
HALT = ROOT / "HALT"
LOCK = STORE / "sidecars/root-rlvr-campaign-v1/COORDINATOR.lock"
KEY = "STRICT_RLM_CALIBRATION_API_KEY"
QUEUE_CAP_SECONDS = 14400
GLOBAL_SCIENCE_CAP_SECONDS = 4200


def read(path: Path | str) -> dict:
    return json.loads(Path(path).read_text())


def sha(path: Path | str) -> str:
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def atomic(path: Path, value: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n")
    temporary.replace(path)


def exclusive(path: Path, value: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("x") as stream:
        json.dump(value, stream, indent=2, sort_keys=True)
        stream.write("\n")
        stream.flush()
        os.fsync(stream.fileno())


def verify_closure(ready: dict, label: str) -> None:
    closure = ready.get("closure_sha256")
    if not isinstance(closure, dict) or not closure:
        raise ValueError(label + " has no immutable closure")
    for raw, expected in closure.items():
        path = Path(raw)
        if not path.is_file() or sha(path) != expected:
            raise ValueError(label + " closure changed: " + raw)


def train_ready() -> dict:
    if sha(TRAIN_READY) != TRAIN_READY_SHA:
        raise ValueError("training READY changed")
    ready = read(TRAIN_READY)
    if ready.get("identity") != TRAIN_READY_IDENTITY:
        raise ValueError("training READY identity changed")
    verify_closure(ready, "training")
    return ready


def eval_ready() -> dict:
    if sha(EVAL_READY) != EVAL_READY_SHA:
        raise ValueError("evaluation READY changed")
    ready = read(EVAL_READY)
    if ready.get("identity") != EVAL_READY_IDENTITY:
        raise ValueError("evaluation READY identity changed")
    verify_closure(ready, "evaluation")
    return ready


def verify_environment() -> dict:
    if sha(ENV_RECEIPT) != ENV_RECEIPT_SHA:
        raise ValueError("training environment receipt changed")
    receipt = read(ENV_RECEIPT)
    pins = {
        receipt.get("pyproject"): receipt.get("pyproject_sha256"),
        receipt.get("uv_lock"): receipt.get("uv_lock_sha256"),
        receipt.get("pyvenv_cfg"): receipt.get("pyvenv_cfg_sha256"),
    }
    if not Path(receipt.get("python_executable", "")).is_file():
        raise ValueError("training Python is absent")
    for raw, expected in pins.items():
        if not raw or not expected or sha(raw) != expected:
            raise ValueError("training environment dependency changed: " + str(raw))
    return receipt


def plan() -> dict:
    training = train_ready()
    evaluation = eval_ready()
    verify_environment()
    return {
        "schema": "openai-mrcr-procedural-sft-fixed4-operation-v1",
        "queue_cap_seconds": QUEUE_CAP_SECONDS,
        "global_science_cap_seconds": GLOBAL_SCIENCE_CAP_SECONDS,
        "stages": {
            "training": {
                "ready": str(TRAIN_READY),
                "ready_sha256": TRAIN_READY_SHA,
                "argv": training["fixed_argv"],
                "output": str(TRAIN / "outputs/attempt-001"),
                "cap_seconds": 700,
                "credential": False,
            },
            "checkpoint_seal": {
                "ready": str(EVAL_READY),
                "ready_sha256": EVAL_READY_SHA,
                "argv": evaluation["checkpoint_seal_argv"],
                "output": str(EVAL / "checkpoint-artifacts"),
                "cap_seconds": 120,
                "credential": False,
            },
            "train_readout": {
                "ready": str(EVAL_READY),
                "ready_sha256": EVAL_READY_SHA,
                "argv": evaluation["stage_argv"]["train"],
                "output": str(EVAL / "outputs/train-readout-001"),
                "cap_seconds": 1000,
                "credential": True,
            },
            "held_base": {
                "ready": str(EVAL_READY),
                "ready_sha256": EVAL_READY_SHA,
                "argv": evaluation["stage_argv"]["held-base"],
                "output": str(EVAL / "outputs/held-base-001"),
                "cap_seconds": 1000,
                "credential": True,
            },
            "held_checkpoint4": {
                "ready": str(EVAL_READY),
                "ready_sha256": EVAL_READY_SHA,
                "argv": evaluation["stage_argv"]["held-checkpoint4"],
                "output": str(EVAL / "outputs/held-checkpoint4-001"),
                "cap_seconds": 1000,
                "credential": True,
            },
        },
    }


def require_not_halted() -> None:
    if HALT.exists():
        raise RuntimeError("HALT present; no new stage may start")


def gpu_pids() -> list[int]:
    completed = subprocess.run(
        ["nvidia-smi", "--query-compute-apps=pid", "--format=csv,noheader,nounits"],
        capture_output=True,
        text=True,
        timeout=20,
        check=True,
    )
    rows = [row.strip() for row in completed.stdout.splitlines() if row.strip()]
    if any(not row.isdecimal() for row in rows):
        raise ValueError("unrecognized GPU PID inventory")
    return [int(row) for row in rows]


def stop_child(child: subprocess.Popen) -> None:
    for sig, grace in ((signal.SIGINT, 90), (signal.SIGTERM, 20), (signal.SIGKILL, 10)):
        if child.poll() is not None:
            return
        os.killpg(child.pid, sig)
        try:
            child.wait(timeout=grace)
            return
        except subprocess.TimeoutExpired:
            pass
    raise RuntimeError("owned stage process did not exit")


def validate_training(target: Path | str) -> dict:
    target = Path(target)
    failure = target / "FAILURE.json"
    result_path = target / "RESULT.json"
    if failure.exists() or not result_path.is_file():
        raise ValueError("training failed or has no RESULT")
    result = read(result_path)
    expected_checkpoint = (target / "checkpoint-0004").resolve()
    if (
        result.get("status") != "COMPLETED_FOUR_UPDATES"
        or result.get("optimizer_steps") != 4
        or Path(result.get("primary_checkpoint", "")).resolve() != expected_checkpoint
        or len(result.get("step_commits") or []) != 4
    ):
        raise ValueError("training did not complete the fixed four-update checkpoint")
    return result


def validate_checkpoint_seal(target: Path | str) -> dict:
    receipt_path = Path(target) / "CHECKPOINT_READY.json"
    if not receipt_path.is_file():
        raise ValueError("checkpoint seal receipt absent")
    receipt = read(receipt_path)
    training = receipt.get("training") or {}
    zero = receipt.get("zero_adapter") or {}
    if (
        receipt.get("fixed_primary_step") != 4
        or training.get("eligible") is not True
        or not str(training.get("checkpoint", "")).endswith("/checkpoint-0004")
        or zero.get("all_tensors_zero") is not True
    ):
        raise ValueError("checkpoint seal is ineligible")
    return receipt


def validate_eval_stage(
    target: Path | str, phase: str, arm: str, require_gate: bool = False
) -> dict:
    target = Path(target)
    terminal_path = target / "OWNER_TERMINAL.json"
    result_path = target / "science/RESULT.json"
    if not terminal_path.is_file() or not result_path.is_file():
        raise ValueError("evaluation terminal or RESULT absent")
    terminal, result = read(terminal_path), read(result_path)
    if (
        terminal.get("complete") is not True
        or terminal.get("released") is not True
        or terminal.get("errors") not in (None, [])
    ):
        raise ValueError("evaluation owner did not complete and release cleanly")
    if (
        result.get("phase") != phase
        or result.get("arm") != arm
        or result.get("complete") is not True
        or result.get("recorded") != 32
        or terminal.get("recorded") not in (None, 32)
    ):
        raise ValueError("evaluation inventory or fixed arm differs")
    if not all(
        result.get(key) is True
        for key in (
            "all_causal_mappings_complete",
            "all_initial_root_prefixes_verified",
            "all_action_caps_respected",
        )
    ):
        raise ValueError("evaluation causal/prefix/action-cap contract failed")
    if require_gate:
        gate = result.get("manipulation_gate") or {}
        if not (
            result.get("scientifically_available") == 32
            and gate.get("eligible") is True
            and gate.get("available") == 32
            and gate.get("raw_exact", -1) >= 8
            and gate.get("exact_contexts", -1) >= 4
        ):
            raise ValueError("train-only manipulation gate failed; heldout remains closed")
    return result


def validate_stage(name: str, stage: dict) -> dict:
    target = Path(stage["output"])
    if name == "training":
        return validate_training(target)
    if name == "checkpoint_seal":
        return validate_checkpoint_seal(target)
    if name == "train_readout":
        return validate_eval_stage(target, "train", "checkpoint4", require_gate=True)
    if name == "held_base":
        return validate_eval_stage(target, "held", "base")
    if name == "held_checkpoint4":
        return validate_eval_stage(target, "held", "checkpoint4")
    raise ValueError("unknown stage")


def run_stage(name: str, stage: dict, secret: str | None, status: dict, deadline: float) -> dict:
    require_not_halted()
    train_ready()
    eval_ready()
    verify_environment()
    target = Path(stage["output"])
    if target.exists():
        raise FileExistsError(str(target) + " exists; refusing rerun")
    if deadline - time.time() < stage["cap_seconds"]:
        raise TimeoutError("insufficient global science time for " + name)
    if gpu_pids():
        raise RuntimeError("GPU has another compute process before " + name)
    stage_dir = OUTPUT / name
    stage_dir.mkdir()
    log_path = stage_dir / "stdout.log"
    started = time.time()
    status["stages"][name] = {
        "state": "running",
        "started_epoch": started,
        "output": str(target),
        "log": str(log_path),
    }
    atomic(OUTPUT / "STATUS.json", status)
    environment = {**os.environ, "PYTHONDONTWRITEBYTECODE": "1"}
    environment.pop(KEY, None)
    if stage["credential"]:
        if not secret:
            raise ValueError("private credential absent for evaluation stage")
        environment[KEY] = secret
    with log_path.open("x") as log:
        child = subprocess.Popen(
            stage["argv"],
            stdout=log,
            stderr=subprocess.STDOUT,
            start_new_session=True,
            env=environment,
        )
    try:
        code = child.wait(timeout=stage["cap_seconds"])
        timed_out = False
    except subprocess.TimeoutExpired:
        timed_out = True
        stop_child(child)
        code = child.returncode
    except BaseException:
        stop_child(child)
        raise
    after = gpu_pids()
    record = {
        "state": "exited",
        "started_epoch": started,
        "ended_epoch": time.time(),
        "returncode": code,
        "timed_out": timed_out,
        "gpu_pids_after": after,
        "output": str(target),
        "log": str(log_path),
    }
    status["stages"][name] = record
    atomic(OUTPUT / "STATUS.json", status)
    if code != 0 or timed_out or after:
        raise RuntimeError(name + " failed, timed out, or retained GPU")
    validated = validate_stage(name, stage)
    record["validated_result_sha256"] = sha(
        target / ("CHECKPOINT_READY.json" if name == "checkpoint_seal" else
                  "RESULT.json" if name == "training" else "science/RESULT.json")
    )
    record["validated"] = validated
    status["stages"][name] = record
    atomic(OUTPUT / "STATUS.json", status)
    return record


def acquire_lock(stream, status: dict, queue_deadline: float) -> None:
    status["lease"] = {"state": "waiting", "deadline_epoch": queue_deadline}
    atomic(OUTPUT / "STATUS.json", status)
    while True:
        require_not_halted()
        try:
            fcntl.flock(stream, fcntl.LOCK_EX | fcntl.LOCK_NB)
            status["lease"] = {"state": "held", "acquired_epoch": time.time()}
            atomic(OUTPUT / "STATUS.json", status)
            return
        except BlockingIOError:
            if time.time() >= queue_deadline:
                raise TimeoutError("four-hour coordinator wait cap expired")
            time.sleep(5)


def execute() -> int:
    if OUTPUT.exists():
        raise FileExistsError("operation output exists; no resume or rerun")
    gpu = os.environ.get("CUDA_VISIBLE_DEVICES", "")
    if not gpu or "," in gpu:
        raise ValueError("MAIN must assign exactly one visible GPU")
    secret = os.environ.pop(KEY, None)
    if not isinstance(secret, str) or not secret:
        raise ValueError("private credential must be supplied only to operation bootstrap")
    spec = plan()
    for stage in spec["stages"].values():
        if Path(stage["output"]).exists():
            raise FileExistsError(stage["output"] + " exists; refusing partial reuse")
    OUTPUT.mkdir(parents=True)
    started = time.time()
    queue_deadline = started + spec["queue_cap_seconds"]
    status = {"state": "running", "started_epoch": started, "lease": None, "stages": {}}
    exclusive(
        OUTPUT / "START.json",
        {
            "schema": "openai-mrcr-procedural-sft-fixed4-operation-start-v1",
            "started_epoch": started,
            "pid": os.getpid(),
            "plan": spec,
            "credential_in_receipt": False,
            "credential_only_in_evaluator_child_environment": True,
        },
    )
    atomic(OUTPUT / "STATUS.json", status)
    handlers = {
        sig: signal.signal(sig, lambda number, _frame: (_ for _ in ()).throw(
            KeyboardInterrupt("operation signal " + str(number))
        ))
        for sig in (signal.SIGTERM, signal.SIGINT)
    }
    try:
        with LOCK.open("r") as lease:
            acquire_lock(lease, status, queue_deadline)
            science_started = time.time()
            science_deadline = science_started + spec["global_science_cap_seconds"]
            status["science_started_epoch"] = science_started
            status["science_deadline_epoch"] = science_deadline
            atomic(OUTPUT / "STATUS.json", status)
            if gpu_pids():
                raise RuntimeError("GPU occupied after coordinator lease acquisition")
            for name, stage in spec["stages"].items():
                run_stage(name, stage, secret, status, science_deadline)
        status.update(state="complete", ended_epoch=time.time())
        atomic(OUTPUT / "STATUS.json", status)
        exclusive(OUTPUT / "RESULT.json", status)
        return 0
    except BaseException as error:
        status.update(
            state="stopped",
            ended_epoch=time.time(),
            error={
                "type": type(error).__name__,
                "message": str(error),
                "traceback": traceback.format_exc(),
            },
        )
        atomic(OUTPUT / "STATUS.json", status)
        exclusive(OUTPUT / "STOP.json", status["error"])
        raise
    finally:
        for sig, handler in handlers.items():
            signal.signal(sig, handler)


def verify() -> dict:
    spec = plan()
    if OUTPUT.exists():
        raise FileExistsError("operation output already exists")
    for stage in spec["stages"].values():
        if Path(stage["output"]).exists():
            raise FileExistsError(stage["output"] + " already exists")
    if not LOCK.is_file():
        raise FileNotFoundError(LOCK)
    return spec


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("command", choices=("verify", "run"))
    args = parser.parse_args()
    value = verify() if args.command == "verify" else execute()
    if args.command == "verify":
        print(json.dumps(value, sort_keys=True))
