from pathlib import Path
import sys

import pytest

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))


def inventory():
    return {"complete": False, "readout_inventory": [
        {"arm": "corrective", "mode": "controlled", "coordinate_id": str(i), "recorded": False}
        for i in range(16)]}


def test_only_the_unattempted_controlled_panel_can_be_completed():
    import completion
    completion.check_original_inventory(inventory(), False)
    value = inventory()
    value["readout_inventory"][0]["recorded"] = True
    with pytest.raises(ValueError):
        completion.check_original_inventory(value, False)
    with pytest.raises(ValueError):
        completion.check_original_inventory(inventory(), True)


def test_collector_keeps_original_mode_plan_and_all_sixteen_seeds():
    import completion
    argv = completion.collector_argv(ROOT / "stage", ROOT / "outputs/attempt-001", 1234.5)
    assert argv[1] == str(completion.SOURCE / "collect.py")
    assert argv[2:10] == ["--mode", "controlled", "--plan", "CONTROLLED_PLAN.json",
                          "--start", "0", "--stop", "16"]
    assert argv[-4:] == ["--output", str(ROOT / "outputs/attempt-001/controlled"),
                         "--deadline", "1234.5"]
    with pytest.raises(ValueError):
        completion.collector_argv(ROOT / "stage", ROOT / "outputs/attempt-002", 1234.5)


def test_missing_native_finals_are_explicit_in_all_planned_slots(tmp_path):
    import completion
    rows = [{"id": str(i)} for i in range(16)]
    result = completion.inventory(rows, tmp_path)
    assert len(result) == 16
    assert all(x["recorded"] is False and x["reward"] is None for x in result)
