"""Seal the additive token-decoding repair and its actual native fixture test."""

import subprocess
import time

import study


def main():
    command = [str(study.NATIVE), "-m", "pytest", "-q", "test_repair.py"]
    completed = subprocess.run(command, cwd=study.ROOT, capture_output=True, text=True)
    if completed.returncode:
        raise RuntimeError(
            "focused CPU repair tests failed:\n" + completed.stdout + completed.stderr
        )
    tests = {
        "schema": "fresh-helper-qualification-v2-cpu-tests-v1",
        "command": command,
        "returncode": completed.returncode,
        "stdout": completed.stdout,
        "stderr": completed.stderr,
        "actual_failed_native_response_fixture_exercised": True,
        "ordered_schema_restoration_exercised": True,
        "created_epoch": time.time(),
    }
    tests_path = study.ROOT / "CPU_TESTS.json"
    study.write_x(tests_path, tests)
    fixture_stem = "19d69f810a1aff4702a7109de1934dbc9441cac72b2d7e8d8ab8b729017e304a"
    paths = [
        study.ROOT / name
        for name in (
            "study.py",
            "collect.py",
            "qualify.py",
            "owner.py",
            "seal.py",
            "test_repair.py",
            "CPU_TESTS.json",
        )
    ] + [
        study.INPUTS,
        study.V1_ROOT / "READY_V4.json",
        study.V1_ATTEMPT / "OWNER_TERMINAL.json",
        study.V1_ATTEMPT / "native" / f"{fixture_stem}-REQUEST.json",
        study.V1_ATTEMPT / "native" / f"{fixture_stem}-RESPONSE.json",
        study.V1_ROOT / "owner.py",
        study.V1_ROOT / "qualify.py",
        study.V1_ROOT / "collect.py",
        study.V1 / "leaf_math.py",
        study.V1 / "prepare.py",
        study.V1 / "train.py",
        study.HOST_GOLD,
        study.SOURCE_BINDING,
        study.CHILD_START / "adapter_model.safetensors",
        study.CHILD_START / "adapter_config.json",
        study.BASE_MODEL / "config.json",
        study.SERVICE_WRAPPER,
        study.SERVICE_READY,
        *study.TOKENIZER_FILES,
    ]
    ready = {
        **study.plan(),
        "closure_sha256": {str(path): study.sha(path) for path in paths},
        "claim_boundary": (
            "Prospective helper-only concurrency4 qualification on 48 newly sampled train actions; "
            "the four failed-V1 raw responses are diagnostic fixtures only and are not samples in "
            "this run. This is not HF/vLLM policy identity, historical validation, "
            "high-concurrency validation, or optimizer-update authority."
        ),
        "failure_action": "persist exact diagnostics and stop without retry or optimizer step",
        "created_epoch": time.time(),
    }
    ready["identity"] = study.digest(ready)
    study.write_x(study.ROOT / "READY_V2.json", ready)
    study.write_x(study.ROOT / "READY.json", ready)
    print(ready["identity"])


if __name__ == "__main__":
    main()
