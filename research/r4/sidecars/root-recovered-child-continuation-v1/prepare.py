"""CPU-only freeze of actual inputs and the newly identified round04 export."""

import json
import os
from pathlib import Path

import common as a
import native_amendment as amended

c = a.c


def main():
    if os.environ.get("CUDA_VISIBLE_DEVICES") != "":
        raise ValueError("prepare with CUDA_VISIBLE_DEVICES='' explicitly")
    c.verify_campaign()
    stops = list(a.OLD_RUN.glob("STOP-*.json"))
    if len(stops) != 1 or c.read(stops[0])["optimizer_steps"] != 3:
        raise ValueError("original exact three-step STOP not present")
    if any(a.OLD_RUN.glob("round-04/training*")) or any(a.OLD_RUN.glob("round-0[5-8]*")):
        raise ValueError("old run has unexpected unfinished/new stages")
    files = [a.OLD_RUN / "RUN.json", a.OLD_RUN / "EXECUTION_V2.json", stops[0],
             a.OLD_RUN / "round-04/GENERATION.json", a.OLD_ROUND04 / "SPEC.json",
             a.OLD_ROUND04.parent / "export/EPISODES.json", a.OLD_ROUND04.parent / "export/MANIFEST.json"]
    policies = {"0": c.original_policy()}
    for step in (1, 2, 3):
        directory = a.OLD_RUN / f"round-{step:02d}"
        generation = c.read(directory / "GENERATION.json")
        c.check_generation(generation, policies[str(step - 1)], step - 1)
        policies[str(step)] = c.checkpoint_policy(directory / "training", generation)
        files.extend([directory / "COMMIT.json", directory / "GENERATION.json",
            directory / "training/INPUTS.json", directory / "training/correction-capture.json",
            directory / f"training/checkpoint-{step}/state.json", directory / "collection/export/GROUP.json",
            directory / "collection/export/EPISODES.json", directory / "collection/export/MANIFEST.json"])
        state = c.read(directory / f"training/checkpoint-{step}/state.json")
        files.extend(directory / f"training/checkpoint-{step}" / name for name in state["files_sha256"])
    if policies["3"]["adapter_sha256"] != a.STEP3_SHA:
        raise ValueError("actualstep3 checkpoint changed")
    validation = {}
    for step in (0, 2):
        path = a.OLD_RUN / f"validation-{step:02d}/export"
        manifest = c.read(path / "MANIFEST.json")
        c.authenticate({path / name: sha for name, sha in manifest["artifact_sha256"].items()})
        files.extend([path / "MANIFEST.json", *[path / name for name in manifest["artifact_sha256"]]])
        validation[str(step)] = {"path": str(path), "manifest_sha256": c.file_hash(path / "MANIFEST.json")}
    prior = {"schema": "immutable-original-campaign-reference-map-v1", "old_run": str(a.OLD_RUN),
        "old_stop": str(stops[0]), "policies": policies, "validation_exports": validation,
        "source_sha256": {str(path): c.file_hash(path) for path in files},
        "old_round04_source_attempt": str(a.OLD_ROUND04), "old_files_mutated": 0}
    c.write_once(a.ROOT / "PRIOR.json", prior)
    source_names = ["common.py", "native_amendment.py", "train.py", "driver.py", "prepare.py", "qualify.py", "test_amendment.py", "test_continuation.py", "DESIGN.md", "PLAN.md"]
    amendment = {"schema": "root-recovered-child-exclusion-continuation-v1", "namespace": a.ROOT.name,
        "new_global_cap_seconds": a.CAP_SECONDS, "inherited_optimizer_steps": 3, "remaining_optimizer_steps": [4, 5, 6, 7, 8],
        "original_campaign_id": c.read(a.OLD / "CAMPAIGN.json")["campaign_id"],
        "original_campaign_sha256": c.file_hash(a.OLD / "CAMPAIGN.json"),
        "original_lifecycle_sha256": c.file_hash(a.OLD / "LIFECYCLE_V2.json"),
        "source_sha256": {str(a.ROOT / name): c.file_hash(a.ROOT / name) for name in source_names},
        "input_sha256": {str(a.ROOT / "PRIOR.json"): c.file_hash(a.ROOT / "PRIOR.json")},
        "admission_change": "none: known unsampled child context-overflow failures remain training exclusions",
        "round04_admitted_before_after": [29, 29], "round04_rerollouts": 0,
        "selection": "unchanged earliest maximum admitted strict successes over original fixed8; endpoint outcomes reported separately",
        "future_larger_amendment_not_implemented": "train authenticated recovered root actions with observed strict0",
        "runtime_overrides": ["campaign.committed_policies", "campaign.owned_command", "campaign_native.binding_for",
            "campaign_native.prepare_spec", "campaign_native.export", "campaign_native.authenticate_export", "campaign_train.authenticate_group"]}
    amendment["amendment_id"] = c.digest(amendment)
    c.write_once(a.ROOT / "AMENDMENT.json", amendment)
    manifest = amended.export(a.OLD_ROUND04, a.ROOT / "prepared-round04")
    proof = amended.authenticate_export(a.ROOT / "prepared-round04")
    c.write_once(a.ROOT / "CPU_RECLASSIFICATION.json", {"amendment_id": amendment["amendment_id"],
        "admitted_before": 29, "admitted_after": manifest["admitted_outcomes"],
        "existing_row_fields_unchanged": True, "integrity_failures": manifest["integrity_failures"],
        "endpoint_outcomes": manifest["endpoint_outcomes"], "reclassified_exclusions": manifest["reclassified_exclusions"],
        "training_group_episodes": manifest["training_group_episodes"], "verification": proof, "gpu_calls": 0})
    print(json.dumps({"amendment_id": amendment["amendment_id"], "admitted": manifest["admitted_outcomes"],
        "selected_training_episodes": manifest["training_group_episodes"], "endpoint_outcomes": manifest["endpoint_outcomes"], "gpu_calls": 0}, sort_keys=True))


if __name__ == "__main__":
    main()
