"""Write-once frozen inputs and CPU-ready receipt for the paired pilot."""

import os
from pathlib import Path
import subprocess
import sys
import time

import collect
import owner
import study


def main():
    if (study.ROOT / "READY.json").exists():
        raise ValueError("READY already exists; preserve the sealed pilot")
    study.write(study.ROOT / "PLAN.json", [row for block in study.make_blocks() for row in block])
    study.write(study.ROOT / "PREFIXES.json", study.build_prefix_manifest())
    binding = collect.binding()
    study.write(study.ROOT / "BINDING.json", binding)
    prior = os.environ.get("STRICT_RLM_CALIBRATION_API_KEY")
    os.environ["STRICT_RLM_CALIBRATION_API_KEY"] = "cpu-structure-only"
    try:
        wrapper, lifecycle = study.runtime()
        suite = owner.dependencies()
        if wrapper.ROOT != study.ALLOCATION_RUNTIME or lifecycle.SERVICE != study.ALLOCATION_RUNTIME / "service_wrapper_v2.py":
            raise ValueError("same-process allocation runtime mismatch")
        if suite.SERVE != study.ALLOCATION_RUNTIME / "service_wrapper_v2.py":
            raise ValueError("owner dependencies use the wrong service wrapper")
        child = subprocess.run(
            [str(study.NATIVE), "-c",
             "import collect; m=collect.qualified.qualified.impl; r,a=m.s.runtime(); "
             "assert r.ROOT==collect.study.ALLOCATION_RUNTIME; "
             "assert a.SERVICE==collect.study.ALLOCATION_RUNTIME/'service_wrapper_v2.py'"],
            cwd=study.ROOT, env={**os.environ, "CUDA_VISIBLE_DEVICES": "",
                                "PYTHONDONTWRITEBYTECODE": "1"},
            text=True, capture_output=True, timeout=60)
        if child.returncode:
            raise RuntimeError(child.stdout + child.stderr)
    finally:
        if prior is None: os.environ.pop("STRICT_RLM_CALIBRATION_API_KEY", None)
        else: os.environ["STRICT_RLM_CALIBRATION_API_KEY"] = prior
    paths = [study.ROOT / name for name in
             ("study.py", "collect.py", "owner.py", "score.py", "test_pilot.py",
              "prepare.py", "DESIGN_AMENDMENTS.md", "PLAN.json", "PREFIXES.json", "BINDING.json")]
    paths += [study.SOURCE_INPUTS / name for name in
              ("PLANS.json", "PUBLIC.json", "HOST_GOLD.json", "TASKS.json", "NATIVE_TEMPLATE.json")]
    paths += [study.SOURCE / name for name in
              ("terminal_study.py", "terminal_collect.py", "terminal_native.py", "terminal_export.py")]
    paths += [study.REFERENCE_SPEC, study.NANO_RLM / "src/rlm/prompt.py",
              Path(binding["campaign_policy"]["path"]) / "adapter_model.safetensors",
              Path(binding["campaign_policy"]["path"]) / "adapter_config.json",
              Path(binding["models"][binding["fixed_child"]]["path"]) / "adapter_model.safetensors",
              Path(binding["models"][binding["fixed_child"]]["path"]) / "adapter_config.json"]
    paths += [study.RECOVERY / name for name in ("owner_v7.py", "study_v7.py", "READY_V7.json")]
    ready = {
        "schema": "root-qs6-recursion-headroom-ready-v1",
        "status": "CPU_READY_FOR_MAIN_GPU_LAUNCH",
        "created_epoch": time.time(),
        "question": "What root-level answer headroom is causally associated with enabling one truthful recursive child depth?",
        "planned_episodes": 96, "tasks": 24, "pairs": 48, "context_clusters": 8,
        "block_modes": list(study.BLOCK_MODES), "block_repeats": list(study.BLOCK_REPEATS),
        "seed_base": study.SEED_BASE, "temperature": 0.5, "max_tokens": 2048,
        "workers": 4, "automatic_retries": 0, "updates": 0,
        "physical_request_admission_stop_trigger": study.ADMISSION_TRIGGER,
        "trigger_is_not_hard_cap": True, "hard_owned_seconds": study.OWNED_SECONDS,
        "hard_external_seconds": study.OUTER_SECONDS,
        "plan_ids": [[row["id"] for row in block] for block in study.make_blocks()],
        "binding": binding,
        "exposure": {
            "root_qs6_optimizer_input": False,
            "c32_sft_saw_all_protected_questions_twice": True,
            "research_exposed": True,
            "generalization_claim": False,
        },
        "analysis": {
            "naive_pair_p_value": None,
            "primary": "descriptive paired counts and eight context-cluster deltas",
            "router": "leave-one-context-out diagnostic with supplied family metadata",
        },
        "closure_sha256": {str(path): study.sha(path) for path in paths},
    }
    ready["identity"] = study.digest({k: v for k, v in ready.items() if k != "identity"})
    study.write(study.ROOT / "READY.json", ready)
    print(study.sha(study.ROOT / "READY.json"), ready["identity"])


if __name__ == "__main__":
    main()
