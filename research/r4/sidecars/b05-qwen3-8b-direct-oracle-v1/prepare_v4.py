"""Seal attempt-003 after the exact engine-entry lifecycle repair."""

import json
import subprocess
import time

import study


READY = study.ROOT / "READY_LIFECYCLE_REPAIR.json"
CLEANUP = study.ROOT.parents[1] / "operations/2026-09-13-b05-alternative-model/OWNED_SIGTERM.json"


def main():
    if READY.exists():
        raise FileExistsError(READY)
    prior = study.read(study.ROOT / "READY_CALL_REPAIR.json")
    failed = study.ROOT / "outputs/attempt-002/OWNER_TERMINAL.json"
    terminal = study.read(failed)
    assert not terminal["complete"] and not terminal["released"]
    assert CLEANUP.exists()
    command = [str(study.NATIVE), "-m", "pytest", "-q", "-p", "no:cacheprovider",
               str(study.ROOT / "test_lifecycle_repair.py")]
    started = time.time()
    process = subprocess.run(command, capture_output=True, text=True, timeout=120)
    receipt = study.ROOT / "CPU_TESTS_LIFECYCLE_REPAIR.json"
    study.write_x(receipt, {"command": command, "returncode": process.returncode,
        "stdout": process.stdout, "stderr": process.stderr, "elapsed_seconds": time.time()-started,
        "actual_suite_start_claim_release_fixture": True, "model_calls": 0, "GPU_calls": 0})
    if process.returncode:
        raise RuntimeError(process.stdout + process.stderr)
    closure = dict(prior["closure_sha256"])
    closure[str(study.ROOT / "READY_CALL_REPAIR.json")] = study.sha(study.ROOT / "READY_CALL_REPAIR.json")
    closure[str(failed)] = study.sha(failed)
    closure[str(CLEANUP)] = study.sha(CLEANUP)
    for name in ("study_v3.py", "collect_v3.py", "owner_v3.py", "test_lifecycle_repair.py",
                 "prepare_v4.py", "CPU_TESTS_LIFECYCLE_REPAIR.json"):
        path = study.ROOT / name
        closure[str(path)] = study.sha(path)
    value = {"schema": "b05-qwen3-8b-direct-oracle-ready-lifecycle-repair-v1",
        "created_epoch": time.time(), "supersedes_ready_sha256": study.sha(study.ROOT / "READY_CALL_REPAIR.json"),
        "same_scientific_inputs": True,
        "repair": "install exact engine-entry lifecycle claim and retain custom 8B service identity",
        "prior_attempt002_preserved_unknown8": True, "prior_cleanup_receipt_sha256": study.sha(CLEANUP),
        "question": prior["question"], "claim_boundary": prior["claim_boundary"],
        "oracle_boundary": prior["oracle_boundary"], "model": prior["model"],
        "renderer": prior["renderer"], "planned": prior["planned"], "sampling": prior["sampling"],
        "seeds": prior["seeds"], "metrics": prior["metrics"], "caps_seconds": prior["caps_seconds"],
        "attempt": str(study.ROOT / "outputs/attempt-003"), "model_calls_during_preparation": 0,
        "GPU_calls_during_preparation": 0,
        "argv": [str(study.NATIVE), str(study.ROOT / "owner_v3.py"), "run", "--outer-seconds", "450"],
        "closure_sha256": dict(sorted(closure.items()))}
    value["identity"] = study.digest(value)
    study.write_x(READY, value)
    print(json.dumps({"sha256": study.sha(READY), "identity": value["identity"]}, sort_keys=True))


if __name__ == "__main__":
    main()
