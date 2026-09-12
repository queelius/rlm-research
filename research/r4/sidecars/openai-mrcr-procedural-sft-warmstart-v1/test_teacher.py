import builtins
import importlib.util
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parent
DATA = ROOT.parent / "openai-mrcr-short-root-data-v1"
SHORT = ROOT.parent / "openai-mrcr-short32-base-calibration-v1"
V7 = ROOT.parent / "mrcr-v3-root-procedure-calibration-v1"


def load_teacher():
    spec = importlib.util.spec_from_file_location("procedural_teacher_tested", ROOT / "teacher.py")
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def train_rows():
    return json.loads((DATA / "MODEL_INPUTS_V2.json").read_text())["train"]


def test_one_generic_public_rule_recovers_all_32_training_answers():
    teacher = load_teacher()
    gold = json.loads((DATA / "host/HOST_GOLD.json").read_text())["train"]
    rows = []
    for source in train_rows():
        question = Path(source["final_question_path"]).read_text()
        messages = json.loads(Path(source["prompt_json_path"]).read_text())
        result = teacher.construct(question, messages)
        rows.append(result)
        assert result["answer"] == gold[source["id"]]["answer"]
        assert result["matching_user_indices"] == result["all_matching_user_indices"]
        assert len(result["matching_user_indices"]) == 2
        assert result["selected_message_index"] == result["matching_user_indices"][
            result["criteria"]["ordinal"] - 1
        ] + 1
    assert len(rows) == 32
    assert {row["criteria"]["ordinal"] for row in rows} == {1, 2}


def test_authored_program_uses_only_public_query_constants_and_context_json():
    teacher = load_teacher()
    for source in train_rows():
        question = Path(source["final_question_path"]).read_text()
        payload = Path(source["prompt_json_path"]).read_bytes()
        messages = json.loads(payload)
        result = teacher.construct(question, messages)
        actual = teacher.execute_authored_code(result["authored_code"], payload)
        assert actual == result["answer"] + "\n"
        assert repr(result["answer"]) not in result["authored_code"]
        assert "selected_message_index" not in result["authored_code"]
        assert result["criteria"]["request_text"] in result["authored_code"]
        assert result["criteria"]["marker"] in result["authored_code"]


def test_renderer_matches_actual_short32_prefix_and_masks_only_root_suffixes():
    teacher = load_teacher()
    rendered = teacher.render_training_rows()
    actual = json.loads((SHORT / "cpu-child-smoke-v2/PROVIDER_REQUESTS.json").read_text())
    assert len(rendered["episodes"]) == 32
    assert rendered["episodes"][0]["turns"][0]["input_ids"][
        : rendered["episodes"][0]["turns"][0]["prompt_length"]
    ] == actual[0]["token_ids"]
    for episode in rendered["episodes"]:
        assert [turn["kind"] for turn in episode["turns"]] == ["root_action", "terminal"]
        for turn in episode["turns"]:
            prefix = turn["prompt_length"]
            assert turn["labels"] == [-100] * prefix + turn["input_ids"][prefix:]
            assert turn["loss_mask"] == [0] * prefix + [1] * turn["target_tokens"]
            assert turn["input_ids"][-1] == 151645
            assert len(turn["input_ids"]) <= 8192
    assert rendered["heldout_query_files_read"] == 0
    assert rendered["heldout_context_files_read"] == 0
    assert rendered["heldout_gold_records_used"] == 0
