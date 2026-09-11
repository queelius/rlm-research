"""Seal the CPU-qualified fresh-context replication."""

import time
from pathlib import Path

import study as s


def main():
    if s.ATTEMPT.exists() or s.READY_PATH.exists():
        raise ValueError("requires unused output and READY paths")
    sources = [s.ROOT / name for name in ("DESIGN.md", "PLAN.md", "IMPLEMENTATION_REPORT.md", "study.py", "protocol.py", "prepare.py", "scoring.py", "collect.py", "owner.py", "service_wrapper.py", "seal.py", "test_science.py", "test_runtime.py", "CPU_TESTS.json")]
    inherited = [s.PRIOR / name for name in ("READY_RECOVERY.json", "study.py", "scoring.py", "collect.py", "owner.py", "service_wrapper_v2.py")] + [s.LOADER / name for name in ("READY.json", "prepare.py")]
    model = Path(s.MODEL["path"])
    auxiliary = [model / name for name in ("config.json", "tokenizer.json", "tokenizer_config.json", "generation_config.json", "local-research-manifest.json")]
    inputs = [s.ROOT / name for name in ("DATA.json", "PUBLIC.json", "ALIEN_DICTIONARIES.json", "PLAN.json", "REQUESTS.json", "ORDERED_REQUESTS.json", "PROMPT_IDS.json", "CPU_NATIVE.json", "PLANNED_NULL_ENDPOINTS.json", "SELECTION_AUDIT.json", "SEED_SCAN.json", "DATASET_MANIFEST.json")]
    ready = {"schema": "leaf-mnli-positional-anchor-new-context-ready-v1", "created_epoch": time.time(), "question": "Does the late-position input-row by output-row interaction replicate on 16 new contexts?", "planned": 192, "contexts": 16, "arms": list(__import__("protocol").ARMS), "primary": "late input-row by output-row interaction averaged over three references", "gate": {"minimum_points": 10, "minimum_positive_contexts": 12, "no_availability_loss": True, "practical_general_remedy_requires_all_three_reference_gains": True}, "secondary": "unchanged output-only late-position gate", "seeds": list(__import__("protocol").SEEDS), "model": s.MODEL, "adapter": None, "workers": 4, "request_seconds": 90, "outer_seconds": 1800, "work_seconds": 1650, "owned_seconds": 1770, "no_gpu_launch": True, "source_sha256": {str(path): s.sha(path) for path in sources + inherited + auxiliary}, "input_sha256": {str(path): s.sha(path) for path in inputs}}
    ready["identity"] = s.digest(ready)
    s.write(s.READY_PATH, ready)
    print(ready["identity"])


if __name__ == "__main__":
    main()
