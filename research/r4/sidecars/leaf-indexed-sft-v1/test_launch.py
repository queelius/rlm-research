import importlib.util
from pathlib import Path

ROOT = Path(__file__).resolve().parent


def launcher():
    assert (ROOT / "launch.py").exists(), "owned overall deadline launcher missing"
    spec = importlib.util.spec_from_file_location(
        "indexed_test_launch", ROOT / "launch.py"
    )
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_owned_child_completion_and_timeout_are_distinct_retained_results(tmp_path):
    m = launcher()
    good = m.run_owned(
        ["/bin/true"], tmp_path / "good", wall_seconds=2, grace_seconds=0.1
    )
    assert good["exit_code"] == 0 and not good["timed_out"]
    stopped = m.run_owned(
        ["/bin/sleep", "5"], tmp_path / "timeout", wall_seconds=0.03, grace_seconds=0.1
    )
    assert stopped["timed_out"] and stopped["exit_code"] != 0
    assert stopped["elapsed_seconds"] < 2
    assert (tmp_path / "timeout/FINISH.json").exists()
    assert (tmp_path / "timeout/RUN.json").exists()
