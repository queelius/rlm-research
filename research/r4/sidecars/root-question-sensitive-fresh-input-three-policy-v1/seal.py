"""Seal the exact CPU-prepared closure; never launches a service or GPU."""
import time
from pathlib import Path
import study as s


def main():
    meta = s.SIDE / "root-question-sensitive-metadata-transfer-v1"
    recovery = s.RECOVERY
    new = s.NEW
    source_names = ("study.py", "prepare.py", "collect.py", "owner.py", "qualify.py",
                    "seal.py", "test_fresh_input.py", "DESIGN.md", "PLAN.md",
                    "IMPLEMENTATION_REPORT.md", "QUALIFICATION.json", "CPU_NATIVE.json")
    sources = {str(s.ROOT / name): s.sha(s.ROOT / name) for name in source_names}
    for ready_path in (s.ORIGINAL / "READY.json", meta / "READY.json",
                       recovery / "POSTCAPTURE_GPU_READY.json", new / "READY.json"):
        ready = s.read(ready_path); sources[str(ready_path)] = s.sha(ready_path)
        sources.update(ready.get("source_sha256", {}))
    external = (
        new / "outputs/attempt-001/training/RESULT.json",
        new / "outputs/attempt-001/training/SELECTION.json",
        recovery / "outputs/attempt-003/training/SELECTION.json",
    )
    for path in external: sources[str(path)] = s.sha(path)
    for chosen in (s.base.starting_policy(), s.original_sft_binding.selected("sft6"), s.selected_new()):
        directory = Path(chosen["checkpoint"])
        for name in ("adapter_model.safetensors", "adapter_config.json", "state.json"):
            sources[str(directory / name)] = s.sha(directory / name)
    for arm in ("new_corpus_sft6", "original_sft6", "fixed24"):
        binding = s.binding(arm)
        child = Path(binding["models"][binding["fixed_child"]]["path"])
        for name in ("adapter_model.safetensors", "adapter_config.json"):
            sources[str(child / name)] = s.sha(child / name)
    inputs = {str(path): s.sha(path) for path in sorted((s.ROOT / "inputs").glob("*.json"))}
    value = {"schema": "question-sensitive-fresh-input-three-policy-ready-v1",
             "status": "CPU_READY_MAIN_ACCEPTANCE_REQUIRED", "created_epoch": time.time(),
             "source_sha256": sources, "input_sha256": inputs,
             "owner_argv": [str(s.NATIVE), str(s.ROOT / "owner.py"), "run", "--output", str(s.ATTEMPT)],
             "verify_argv": [str(s.NATIVE), str(s.ROOT / "owner.py"), "verify"],
             "policy_order": ["new_corpus_sft6", "original_sft6", "fixed24"],
             "planned": 216, "episodes_per_policy": 72, "contexts": 8,
             "operators": 9, "selected_groups": 128, "eligible_groups": 181,
             "unused_eligible_groups": 53, "outer_seconds": 5400,
             "owned_seconds": 5370, "work_seconds": 5250, "no_training": True,
             "no_retry": True, "no_rerank_after_gold": True,
             "gpu_launch_authority": "MAIN only", "gpu_calls_during_preparation": 0}
    value["identity"] = s.digest(value)
    s.write(s.ROOT / "READY.json", value)
    print(value["identity"])


if __name__ == "__main__":
    main()
