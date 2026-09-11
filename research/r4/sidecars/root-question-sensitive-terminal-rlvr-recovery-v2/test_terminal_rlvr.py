import importlib
import importlib.util
import json
import math
import os
from pathlib import Path
import subprocess
from types import SimpleNamespace

import pytest


ROOT = Path(__file__).resolve().parent


def modules():
    return (
        importlib.import_module("terminal_study"),
        importlib.import_module("terminal_prepare"),
        importlib.import_module("terminal_common"),
        importlib.import_module("terminal_owner"),
    )


def test_exact_qs6_root_and_distinct_fixed_c32_child():
    study, _, _, _ = modules()
    policy = study.fixed_start()
    assert policy["path"].endswith("outputs/attempt-003/training/checkpoint-0006")
    assert policy["adapter_sha256"] == "4d8287537a9ff3d8e33bc0314f64315dee06e71b801257b389dab8b667e27aca"
    assert policy["source_sft_step"] == 6 and policy["step"] == 0
    assert study.ROOT_START_SHA == policy["adapter_sha256"]
    assert study.CHILD_SHA == "c32de1293c01bba5104eb1f123867649c71dd38e5194661ace4b17dcbbe66ba3"
    assert study.CHILD_SHA != policy["adapter_sha256"]


def test_fixed_composed_192_and_protected_144():
    _, prepare, _, _ = modules()
    values = prepare.build_inputs()
    windows = values["PLANS.json"]["training"]
    assert set(windows) == {str(i) for i in range(1, 9)}
    rows = [row for window in windows.values() for row in window]
    assert len(rows) == 192 and len({row["id"] for row in rows}) == 192
    assert {row["slot"] for row in rows} == {"T1", "T2", "M1", "M2", "J1", "J2"}
    for window in windows.values():
        assert len(window) == 24 and len({row["context_id"] for row in window}) == 1
        assert sorted(row["repeat"] for row in window if row["slot"] == "J1") == [0, 1, 2, 3]
    readout = values["PLANS.json"]["readout"]
    assert len(readout) == 72 and all(row["split"] == "protected" for row in readout)
    assert len(values["PLANS.json"]["evaluation"]) == 144
    assert {row["context_id"] for row in rows}.isdisjoint({row["context_id"] for row in readout})


def test_reward_and_noop_rules_do_not_manufacture_outcomes():
    study, _, common, _ = modules()
    assert study.endpoint_reward("Answer: 7", 7, True, True) == 1
    assert study.endpoint_reward("", 7, True, True) == 0
    assert study.endpoint_reward("malformed", 7, True, True) == 0
    assert study.endpoint_reward(None, 7, False, False) is None
    policy = study.fixed_start()
    generation = common.generation(1, policy)
    noop = common.transition(0, policy, 1, None)
    assert generation["round"] == 1 and noop["policy"] == policy
    assert noop["completed_windows"] == 1 and noop["decision"] == "noop"
    with pytest.raises(ValueError):
        common.generation(9, policy)


def test_budget_and_checkpoint_namespaces_are_fixed(tmp_path):
    _, _, _, owner = modules()
    budget = owner.budget(1000.0)
    assert budget == {"started": 1000.0, "training_end": 5500.0, "work": 7900.0, "owned": 8170.0, "outer": 8200.0}
    a = owner.trainer_output(tmp_path / "window-01")
    b = owner.trainer_output(tmp_path / "window-02")
    assert a != b and a.name == b.name == "training"


def test_no_host_gold_is_embedded_in_tasks_or_prompts():
    _, prepare, _, _ = modules()
    values = prepare.build_inputs()
    assert all("gold" not in task and "answer" not in task for task in values["TASKS.json"].values())
    assert all("gold" not in prompt and "answer" not in prompt for prompt in values["PROMPTS_ACCURATE.json"].values())


def test_qualified_binding_uses_qs6_root_and_distinct_c32_child(monkeypatch):
    study, _, common, _ = modules()
    collect = importlib.import_module("terminal_collect")
    monkeypatch.setattr(study, "verify_prepared", study.verify_campaign)
    binding = collect.binding_for(study.fixed_start())
    assert binding["campaign_policy"] == study.fixed_start()
    models = binding["models"]
    assert models[binding["role_map"]["root"]]["adapter_sha256"] == study.ROOT_START_SHA
    assert models[binding["fixed_child"]]["adapter_sha256"] == study.CHILD_SHA
    generation = common.generation(1, study.fixed_start())
    assert generation["fixed_child_sha256"] == study.CHILD_SHA


def test_actual_entrypoint_names_and_fixed_inventory():
    owner = importlib.import_module("terminal_owner")
    collect = importlib.import_module("terminal_collect")
    train = importlib.import_module("terminal_train")
    assert callable(collect.collect) and callable(train.authenticate_group)
    inventory = owner.planned_inventory(ROOT / "outputs/fixture")
    assert len(inventory) == 336
    assert sum(row["phase"] == "training" for row in inventory) == 192
    assert sum(row["phase"] == "readout" for row in inventory) == 144
    assert {row["arm"] for row in inventory if row["phase"] == "readout"} == {
        "start", "rl_last"
    }


def test_capture_and_optimizer_timing_are_separate(tmp_path):
    study, _, _, owner = modules()
    for window, capture, optimizer in ((1, (10.0, 14.5), (15.0, 17.0)),
                                       (2, (20.0, 23.0), None)):
        stage = tmp_path / f"window-{window:02d}"
        (stage / "collection/rollout").mkdir(parents=True)
        study.write(stage / "collection/rollout/STATUS.json",
                    {"started_epoch": capture[0], "ended_epoch": capture[1]})
        if optimizer:
            study.write(stage / "TRAIN_COMMAND.json", {"started_epoch": optimizer[0]})
            study.write(stage / "TRAIN_EXIT.json", {"ended_epoch": optimizer[1]})
    for arm, interval in (("start", (30.0, 35.0)), ("rl_last", (40.0, 46.0))):
        stage = tmp_path / f"readout-{arm}/rollout"
        stage.mkdir(parents=True)
        study.write(stage / "STATUS.json",
                    {"started_epoch": interval[0], "ended_epoch": interval[1]})
    timing = owner.timing_summary(tmp_path)
    assert timing["training_capture"] == {"measured_stages": 2, "seconds": 7.5}
    assert timing["optimizer"] == {"measured_stages": 1, "seconds": 2.0}
    assert timing["protected_readout_capture"] == {"measured_stages": 2, "seconds": 11.0}
    assert timing["source"] == "native STATUS and TRAIN_COMMAND/TRAIN_EXIT epochs"


def test_collection_stage_resets_owner_alarm_to_collection_deadline(monkeypatch):
    _, _, _, owner = modules()
    calls = []
    monkeypatch.setattr(owner.qualified.time, "time", lambda: 1000.0)
    monkeypatch.setattr(owner, "remaining", lambda deadline, cap: min(cap, deadline - 1000.0))
    monkeypatch.setattr(owner, "alarm", lambda deadline: calls.append(deadline))
    monkeypatch.setattr(owner, "_qualified_collection_stage",
                        lambda *args, **kwargs: (args, kwargs))
    result = owner.collection_stage("suite", "service", "stage", "phase", 1500.0,
                                    "generation", 360)
    assert calls == [1360.0]
    assert result[0][4] == 1500.0


def test_actual_trainer_dispatch_preserves_exact_assigned_gpu(tmp_path, monkeypatch):
    study, _, common, owner = modules()
    stage = tmp_path / "window-01"
    stage.mkdir()
    spawned = []
    monkeypatch.setenv("CUDA_VISIBLE_DEVICES", "MIG-CPU-INTERCEPT")

    class Process:
        pid = 987654
        returncode = 0

        @staticmethod
        def wait(**_kwargs):
            return 0

    def popen(argv, **kwargs):
        spawned.append((argv, kwargs))
        return Process()

    monkeypatch.setattr(owner.qualified.subprocess, "Popen", popen)
    life = SimpleNamespace(observe=lambda pid: {"pid": pid}, safe_observation=lambda row: row)
    suite = SimpleNamespace(life=life, stop_child=lambda *_args: None)
    monkeypatch.setattr(common.c, "checkpoint_policy", lambda *_args: {"step": 1})
    result = owner.train_window(
        suite, stage, owner.qualified.time.time() + 500,
        common.generation(1, study.fixed_start()),
    )
    assert result == {"step": 1} and len(spawned) == 1
    argv, kwargs = spawned[0]
    assert kwargs["env"]["CUDA_VISIBLE_DEVICES"] == "MIG-CPU-INTERCEPT"
    assert argv[0] == str(study.TRAIN)
    assert argv[1] == str(study.ROOT / "terminal_train.py")


def test_pinned_qualified_cpu_collector_dispatch_hides_gpu():
    study, _, _, _ = modules()
    suite_source = study.SIDE / "leaf-post-sft-suite-v1/suite.py"
    source = suite_source.read_text()
    assert "'CUDA_VISIBLE_DEVICES': ''" in source
    assert "'gpu_visible_to_command': False" in source
    campaign = study.read(study.ROOT / "CAMPAIGN.json")
    assert campaign["input_sha256"][str(suite_source)] == study.sha(suite_source)


def test_paired_summary_uses_exact_start_and_rl_last_arm_names():
    metrics = importlib.import_module("terminal_metrics")
    coordinate = {"id": "fixture", "context_id": "context", "heldout_cell": False,
                  "records": 16}
    inventory = [
        {"phase": "readout", "arm": "start", "coordinate": coordinate, "reward": 0},
        {"phase": "readout", "arm": "rl_last", "coordinate": coordinate, "reward": 1},
    ]
    summary = metrics.paired_summary(inventory)
    assert set(summary["policies"]) == {"start", "rl_last"}
    assert summary["paired"] == {"wins": 1, "losses": 0, "ties": 0, "unknown": 0}


def test_authenticated_empty_native_final_is_observed_zero():
    metrics = importlib.import_module("terminal_metrics")
    assert metrics.endpoint.__globals__["score_message"] is metrics.score_message
    assert "terminal_native" in metrics.endpoint.__code__.co_names
    observed = metrics.score_message(None, "", [], "stop", 7)
    assert observed == {"available": True, "reward": 0, "format": False, "reply": "",
                        "finish_reason": "stop", "reason": None}
    missing = metrics.score_message(None, None, [], None, 7)
    assert missing["available"] is False and missing["reward"] is None


def test_recipe_and_fresh_cli_entrypoints_are_materialized():
    study, _, _, _ = modules()
    recipe = study.read(ROOT / "RECIPE.json")
    assert recipe["learning_rate"] == 5e-5
    assert recipe["ppo_clip_epsilon"] == 0.2 and recipe["tis_cap"] == 2.0
    assert recipe["fresh_optimizer"] is True and recipe["root_action_only"] is True
    assert recipe["root_adapter_sha256"] == study.ROOT_START_SHA
    assert recipe["fixed_child_adapter_sha256"] == study.CHILD_SHA
    environment = {**os.environ, "CUDA_VISIBLE_DEVICES": "", "PYTHONDONTWRITEBYTECODE": "1"}
    for python, script in ((study.NATIVE, "terminal_native.py"),
                           (study.NATIVE, "terminal_collect.py"),
                           (study.TRAIN, "terminal_train.py")):
        result = subprocess.run([str(python), str(ROOT / script), "--help"], cwd=ROOT,
                                env=environment, text=True, capture_output=True, timeout=30)
        assert result.returncode == 0, (script, result.stdout, result.stderr)
        assert "usage:" in result.stdout
    probe = subprocess.run(
        [str(study.NATIVE), "-c",
         "import json,terminal_collect as c,terminal_export as e,terminal_metrics as m;"
         "print(json.dumps({'collect_study':str(c.collect.__globals__['s'].ROOT),"
         "'collect_native':c.collect.__globals__['n'].__name__,"
         "'export_import_bound':'terminal_collect' in e.rebuild.__code__.co_names,"
         "'metrics_study':str(m.endpoint.__globals__['s'].ROOT),"
         "'metric_import_bound':'terminal_native' in m.endpoint.__code__.co_names}))"],
        cwd=ROOT, env=environment, text=True, capture_output=True, timeout=30, check=True,
    )
    bindings = json.loads(probe.stdout)
    assert bindings == {"collect_study": str(ROOT), "collect_native": "terminal_native",
                        "export_import_bound": True,
                        "metrics_study": str(ROOT), "metric_import_bound": True}


def test_actual_qualified_export_groups_four_per_qs_task_and_reaches_trainer(monkeypatch):
    study, prepare, common, _ = modules()
    export = importlib.import_module("terminal_export")
    train = importlib.import_module("terminal_train")
    source = study.SIDE / "single-gpu-rlvr-v2/source/single_gpu_rlvr.py"
    spec = importlib.util.spec_from_file_location("terminal_group4_generic", source)
    generic = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(generic)
    monkeypatch.setattr(export.qualified.impl.n, "stack", lambda: SimpleNamespace(
        native=SimpleNamespace(e=SimpleNamespace(capture=SimpleNamespace(
            recursive=SimpleNamespace(exporter=SimpleNamespace(
                trainer_module=lambda: generic)))))))
    plan = prepare.build_inputs()["PLANS.json"]["training"]["1"]
    generation = common.generation(1, study.fixed_start())
    turn = {"input_ids": [1, 2, 3, 4], "labels": [-100, -100, 3, 4],
            "loss_mask": [0, 0, 1, 1], "old_logprobs": [-math.log(5), -math.log(5)],
            "prompt_length": 2}
    rows = [{"episode_id": row["id"], "task_id": row["task_name"], "split": "training",
             "sample_seed": row["seed"], "temperature": 0.5, "trace_trainable": True,
             "reward": row["repeat"] % 2, "turns": [turn], "coordinate": row,
             "qualification_only": False, "generation_id": generation["generation_id"]}
            for row in plan]
    group = export.qualified.impl.mixed_group(rows, generation, {"fixture": True}, "fixture-dataset")
    assert group["group_id"] and len(group["episodes"]) == 24
    assert len({row["task_id"] for row in group["episodes"]}) == 6
    for task_id in {row["task_id"] for row in group["episodes"]}:
        values = [row["advantage"] for row in group["episodes"] if row["task_id"] == task_id]
        assert values == pytest.approx([-1.0, 1.0, -1.0, 1.0])
    train.check_members(rows, plan, generation)
