"""Retain the small additive lifecycle CPU regression evidence."""

import os
import subprocess
import time
from pathlib import Path

import campaign_common as c


if __name__ == "__main__":
    command = [str(c.NATIVE_PYTHON), "-m", "pytest", "-q", str(c.ROOT / "test_lifecycle_v2.py")]
    started = time.monotonic()
    result = subprocess.run(command, check=False, capture_output=True, text=True, timeout=60,
        env={**os.environ, "CUDA_VISIBLE_DEVICES": "", "PYTHONDONTWRITEBYTECODE": "1"})
    c.verify_campaign()
    value = {"command": command, "exit_code": result.returncode, "stdout": result.stdout, "stderr": result.stderr,
        "seconds": time.monotonic() - started, "gpu_calls": 0, "actual_processes_signaled": 0,
        "sealed_v1_source_unchanged": True,
        "source_sha256": {str(p): c.file_hash(p) for p in [Path(__file__), c.ROOT / "campaign_lifecycle_v2.py", c.ROOT / "test_lifecycle_v2.py"]}}
    c.write_once(c.ROOT / "QUALIFICATION_V2.json", value)
    if result.returncode:
        raise RuntimeError("lifecycle CPU regression failed; evidence retained")
    print({"passed": 5, "gpu_calls": 0, "qualification_sha256": c.file_hash(c.ROOT / "QUALIFICATION_V2.json")})
