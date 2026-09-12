"""CPU qualification and immutable READY seal."""

import json
import os
import subprocess
import time

import collect
import study


def main():
    if os.environ.get("CUDA_VISIBLE_DEVICES") != "":
        raise ValueError("CPU-only preparation")
    ready_path = study.ROOT / "READY.json"
    if ready_path.exists():
        raise FileExistsError(ready_path)
    frozen_prefixes = study.read(study.ROOT / "PREFIXES.json")
    rebuilt = study.build_prefix_manifest()
    if rebuilt != frozen_prefixes:
        raise ValueError("frozen prefixes differ from actual renderer output")
    tasks = collect.task_tables()
    if study.sha(study.ROOT / "BINDING.json") != study.sha(study.HEADROOM / "BINDING.json"):
        raise ValueError("QS6/c32 binding differs from original headroom pilot")
    for mode in study.MODES:
        for row in study.make_blocks()[study.BLOCK_MODES.index(mode)]:
            entry = tasks["modes"][mode][row["task_name"]]
            if entry["prompt"] != study.common_prompt(
                study.public()[row["context_id"]], row["question"]
            ):
                raise ValueError("frozen prompt differs")
            if row["seed"] != study.SOURCE_SEEDS[row["family"]]:
                raise ValueError("original headroom seed changed")
    env = {
        **os.environ,
        "CUDA_VISIBLE_DEVICES": "",
        "STRICT_RLM_CALIBRATION_API_KEY": "cpu-fixture-not-used",
    }
    started = time.time()
    tests = subprocess.run(
        [str(study.NATIVE), "-m", "pytest", "-q", "test_qualifier.py"],
        cwd=study.ROOT,
        env=env,
        capture_output=True,
        text=True,
        timeout=90,
    )
    audit = {
        "schema": "root-qs6-recursion-interface-qualifier-cpu-audit-v1",
        "returncode": tests.returncode,
        "stdout": tests.stdout,
        "stderr": tests.stderr,
        "elapsed_seconds": time.time() - started,
        "gpu_visible": False,
        "service_started": False,
        "actual_dependencies_called": True,
        "actual_both_mode_specs_prepared": True,
        "semantic_request_id_fixture": True,
        "prefix_coordinates": len(rebuilt["coordinates"]),
        "max_prefix_tokens": max(row["token_count"] for row in rebuilt["coordinates"]),
    }
    audit_path = study.ROOT / "CPU_AUDIT.json"
    study.write(audit_path, audit)
    if tests.returncode:
        raise ValueError("CPU qualification failed")

    local_names = (
        "BINDING.json",
        "DESIGN.md",
        "PREFIXES.json",
        "TASKS.json",
        "build_inputs.py",
        "collect.py",
        "owner.py",
        "prepare.py",
        "score.py",
        "study.py",
        "test_qualifier.py",
        "CPU_AUDIT.json",
    )
    closure = {str(study.ROOT / name): study.sha(study.ROOT / name) for name in local_names}
    parent = study.read(study.HEADROOM / "READY_V4.json")
    closure[str(study.HEADROOM / "READY_V4.json")] = study.sha(
        study.HEADROOM / "READY_V4.json"
    )
    closure.update(parent["closure_sha256"])
    for path in (
        study.SOURCE_INPUTS / "PLANS.json",
        study.SOURCE_INPUTS / "PUBLIC.json",
        study.SOURCE_INPUTS / "HOST_GOLD.json",
        study.SOURCE_INPUTS / "NATIVE_TEMPLATE.json",
        study.REFERENCE_SPEC,
    ):
        closure[str(path)] = study.sha(path)

    value = {
        "schema": "root-qs6-recursion-interface-qualifier-ready-v1",
        "status": "CPU_READY_FOR_MAIN_GPU_LAUNCH",
        "created_epoch": time.time(),
        "question": "Does an explicit, byte-identical conditional global-rlm ABI restore a functioning paired recursion/no-recursion interface?",
        "not_an_accuracy_headroom_claim": True,
        "prompt_intervention_separate_from_original_pilot": True,
        "fixed_argv": [
            str(study.NATIVE),
            str(study.ROOT / "owner.py"),
            "run",
            "--output",
            str(study.ATTEMPT),
            "--outer-seconds",
            str(study.OUTER_SECONDS),
        ],
        "science": {
            "episodes": 12,
            "modes": list(study.MODES),
            "block_order": list(study.BLOCK_MODES),
            "families": list(study.FAMILIES),
            "selected_context_by_family": study.SELECTION,
            "seeds_by_family": study.SOURCE_SEEDS,
            "temperature": 0.5,
            "max_tokens_per_call": 2048,
            "root": "QS6 fixed",
            "child": "c32 fixed",
            "updates": 0,
            "admission_stop_trigger": study.ADMISSION_TRIGGER,
            "trigger_is_not_hard_cap": True,
            "owned_seconds": study.OWNED_SECONDS,
            "outer_seconds": study.OUTER_SECONDS,
            "no_retry_or_fallback": True,
        },
        "gate": {
            "bad_import_attempts": 0,
            "max_consecutive_identical_code_calls": 1,
            "minimum_observable_endpoints": 10,
            "all_six_families_in_both_modes": True,
            "semantic_typed_role_request_id_parity": True,
        },
        "plan_ids": [[row["id"] for row in block] for block in study.make_blocks()],
        "closure_sha256": closure,
    }
    value["identity"] = study.digest({key: item for key, item in value.items() if key != "identity"})
    study.write(ready_path, value)
    print(
        json.dumps(
            {"path": str(ready_path), "sha256": study.sha(ready_path), "identity": value["identity"]},
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
