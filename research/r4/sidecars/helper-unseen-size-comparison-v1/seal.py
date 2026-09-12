"""Freeze every request, source/provenance hash and runtime before native scoring."""

import importlib.metadata
import os
import platform
import subprocess
import time
from collections import Counter

import size_study as study


def main():
    if os.environ.get("CUDA_VISIBLE_DEVICES") != "":
        raise ValueError("sealing is CPU-only")
    if (study.ROOT / "READY.json").exists():
        raise ValueError("preserve existing immutable READY")
    receipt_paths = [study.C32 / "READY.json", study.PANEL / "CPU_READY.json"]
    receipt_paths += [
        study.INVARIANT / name
        for name in ("READY.json", "READY_V2.json", "READY_REPAIR.json", "READY_ATTEMPT003.json")
    ]
    closure = {}
    for path in receipt_paths:
        receipt = study.read(path)
        for raw, expected in receipt.get("closure_sha256", receipt.get("closure", {})).items():
            if raw in closure and closure[raw] != expected:
                raise ValueError("source seals disagree: " + raw)
            closure[raw] = expected
        closure[str(path)] = study.sha(path)
    for raw, expected in closure.items():
        if study.sha(raw) != expected:
            raise ValueError("sealed source changed: " + raw)
    rows = study.make_schedule()
    study.write(study.ROOT / "inputs/SCHEDULE.json", rows)
    sizes = Counter(row["batch_size"] for row in rows)
    record_visits = Counter(
        (row["batch_size"], identifier) for row in rows for identifier in row["ids"]
    )
    if (
        sizes != {16: 16, 4: 64, 1: 256}
        or len(record_visits) != 768
        or set(record_visits.values()) != {1}
    ):
        raise ValueError("wrong exact336/768 inventory")
    metrics = {}
    for dataset in ("trec", "ag_news"):
        for size in study.SIZES:
            selected = [
                row for row in rows if row["dataset"] == dataset and row["batch_size"] == size
            ]
            metrics[f"{dataset}:{size}"] = {
                "physical_calls": len(selected),
                "record_predictions": sum(len(row["ids"]) for row in selected),
                "planned_prompt_tokens": sum(len(row["body"]["token_ids"]) for row in selected),
                "maximum_prompt_tokens": max(len(row["body"]["token_ids"]) for row in selected),
                "seed": selected[0]["body"]["sampling_params"]["seed"],
            }
    context_limit = study.read(study.CONTEXT_SOURCE)["vllm"]["max_model_len"]
    maximum_prompt = max(len(row["body"]["token_ids"]) for row in rows)
    maximum_total = max(
        len(row["body"]["token_ids"]) + row["body"]["sampling_params"]["max_tokens"] for row in rows
    )
    if context_limit != 8192 or maximum_total > context_limit:
        raise ValueError("fixed request/template exceeds unchanged attested service context limit")
    manifest = {
        "schema": "helper-unseen-size-comparison-input-manifest-v1",
        "panel_manifest_identity": study.source().panel()[0]["manifest_identity"],
        "panel_manifest_path": str(study.PANEL / "MANIFEST.json"),
        "panel_manifest_sha256": study.sha(study.PANEL / "MANIFEST.json"),
        "public_records_sha256": study.sha(study.PANEL / "PUBLIC.json"),
        "host_gold_sha256": study.sha(study.PANEL / "HOST_GOLD.json"),
        "source_builder_sha256": study.sha(study.PANEL / "build_panel.py"),
        "source_size4_requests_sha256": study.sha(study.PANEL / "REQUESTS.json"),
        "request_schedule_sha256": study.digest(study.schedule()),
        "inventory": metrics,
        "physical_calls": 336,
        "record_predictions": 768,
        "records_per_dataset": 128,
        "unique_records": 256,
        "context_bound": {
            "service_max_model_len": context_limit,
            "maximum_prompt_tokens": maximum_prompt,
            "maximum_prompt_plus_output_tokens": maximum_total,
            "output_token_cap": 1024,
            "all_requests_fit": True,
            "source_configuration": str(study.CONTEXT_SOURCE),
            "source_configuration_sha256": study.sha(study.CONTEXT_SOURCE),
            "runtime_configuration_rechecked_before_calls": True,
        },
        "request_hashes": {
            row["call_id"]: {
                "body": study.digest(row["body"]),
                "ordered_schema": study.digest(row["schema_ordered_json"]),
                "input_tokens": study.digest(row["body"]["token_ids"]),
            }
            for row in rows
        },
        "rotation": "consecutive16-record blocks; size order rotated by(dataset index+block) mod3",
        "fresh_control": "all sizes newly generated under the same batch-invariant-v4 service",
        "older_results_reused": False,
        "runtime_flag_off_results_poolable": False,
        "gold_isolation": "PUBLIC only enters prompt builder; HOST_GOLD is owner-scoring only",
        "exposure": (
            "absent from verified c32 SFT/new32; not base-pretraining unseen; now research-exposed"
        ),
        "binding": study.source().binding(),
        "source_receipts_sha256": {str(path): study.sha(path) for path in receipt_paths},
    }
    study.write(study.ROOT / "MANIFEST.json", manifest)
    command = [str(study.NATIVE), "-m", "pytest", "-q", "test_size.py"]
    began = time.monotonic()
    tests = subprocess.run(
        command,
        cwd=study.ROOT,
        text=True,
        capture_output=True,
        timeout=120,
        env={**os.environ, "CUDA_VISIBLE_DEVICES": ""},
    )
    study.write(
        study.ROOT / "CPU_TESTS.json",
        {
            "command": command,
            "returncode": tests.returncode,
            "stdout": tests.stdout,
            "stderr": tests.stderr,
            "elapsed_seconds": time.monotonic() - began,
        },
    )
    if tests.returncode:
        raise ValueError("focused CPU qualification failed; no READY")
    paths = list(study.ROOT.glob("*.py")) + [
        study.ROOT / "PLAN.md",
        study.ROOT / "MANIFEST.json",
        study.ROOT / "CPU_TESTS.json",
        study.ROOT / "inputs/SCHEDULE.json",
        study.PANEL / "build_panel.py",
        study.CONTEXT_SOURCE,
        study.SERVICE,
        study.NATIVE,
        study.NATIVE.parent.parent / "pyvenv.cfg",
    ]
    closure.update({str(path): study.sha(path) for path in paths})
    ready = {
        "schema": "helper-unseen-size-comparison-ready-v1",
        "status": "CPU_READY_MAIN_REVIEW_REQUIRED",
        "identity": study.digest(closure),
        "created_epoch": time.time(),
        "gpu_launched": False,
        "closure_sha256": closure,
        "manifest_sha256": study.sha(study.ROOT / "MANIFEST.json"),
        "schedule_sha256": study.digest(study.schedule()),
        "command": [
            str(study.NATIVE),
            str(study.ROOT / "owner.py"),
            "run",
            "--outer-seconds",
            "1200",
        ],
        "owner_cap_seconds": 1200,
        "external_timeout_seconds": 1300,
        "launch_authority": "MAIN only under shared GPU flock",
        "question": "Do smaller requests transfer beyond c32 SFT inputs, at what total cost?",
        "physical_calls": 336,
        "record_predictions": 768,
        "unique_records": 256,
        "sizes": [16, 4, 1],
        "temperature": 0,
        "root_calls": 0,
        "training_updates": 0,
        "runtime": {
            "service_launcher": str(study.SERVICE),
            "VLLM_BATCH_INVARIANT": "1",
            "engine_preexec_attestation_required": True,
            "one_shared_service": True,
            "older_flag_off_counts_not_pooled": True,
        },
        "metrics": [
            "fixed-denominator correct/wrong/unavailable by dataset/size",
            "paired record wins/losses and unavailable branches",
            "calls/tokens/cache/time",
            "invalid, request-error, integrity-error and unattempted slots",
        ],
        "decision_rule": "evaluate all3 sizes regardless of interim outcomes; dataset-specific",
        "environment": {
            "python": platform.python_version(),
            "executable": str(study.NATIVE),
            "packages": {
                name: importlib.metadata.version(name)
                for name in ("torch", "transformers", "vllm", "xgrammar", "pyarrow")
            },
        },
        "claim_boundary": (
            "256 records, 3 related partitions; not 768 independent cases or root evidence"
        ),
        "cost_accounting": "observed usage subtotals and unknown-usage counts; not zero-cost errors",
        "context_bound": manifest["context_bound"],
    }
    study.write(study.ROOT / "READY.json", ready)
    print(
        {
            "ready": str(study.ROOT / "READY.json"),
            "sha256": study.sha(study.ROOT / "READY.json"),
            "identity": ready["identity"],
            "pins": len(closure),
            "tests": tests.stdout.strip(),
            "inventory": metrics,
        }
    )


if __name__ == "__main__":
    main()
