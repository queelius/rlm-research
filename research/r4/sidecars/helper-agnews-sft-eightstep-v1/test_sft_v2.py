"""V2 changes only diagnostic label spans and binds the real trainer locally."""

import importlib


def test_inner_value_span_and_objective_inputs_unchanged():
    v1 = importlib.import_module("sft_study")
    v2 = importlib.import_module("sft_study_v2")
    old, new = v1.teacher_schedule(), v2.teacher_schedule()
    assert sum(sum(row["label_token_mask"]) for rows in old for row in rows) == 3584
    assert sum(sum(row["label_token_mask"]) for rows in new for row in rows) == 1536
    for old_rows, new_rows in zip(old, new, strict=True):
        for before, after in zip(old_rows, new_rows, strict=True):
            assert before["input_ids"] == after["input_ids"]
            assert before["labels"] == after["labels"]
            probe = dict(after)
            probe["label_token_mask"] = before["label_token_mask"]
            assert probe == before


def test_actual_v2_owner_trainer_study_binding():
    study = importlib.import_module("sft_study_v2")
    train = importlib.import_module("train_sft_v2")
    owner = importlib.import_module("owner_v2")
    assert train.study is study and train.source.study is study
    assert owner.study is study and owner.train_sft is train
    assert callable(train.run) and callable(owner.execute)
    assert study.plan()["command"][1].endswith("owner_v2.py")
