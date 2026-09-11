"""Seal the CPU-qualified study without touching an output namespace."""
import time
from pathlib import Path

import study as s


def main():
    if s.ATTEMPT.exists() or (s.ROOT / "READY.json").exists():
        raise ValueError("requires unused output and READY paths")
    sources = [s.ROOT / name for name in ("DESIGN.md", "PLAN.md", "IMPLEMENTATION_REPORT.md", "study.py", "protocol.py", "prepare.py", "collect.py", "owner.py", "seal.py", "test_study.py", "test_frozen.py", "CPU_INPUT_NATIVE.json", "CPU_TESTS.json")]
    inherited = [s.PRIOR / "READY.json", s.PRIOR / "bg_study.py", s.PRIOR / "bg_collect.py"]
    model = Path(s.BASE_MODEL)
    auxiliary = [model / name for name in ("config.json", "tokenizer.json", "tokenizer_config.json", "generation_config.json", "local-research-manifest.json")]
    inputs = [s.ROOT / "inputs" / name for name in ("PUBLIC.json", "HOST_GOLD.json", "PLAN.json", "REQUESTS.json", "PROVENANCE.json", "SEED_SCAN.json")]
    ready = {"schema": "leaf-trec-test-adapter-granularity-ready-v1", "created_epoch": time.time(), "question": "Does c32's exposed-context semantic gain transfer to the complete official TREC test source, and does width change it?", "planned": 148, "official_test_rows": 500, "normalized_groups": 500, "optimizer_train_intersection": 0, "prior_research_evaluated_groups": 489, "raw_train_overlap_groups": 11, "model_policies": ["base", "c32"], "arms": ["W100", "S16"], "seeds": list(s.SEEDS), "base_model": s.BASE_MODEL, "child": s.read(s.PRIOR / "READY.json")["child"], "workers": 4, "request_seconds": 90, "outer_seconds": 1800, "work_seconds": 1650, "owned_seconds": 1770, "no_training": True, "no_gpu_launch": True, "source_sha256": {str(path): s.sha(path) for path in sources + inherited + auxiliary}, "input_sha256": {str(path): s.sha(path) for path in inputs}}
    ready["identity"] = s.digest(ready)
    s.write(s.ROOT / "READY.json", ready)
    print(ready["identity"])


if __name__ == "__main__":
    main()
