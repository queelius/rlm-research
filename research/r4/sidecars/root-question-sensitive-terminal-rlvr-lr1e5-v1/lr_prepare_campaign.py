"""Freeze the CPU-prepared LR1e-5 source/input closure; never creates READY."""
import lr_study as study


SOURCE_NAMES = (
    "DESIGN.md", "RECIPE.json", "START.json", "terminal_study.py", "lr_study.py", "prepare_inputs.py",
    "terminal_prepare.py", "regenerate_tasks.py", "qualify_transport_one.py", "qualify_adam.py",
    "terminal_common.py", "terminal_native.py", "terminal_metrics.py", "terminal_collect.py",
    "terminal_export.py", "terminal_train.py", "lr_train.py", "lr_owner.py",
    "test_lr1e5.py", "lr_prepare_campaign.py", "lr_seal.py", "RUNBOOK.md",
    "ATTEMPT002_RECOVERY.md",
)


def build():
    baseline_owner = study.SOURCE / "outputs/attempt-003/OWNER_TERMINAL.json"
    owner = study.read(baseline_owner)
    if not owner.get("complete") or not owner.get("released"):
        raise ValueError("authenticated QS6 baseline owner is not complete/released")
    baseline_manifest = study.BASELINE / "MANIFEST.json"
    baseline_episodes = study.BASELINE / "EPISODES.json"
    manifest = study.read(baseline_manifest)
    if not manifest.get("complete") or manifest.get("planned") != 72 or manifest.get("recorded") != 72:
        raise ValueError("reused start baseline is not complete72")
    source_sha = {str(study.ROOT / name): study.sha(study.ROOT / name)
                  for name in SOURCE_NAMES}
    input_sha = {str(path): study.sha(path)
                 for path in sorted((study.ROOT / "inputs").glob("*.json"))}
    for directory in (study.ROOT / "qualification-transport1", study.ROOT / "qualification-adam"):
        input_sha.update({str(path): study.sha(path) for path in sorted(directory.rglob("*"))
                          if path.is_file()})
    external = (
        baseline_owner, baseline_manifest, baseline_episodes,
        study.SELECTION, study.CHECKPOINT / "adapter_model.safetensors",
        study.CHECKPOINT / "adapter_config.json", study.CHECKPOINT / "state.json",
        study.QSR / "qsr_common.py", study.QSR / "qsr_train.py", study.QSR / "qsr_collect.py",
        study.QSR / "qsr_native.py", study.QSR / "qsr_export.py", study.WARM / "warm_owner.py",
        study.SPARSE / "sparse_math.py",
        study.SIDE / "root-rlvr-campaign-v1/campaign_train.py",
        study.SIDE / "leaf-post-sft-suite-v1/suite.py",
        study.SIDE / "root-seed-lifecycle-continuation-v1/driver.py",
    )
    input_sha.update({str(path): study.sha(path) for path in external})
    value = {
        "schema": "root-question-sensitive-terminal-rlvr-lr1e5-campaign-v1",
        "campaign_id": study.CAMPAIGN_ID,
        "question": "Does LR1e-5 improve the same tiny composed-task RLVR intervention?",
        "intervention": {"field": "learning_rate", "from": 5e-5, "to": 1e-5},
        "start": study.fixed_start(),
        "fixed_child_sha256": study.CHILD_SHA,
        "training": {"planned": 192, "windows": 8, "groups_per_window": 6,
                     "samples_per_group": 4, "max_updates": 8, "no_refill": True,
                     "optimizer_process_cap_seconds": 1800},
        "readout": {"new_calls": 72, "policy": "lr1e5_last", "reused_start_calls": 72},
        "baseline": {"owner_terminal": str(baseline_owner),
                     "owner_terminal_sha256": study.sha(baseline_owner),
                     "manifest_sha256": study.sha(baseline_manifest),
                     "episodes_sha256": study.sha(baseline_episodes)},
        "budget_seconds": {"training": 12000, "readout": 2700, "cleanup": 270,
                           "parent_margin": 30, "owned": 14970, "inclusive": 15000},
        "sparse_numerics_not_bitwise_dense": True,
        "qualification": {
            "transport_result_sha256": study.sha(study.ROOT / "qualification-transport1/RESULT.json"),
            "adam_result_sha256": study.sha(study.ROOT / "qualification-adam/RESULT.json"),
            "gpu_calls": 0,
        },
        "numerical_disclosure": "objective-matched sparse credited-position logits; original high-LR first update used dense logits",
        "reporting": "raw/native final accuracy plus agent-reviewed faithful+strict execution; no gold-zero coincidence promotion; NULL not zero; raw role-audit cost recount authoritative",
        "source_sha256": source_sha,
        "input_sha256": input_sha,
        "ready_status": "requires exact MAIN_REVIEW.json and seal.py; no GPU launch authorized",
    }
    value["identity"] = study.digest(value)
    return value


if __name__ == "__main__":
    value = build()
    path = study.ROOT / "CAMPAIGN.json"
    if path.exists():
        if study.read(path) != value:
            raise ValueError("existing campaign differs; preserve revision")
    else:
        study.write(path, value)
    print(value["identity"])
