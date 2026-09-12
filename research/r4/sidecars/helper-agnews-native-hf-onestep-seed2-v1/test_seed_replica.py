"""Focused seed-only replica and inherited runtime-boundary contracts."""

import copy
import importlib
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parent
SOURCE = ROOT.parent / "helper-agnews-native-hf-onestep-v1"


def load_local():
    sys.path.insert(0, str(ROOT))
    try:
        for name in ("owner", "native_collect", "train_ag", "prepare_masks", "ag_study"):
            sys.modules.pop(name, None)
        return importlib.import_module("ag_study")
    finally:
        sys.path.remove(str(ROOT))


def test_schedule_changes_only_seed_and_coordinate_namespace():
    study = load_local()
    old = study.source_study.schedule()
    new = study.schedule()
    assert len(old) == len(new) == 128
    assert [row["seed"] for row in new] == [
        202609127000 + 4 * group + repeat for repeat in range(4) for group in range(32)
    ]
    assert len({row["coordinate_id"] for row in new}) == 128
    for before, after in zip(old, new, strict=True):
        expected = copy.deepcopy(after)
        expected["seed"] = before["seed"]
        expected["coordinate_id"] = before["coordinate_id"]
        expected["body"]["sampling_params"]["seed"] = before["body"]["sampling_params"][
            "seed"
        ]
        assert expected == before
    assert study.SEED == 202609127300
    assert study.ATTEMPT == ROOT / "outputs/attempt-001"


def test_actual_owner_and_numeric_subprocess_dependencies_resolve():
    study = load_local()
    owner = importlib.import_module("owner")
    native = importlib.import_module("native_collect")
    prepare = importlib.import_module("prepare_masks")
    train = importlib.import_module("train_ag")
    assert owner.study is study
    assert native.study is study
    assert prepare.study is study
    assert train.study is study
    assert callable(owner.execute)
    assert callable(prepare.prepare)
    assert callable(train.numeric_update)
    assert len(native.study.schedule()) == 128
    assert train.study.SEED == 202609127300
