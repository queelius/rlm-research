"""CPU-only first seal; all possible component requests and inherited closure pinned."""

import importlib.metadata
import os
import platform
import subprocess
import time
from collections import Counter

import adaptive_study as study


def main():
    if os.environ.get("CUDA_VISIBLE_DEVICES") != "" or (study.ROOT / "READY.json").exists():
        raise ValueError("CPU-only first seal required")
    inherited = study.target.verify()
    closure = dict(inherited["closure_sha256"])
    closure[str(study.TARGET / "READY.json")] = study.sha(study.TARGET / "READY.json")
    panel = study.read(study.PANEL / "MANIFEST.json")
    for path, expected in panel["source_and_artifact_sha256"].items():
        if study.sha(path) != expected:
            raise ValueError("fresh panel source changed: " + path)
        closure[path] = expected
    closure[str(study.PANEL / "MANIFEST.json")] = study.sha(study.PANEL / "MANIFEST.json")
    rows = study.make_schedule()
    study.write(study.ROOT / "inputs/SCHEDULE.json", rows)
    visits = Counter((r["arm"], i) for r in rows for i in r["ids"])
    if len(rows) != 152 or len(visits) != 512 or set(visits.values()) != {1}:
        raise ValueError("wrong152/512 inventory")
    context = study.context_bound(rows, study.read(study.CONTEXT_SOURCE)["vllm"]["max_model_len"])
    if context["service_max_model_len"] != 8192:
        raise ValueError("fixed8192 context required")
    inventory = {}
    for dataset in ("trec", "ag_news"):
        for arm in ("original", "neighbor_A", "neighbor_B", "singleton"):
            selected = [r for r in rows if r["dataset"] == dataset and r["arm"] == arm]
            inventory[f"{dataset}:{arm}"] = {
                "calls": len(selected),
                "records": sum(len(r["ids"]) for r in selected),
                "planned_prompt_tokens": sum(len(r["body"]["token_ids"]) for r in selected),
                "maximum_prompt_tokens": max(len(r["body"]["token_ids"]) for r in selected),
            }
    manifest = {
        "schema": "fresh-adaptive-helper-manifest-v1",
        "physical_calls": 152,
        "prediction_slots": 512,
        "unique_records": 128,
        "context_bound": context,
        "inventory": inventory,
        "schedule_sha256": study.digest(study.schedule()),
        "design_sha256": study.sha(study.ROOT / "DESIGN.md"),
        "binding": study.source().binding(),
        "panel_manifest_sha256": study.sha(study.PANEL / "MANIFEST.json"),
        "panel_identity": panel["identity"],
        "public_sha256": study.sha(study.PANEL / "PUBLIC.json"),
        "host_gold_sha256": study.sha(study.PANEL / "HOST_GOLD.json"),
        "permutation_namespace": (
            "helper-adaptive-fresh-live-v1|202609121212|dataset|neighbor_A_or_B|column"
        ),
        "model_seeds": {"trec": 202609121210, "ag_news": 202609121211},
        "temperature": 0,
        "policy_calls": {
            "original16": 8,
            "three_vote": 24,
            "selective_singleton": "16+D",
            "always_singleton": 128,
        },
        "stages": [
            "O+A:16",
            "ESCALATION_COMMIT",
            "selected_singletons:D",
            "B:8",
            "remaining_singletons:128-D",
        ],
        "gold_isolation": (
            "CPU host stratification only; public-only grouping and routing; "
            "owner reads gold only after generation terminal/release."
        ),
        "previous_responses_reused": False,
        "neighbor_slot_preserved": True,
        "absolute_token_offsets_preserved": False,
        "exposure": panel["limitations"],
        "runtime": "one fresh v4 batch-invariant service; no prior-run pooling",
        "request_hashes": {
            r["call_id"]: {
                "body": study.digest(r["body"]),
                "ordered_schema": study.digest(r["schema_ordered_json"]),
                "prompt_ids": study.digest(r["body"]["token_ids"]),
            }
            for r in rows
        },
    }
    study.write(study.ROOT / "MANIFEST.json", manifest)
    command = [str(study.NATIVE), "-m", "pytest", "-q", "test_adaptive.py"]
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
            "red_evidence": (
                "Initial two fixtures failed with missing adaptive_metrics/adaptive_study "
                "before implementation (2 failed in0.08s)."
            ),
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
    closure.update({str(p): study.sha(p) for p in paths})
    ready = {
        "schema": "fresh-adaptive-helper-ready-v1",
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
            "1100",
        ],
        "owner_cap_seconds": 1100,
        "external_timeout_seconds": 1200,
        "gpu_launched": False,
        "launch_authority": "MAIN only under shared GPU flock",
        "physical_calls": 152,
        "prediction_slots": 512,
        "unique_records": 128,
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
            "ready_sha256": study.sha(study.ROOT / "READY.json"),
            "identity": ready["identity"],
            "pins": len(closure),
            "tests": tests.stdout.strip(),
            "context_bound": context,
            "inventory": inventory,
        }
    )


if __name__ == "__main__":
    main()
