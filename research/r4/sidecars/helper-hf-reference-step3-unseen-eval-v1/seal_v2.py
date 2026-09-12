"""Seal the additive response-interface repair without modifying V1."""

import copy
import json
import os
import subprocess
import time

import study as base


def main():
    if os.environ.get("CUDA_VISIBLE_DEVICES") != "": raise ValueError("CPU-only seal")
    output = base.ROOT / "READY_V2.json"
    if output.exists(): raise FileExistsError(output)
    tests = subprocess.run([str(base.NATIVE), "-m", "pytest", "-q", "test_reference_step3_v2.py"],
        cwd=base.ROOT, capture_output=True, text=True, timeout=60,
        env={**os.environ, "CUDA_VISIBLE_DEVICES": ""})
    base.write_x(base.ROOT / "CPU_TESTS_V2.json", {"returncode": tests.returncode,
        "stdout": tests.stdout, "stderr": tests.stderr})
    if tests.returncode: raise ValueError("V2 tests failed")
    prior_path = base.ROOT / "READY.json"; value = copy.deepcopy(base.read(prior_path)); value.pop("identity")
    value.update(schema="helper-hf-reference-step3-unseen-ready-v2",
        status="CPU_READY_REFERENCE_MATCHED_THREE_UPDATE_CONTROL_V2", created_epoch=time.time(),
        supersedes_unlaunched_ready=str(prior_path), supersedes_unlaunched_ready_sha256=base.sha(prior_path),
        repair="Export the exact child alias through the collector study facade and exercise native response normalization.",
        command=[str(base.NATIVE), str(base.ROOT / "owner_v2.py"), "run", "--outer-seconds", "600"],
        cpu_tests=tests.stdout.strip())
    closure = dict(value["closure_sha256"])
    files = [prior_path, base.ROOT / "study_v2.py", base.ROOT / "owner_v2.py",
        base.ROOT / "test_reference_step3_v2.py", base.ROOT / "seal_v2.py", base.ROOT / "CPU_TESTS_V2.json"]
    closure.update({str(file): base.sha(file) for file in files}); value["closure_sha256"] = closure
    value["identity"] = base.digest(value); base.write_x(output, value)
    print(json.dumps({"path": str(output), "sha256": base.sha(output), "identity": value["identity"]}, sort_keys=True))


if __name__ == "__main__": main()
