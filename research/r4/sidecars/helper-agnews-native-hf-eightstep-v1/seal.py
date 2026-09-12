"""Seal CPU preparation only; MAIN admission remains a separate reviewed receipt."""

import datetime
import json
import os
import subprocess

import core


def main():
    if os.environ.get("CUDA_VISIBLE_DEVICES") != "" or (core.ROOT / "READY.json").exists():
        raise ValueError("CPU-only fresh seal required")
    source_ready = core.read(core.SOURCE / "READY.json")
    closure = dict(source_ready["closure_sha256"])
    closure[str(core.SOURCE / "READY.json")] = core.sha(core.SOURCE / "READY.json")
    data = core.read(core.DATA / "inputs/MANIFEST.json")
    for field in ("source_closure_sha256", "artifacts_sha256"):
        closure.update(data[field])
    for raw, expected in closure.items():
        if core.sha(raw) != expected:
            raise ValueError("sealed source/data changed: " + raw)
    tests = []
    for python, name in (
        (core.original.TRAIN_PYTHON, "test_continuity.py"),
        (core.original.NATIVE, "test_native.py"),
    ):
        command = [str(python), "-m", "pytest", "-q", str(core.ROOT / name)]
        result = subprocess.run(
            command,
            capture_output=True,
            text=True,
            timeout=120,
            env={**os.environ, "CUDA_VISIBLE_DEVICES": "", "PYTHONDONTWRITEBYTECODE": "1"},
        )
        tests.append(
            {
                "command": command,
                "returncode": result.returncode,
                "stdout": result.stdout,
                "stderr": result.stderr,
            }
        )
        if result.returncode:
            raise RuntimeError(result.stdout + result.stderr)
    core.write_x(
        core.ROOT / "CPU_TESTS.json",
        {
            "tests": tests,
            "GPU_launched": False,
            "two_step_real_hf_adam_rng_all_lora_gradients_equivalent": True,
            "actual_native_four_key_raw_masks_and_parent_weight_binding": True,
            "known_warnings": (
                "tiny PEFT base has no model config path; native XGrammar SWIG deprecations"
            ),
        },
    )
    source_seal = core.load_bound(
        "ag_eight_source_environment",
        core.SOURCE / "seal.py",
        {
            "ag_study": core.original,
            "eval_owner": core.load_bound(
                "ag_eight_original_eval", core.SOURCE / "eval_owner.py", {"ag_study": core.original}
            ),
        },
    )
    environment = {
        "native": source_seal.environment(core.original.NATIVE),
        "training": source_seal.environment(core.original.TRAIN_PYTHON),
    }
    core.write_x(core.ROOT / "ENVIRONMENT.json", environment)
    direct = [
        core.DATA / "inputs/MANIFEST.json",
        core.DATA / "DATA_READY.json",
        core.DATA / "VERIFIED.json",
        core.DATA / "TOKEN_RECHECK.json",
        core.SOURCE / "ag_study.py",
        core.SOURCE / "owner.py",
        core.SOURCE / "native_collect.py",
        core.SOURCE / "train_ag.py",
        core.SOURCE / "prepare_masks.py",
        core.SOURCE / "eval_owner.py",
        core.SOURCE / "seal.py",
        core.SOURCE / "outputs/attempt-001/OWNER_TERMINAL.json",
        core.SOURCE / "outputs/attempt-001/RESULT.json",
        core.SIDE.parent / "ideas/2026-09-12-agnews-native-hf-eightstep-dose.md",
    ]
    other = core.SIDE / "helper-hf-onpolicy-fourstep-v1/outputs/attempt-001/checkpoint-0004"
    direct.extend(other / name for name in ("adapter_model.safetensors", "adapter_config.json"))
    for pattern in ("*.py", "*.md", "*.yaml", "*.json", "inputs/*.json", "inputs/step-*/*.json"):
        direct.extend(core.ROOT.glob(pattern))
    closure.update({str(path.resolve()): core.sha(path) for path in direct})
    core.write_x(
        core.ROOT / "SOURCE_INVENTORY.json",
        {
            "closure_sha256": dict(sorted(closure.items())),
            "all_previous_sources_unchanged": True,
            "training_records": 1024,
            "fresh512_model_calls": 0,
            "GPU_launched": False,
        },
    )
    closure[str(core.ROOT / "SOURCE_INVENTORY.json")] = core.sha(
        core.ROOT / "SOURCE_INVENTORY.json"
    )
    runtime = core.read(core.ROOT / "RUNTIME.json")
    ready = {
        "schema": "agnews-native-hf-eightstep-ready-v1",
        "status": "CPU_READY_NOT_ADMITTED",
        "created_utc": datetime.datetime.now(datetime.UTC).isoformat(),
        "output": str(core.ATTEMPT),
        "command": [
            str(core.original.NATIVE),
            str(core.ROOT / "owner.py"),
            "run",
            "--owner-seconds",
            str(runtime["owner_seconds"]),
            "--admission-json",
            str(core.ROOT / "ADMISSION.json"),
        ],
        "runtime": runtime,
        "policy": source_ready["policy"],
        "starting_child_sha256": core.original.CHILD_SHA,
        "optimizer_continuation": (
            "one logical Adam trajectory; full moments/counters/RNG saved/restored"
        ),
        "inventory": {
            "updates": 8,
            "unique_training_records": 1024,
            "new_training_records_per_step": 128,
            "native_actions_per_step": 128,
            "native_actions_total": 1024,
            "native_category_decisions_total": 4096,
            "final_heldout_records": 512,
            "final_heldout_calls_per_arm": 128,
        },
        "fixed_primary_step": 8,
        "intermediate_evaluation_prohibited": True,
        "data_manifest_sha256": core.sha(core.DATA / "inputs/MANIFEST.json"),
        "environment": environment,
        "closure_sha256": dict(sorted(closure.items())),
        "no_gpu_launch": True,
        "explicit_MAIN_admission_required": True,
        "source_one_step_tiny_positive_prioritizes_seed_replication": True,
        "native_hf_model_loads": (
            "eight sequential native starts and eight HF loads; never co-resident"
        ),
        "evaluation_interface": str(core.ROOT / "ENDPOINT_INTERFACE.md"),
    }
    ready["identity"] = core.digest(ready)
    core.write_x(core.ROOT / "READY.json", ready)
    core.verify()
    print(
        json.dumps(
            {
                "ready_sha256": core.sha(core.ROOT / "READY.json"),
                "identity": ready["identity"],
                "closure_files": len(closure),
                "tests": tests,
                "status": ready["status"],
            },
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
