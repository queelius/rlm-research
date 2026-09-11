"""Seal the immutable CPU-qualified positional-anchor96 package."""

import json
import time
from pathlib import Path

import protocol as p
import study as s


SOURCE_NAMES = (
    "DESIGN.md",
    "PLAN.md",
    "IMPLEMENTATION_REPORT.md",
    "CPU_TESTS.json",
    "study.py",
    "protocol.py",
    "scoring.py",
    "collect.py",
    "owner.py",
    "service_wrapper.py",
    "prepare.py",
    "seal.py",
    "test_position_anchor.py",
    "test_runtime.py",
    "test_frozen.py",
)


def main():
    if s.READY_PATH.exists() or s.ATTEMPT.exists():
        raise ValueError("unused seal and attempt required")
    plan = s.read(s.ROOT / "inputs/PLAN.json")
    if plan != p.plan() or len(plan) != 96:
        raise ValueError("frozen plan changed")
    inputs = sorted(path for path in (s.ROOT / "inputs").glob("*.json"))
    ready = {
        "schema": "leaf_mnli_positional_anchor_binding_ready_v1",
        "created_epoch": time.time(),
        "question": "Can fixed output row anchors preserve late-position classification correspondence, and does a matching input row marker strengthen that effect?",
        "planned": 96,
        "contexts": 8,
        "records_per_call": 48,
        "arms": list(p.ARMS),
        "seeds": list(p.SEEDS),
        "model": s.MODEL,
        "outer_seconds": 1800,
        "work_seconds": 1650,
        "owned_seconds": 1770,
        "workers": 4,
        "request_seconds": 90,
        "no_training": True,
        "no_gpu_launch": True,
        "source_sha256": {
            **{str(s.ROOT / name): s.sha(s.ROOT / name) for name in SOURCE_NAMES},
            str(s.PRIOR / "READY_v2.json"): s.sha(s.PRIOR / "READY_v2.json"),
            str(s.PRIOR / "service_wrapper_v2.py"): s.sha(s.PRIOR / "service_wrapper_v2.py"),
            str(s.SIDE / "leaf-role-tool-contract-v1/scoring_v2.py"): s.sha(s.SIDE / "leaf-role-tool-contract-v1/scoring_v2.py"),
            str(Path(s.MODEL["path"]) / "config.json"): s.sha(Path(s.MODEL["path"]) / "config.json"),
            str(Path(s.MODEL["path"]) / "generation_config.json"): s.sha(Path(s.MODEL["path"]) / "generation_config.json"),
            str(Path(s.MODEL["path"]) / "tokenizer.json"): s.sha(Path(s.MODEL["path"]) / "tokenizer.json"),
            str(Path(s.MODEL["path"]) / "tokenizer_config.json"): s.sha(Path(s.MODEL["path"]) / "tokenizer_config.json"),
        },
        "input_sha256": {str(path): s.sha(path) for path in inputs},
    }
    ready["identity"] = s.digest(ready)
    s.write(s.READY_PATH, ready)
    print({"identity": ready["identity"], "source_pins": len(ready["source_sha256"]), "input_pins": len(ready["input_sha256"])})


if __name__ == "__main__":
    main()
