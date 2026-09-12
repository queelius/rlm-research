"""CPU-only input preparation, fixture qualification, and immutable READY seal."""

import json
import os
from pathlib import Path
import subprocess
import time

import study


def main():
    if os.environ.get("CUDA_VISIBLE_DEVICES") != "": raise ValueError("CPU-only preparation")
    if (study.ROOT / "READY.json").exists(): raise FileExistsError("READY already exists")
    prepared = study.prepare_inputs(study.ROOT / "inputs")
    spec = {"schema": "mrcr-v3-root-procedure-calibration-spec-v1",
        "question": "Can unadapted 4B root discover an external-context MRCR procedure with useful within-target reward variation?",
        "claim_boundary": "Eight target questions over one underlying research-exposed context; calibration only, not held-out/generalization or tool-free MRCR.",
        "plan": study.plan(), "plan_sha256": study.digest(study.plan()),
        "context_sha256": prepared["context_sha256"], "one_underlying_context": True,
        "model": {"root": study.MODEL_ALIAS, "child": study.MODEL_ALIAS,
            "path": str(study.MODEL), "adapter": None},
        "sampling": {"temperature": 0.5, "top_p": 1.0, "top_k": -1, "min_p": 0.0,
            "max_tokens_per_call": 2048, "seeds": list(study.SEEDS)},
        "runtime": {"max_turns_total_root_plus_child": 6, "max_depth": 1,
            "literal_six_root_turns_not_guaranteed": True,
            "interpretation": "Child calls consume the same six-turn WireTrace budget; report root/child counts and turn-limit finals."},
        "budget": {"owner_seconds": 900, "external_seconds": 1000,
            "science_seconds": study.SCIENCE_SECONDS, "per_episode_seconds": 180,
            "workers": 4, "service_release_grace_seconds": 60},
        "checkpoint": "Immutable native start/result per model call, episode record per completed/censored coordinate, progress after every episode; no retries.",
        "metric": {"official_source": str(study.OFFICIAL), "official_source_sha256": study.OFFICIAL_SHA,
            "official_behavior": "last random-hash occurrence (rfind), then SequenceMatcher",
            "separate_diagnostics": ["strict_prefix", "hash_present", "content_similarity"]},
        "future_rl_gate": {"mixed_groups_at_least": 2, "mean_official_score_below": 0.90,
            "protocol_good": True, "real_external_inspection": True, "optimizer_in_this_run": False},
        "code_access_ceiling": "The official README says code access makes MRCR considerably simpler; this measures procedure/tool use, not semantic recursion."}
    study.write_x(study.ROOT / "SPEC.json", spec)
    os.chmod(study.ROOT / "bin/docker", 0o755)
    env = {**os.environ, "CUDA_VISIBLE_DEVICES": "", "PYTHONDONTWRITEBYTECODE": "1"}
    test = subprocess.run([str(study.NATIVE), "-m", "pytest", "-q", "test_calibration.py"],
        cwd=study.ROOT, env=env, capture_output=True, text=True, timeout=180)
    audit = {"schema": "mrcr-v3-root-procedure-calibration-cpu-audit-v1",
        "returncode": test.returncode, "stdout": test.stdout, "stderr": test.stderr,
        "gpu_visible": False, "service_started": False,
        "boundaries": ["frozen rows and prompt", "official scorer fixture", "actual taskset and ModelContext", "native token/logprob response", "no-adapter binding and owner cap"]}
    study.write_x(study.ROOT / "CPU_AUDIT.json", audit)
    if test.returncode: raise ValueError("focused CPU qualification failed")
    closure_paths = [study.ROOT / name for name in ("PLAN.md", "study.py", "collect.py", "owner.py",
        "prepare.py", "boundary.py", "bin/docker", "test_calibration.py", "SPEC.json", "CPU_AUDIT.json")]
    closure_paths += [study.SELECTION, study.DATA, study.OFFICIAL,
        study.OLD / "source/mrcr_rootless_document_baseline_v2.py",
        study.OLD / "source/boundary.py", study.BASE / "READY_REPAIR.json",
        study.BASE / "base_panel_study.py", study.BASE / "base_panel_study_v2.py",
        study.BASE / "service_wrapper_v2.py"]
    closure_paths += sorted((study.ROOT / "inputs").rglob("*"))
    closure = {str(path): study.sha(path) for path in closure_paths if path.is_file()}
    ready = {"schema": "mrcr-v3-root-procedure-calibration-ready-v1",
        "status": "CPU_READY_FOR_MAIN_GPU_LAUNCH", "created_epoch": time.time(),
        "fixed_argv": [str(study.NATIVE), str(study.ROOT / "owner.py"), "run",
            "--output", str(study.ATTEMPT), "--outer-seconds", "900"],
        "external_cap_seconds": 1000, "planned_episodes": 32, "optimizer_steps": 0,
        "turn_budget": "max six completed model turns total across root plus child; depth1",
        "one_underlying_context": True, "no_generalization_claim": True,
        "private_credential": "STRICT_RLM_CALIBRATION_API_KEY inherited in process memory only; never persisted",
        "closure_sha256": closure}
    ready["identity"] = study.digest(ready)
    study.write_x(study.ROOT / "READY.json", ready)
    print(json.dumps({"ready": str(study.ROOT / "READY.json"),
        "sha256": study.sha(study.ROOT / "READY.json"), "identity": ready["identity"],
        "tests": test.stdout.strip()}, sort_keys=True))


if __name__ == "__main__": main()

