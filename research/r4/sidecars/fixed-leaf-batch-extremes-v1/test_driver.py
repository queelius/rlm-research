import importlib.util
from pathlib import Path

import pytest

loader = importlib.util.spec_from_file_location(
    "batch_extremes", Path(__file__).with_name("driver.py")
)
module = importlib.util.module_from_spec(loader)
loader.loader.exec_module(module)


@pytest.mark.parametrize("size,calls", [(1, 3072), (64, 48)])
def test_batch_extremes_preserve_questions_pairing_seeds_and_request_inputs(size, calls):
    spec = module.make_spec(size)
    design = spec["design"]
    assert len(design["coordinates"]) == 48
    assert len(design["plan"]) == calls
    assert len({r["id"] for r in design["plan"]}) == calls
    assert design["max_tokens"] == 1024
    assert all(len(batch["questions"]) == size for batch in design["batches"])
    for coordinate in design["coordinates"]:
        rows = [r for r in design["plan"] if r["coordinate_id"] == coordinate["id"]]
        assert len(rows) == 64 // size
        assert {r["seed"] for r in rows} == {coordinate["seed"]}
        groups = [g for r in rows for g in design["batches"][r["batch_id"]]["question_group_ids"]]
        assert len(groups) == len(set(groups)) == 64
    row = design["plan"][0]
    expected = module.fixed.make_request(design, row)
    design["batches"][row["batch_id"]]["gold"] = ["HOST_GOLD_SENTINEL"] * size
    assert module.fixed.make_request(design, row) == expected


def test_unsupported_batch_size_is_rejected():
    with pytest.raises(ValueError, match="one or sixty-four"):
        module.make_spec(16)
