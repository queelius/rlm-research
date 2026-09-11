"""Own one training process group and enforce the overall90-minute envelope."""

import argparse
import json
import os
import signal
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent


def write(path, value):
    with path.open("x") as stream:
        json.dump(value, stream, indent=2, allow_nan=False)
        stream.write("\n")


def run_owned(command, output, *, wall_seconds=5400, grace_seconds=30):
    output.mkdir(parents=True, exist_ok=False)
    started = time.monotonic()
    write(
        output / "RUN.json",
        {
            "command": command,
            "started_utc": datetime.now(timezone.utc).isoformat(),
            "started_epoch": time.time(),
            "overall_wall_cap_seconds": wall_seconds,
            "cleanup_grace_seconds": grace_seconds,
            "cuda_visible_devices": os.environ.get("CUDA_VISIBLE_DEVICES"),
            "ownership": "new child process group only",
        },
    )
    timed_out = False
    with (output / "stdout.log").open("x") as log:
        process = subprocess.Popen(
            command, stdout=log, stderr=subprocess.STDOUT, start_new_session=True
        )
        write(
            output / "OWNER.json",
            {"pid": process.pid, "pgid": process.pid, "command": command},
        )
        try:
            code = process.wait(timeout=wall_seconds)
        except subprocess.TimeoutExpired:
            timed_out = True
            os.killpg(process.pid, signal.SIGTERM)
            try:
                code = process.wait(timeout=grace_seconds)
            except subprocess.TimeoutExpired:
                os.killpg(process.pid, signal.SIGKILL)
                code = process.wait()
        except BaseException:
            if process.poll() is None:
                os.killpg(process.pid, signal.SIGTERM)
                try:
                    process.wait(timeout=grace_seconds)
                except subprocess.TimeoutExpired:
                    os.killpg(process.pid, signal.SIGKILL)
                    process.wait()
            raise
    result = {
        "exit_code": code,
        "timed_out": timed_out,
        "elapsed_seconds": time.monotonic() - started,
        "finished_utc": datetime.now(timezone.utc).isoformat(),
        "last_committed_checkpoints_retained": True,
    }
    write(output / "FINISH.json", result)
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--attempt", type=Path, default=ROOT / "outputs/attempt-001")
    parser.add_argument("--resume", action="store_true")
    args = parser.parse_args()
    if not os.environ.get("CUDA_VISIBLE_DEVICES"):
        raise ValueError("parent must explicitly assign the released GPU")
    # Deadline belongs to the attempt, not a fresh90-minute allowance on resume.
    clock_path = args.attempt.parent / (args.attempt.name + "-OVERALL_CLOCK.json")
    args.attempt.parent.mkdir(parents=True, exist_ok=True)
    if clock_path.exists():
        if not args.resume:
            raise ValueError("existing overall attempt clock requires explicit resume")
        clock = json.loads(clock_path.read_text())
    else:
        if args.resume:
            raise ValueError("resume requires existing overall clock")
        clock = {
            "attempt": str(args.attempt),
            "started_epoch": time.time(),
            "deadline_epoch": time.time() + 5400,
            "overall_cap_seconds": 5400,
        }
        write(clock_path, clock)
    if clock["attempt"] != str(args.attempt):
        raise ValueError("attempt clock identity differs")
    remaining = clock["deadline_epoch"] - time.time()
    if remaining <= 0:
        raise TimeoutError("attempt overall90-minute deadline exhausted")
    command = [
        sys.executable,
        str(ROOT / "driver.py"),
        "train",
        "--attempt",
        str(args.attempt),
    ]
    if args.resume:
        command.append("--resume")
    launch_dir = args.attempt.parent / (
        args.attempt.name + "-launch-" + str(time.time_ns())
    )
    result = run_owned(command, launch_dir, wall_seconds=remaining)
    print(json.dumps({"launch_dir": str(launch_dir), **result}), flush=True)
    raise SystemExit(124 if result["timed_out"] else result["exit_code"])


if __name__ == "__main__":
    main()
