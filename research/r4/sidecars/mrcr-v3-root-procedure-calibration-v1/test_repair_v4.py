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


def test_v4_changes_only_runtime_image_and_preserves_exact_v3_inputs():
    base = load("study")
    v3 = load("study_v3")
    v4 = load("study_v4")
    expected = v3.environment_config(v3.INPUTS)
    actual = v4.environment_config(v4.INPUTS)
    expected["agent"]["runtime"] = {
        "type": "docker",
        "image": v4.IMAGE,
        "workdir": "/app",
    }
    assert actual == expected
    assert v4.INPUTS == v3.INPUTS
    assert v4.SPEC == v3.SPEC
    assert v4.plan() == base.plan()
    assert v4.ATTEMPT == ROOT / "outputs/attempt-004"
    assert v4.RUNTIME_BIN == Path(
        "/project/alex_phd/runs/rlm-research-r4/sidecars/runtime-an22-5801-v1/bin"
    )


def test_collector_path_proxy_replaces_failed_local_wrapper_with_allocation_runtime():
    load("study")
    load("study_v3")
    v4 = load("study_v4")
    collector = load("collect_v4")
    original = str(ROOT / "bin") + ":/usr/bin"
    environment = {"PATH": original}
    proxy = collector._EnvironmentProxy(environment)
    proxy["PATH"] = original
    assert environment["PATH"] == str(v4.RUNTIME_BIN) + ":/usr/bin"


def test_v4_owner_points_only_at_new_attempt_and_collector():
    load("study")
    load("study_v3")
    v4 = load("study_v4")
    owner = load("owner_v4")
    assert owner.ATTEMPT == v4.ATTEMPT
    assert owner.COLLECTOR == ROOT / "collect_v4.py"
    assert owner.OWNER_SECONDS == 900

