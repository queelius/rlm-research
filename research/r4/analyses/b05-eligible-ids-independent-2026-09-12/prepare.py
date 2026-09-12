"""Seal the one-shot IDs-only CPU analyzer; no model calls."""

from datetime import datetime, timezone
import json
from pathlib import Path
import subprocess

import analyze


HERE = Path(__file__).resolve().parent
PYTHON = Path("/project/alex_phd/envs/prime-rl-5990b1b/bin/python")


def main():
    path = HERE / "CPU_READY.json"
    if path.exists():
        raise FileExistsError(path)
    command = [str(PYTHON), "-m", "pytest", "-q", "test_analyze.py"]
    completed = subprocess.run(command, cwd=HERE, capture_output=True, text=True, check=True)
    files = [HERE / name for name in ("analyze.py", "test_analyze.py", "run_if_terminal.py", "prepare.py")]
    ready = {
        "schema": "b05-eligible-ids-independent-analyzer-ready-v1",
        "status": "CPU_READY_ONE_SHOT_NO_POLL",
        "created_utc": datetime.now(timezone.utc).isoformat(),
        "source_ready": str(analyze.READY),
        "source_ready_sha256": analyze.sha(analyze.READY),
        "source_attempt": str(analyze.ATTEMPT),
        "paired_baseline_ready": str(analyze.BASELINE_READY),
        "paired_baseline_ready_sha256": analyze.sha(analyze.BASELINE_READY),
        "command": [str(PYTHON), str(HERE / "run_if_terminal.py")],
        "tests": {"command": command, "passed": 3, "stdout": completed.stdout},
        "closure_sha256": {str(file): analyze.sha(file) for file in files},
        "gpu_calls": 0,
        "model_calls": 0,
    }
    study, _interface = analyze.modules()
    ready["identity"] = study.digest(ready)
    analyze.write_x(path, ready)
    print(
        json.dumps(
            {"ready": str(path), "sha256": analyze.sha(path), "identity": ready["identity"]}
        )
    )


if __name__ == "__main__":
    main()
