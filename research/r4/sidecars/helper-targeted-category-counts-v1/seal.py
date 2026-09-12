"""CPU-only freeze and focused qualification; never launches a GPU service."""

import importlib.metadata
import os
import platform
import subprocess
import time
from collections import Counter

import target_study as study


def main():
    if os.environ.get("CUDA_VISIBLE_DEVICES") != "" or (study.ROOT / "READY.json").exists():
        raise ValueError("CPU-only first seal required; preserve immutable READY")
    inherited = study.prior.verify()
    closure = dict(inherited["closure_sha256"])
    closure[str(study.SIZE / "READY.json")] = study.sha(study.SIZE / "READY.json")
    rows = study.make_schedule()
    study.write(study.ROOT / "inputs/SCHEDULE.json", rows)
    inventory = Counter((row["dataset"], row["arm"]) for row in rows)
    if inventory != {
        ("trec", "full"): 8,
        ("trec", "targeted"): 48,
        ("ag_news", "full"): 8,
        ("ag_news", "targeted"): 32,
    }:
        raise ValueError("wrong full/target schedule inventory")
    limit = study.read(study.CONTEXT_SOURCE)["vllm"]["max_model_len"]
    if limit != 8192:
        raise ValueError("unchanged8192 service context required")
    manifest = {
        "schema": "targeted-category-counts-manifest-v1",
        "physical_calls": 96,
        "physical_prediction_slots": 1536,
        "binary_decisions_per_arm": 1280,
        "unique_records": 256,
        "target_count_tasks": 80,
        "approved_design_sha256": study.sha(study.ROOT / "DESIGN.md"),
        "source_panel_manifest_sha256": study.sha(study.PANEL / "MANIFEST.json"),
        "public_sha256": study.sha(study.PANEL / "PUBLIC.json"),
        "host_gold_sha256": study.sha(study.PANEL / "HOST_GOLD.json"),
        "source_size_manifest_sha256": study.sha(study.SIZE / "MANIFEST.json"),
        "binding": study.source().binding(),
        "schedule_sha256": study.digest(study.schedule()),
        "context_bound": study.context_bound(rows, limit),
        "inventory": {
            f"{dataset}:{arm}": {
                "calls": count,
                "planned_prompt_tokens": sum(
                    len(row["body"]["token_ids"])
                    for row in rows
                    if row["dataset"] == dataset and row["arm"] == arm
                ),
            }
            for (dataset, arm), count in inventory.items()
        },
        "target_tasks": [
            {
                "dataset": row["dataset"],
                "block": row["block"],
                "target": row["target"],
                "targeted_call_id": row["call_id"],
                "full_call_id": next(
                    full["call_id"]
                    for full in rows
                    if full["arm"] == "full"
                    and full["dataset"] == row["dataset"]
                    and full["block"] == row["block"]
                ),
            }
            for row in rows
            if row["arm"] == "targeted"
        ],
        "request_hashes": {
            row["call_id"]: {
                "body": study.digest(row["body"]),
                "ordered_schema": study.digest(row["schema_ordered_json"]),
                "prompt_ids": study.digest(row["body"]["token_ids"]),
            }
            for row in rows
        },
        "seed_by_dataset": {"trec": 202609120820, "ag_news": 202609120821},
        "temperature": 0,
        "batch_size": 16,
        "one_shared_service": True,
        "prior_counts_reused": False,
        "flag_off_results_poolable": False,
        "gold_isolation": "frozen public-only requests; host gold used only for scoring",
        "exposure": (
            "not verified c32 SFT/new32 inputs; base-pretraining unknown; now research-exposed"
        ),
        "prospective_token_ratio_screen": 1.25,
        "decision": "report all tradeoffs; approved screen is not an optimal-budget claim",
    }
    study.write(study.ROOT / "MANIFEST.json", manifest)
    command = [str(study.NATIVE), "-m", "pytest", "-q", "test_target.py"]
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
    paths = (
        list(study.ROOT.glob("*.py"))
        + list(study.ROOT.glob("*.md"))
        + [
            study.ROOT / "MANIFEST.json",
            study.ROOT / "CPU_TESTS.json",
            study.ROOT / "inputs/SCHEDULE.json",
        ]
    )
    closure.update({str(path): study.sha(path) for path in paths})
    ready = {
        "schema": "targeted-category-counts-ready-v1",
        "status": "CPU_READY_MAIN_REVIEW_REQUIRED",
        "identity": study.digest(closure),
        "closure_sha256": closure,
        "created_epoch": time.time(),
        "schedule_sha256": study.digest(study.schedule()),
        "manifest_sha256": study.sha(study.ROOT / "MANIFEST.json"),
        "command": [
            str(study.NATIVE),
            str(study.ROOT / "owner.py"),
            "run",
            "--outer-seconds",
            "900",
        ],
        "owner_cap_seconds": 900,
        "external_timeout_seconds": 1000,
        "launch_authority": "MAIN only under shared GPU flock",
        "gpu_launched": False,
        "physical_calls": 96,
        "physical_prediction_slots": 1536,
        "target_tasks": 80,
        "environment": {
            "python": platform.python_version(),
            "executable": str(study.NATIVE),
            "packages": {
                name: importlib.metadata.version(name)
                for name in ("torch", "transformers", "vllm", "xgrammar", "pyarrow")
            },
        },
        "runtime": {
            "service": str(study.SERVICE),
            "engine_preexec_attestation_required": True,
            "final_actual_enginecore_batch_invariant_marker_required": True,
            "no_flag_off_pooling": True,
        },
        "training_updates": 0,
        "root_calls": 0,
    }
    study.write(study.ROOT / "READY.json", ready)
    print(
        {
            "ready": str(study.ROOT / "READY.json"),
            "sha256": study.sha(study.ROOT / "READY.json"),
            "identity": ready["identity"],
            "pins": len(closure),
            "tests": tests.stdout.strip(),
            "context_bound": manifest["context_bound"],
            "inventory": manifest["inventory"],
        }
    )


if __name__ == "__main__":
    main()
