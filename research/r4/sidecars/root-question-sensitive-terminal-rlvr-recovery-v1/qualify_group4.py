"""CPU-only proof that six exact QS task groups of four reach trainer admission."""
import importlib.util
import math
from pathlib import Path
from types import SimpleNamespace

import terminal_common as common
import terminal_export as export
import terminal_prepare as prepare
import terminal_study as study
import terminal_train as train


def qualify():
    source = study.SIDE / "single-gpu-rlvr-v2/source/single_gpu_rlvr.py"
    spec = importlib.util.spec_from_file_location("terminal_group4_qualification_generic", source)
    generic = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(generic)
    original = export.qualified.impl.n.stack
    export.qualified.impl.n.stack = lambda: SimpleNamespace(native=SimpleNamespace(
        e=SimpleNamespace(capture=SimpleNamespace(recursive=SimpleNamespace(
            exporter=SimpleNamespace(trainer_module=lambda: generic))))))
    try:
        plan = prepare.build_inputs()["PLANS.json"]["training"]["1"]
        generation = common.generation(1, study.fixed_start())
        turn = {"input_ids": [1, 2, 3, 4], "labels": [-100, -100, 3, 4],
                "loss_mask": [0, 0, 1, 1],
                "old_logprobs": [-math.log(5), -math.log(5)], "prompt_length": 2}
        rows = [{"episode_id": row["id"], "task_id": row["task_name"], "split": "training",
                 "sample_seed": row["seed"], "temperature": 0.5, "trace_trainable": True,
                 "reward": row["repeat"] % 2, "turns": [turn], "coordinate": row,
                 "qualification_only": False, "generation_id": generation["generation_id"]}
                for row in plan]
        group = export.qualified.impl.mixed_group(
            rows, generation, {"fixture": "CPU-only role binding"}, "group4-fixture")
        train.check_members(rows, plan, generation)
    finally:
        export.qualified.impl.n.stack = original
    grouped = {}
    for row in group["episodes"]:
        grouped.setdefault(row["task_id"], []).append(row["advantage"])
    if len(grouped) != 6 or any(values != [-1.0, 1.0, -1.0, 1.0]
                                for values in grouped.values()):
        raise ValueError("not six exact four-sample centered groups")
    return {
        "schema": "question-sensitive-terminal-rlvr-group4-qualification-v1",
        "cpu_only": True,
        "qualified_export_function": "qsr_export.impl.mixed_group",
        "qualified_trainer_boundary": "qsr_train.check_members",
        "group_id": group["group_id"],
        "episodes_reaching_trainer_boundary": len(group["episodes"]),
        "distinct_exact_qs_tasks": len(grouped),
        "samples_per_task": {key: len(value) for key, value in sorted(grouped.items())},
        "advantages": {key: value for key, value in sorted(grouped.items())},
        "root_action_mask": turn["loss_mask"],
        "prompt_labels_masked": turn["labels"][:turn["prompt_length"]],
        "conditional_on_format_valid": True,
        "malformed_or_missing_not_in_fixture": True,
        "source_sha256": {str(source): study.sha(source),
                          str(study.QSR / "qsr_export.py"): study.sha(study.QSR / "qsr_export.py"),
                          str(study.QSR / "qsr_train.py"): study.sha(study.QSR / "qsr_train.py")},
    }


if __name__ == "__main__":
    result = qualify()
    output = study.ROOT / "GROUP4_QUALIFICATION.json"
    study.write(output, result)
    print(result["group_id"])
