"""Seal the CPU-qualified study without creating its output namespace."""

import time
from pathlib import Path

import study as s


def main():
    if s.ATTEMPT.exists() or (s.ROOT / "READY.json").exists():
        raise ValueError("requires unused output and READY paths")
    sources = [s.ROOT / name for name in (
        "DESIGN.md", "PLAN.md", "IMPLEMENTATION_REPORT.md", "study.py", "protocol.py",
        "prepare.py", "collect.py", "owner.py", "seal.py", "test_task.py",
        "test_native_entry.py", "test_frozen.py", "CPU_INPUT_NATIVE.json", "CPU_TESTS.json",
    )]
    inherited = [s.PRIOR / name for name in ("READY.json", "study.py", "collect.py", "owner.py")]
    model = Path(s.BASE_MODEL)
    auxiliary = [model / name for name in ("config.json", "tokenizer.json", "tokenizer_config.json", "generation_config.json", "local-research-manifest.json")]
    inputs = [s.ROOT / "inputs" / name for name in ("PUBLIC.json", "HOST_GOLD.json", "PLAN.json", "REQUESTS.json", "PROVENANCE.json", "SEED_SCAN.json")]
    ready = {
        "schema": "leaf-trec-query-conditioned-interface-ready-v1",
        "created_epoch": time.time(),
        "question": "Does asking the child only for A/B/other improve task-relevant TREC classification over full-six labels?",
        "planned": 192,
        "selected_official_test_records": 128,
        "batches": 8,
        "pairs": 6,
        "model_policies": ["base", "c32"],
        "interfaces": ["full6", "abo"],
        "seeds": list(s.SEEDS),
        "base_model": s.BASE_MODEL,
        "child": s.read(s.PRIOR / "READY.json")["child"],
        "workers": 4,
        "request_seconds": 90,
        "outer_seconds": 1800,
        "work_seconds": 1650,
        "owned_seconds": 1770,
        "no_training": True,
        "no_root_calls": True,
        "no_gpu_launch": True,
        "source_sha256": {str(path): s.sha(path) for path in sources + inherited + auxiliary},
        "input_sha256": {str(path): s.sha(path) for path in inputs},
    }
    ready["identity"] = s.digest(ready)
    s.write(s.ROOT / "READY.json", ready)
    print(ready["identity"])


if __name__ == "__main__":
    main()
