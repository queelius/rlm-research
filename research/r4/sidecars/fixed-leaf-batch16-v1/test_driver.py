import importlib.util
from pathlib import Path

spec = importlib.util.spec_from_file_location("batch16", Path(__file__).with_name("driver.py"))
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)


def test_batch16_preserves_all_coordinates_questions_and_seeds():
    frozen = module.make_spec()
    design = frozen["design"]
    assert len(design["coordinates"]) == 48
    assert len(design["plan"]) == 192
    assert all(len(batch["questions"]) == 16 for batch in design["batches"])
    assert len({row["id"] for row in design["plan"]}) == 192
    for coordinate in design["coordinates"]:
        calls = [r for r in design["plan"] if r["coordinate_id"] == coordinate["id"]]
        assert len(calls) == 4
        assert {r["seed"] for r in calls} == {coordinate["seed"]}
        groups = [g for r in calls for g in design["batches"][r["batch_id"]]["question_group_ids"]]
        assert len(groups) == len(set(groups)) == 64
