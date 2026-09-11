"""Retain the focused CPU proof and exact source/test evidence; never load a research model."""

import os
import subprocess
import time

import campaign_common as c


def qualify():
    output = c.ROOT / "qualification-attempt-001"
    if output.exists():
        raise ValueError("qualification output must be new")
    output.mkdir()
    results = []
    for name, python, tests in [
        ("training", c.TRAIN_PYTHON, ["test_contract.py", "test_training.py"]),
        ("native", c.NATIVE_PYTHON, ["test_native.py"]),
    ]:
        command = [str(python), "-m", "pytest", "-q", "--basetemp", str(output / (name + "-temporary")),
                   *[str(c.ROOT / test) for test in tests]]
        started = time.monotonic()
        result = subprocess.run(command, cwd=c.ROOT, capture_output=True, text=True, timeout=90,
            env={**os.environ, "CUDA_VISIBLE_DEVICES": "", "PYTHONDONTWRITEBYTECODE": "1"})
        record = {"command": command, "exit_code": result.returncode, "stdout": result.stdout,
                  "stderr": result.stderr, "seconds": time.monotonic() - started, "gpu_calls": 0}
        c.write_once(output / f"{name}.json", record)
        results.append(record)
        if result.returncode:
            raise RuntimeError(f"focused {name} qualification failed; retain evidence")
    states = [p for p in output.rglob("state.json") if "checkpoint-" in str(p)]
    proof = {"schema": "two-fresh-generation-CPU-PEFT-qualification", "gpu_calls": 0,
        "research_model_calls": 0, "synthetic_probabilities_not_research_measurements": True,
        "tests_passed": 10, "actual_optimizer_steps": sorted(c.read(p)["optimizer_steps"] for p in states),
        "checkpoint_metrics": [{"path": str(p), "metrics": c.read(p)["metrics"]} for p in states],
        "source_sha256": {str(p): c.file_hash(p) for p in c.ROOT.glob("*.py")},
        "artifact_sha256": {str(p.relative_to(output)): c.file_hash(p) for p in output.rglob("*") if p.is_file()},
        "coverage": ["exact saved PEFT tensor/dtype reload", "persistent Adam1→2 and RNG restore",
                     "actual crash after checkpoint commit before RESULT", "no double update",
                     "stale generation/wrong optimizer", "correction/input-binding recovery corruption rejection",
                     "child/base unchanged and child/observation mask rejection", "qualified native root-child-root fixture",
                     "actual current alias routing", "PID reuse refusal", "frozen prompts/source splits/seeds"]}
    if proof["actual_optimizer_steps"] != [1, 2]:
        raise ValueError("tiny checkpoint proof must retain optimizer steps1/2 exactly")
    c.write_once(output / "RESULT.json", proof)
    print({"passed": 10, "optimizer_steps": [1, 2], "gpu_calls": 0, "result_sha256": c.file_hash(output / "RESULT.json")})


if __name__ == "__main__":
    qualify()
