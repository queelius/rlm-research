"""Seal the additive Collector.call clock repair without changing V1 inputs."""

import json
import subprocess
import time

import study


READY = study.ROOT / "READY_CALL_REPAIR.json"


def main():
    if READY.exists():
        raise FileExistsError(READY)
    prior = study.verify()
    command = [
        str(study.NATIVE),
        "-m",
        "pytest",
        "-q",
        "-p",
        "no:cacheprovider",
        str(study.ROOT / "test_call_repair.py"),
    ]
    started = time.time()
    process = subprocess.run(command, capture_output=True, text=True, timeout=120)
    receipt_path = study.ROOT / "CPU_TESTS_CALL_REPAIR.json"
    study.write_x(
        receipt_path,
        {
            "command": command,
            "returncode": process.returncode,
            "stdout": process.stdout,
            "stderr": process.stderr,
            "elapsed_seconds": time.time() - started,
            "actual_inherited_collector_call_http_fixture": True,
            "actual_native_decode_and_source_grade": True,
            "model_calls": 0,
            "GPU_calls": 0,
        },
    )
    if process.returncode:
        raise RuntimeError(process.stdout + process.stderr)

    closure = dict(prior["closure_sha256"])
    closure[str(study.READY)] = study.sha(study.READY)
    for name in (
        "study_v2.py",
        "collect_v2.py",
        "owner_v2.py",
        "test_call_repair.py",
        "prepare_v3.py",
        "CALL_REPAIR_ADDENDUM.md",
        "CPU_TESTS_CALL_REPAIR.json",
    ):
        path = study.ROOT / name
        closure[str(path)] = study.sha(path)
    value = {
        "schema": "b05-qwen3-8b-direct-oracle-ready-call-repair-v1",
        "created_epoch": time.time(),
        "supersedes_ready_sha256": study.sha(study.READY),
        "same_scientific_inputs": True,
        "repair": "bind inherited Collector.call clock to time.time",
        "question": prior["question"],
        "claim_boundary": prior["claim_boundary"],
        "oracle_boundary": "nondeployable exact child reports supplied; root answer not supplied",
        "model": prior["model"],
        "renderer": prior["renderer"],
        "planned": prior["planned"],
        "sampling": prior["sampling"],
        "seeds": prior["seeds"],
        "metrics": prior["metrics"],
        "caps_seconds": prior["caps_seconds"],
        "attempt": str(study.ROOT / "outputs/attempt-002"),
        "model_calls_during_preparation": 0,
        "GPU_calls_during_preparation": 0,
        "argv": [
            str(study.NATIVE),
            str(study.ROOT / "owner_v2.py"),
            "run",
            "--outer-seconds",
            "450",
        ],
        "closure_sha256": dict(sorted(closure.items())),
    }
    value["identity"] = study.digest(value)
    study.write_x(READY, value)
    print(json.dumps({"sha256": study.sha(READY), "identity": value["identity"]}, sort_keys=True))


if __name__ == "__main__":
    main()
