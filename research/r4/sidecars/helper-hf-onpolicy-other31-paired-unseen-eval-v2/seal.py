"""Seal both conditional native arms without initializing any GPU runtime."""

import datetime
import os
import subprocess

import paired_eval_study as study


def main():
    if os.environ.get("CUDA_VISIBLE_DEVICES") != "":
        raise ValueError("CPU seal requires hidden CUDA")
    if any(row["ready"].exists() for row in study.ARMS.values()):
        raise ValueError("READY already exists")
    training_path = study.TRAINING / "READY.json"
    training = study.read(training_path)
    if (
        study.sha(training_path) != study.TRAIN_READY_SHA256
        or training["identity"] != study.TRAIN_READY_IDENTITY
    ):
        raise ValueError("wrong repaired training source")
    old_path = study.V1 / "READY_RLOO.json"
    old = study.read(old_path)
    pins = {}
    for ready in (old, training):
        study.verify_hash_map(ready["closure_sha256"])
        for path, expected in ready["closure_sha256"].items():
            if path in pins and pins[path] != expected:
                raise ValueError("source closures conflict")
            pins[path] = expected
    command = [str(study.NATIVE), "-m", "pytest", "-q", str(study.ROOT / "test_eval.py")]
    result = subprocess.run(
        command, cwd=study.ROOT, env=dict(os.environ), capture_output=True, text=True, timeout=90
    )
    study.write_x(
        study.ROOT / "CPU_TESTS.json",
        {
            "argv": command,
            "returncode": result.returncode,
            "stdout": result.stdout,
            "stderr": result.stderr,
            "CUDA_VISIBLE_DEVICES": "",
        },
    )
    if result.returncode:
        raise RuntimeError(result.stdout + result.stderr)
    direct = [training_path, old_path, study.V1 / "paired_eval_study.py", study.V1 / "owner.py"]
    direct += list(study.ROOT.glob("*.py")) + list(study.ROOT.glob("*.md"))
    direct.append(study.ROOT / "CPU_TESTS.json")
    pins.update({str(path.resolve()): study.sha(path) for path in direct})
    output = {}
    for branch in study.ARMS:
        ready = {
            **study.plan(branch),
            "created_at": datetime.datetime.now(datetime.UTC).isoformat(),
            "closure_sha256": dict(sorted(pins.items())),
            "training_ready_sha256": study.TRAIN_READY_SHA256,
            "training_ready_identity": study.TRAIN_READY_IDENTITY,
            "eligibility": (
                "both UPDATED plus original full gates, source byte reuse, actual initial states"
            ),
            "comparison": (
                "fixed rloo versus other31; same128 training actions and frozen256 readout"
            ),
            "claim_boundary": (
                "exploratory; readout exposed to earlier research, no outcome selection"
            ),
            "source_v1_readout_unchanged": True,
            "gpu_launched": False,
        }
        ready["identity"] = study.digest(ready)
        study.write_x(study.ready_path(branch), ready)
        study.verify(branch, require_training=False)
        output[branch] = {
            "ready_sha256": study.sha(study.ready_path(branch)),
            "identity": ready["identity"],
            "closure_files": len(pins),
            "argv": ready["command"],
        }
    print({"arms": output, "tests": result.stdout})


if __name__ == "__main__":
    main()
