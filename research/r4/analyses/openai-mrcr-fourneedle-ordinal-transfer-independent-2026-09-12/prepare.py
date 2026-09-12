"""Seal the one-shot independent CPU analyzer."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
import time


ROOT = Path(__file__).resolve().parent
READY = ROOT / "CPU_READY.json"


def sha(path: Path) -> str:
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def digest(value) -> str:
    return hashlib.sha256(
        json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False).encode()
    ).hexdigest()


def build():
    files = [
        ROOT / name
        for name in ("analyze.py", "test_analyze.py", "run_if_terminal.py", "CPU_TESTS.json", "prepare.py")
    ]
    value = {
        "schema": "openai-mrcr-fourneedle-ordinal-transfer-independent-ready-v1",
        "created_epoch": time.time(),
        "source_ready": str(
            ROOT.parents[1] / "sidecars/openai-mrcr-fourneedle-ordinal-transfer-eval-v1/READY.json"
        ),
        "source_ready_sha256": "02e90c8e7c30a3fc6070a94d03b93b43a14fac3db675d297b84d4b4b8a56324c",
        "attempts": {"base": "outputs/base-001", "checkpoint32": "outputs/checkpoint32-001"},
        "one_shot_after_both_owner_terminals": True,
        "polling": False,
        "gpu_calls": 0,
        "closure_sha256": {str(path): sha(path) for path in files},
    }
    value["identity"] = digest(value)
    with READY.open("x") as stream:
        json.dump(value, stream, indent=2, sort_keys=True, allow_nan=False)
        stream.write("\n")
    return value


def verify():
    value = json.loads(READY.read_text())
    assert value["identity"] == digest({key: item for key, item in value.items() if key != "identity"})
    for path, expected in value["closure_sha256"].items():
        assert sha(Path(path)) == expected, path
    return value


if __name__ == "__main__":
    value = verify() if READY.exists() else build()
    print(json.dumps({"identity": value["identity"], "sha256": sha(READY)}, sort_keys=True))
