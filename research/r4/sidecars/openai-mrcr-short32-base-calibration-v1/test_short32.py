import asyncio
import hashlib
import json

import pytest

import study


def test_plan_is_first_eight_train_only_g4_repeat_major():
    public = study.read(study.DATA / "MODEL_INPUTS_V2.json")
    plan = study.plan()
    expected_ids = [row["id"] for row in public["train"][:8]]
    assert len(plan) == 32
    assert [row["record_id"] for row in plan[:8]] == expected_ids
    assert [row["repeat"] for row in plan] == [r for r in range(4) for _ in range(8)]
    assert {row["record_id"] for row in plan} == set(expected_ids)
    assert not ({row["record_id"] for row in plan} & {row["id"] for row in public["heldout"]})
    assert [row["seed"] for row in plan] == [
        2026091300 + 4 * index + repeat
        for repeat in range(4)
        for index in range(8)
    ]
    assert max(row["seed"] for row in plan) < 2**32


def test_task_inputs_preserve_original_json_and_disclose_no_gold(tmp_path):
    receipt = study.prepare_inputs(tmp_path)
    tasks = study.read(tmp_path / "tasks.json")
    public = study.read(study.DATA / "MODEL_INPUTS_V2.json")["train"][:8]
    gold = study.read(study.DATA / "host/HOST_GOLD.json")["train"]
    assert receipt["tasks"] == 32
    assert len(tasks) == 32
    for task in tasks:
        row = next(item for item in public if item["id"] == task["row_id"])
        payload = (tmp_path / "contexts" / f"{task['document_sha256']}.json").read_bytes()
        assert payload == study.Path(row["prompt_json_path"]).read_bytes()
        assert hashlib.sha256(payload).hexdigest() == task["document_sha256"]
        assert gold[task["row_id"]]["answer"] not in task["prompt"]
        assert "desired_msg_index" not in task["prompt"]
        assert "needle" not in task["prompt"].lower()
        assert "/context.json" in task["prompt"]
    assert not (tmp_path / "HOST_GOLD_HELDOUT.json").exists()


def test_official_score_and_failure_taxonomy_are_distinct():
    answer = "MARKER1234payload"
    valid = study.classify_outcome(
        root_reply=answer,
        answer=answer,
        marker="MARKER1234",
        stop_condition="agent_completed",
        trace_ok=True,
        trace_errors=[],
        returned_root_actions=1,
        returned_child_actions=0,
        native_mapping_complete=True,
    )
    assert valid["scientifically_available"] is True
    assert valid["reward"] == pytest.approx(1.0)
    limited = study.classify_outcome(
        root_reply=None,
        answer=answer,
        marker="MARKER1234",
        stop_condition="max_turns",
        trace_ok=False,
        trace_errors=[],
        returned_root_actions=2,
        returned_child_actions=1,
        native_mapping_complete=True,
    )
    assert limited["scientifically_available"] is True
    assert limited["reward"] == 0.0
    assert limited["failure_class"] == "model_finite_horizon"
    infra = study.classify_outcome(
        root_reply=None,
        answer=answer,
        marker="MARKER1234",
        stop_condition="max_turns",
        trace_ok=False,
        trace_errors=[{"type": "TransportError"}],
        returned_root_actions=2,
        returned_child_actions=0,
        native_mapping_complete=False,
    )
    assert infra["scientifically_available"] is False
    assert infra["reward"] is None
    assert infra["failure_class"] == "infrastructure_unavailable"


def test_canonical_task_setup_writes_exact_context_json(tmp_path):
    study.prepare_inputs(tmp_path)
    env = study.environment(tmp_path)
    task = list(env.taskset)[0]
    writes = {}

    class Runtime:
        async def write(self, path, payload):
            writes[path] = payload

        async def read(self, path):
            return writes[path]

    asyncio.run(task.setup(None, Runtime()))
    assert set(writes) == {"/context.json"}
    assert hashlib.sha256(writes["/context.json"]).hexdigest() == task.data.document_sha256


def test_repaired_recorder_is_loaded_from_sealed_v7_source():
    import collect

    recorder = collect.v7_recorder()
    assert study.Path(recorder.__file__).resolve() == (study.V7 / "collect_v7.py").resolve()
    assert recorder.pending_turn_metadata.__module__ == "short32_v7_collect"


def test_summarize_keeps_model_failures_zero_and_infra_missing():
    import collect

    records = []
    for coordinate in study.plan():
        reward = 1.0 if coordinate["repeat"] == 0 else 0.0
        records.append(
            {
                "coordinate": coordinate,
                "derived": {
                    "scientifically_available": True,
                    "reward": reward,
                    "failure_class": "model_finite_horizon" if reward == 0 else None,
                    "root_actions_returned": 1,
                    "child_actions_returned": 0,
                    "delegated": False,
                    "native_attempts": 1,
                    "native_returned": 1,
                    "native_errors": 0,
                    "trace_ambiguous_calls": 0,
                    "action_tokens": 2,
                    "six_total_root_child_cap_respected": True,
                },
            }
        )
    value = collect.summarize(records)
    assert value["complete"] is True
    assert value["scientifically_available"] == 32
    assert value["infrastructure_unavailable"] == 0
    assert value["model_finite_horizon"] == 24
    assert value["mixed_groups"] == 8
    assert value["future_root_rl_gate"]["eligible"] is True
    records[0]["derived"].update(
        scientifically_available=False,
        reward=None,
        failure_class="infrastructure_unavailable",
    )
    value = collect.summarize(records)
    assert value["future_root_rl_gate"]["eligible"] is False
    assert value["infrastructure_unavailable"] == 1


def test_runtime_condition_requires_real_v7_returned_calls_and_clean_release(tmp_path):
    import owner

    attempt = tmp_path / "attempt"
    (attempt / "science").mkdir(parents=True)
    study.write_x(
        attempt / "OWNER_TERMINAL.json",
        {"complete": True, "released": True, "errors": None, "elapsed_seconds": 420},
    )
    study.write_x(
        attempt / "science/RESULT.json",
        {
            "complete": True,
            "recorded": 32,
            "native_start_files": 70,
            "native_result_files": 70,
        },
    )
    value = owner.runtime_condition(attempt)
    assert value["qualified"] is True
    assert value["observed_elapsed_seconds"] == 420
    (attempt / "science/RESULT.json").unlink()
    study.write_x(
        attempt / "science/RESULT.json",
        {"complete": True, "recorded": 32, "native_start_files": 70, "native_result_files": 0},
    )
    assert owner.runtime_condition(attempt)["qualified"] is False


def test_owner_has_no_retry_and_exact_caps():
    import owner

    assert owner.OWNER_SECONDS == 900
    assert owner.SCIENCE_SECONDS == 600
    assert owner.COLLECTOR == study.ROOT / "collect.py"


def test_finalizer_keeps_caps_only_after_valid_v7_runtime():
    import finalize_after_v7 as finalize

    condition = {
        "qualified": True,
        "observed_elapsed_seconds": 590,
        "recorded": 32,
        "returned_native_responses": 64,
        "pending_turn_serialization_errors": 0,
        "terminal_sha256": "a" * 64,
        "result_sha256": "b" * 64,
        "reason": None,
    }
    assert finalize.validate_runtime(condition)["caps_retained"] is True
    condition["observed_elapsed_seconds"] = 601
    with pytest.raises(ValueError, match="600-second science cap"):
        finalize.validate_runtime(condition)


def test_conditional_receipt_is_not_launch_ready():
    import prepare

    value = prepare.receipt_value({"returncode": 0, "stdout": "9 passed", "stderr": ""}, {})
    assert value["status"] == "CPU_READY_CONDITIONAL_ON_ACTUAL_V7_RUNTIME"
    assert value["fixed_argv"][-1] == "900"
    assert value["science"]["heldout_model_queries"] == 0
    assert value["science"]["max_completed_turns_cumulative_root_child"] == 6
    assert "identity" not in value
