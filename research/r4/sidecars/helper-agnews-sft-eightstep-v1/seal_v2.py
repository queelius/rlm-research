"""Additive V2 seal for corrected loss-decomposition spans only."""

import datetime
import json
import os
import subprocess

import sft_study_v2 as study


def main():
    if os.environ.get("CUDA_VISIBLE_DEVICES") != "" or study.ATTEMPT.exists() or (study.ROOT / "READY_V2.json").exists():
        raise ValueError("CPU-only unused output/V2 READY required")
    prior_path = study.ROOT / "READY.json"
    prior = study.read(prior_path)
    if study.digest({k: v for k, v in prior.items() if k != "identity"}) != prior["identity"]:
        raise ValueError("V1 READY identity changed")
    for path, expected in prior["closure_sha256"].items():
        if study.sha(path) != expected:
            raise ValueError("V1 closure changed: " + path)
    if study.sha(study.ROOT / "train_sft.py") != study.sha(study.ROOT / "train_sft_v2_source.py"):
        raise ValueError("V2 changed training objective source")
    command = [str(study.TRAIN_PYTHON), "-m", "pytest", "-q", str(study.ROOT / "test_sft_v2.py")]
    tested = subprocess.run(
        command, cwd=study.ROOT, env={**os.environ, "CUDA_VISIBLE_DEVICES": "", "PYTHONDONTWRITEBYTECODE": "1"},
        capture_output=True, text=True, timeout=120,
    )
    if tested.returncode:
        raise RuntimeError(tested.stdout + tested.stderr)
    study.write_x(
        study.ROOT / "CPU_TESTS_V2.json",
        {
            "command": command,
            "returncode": tested.returncode,
            "stdout": tested.stdout,
            "stderr": tested.stderr,
            "unchanged_objective_source_sha256": study.sha(study.ROOT / "train_sft.py"),
            "inner_label_overlap_tokens": 1536,
            "prior_quote_inclusive_overlap_tokens": 3584,
            "CUDA_VISIBLE_DEVICES": "",
        },
    )
    closure = dict(prior["closure_sha256"])
    closure[str(prior_path)] = study.sha(prior_path)
    for name in (
        "sft_study_v2.py", "train_sft_v2_source.py", "train_sft_v2.py", "owner_v2.py",
        "test_sft_v2.py", "seal_v2.py", "CPU_TESTS_V2.json",
    ):
        path = study.ROOT / name
        closure[str(path)] = study.sha(path)
    ready = {
        **study.plan(),
        "created_at": datetime.datetime.now(datetime.UTC).isoformat(),
        "closure_sha256": dict(sorted(closure.items())),
        "supersedes_unlaunched_ready_sha256": study.sha(prior_path),
        "repair_scope": "diagnostic inner label-value token spans only; objective inputs and gradients unchanged",
        "full_vocab_supervised_tokens": 20591,
        "inner_label_overlap_tokens": 1536,
        "inner_label_fraction": 1536 / 20591,
        "gpu_launched": False,
    }
    ready["identity"] = study.digest(ready)
    study.write_x(study.ROOT / "READY_V2.json", ready)
    study.verify()
    print(json.dumps({"ready_sha256": study.sha(study.ROOT / "READY_V2.json"), "identity": ready["identity"], "command": ready["command"], "tests": tested.stdout.strip()}, sort_keys=True))


if __name__ == "__main__":
    main()
