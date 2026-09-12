"""CPU-only first seal of64 ordered requests and inherited immutable runtime closure."""

import importlib.metadata
import os
import platform
import subprocess
import time
from collections import Counter

import companion_study as study


def main():
    if os.environ.get("CUDA_VISIBLE_DEVICES") != "" or (study.ROOT / "READY.json").exists():
        raise ValueError("CPU-only first seal required")
    inherited = study.target.verify()
    closure = dict(inherited["closure_sha256"])
    closure[str(study.TARGET / "READY.json")] = study.sha(study.TARGET / "READY.json")
    rows = study.make_schedule()
    study.write(study.ROOT / "inputs/SCHEDULE.json", rows)
    visits = Counter((row["arm"], identifier) for row in rows for identifier in row["ids"])
    if len(rows) != 64 or len(visits) != 1024 or set(visits.values()) != {1}:
        raise ValueError("wrong64/1024 inventory")
    context = study.context_bound(rows, study.read(study.CONTEXT_SOURCE)["vllm"]["max_model_len"])
    if context["service_max_model_len"] != 8192:
        raise ValueError("fixed8192 context required")
    inventory = {}
    for dataset in ("trec", "ag_news"):
        for arm in study.ARMS:
            selected = [row for row in rows if row["dataset"] == dataset and row["arm"] == arm]
            if len(selected) != 8:
                raise ValueError("each dataset/arm requires8 requests")
            inventory[f"{dataset}:{arm}"] = {
                "calls": 8,
                "records": 128,
                "planned_prompt_tokens": sum(len(row["body"]["token_ids"]) for row in selected),
                "maximum_prompt_tokens": max(len(row["body"]["token_ids"]) for row in selected),
                "retained_companions_total": sum(
                    p["retained_companions"] for row in selected for p in row["position_provenance"]
                ),
            }
    manifest = {
        "schema": "companion-position-manifest-v1",
        "physical_calls": 64,
        "prediction_slots": 1024,
        "unique_records": 256,
        "arms": list(study.ARMS),
        "context_bound": context,
        "inventory": inventory,
        "schedule_sha256": study.digest(study.schedule()),
        "design_sha256": study.sha(study.ROOT / "DESIGN.md"),
        "binding": study.source().binding(),
        "panel_manifest_sha256": study.sha(study.PANEL / "MANIFEST.json"),
        "public_sha256": study.sha(study.PANEL / "PUBLIC.json"),
        "host_gold_sha256": study.sha(study.PANEL / "HOST_GOLD.json"),
        "permutation_namespace": (
            "helper-companion-position-v1|202609120932|dataset|neighbor_A_or_B|column"
        ),
        "model_seeds": {"trec": 202609120930, "ag_news": 202609120931},
        "temperature": 0,
        "batch_size": 16,
        "previous_responses_reused": False,
        "gold_isolation": "PUBLIC-only permutations/prompts; HOST_GOLD host scoring only",
        "request_hashes": {
            row["call_id"]: {
                "body": study.digest(row["body"]),
                "ordered_schema": study.digest(row["schema_ordered_json"]),
                "prompt_ids": study.digest(row["body"]["token_ids"]),
            }
            for row in rows
        },
        "exposure": "absent from verified c32 SFT/new32; pretraining unknown; now research-exposed",
        "neighbor_slot_preserved": True,
        "absolute_token_offsets_preserved": False,
        "runtime": "one fresh v4 batch-invariant service; no flag-off pooling",
    }
    study.write(study.ROOT / "MANIFEST.json", manifest)
    command = [str(study.NATIVE), "-m", "pytest", "-q", "test_companion.py"]
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
        raise ValueError("CPU qualification failed; no READY")
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
        "schema": "companion-position-ready-v1",
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
        "gpu_launched": False,
        "launch_authority": "MAIN only under shared GPU flock",
        "physical_calls": 64,
        "prediction_slots": 1024,
        "unique_records": 256,
        "context_bound": context,
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
            "context_bound": context,
            "inventory": inventory,
        }
    )


if __name__ == "__main__":
    main()
