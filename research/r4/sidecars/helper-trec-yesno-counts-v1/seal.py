"""Freeze56 requests, human-readable instruction diffs, explicit scoring map and provenance."""

import importlib.metadata
import os
import platform
import subprocess
import time
from collections import Counter

import yesno_study as study


def main():
    if os.environ.get("CUDA_VISIBLE_DEVICES") != "" or (study.ROOT / "READY.json").exists():
        raise ValueError("CPU-only first seal required")
    inherited = study.target.verify()
    closure = dict(inherited["closure_sha256"])
    closure[str(study.TARGET / "READY.json")] = study.sha(study.TARGET / "READY.json")
    rows = study.make_schedule()
    study.write(study.ROOT / "inputs/SCHEDULE.json", rows)
    if (
        Counter(row["arm"] for row in rows) != {"full": 8, "targeted": 48}
        or sum(len(row["ids"]) for row in rows) != 896
    ):
        raise ValueError("wrong56/896 inventory")
    diffs, mapping = {}, {}
    for row in rows:
        if row["arm"] == "targeted":
            diffs.setdefault(row["target"], row["instruction_diff"])
            mapping[row["target"]] = {
                "positive_output": "yes",
                "negative_output": "no",
                "positive_meaning": row["target"],
                "negative_meaning": [label for label in row["labels"] if label != row["target"]],
            }
    (study.ROOT / "INSTRUCTION_DIFFS.md").write_text(
        "# Frozen instruction-only verbalizer diffs\n\n"
        "Definitions and record text are unchanged.\n\n"
        + "\n".join(f"## {target}\n\n```diff\n{diff}```\n" for target, diff in diffs.items())
    )
    study.write(study.ROOT / "inputs/SCORING_MAP.json", mapping)
    old = study.read(study.OLD_RESULT)
    old_blocks = [
        block
        for block in range(8)
        if all(
            task["arms"][arm]["predicted_count"] is not None
            for task in old["tasks"]
            if task["dataset"] == "trec" and task["block"] == block
            for arm in ("full", "targeted")
        )
    ]
    if len(old_blocks) != 7:
        raise ValueError("original seven-completed-block secondary inventory changed")
    context = study.context_bound(rows, study.read(study.CONTEXT_SOURCE)["vllm"]["max_model_len"])
    if context["service_max_model_len"] != 8192:
        raise ValueError("fixed8192 context required")
    manifest = {
        "schema": "trec-yesno-counts-manifest-v1",
        "physical_calls": 56,
        "prediction_slots": 896,
        "target_count_tasks": 48,
        "unique_records": 128,
        "context_bound": context,
        "schedule_sha256": study.digest(study.schedule()),
        "binding": study.source().binding(),
        "design_sha256": study.sha(study.ROOT / "DESIGN.md"),
        "panel_manifest_sha256": study.sha(study.PANEL / "MANIFEST.json"),
        "public_sha256": study.sha(study.PANEL / "PUBLIC.json"),
        "host_gold_sha256": study.sha(study.PANEL / "HOST_GOLD.json"),
        "source_literal_result_sha256": study.sha(study.OLD_RESULT),
        "secondary_old_complete_blocks": old_blocks,
        "secondary_boundary": (
            "old42 tasks only, cross-service/cache history; fresh full-control drift reported"
        ),
        "model_seed": 202609120820,
        "temperature": 0,
        "batch_size": 16,
        "primary_old_responses_reused": False,
        "gold_isolation": "public-only prompt transformation; host-only scoring",
        "inventory": {
            arm: {
                "calls": sum(row["arm"] == arm for row in rows),
                "planned_prompt_tokens": sum(
                    len(row["body"]["token_ids"]) for row in rows if row["arm"] == arm
                ),
            }
            for arm in ("full", "targeted")
        },
        "request_hashes": {
            row["call_id"]: {
                "source_call_id": row["source_call_id"],
                "body": study.digest(row["body"]),
                "ordered_schema": study.digest(row["schema_ordered_json"]),
                "prompt_ids": study.digest(row["body"]["token_ids"]),
            }
            for row in rows
        },
        "exposure": "absent from verified c32 SFT/new32; pretraining unknown; now research-exposed",
        "prospective_token_ratio_screen": 1.25,
        "calibration_explanation_is_hypothesis": True,
    }
    study.write(study.ROOT / "MANIFEST.json", manifest)
    command = [str(study.NATIVE), "-m", "pytest", "-q", "test_yesno.py"]
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
            study.ROOT / "inputs/SCORING_MAP.json",
            study.OLD_RESULT,
            study.OLD_RESULT.parent / "OWNER_TERMINAL.json",
            study.OLD_RESULT.parent / "ENGINECORE_BATCH_INVARIANT_FINAL.json",
        ]
    )
    closure.update({str(path): study.sha(path) for path in paths})
    ready = {
        "schema": "trec-yesno-counts-ready-v1",
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
            "750",
        ],
        "owner_cap_seconds": 750,
        "external_timeout_seconds": 850,
        "gpu_launched": False,
        "launch_authority": "MAIN only under shared GPU flock",
        "physical_calls": 56,
        "prediction_slots": 896,
        "target_count_tasks": 48,
        "unique_records": 128,
        "environment": {
            "python": platform.python_version(),
            "executable": str(study.NATIVE),
            "packages": {
                name: importlib.metadata.version(name)
                for name in ("torch", "transformers", "vllm", "xgrammar", "pyarrow")
            },
        },
        "context_bound": context,
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
            "inventory": manifest["inventory"],
            "secondary_blocks": old_blocks,
        }
    )


if __name__ == "__main__":
    main()
