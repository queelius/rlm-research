"""Additive watcher for the exact audited source-to-raw comparator."""

import hashlib
import json
import os
from pathlib import Path
import subprocess
import time

HERE = Path(__file__).resolve().parent
STORE = HERE.parents[1]
SIDE = STORE / "sidecars/helper-trec-retention-b4-eval-v1"
ARMS = ("c32", "rl_step8", "sft_step8")
PYTHON = "/project/alex_phd/envs/prime-rl-5990b1b/bin/python"


def main():
    started = time.time()
    terminals = [SIDE / "outputs" / f"{arm}-001/OWNER_TERMINAL.json" for arm in ARMS]
    deadline = started + 4 * 60 * 60
    while time.time() < deadline and not all(path.exists() for path in terminals):
        time.sleep(min(30, max(0, deadline - time.time())))
    status = "TIMEOUT"
    run = None
    if all(path.exists() for path in terminals):
        run = subprocess.run(
            [PYTHON, str(HERE / "compare.py")], cwd=HERE, capture_output=True, text=True, timeout=900,
            env={**os.environ, "CUDA_VISIBLE_DEVICES": "", "PYTHONDONTWRITEBYTECODE": "1"},
        )
        status = "COMPLETE" if run.returncode == 0 else "COMPARATOR_FAILED"
        if run.returncode == 0:
            result = json.loads(run.stdout)
            with (HERE / "SOURCE_TO_RAW_RESULT.json").open("x") as stream:
                json.dump(result, stream, indent=2, sort_keys=True)
                stream.write("\n")
    receipt = {
        "status": status,
        "elapsed_seconds": time.time() - started,
        "returncode": run.returncode if run else None,
        "stderr": run.stderr if run else "",
        "terminal_sha256": {str(path): hashlib.sha256(path.read_bytes()).hexdigest() for path in terminals if path.exists()},
        "comparator_sha256": hashlib.sha256((HERE / "compare.py").read_bytes()).hexdigest(),
        "gpu_calls": 0,
    }
    with (HERE / "SOURCE_TO_RAW_WATCH_TERMINAL.json").open("x") as stream:
        json.dump(receipt, stream, indent=2, sort_keys=True)
        stream.write("\n")
    raise SystemExit(run.returncode if run else 2)


if __name__ == "__main__":
    if os.environ.get("CUDA_VISIBLE_DEVICES") not in (None, ""):
        raise ValueError("watcher requires CUDA hidden")
    main()

