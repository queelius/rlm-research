"""Seal exact-full-query V3 after focused CPU integration checks."""

import json
import os
import subprocess
import time

import study
import study_v3


def main():
    if os.environ.get("CUDA_VISIBLE_DEVICES") != "": raise ValueError("CPU-only preparation")
    ready_path = study.ROOT / "READY_V3.json"
    if ready_path.exists(): raise FileExistsError(ready_path)
    prepared = study_v3.prepare_inputs(study_v3.INPUTS)
    original = study.read(study.ROOT / "SPEC.json")
    spec = {**original,
        "schema": "mrcr-v3-root-procedure-calibration-spec-v3-exact-full-queries",
        "external_context": {"path_in_runtime": "/context.txt", "content": "exact per-row CSV queries field",
            "files": 8, "query_map_sha256": prepared["query_map_sha256"],
            "written_in_task_setup": True, "host_parser_output_exposed": False},
        "one_underlying_context": True,
        "one_underlying_context_note": "The eight exact queries files differ only in their final target question; their preceding conversation context is identical.",
        "supersedes_spec_v1": "V1 mounted queries minus final view_ops; V3 writes the exact full queries field and also shows the ordinary final question."}
    study.write_x(study_v3.SPEC, spec); os.chmod(study.ROOT / "bin-v3/docker", 0o755)
    env = {**os.environ, "CUDA_VISIBLE_DEVICES": "", "PYTHONDONTWRITEBYTECODE": "1"}
    test = subprocess.run([str(study.NATIVE), "-m", "pytest", "-q", "test_calibration.py",
        "test_repair_v2.py", "test_full_queries_v3.py"], cwd=study.ROOT, env=env,
        capture_output=True, text=True, timeout=240)
    audit = {"schema": "mrcr-v3-root-procedure-calibration-cpu-audit-v3",
        "returncode": test.returncode, "stdout": test.stdout, "stderr": test.stderr,
        "gpu_visible": False, "service_started": False,
        "boundaries": ["all V1 science fixtures", "fresh-process wrapper regression",
            "eight exact full-query files", "real task setup write/read hash", "unmounted runtime facade"]}
    study.write_x(study.ROOT / "CPU_AUDIT_V3.json", audit)
    if test.returncode: raise ValueError("V3 CPU qualification failed")
    files = [study.ROOT / name for name in ("READY.json", "READY_V2.json", "study_v3.py",
        "collect_v3.py", "owner_v3.py", "prepare_v3.py", "test_full_queries_v3.py",
        "bin-v3/docker", "SPEC_V3.json", "CPU_AUDIT_V3.json")]
    files += sorted(study_v3.INPUTS.rglob("*"))
    closure = {str(path): study.sha(path) for path in files if path.is_file()}
    ready = {"schema": "mrcr-v3-root-procedure-calibration-ready-v3",
        "status": "CPU_READY_FOR_MAIN_GPU_LAUNCH", "created_epoch": time.time(),
        "supersedes_unlaunched_ready_v2": "Exact full CSV queries is now the row-specific external /context.txt object.",
        "parent_ready_v2_sha256": study.sha(study.ROOT / "READY_V2.json"),
        "fixed_argv": [str(study.NATIVE), str(study.ROOT / "owner_v3.py"), "run",
            "--output", str(study_v3.ATTEMPT), "--outer-seconds", "900"],
        "external_cap_seconds": 1000, "planned_episodes": 32, "optimizer_steps": 0,
        "science": {"rows": 8, "rollouts_per_row": 4, "seeds": list(study.SEEDS),
            "temperature": 0.5, "top_p": 1.0, "top_k": -1, "min_p": 0.0,
            "max_tokens_per_call": 2048, "same_base_root_and_child": study.MODEL_ALIAS,
            "turn_budget": "maximum six completed turns total across root+child; depth1",
            "one_underlying_context": True, "external_object": "exact full queries per row",
            "ordinary_final_question_also_visible": True},
        "claim_boundary": "Calibration only; code-assisted MRCR over one underlying context, no heldout/generalization claim.",
        "closure_sha256": closure}
    ready["identity"] = study.digest(ready); study.write_x(ready_path, ready)
    print(json.dumps({"ready": str(ready_path), "sha256": study.sha(ready_path),
        "identity": ready["identity"], "tests": test.stdout.strip()}, sort_keys=True))


if __name__ == "__main__": main()

