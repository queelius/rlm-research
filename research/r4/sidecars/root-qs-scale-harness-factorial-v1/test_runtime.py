import importlib.util
from pathlib import Path


ROOT = Path(__file__).resolve().parent


def load(name):
    spec = importlib.util.spec_from_file_location(name, ROOT / f"{name}.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_binding_is_exact_policy_pair_with_fixed_child_and_honest_bundle():
    study = load("study")
    bindings = {arm: study.binding(arm) for arm in ("unchanged", "sft6")}
    for arm, binding in bindings.items():
        assert binding["question_sensitive"]["arm"] == arm
        assert binding["models"][binding["fixed_child"]]["adapter_sha256"] == study.CHILD_SHA
        assert binding["scale_harness_factorial"]["return_arms"] == ["B", "C"]
        assert binding["scale_harness_factorial"]["visible_view_max_bytes"] == [4096, 20000]
        assert binding["scale_harness_factorial"]["visible_view_unit"] == "bytes"
    assert bindings["unchanged"]["role_map"]["root"] != bindings["sft6"]["role_map"]["root"]


def test_owner_common_budget_includes_both_serial_services():
    owner = load("owner")
    budget = owner.budget(1000.0)
    assert budget == {
        "outer_deadline": 4600.0,
        "owned_deadline": 4570.0,
        "work_deadline": 4420.0,
    }
    assert owner.clock_metadata(budget) == {
        "outer_deadline_epoch": 4600.0,
        "owned_deadline_epoch": 4570.0,
        "work_deadline_epoch": 4420.0,
    }
    assert owner.POLICY_ORDER == ("sft6", "unchanged")


def test_verify_invokes_reused_qs_replication_verifier():
    study = load("study")
    called = []
    original = study.base.verify
    ready_body = {"source_sha256": {}, "input_sha256": {}}
    synthetic_ready = {**ready_body, "identity": study.digest(ready_body)}
    original_read = study.read

    def verified():
        called.append(True)
        return original()

    study.base.verify = verified
    study.read = lambda path: synthetic_ready if path.name.startswith("READY_v") else original_read(path)
    study.verify()
    assert called == [True]
