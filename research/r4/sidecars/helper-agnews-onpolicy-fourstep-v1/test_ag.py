import importlib.util
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parent


def load(name):
    spec = importlib.util.spec_from_file_location(name, ROOT / f"{name}.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_frozen_groups_have_ag_prompt_schema_and_balanced_steps():
    prepare = load("prepare_inputs")
    bundle = prepare.make_inputs()
    groups, gold = bundle["step_groups"], bundle["gold"]
    from transformers import AutoTokenizer

    tokenizer = AutoTokenizer.from_pretrained(prepare.MODEL, local_files_only=True)
    decoded = tokenizer.decode(groups[0][0]["prompt_ids"], skip_special_tokens=False)
    assert "Classify the primary topic of each news item" in decoded
    assert "Classify the type of answer requested" not in decoded
    assert len(groups) == 4
    assert all(len(step) == 32 for step in groups)
    assert len({row["group_id"] for step in groups for row in step}) == 128
    for step in groups:
        labels = [gold[row["group_id"]] for row in step]
        assert {label: labels.count(label) for label in prepare.AG_VALUES} == {
            label: 8 for label in prepare.AG_VALUES
        }
        for row in step:
            assert "Classify the primary topic of each news item" in row["request_text"]
            assert "Classify the type of answer requested" not in row["request_text"]
            schema = json.loads(row["schema_ordered_json"])
            assert list(schema["properties"]) == row["requested_ids"]
            assert schema["required"] == row["requested_ids"]
            assert schema["properties"][row["requested_ids"][0]]["enum"] == list(
                prepare.AG_VALUES
            )


def test_reward_accepts_all_four_ag_labels_and_rejects_trec_value():
    runtime = load("ag_runtime")
    for label in runtime.AG_VALUES:
        assert runtime.local_reward(json.dumps({"x": label}), "x", label, True) == 1.0
    assert runtime.local_reward(json.dumps({"x": "entity"}), "x", "World", True) == 0.0
    assert runtime.local_reward(json.dumps({"x": "World"}), "x", "World", False) == 0.0


def test_training_step_selector_uses_four_disjoint_inventories():
    runtime = load("ag_runtime")
    steps = runtime.load_training_inputs()
    assert len(steps) == 4
    assert all(len(step) == runtime.GROUPS for step in steps)
    assert len({row["group_id"] for step in steps for row in step}) == 128


def test_actual_true_hf_collector_binding_uses_ag_reward():
    runtime = load("train_ag")
    assert callable(runtime.reference.execute_update)
    assert runtime.core.v1.local_reward(
        json.dumps({"x": "Sci/Tech"}), "x", "Sci/Tech", True
    ) == 1.0
    assert runtime.core.v1.SAMPLES == 128
    assert runtime.core.v1.TEMPERATURE == 1.0
