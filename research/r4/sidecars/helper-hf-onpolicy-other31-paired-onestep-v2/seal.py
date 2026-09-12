"""CPU seal of the diagnosed branch repair and exact source-action proof."""

import os
import shutil
import subprocess
import time

import repair as r


def main():
    if os.environ.get("CUDA_VISIBLE_DEVICES") != "" or (r.ROOT / "READY.json").exists():
        raise ValueError("CPU-only unused repair seal required")
    source = r.old.verify()
    proof, _ordered, _records, _collection = r.validate_source()
    r.old.write(r.ROOT / "SOURCE_PROOF.json", proof)
    (r.ROOT / "inputs").mkdir(exist_ok=True)
    for name in ("GROUPS.json", "TRAIN_GOLD.json", "SOURCES.json"):
        shutil.copyfile(r.V1 / "inputs" / name, r.ROOT / "inputs" / name)
    began = time.monotonic()
    argv = [str(r.old.TRAIN_PYTHON), "-m", "pytest", "-q", str(r.ROOT / "test_repair.py")]
    result = subprocess.run(argv, capture_output=True, text=True, timeout=120, check=False)
    tests = {
        "argv": argv,
        "returncode": result.returncode,
        "stdout": result.stdout,
        "stderr": result.stderr,
        "elapsed_seconds": time.monotonic() - began,
        "actual_branch_initializer_wired": True,
        "actual_adam_step_then_model_rng_restore": True,
    }
    r.old.write(r.ROOT / "CPU_TESTS.json", tests)
    if result.returncode:
        raise RuntimeError("actual branch restore regression failed")
    closure = dict(source["closure_sha256"])
    closure.update(proof["source_files_sha256"])
    own = list(r.ROOT.glob("*.py")) + list(r.ROOT.glob("*.md"))
    own += [r.ROOT / "SOURCE_PROOF.json", r.ROOT / "CPU_TESTS.json", r.V1 / "READY.json"]
    own += list((r.ROOT / "inputs").glob("*.json"))
    closure.update({str(path): r.old.sha(path) for path in own})
    ready = {
        **r.plan(),
        "closure_sha256": closure,
        "source_reuse": proof,
        "source_restore_rng": str(r.old.REFERENCE / "rng_receipts.py"),
        "source_restore_binding": "implementation.save_rng.__globals__[restore_rng]",
        "gpu_launched": False,
        "cpu_tests": tests["stdout"],
        "created_epoch": time.time(),
    }
    ready["identity"] = r.old.digest(ready)
    r.old.write(r.ROOT / "READY.json", ready)
    r.verify()
    print(
        {
            "ready_sha256": r.old.sha(r.ROOT / "READY.json"),
            "identity": ready["identity"],
            "closure_files": len(closure),
            "source_correct": proof["correct"],
            "source_mixed_groups": proof["mixed_groups"],
            "tests": tests["stdout"],
        }
    )


if __name__ == "__main__":
    main()
