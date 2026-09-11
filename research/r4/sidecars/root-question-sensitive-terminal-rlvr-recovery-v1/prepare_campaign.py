"""Freeze source and input closure for MAIN review; does not create READY."""
import terminal_prepare as prepare
import terminal_study as study


def build():
    values = prepare.build_inputs()
    for name, value in values.items():
        if study.read(study.ROOT / "inputs" / name) != value:
            raise ValueError("frozen input differs from builder: " + name)
    source_names = [
        "ATTEMPT001_FAILURE.json", "DESIGN.md", "PLAN.md", "RUNBOOK.md", "RECIPE.json", "START.json", "terminal_study.py", "terminal_prepare.py",
        "terminal_common.py", "terminal_native.py", "terminal_metrics.py", "terminal_collect.py",
        "terminal_export.py", "terminal_train.py", "terminal_owner.py", "qualify_group4.py",
        "GROUP4_QUALIFICATION.json", "qualify_transport.py", "test_terminal_rlvr.py", "prepare_campaign.py", "seal.py",
    ]
    source_sha = {str(study.ROOT / name): study.sha(study.ROOT / name) for name in source_names}
    input_sha = {str(path): study.sha(path) for path in sorted((study.ROOT / "inputs").glob("*.json"))}
    external = [
        study.SELECTION,
        study.CHECKPOINT / "adapter_model.safetensors",
        study.CHECKPOINT / "adapter_config.json",
        study.CHECKPOINT / "state.json",
        study.QS / "READY.json",
        study.QSR / "qsr_common.py",
        study.QSR / "qsr_native.py",
        study.QSR / "qsr_metrics.py",
        study.QSR / "qsr_collect.py",
        study.QSR / "qsr_export.py",
        study.QSR / "qsr_train.py",
        study.QSR / "owner.py",
        study.WARM / "warm_owner.py",
        study.WARM / "warm_study.py",
        study.QS / "qs_study.py",
        study.PRIOR / "READY.json",
        study.PRIOR / "launch.py",
        study.SIDE / "leaf-post-sft-suite-v1/suite.py",
        study.SIDE / "root-seed-lifecycle-continuation-v1/driver.py",
        study.LOCAL / "READY.json",
    ]
    input_sha.update({str(path): study.sha(path) for path in external})
    input_sha.update({str(path): study.sha(path) for path in
                      sorted((study.ROOT / "qualification-transport-attempt-002").rglob("*"))
                      if path.is_file()})
    value = {
        "schema": "question-sensitive-terminal-rlvr-recovery-campaign-v1",
        "campaign_id": study.CAMPAIGN_ID,
        "question": "Does terminal RL on composed QS tasks strengthen learned task-sensitive routines? Additive attempt-002 repairs only missing TASKS native identity fields after attempt-001 made zero physical calls.",
        "start": study.fixed_start(),
        "fixed_child_sha256": study.CHILD_SHA,
        "root_child_distinct": True,
        "training": {"contexts": 8, "tasks_per_context": 6, "samples_per_task": 4,
                     "planned": 192, "max_updates": 8, "fixed_cursor_noops": True},
        "readout": {"protected_tasks": 72, "policies": ["start", "rl_last"],
                    "planned": 144, "selection": "fixed-last; no selection"},
        "budget_seconds": {"inclusive": 7200, "training": 4500, "readout": 2400,
                           "cleanup": 300, "owned": 7170, "parent_margin": 30},
        "source_sha256": source_sha,
        "input_sha256": input_sha,
        "ready_status": "requires MAIN_REVIEW.json then seal.py; no GPU launch authorized",
    }
    value["identity"] = study.digest(value)
    return value


if __name__ == "__main__":
    campaign = build()
    study.write(study.ROOT / "CAMPAIGN.json", campaign)
    print(campaign["identity"])
