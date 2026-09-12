import importlib.util
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parent


def load(name):
    spec = importlib.util.spec_from_file_location(name, ROOT / (name + ".py"))
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def test_owner_run_metadata_names_the_allocation_runtime_repair():
    load("study")
    load("study_v3")
    load("study_v4")
    load("owner_v4")
    owner = load("owner_v4_1")
    value = owner.correct_owner_run({"repair": "stale", "planned_episodes": 32})
    assert value["repair"] == owner.REPAIR
    assert value["planned_episodes"] == 32

