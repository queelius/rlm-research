"""Wait outside the GPU flock, then run the fixed held16 base/updated pair once."""

from __future__ import annotations

import fcntl
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import time


ROOT = Path(__file__).resolve().parent
STORE = ROOT.parents[1]
SIDE = STORE / "sidecars/openai-mrcr-short-root-shaped-eval-v1"
READY = SIDE / "CPU_READY.json"
READY_SHA = "b5875be06892d2e6d907984e82fef162f358184deca3be1fbe0ff56eabd0e8d9"
READY_IDENTITY = "2888a8a25995d325a0d2f8681e12874e09400c2b2da2aa89f72c1a0cacbe220e"
TRAIN_QUEUE = STORE / "operations/2026-09-12-shaped-root-rl-queue"
TRAIN_EXIT = TRAIN_QUEUE / "shaped_root_rl_step1_EXIT.json"
TRAIN_OUTPUT = STORE / "sidecars/openai-mrcr-short-root-shaped-rl-v1/outputs/attempt-001"
LOCK = STORE / "sidecars/root-rlvr-campaign-v1/COORDINATOR.lock"
OUTPUT = ROOT / "outputs/attempt-001"
GPU = "MIG-c0ac02b2-b43f-58cf-ab06-dc24b64b023a"
SMI = "/export/software/system/nvidia/580.126.20/bin/nvidia-smi"
KEY_SOURCE = STORE / "sidecars/leaf-output-cue-order-v1/owned/attempt-001/service/inference.json"
WAIT_SECONDS = 14400


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def read(path):
    return json.loads(Path(path).read_text())


def write_x(path, value):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("x") as stream:
        json.dump(value, stream, indent=2, sort_keys=True, allow_nan=False)
        stream.write("\n")


def verify_ready():
    if sha(READY) != READY_SHA:
        raise ValueError("held16 READY changed")
    ready = read(READY)
    if ready.get("identity") != READY_IDENTITY:
        raise ValueError("held16 READY identity changed")
    for raw, expected in ready["closure_sha256"].items():
        if sha(raw) != expected:
            raise ValueError("held16 closure changed: " + raw)
    return ready


def gpu_pids():
    result = subprocess.run(
        [SMI, "--query-compute-apps=pid", "--format=csv,noheader,nounits"],
        capture_output=True,
        text=True,
        timeout=20,
        check=True,
    )
    return [row.strip() for row in result.stdout.splitlines() if row.strip()]


def wait_for_training(deadline):
    # This deliberately occurs before opening/acquiring the GPU coordinator lock.
    while time.time() < deadline:
        if TRAIN_EXIT.exists():
            exited = read(TRAIN_EXIT)
            if exited.get("returncode") != 0:
                raise ValueError("shaped-root training queue exited unsuccessfully")
            sys.path.insert(0, str(SIDE))
            try:
                import checkpoint

                qualified = checkpoint.qualify_training(TRAIN_OUTPUT)
            finally:
                sys.path.pop(0)
            return {"queue_exit_sha256": sha(TRAIN_EXIT), "qualification": qualified}
        time.sleep(15)
    raise TimeoutError("four-hour training dependency wait expired")


def run_stage(stage, ready, secret):
    argv = ready["stage_argv"][stage]
    target = Path(argv[argv.index("--output") + 1])
    if target.exists():
        raise FileExistsError("preserve existing evaluation output: " + str(target))
    if gpu_pids():
        raise RuntimeError("GPU is not empty before " + stage)
    log = OUTPUT / (stage + ".log")
    environment = {
        **os.environ,
        "CUDA_VISIBLE_DEVICES": GPU,
        "STRICT_RLM_CALIBRATION_API_KEY": secret,
        "PYTHONDONTWRITEBYTECODE": "1",
        "OMP_NUM_THREADS": "4",
    }
    started = time.time()
    with log.open("x") as stream:
        result = subprocess.run(
            ["timeout", "--signal=TERM", "--kill-after=30", "700", *argv],
            cwd=SIDE,
            env=environment,
            stdout=stream,
            stderr=subprocess.STDOUT,
        )
    terminal_path = target / "OWNER_TERMINAL.json"
    terminal = read(terminal_path) if terminal_path.exists() else None
    record = {
        "stage": stage,
        "started_epoch": started,
        "ended_epoch": time.time(),
        "returncode": result.returncode,
        "output": str(target),
        "terminal_sha256": sha(terminal_path) if terminal else None,
        "terminal": terminal,
        "gpu_pids_after": gpu_pids(),
    }
    write_x(OUTPUT / (stage + "_EXIT.json"), record)
    if record["gpu_pids_after"] or not terminal or terminal.get("released") is not True:
        raise RuntimeError(stage + " did not cleanly release; suppressing the next arm")
    return record


def main():
    if OUTPUT.exists():
        raise FileExistsError("preserve existing held16 queue output")
    ready = verify_ready()
    dependency = wait_for_training(time.time() + WAIT_SECONDS)
    OUTPUT.mkdir(parents=True)
    write_x(
        OUTPUT / "START.json",
        {
            "started_epoch": time.time(),
            "ready_sha256": READY_SHA,
            "ready_identity": READY_IDENTITY,
            "dependency": dependency,
            "dependency_wait_outside_gpu_flock": True,
            "stage_order": ["base", "updated"],
            "external_cap_each": 700,
            "no_retry": True,
        },
    )
    private = read(KEY_SOURCE)
    secret = private["vllm"]["api_key"][0]
    records = []
    LOCK.parent.mkdir(parents=True, exist_ok=True)
    with LOCK.open("a+") as lock:
        fcntl.flock(lock, fcntl.LOCK_EX)
        for stage in ("base", "updated"):
            records.append(run_stage(stage, ready, secret))
    write_x(
        OUTPUT / "TERMINAL.json",
        {
            "ended_epoch": time.time(),
            "all_stages_attempted": len(records) == 2,
            "all_stages_complete": all(
                row["returncode"] == 0 and row["terminal"].get("complete") is True
                for row in records
            ),
            "stages": records,
            "credential_persisted": False,
        },
    )


if __name__ == "__main__":
    if len(sys.argv) == 2 and sys.argv[1] == "--verify":
        value = verify_ready()
        print(json.dumps({"ready": value["identity"], "wait_before_flock": True}, sort_keys=True))
    elif len(sys.argv) == 1:
        main()
    else:
        raise SystemExit("usage: run.py [--verify]")
