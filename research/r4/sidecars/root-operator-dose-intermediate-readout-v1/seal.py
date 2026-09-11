"""CPU-only qualification and immutable READY seal."""
import json
import os
from pathlib import Path
import subprocess
import time

import id_prepare as prepare
import id_study as study


def pin_tree(directory):
    return {str(path): study.sha(path) for path in sorted(Path(directory).rglob("*")) if path.is_file()}


def seed_receipt():
    roots = [study.SOURCE / "inputs", study.base.dose.ROOT / "inputs"]
    catalog = []
    scanned = []
    for root in roots:
        for path in sorted(root.glob("*.json")):
            catalog.append(json.loads(path.read_text()))
            scanned.append({"path": str(path), "sha256": study.sha(path)})
    candidates = {981681001, *range(981681101, 981681117), *range(981681201, 981681213)}
    collisions = prepare.seed_collisions(candidates, catalog)
    return {
        "scan_started_epoch": time.time(),
        "scope": "exact source readout and fixed24-continuation input directories",
        "files": scanned,
        "candidate_seeds": sorted(candidates),
        "collisions": collisions,
        "scan_ended_epoch": time.time(),
        "not_global_unseen_claim": True,
    }


def main():
    if (study.ROOT / "READY.json").exists():
        raise FileExistsError("READY already sealed")
    started = time.time()
    receipt = seed_receipt()
    if receipt["collisions"]:
        raise ValueError(f"seed collision in named scan: {receipt['collisions']}")
    study.write(study.ROOT / "SEED_SCAN.json", receipt)
    correction = {
        "scope": "pre-READY metadata/collector correction; no sampled outputs existed",
        "preserved_pre_review_inputs": "inputs-pre-review-v1",
        "preserved_pre_review_sha256": pin_tree(study.ROOT / "inputs-pre-review-v1"),
        "changes": ["selected16 baseline receipt", "authoritative versus historical provenance",
                    "fixed-checkpoint policy prose", "collector free-mode and lazy aliases"],
        "scientific_coordinates_changed": False,
    }
    study.write(study.ROOT / "PRE_READY_CORRECTION.json", correction)
    argv = [str(study.NATIVE), "-m", "pytest", "-q", "-p", "no:cacheprovider",
            "test_selection.py", "test_inputs.py", "test_binding_owner.py", "test_entry.py",
            "test_execute.py", "test_native.py", "test_service.py", "--basetemp",
            str(study.ROOT / "qualification-final-001")]
    result = subprocess.run(argv, cwd=study.ROOT,
                            env={**os.environ, "CUDA_VISIBLE_DEVICES": "", "PYTHONDONTWRITEBYTECODE": "1"},
                            text=True, capture_output=True, timeout=240)
    report = {
        "argv": argv, "returncode": result.returncode, "stdout": result.stdout,
        "stderr": result.stderr, "elapsed_seconds": time.time() - started,
        "gpu_calls": 0, "scientific_model_calls": 0,
        "actual_native_authored_fixture": True,
        "actual_owner_service_entry_to_inference_popen_intercepted": True,
        "pre_ready_failures": [
            "RED tests caught copied48 baseline, ambiguous historical provenance, inherited fixed6/24 rule, and missing free mode.",
            "Authored native fixture initially caught missing private credential fixture environment; fixture-only environment corrected.",
        ],
    }
    study.write(study.ROOT / "CPU_REPORT.json", report)
    if result.returncode:
        raise RuntimeError(result.stdout + result.stderr)
    ancestor = study.read(study.SOURCE / "READY.json")
    sources = dict(ancestor["source_sha256"])
    sources[str(study.SOURCE / "READY.json")] = study.SOURCE_READY_SHA
    sources.update({str(path): study.sha(path) for path in study.ROOT.iterdir()
                    if path.is_file() and path.name != "READY.json"})
    inputs = dict(ancestor["input_sha256"])
    inputs.update(pin_tree(study.ROOT / "inputs"))
    inputs.update(pin_tree(study.ROOT / "inputs-pre-review-v1"))
    for policy in ("sft6", "sft12", "sft18", "sft24"):
        selected = study.selected(policy)
        directory = Path(selected["checkpoint"])
        for name in ("adapter_model.safetensors", "adapter_config.json", "state.json"):
            inputs[str(directory / name)] = study.sha(directory / name)
    for path, digest in {**sources, **inputs}.items():
        study.base.dose.check(path, digest)
    plan = study.read(study.ROOT / "inputs/EVALUATION_PLAN.json")
    ready = {
        "schema": "operator-dose-intermediate-readout-ready-v1",
        "status": "CPU_READY_NOT_LAUNCHED",
        "source_sha256": sources,
        "input_sha256": inputs,
        "source_ancestor_ready_sha256": study.SOURCE_READY_SHA,
        "source_ancestor_transitive_pins_included": True,
        "owner_argv": [str(study.NATIVE), str(study.ROOT / "id_owner.py"), "run",
                       "--output", str(study.ATTEMPT)],
        "verify_argv": [str(study.NATIVE), str(study.ROOT / "id_owner.py"), "verify"],
        "policy_order": plan["policy_order"],
        "planned_full": 64, "planned_first_action": 48,
        "work_seconds": 3150, "owned_seconds": 3270, "outer_seconds": 3300,
        "four_phase_seconds": 750, "harvest_seconds": 150,
        "main_launch_only": True, "cpu_only": True, "no_training": True,
        "no_sampled_output_at_seal": True,
    }
    ready["identity"] = study.digest(ready)
    study.write(study.ROOT / "READY.json", ready)
    study.verify()
    print({"ready_sha256": study.sha(study.ROOT / "READY.json"),
           "identity": ready["identity"], "source_pins": len(sources),
           "input_pins": len(inputs), "cpu_report_sha256": study.sha(study.ROOT / "CPU_REPORT.json"),
           "tests": result.stdout, "elapsed_seconds": time.time() - started})


if __name__ == "__main__":
    main()
