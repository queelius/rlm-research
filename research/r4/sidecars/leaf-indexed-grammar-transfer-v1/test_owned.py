"""CPU wrapper checks; real orchestration logic with no service/process launches."""
import importlib
import json
from pathlib import Path
from types import SimpleNamespace

import pytest

ROOT = Path(__file__).resolve().parent


def module():
    assert (ROOT / "owned.py").exists(), "owned wrapper not implemented"
    return importlib.import_module("owned")


def test_binding_uses_semantic_old_and_indexed_paths_not_filename_labels(tmp_path):
    m = module()
    path = tmp_path / "weights.json"
    path.write_text("{}")
    weights = {"models": {"old_sft": {"path": "/old-c32", "model_sha256": "a", "config_sha256": "ca"},
                          "indexed_final": {"path": "/final204", "model_sha256": "b", "config_sha256": "cb"}}}
    binding = m.service_binding(weights, path)
    assert binding["models"][m.OLD_ALIAS] == {"path": "/old-c32", "adapter_sha256": "a", "config_sha256": "ca"}
    assert binding["models"][m.INDEXED_ALIAS]["path"] == "/final204"
    assert binding["role_map"]["root"] == m.OLD_ALIAS
    assert binding["post_training_test_consulted_for_binding"] is False


def test_failure_preserves_inclusive_start_epoch_and_always_releases(tmp_path):
    m = module()
    events = []

    def write(path, value):
        with path.open("x") as stream:
            json.dump(value, stream)

    def start(directory, binding, deadline):
        events.append(("start", deadline))

    def command(directory, label, argv, cap, deadline):
        events.append((label, argv, cap, deadline))
        if label == "grammar-run":
            raise RuntimeError("collector failed")

    def release(directory):
        write(directory / "SERVICE_STOPPED.json", {"all_owned_process_identities_exited": True})
        events.append(("release", directory))

    suite = SimpleNamespace(c=SimpleNamespace(write_once=write), PYTHON="/native/python", start_service=start,
        command=command, release_service=release)
    weights = {"models": {"old_sft": {"path": "/old", "model_sha256": "a", "config_sha256": "ca"},
                          "indexed_final": {"path": "/new", "model_sha256": "b", "config_sha256": "cb"}}}
    path = tmp_path / "weights.json"
    path.write_text("{}")
    directory = tmp_path / "owned"
    with pytest.raises(RuntimeError, match="collector failed"):
        m.execute(directory, suite, weights, path)
    attempt = json.loads((directory / "WRAPPER_ATTEMPT.json").read_text())
    run = next(e for e in events if e[0] == "grammar-run")
    assert float(run[1][run[1].index("--overall-start-epoch") + 1]) == attempt["started_epoch"]
    assert events[0][1] == attempt["started_epoch"] + 2580
    assert events[-1] == ("release", directory)
    assert json.loads((directory / "FINISH.json").read_text())["owned_release_completed"]
    assert json.loads((directory / "ERROR.json").read_text())["type"] == "RuntimeError"
