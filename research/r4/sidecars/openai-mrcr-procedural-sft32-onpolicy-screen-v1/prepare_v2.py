"""Seal additive V2 launch repair without changing scientific inputs."""

from __future__ import annotations

import json
from pathlib import Path
import time

import checkpoint_v2 as checkpoint
import study_v2 as study


V1 = study.ROOT / "CPU_READY.json"


def build() -> dict:
    if study.READY.exists():
        raise FileExistsError("CPU_READY_V2 already exists")
    v1 = study.read(V1)
    if v1.get("identity") != study.digest({key: value for key, value in v1.items() if key != "identity"}):
        raise ValueError("V1 READY identity changed")
    for raw, expected in v1["closure_sha256"].items():
        if study.sha(Path(raw)) != expected:
            raise ValueError("V1 closure changed: " + raw)
    checkpoint.verify_checkpoint()
    study.terminal_hooks()
    added = [study.ROOT / name for name in (
        "study_v2.py", "checkpoint_v2.py", "collect_v2.py", "owner_v2.py",
        "prepare_v2.py", "test_repair_v2.py",
    )]
    value = {
        **{key: item for key, item in v1.items() if key not in ("identity", "created_epoch", "closure_sha256", "output")},
        "schema": "openai-mrcr-procedural-sft32-onpolicy-screen-ready-v2",
        "created_epoch": time.time(),
        "repair": {
            "only_change": "collector READY lookup uses inputs.schedule_sha256 exactly as sealed",
            "v1_ready": str(V1),
            "v1_ready_sha256": study.sha(V1),
            "v1_identity": v1["identity"],
            "science_schedule_changed": False,
            "sampling_changed": False,
            "checkpoint_changed": False,
            "terminal_hooks_changed": False,
        },
        "output": str(study.ROOT / "outputs/attempt-002"),
        "closure_sha256": {
            **v1["closure_sha256"], str(V1): study.sha(V1),
            **{str(path): study.sha(path) for path in added},
        },
    }
    value["identity"] = study.digest(value)
    study.write_x(study.READY, value)
    return value


def verify() -> dict:
    ready = study.read(study.READY)
    if ready.get("identity") != study.digest({key: value for key, value in ready.items() if key != "identity"}):
        raise ValueError("V2 READY identity changed")
    for raw, expected in ready["closure_sha256"].items():
        if study.sha(Path(raw)) != expected:
            raise ValueError("V2 closure changed: " + raw)
    return ready


if __name__ == "__main__":
    value = verify() if study.READY.exists() else build()
    print(json.dumps({"identity": value["identity"], "sha256": study.sha(study.READY)}, sort_keys=True))
