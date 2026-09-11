from pathlib import Path
import copy
import pytest


def test_v3_identity_is_used_by_combined_corpus_across_process_module(monkeypatch):
    import recovery_study_v3 as s
    seen = []
    monkeypatch.setattr(s.v1, "build_corpus_ready", lambda: seen.append(s.v1.verify()["identity"]) or [])
    monkeypatch.setattr(s, "verify", lambda: {"identity": "V3-IDENTITY"})
    s.build_corpus_ready()
    assert seen == ["V3-IDENTITY"]


def test_original_protected_deadline_formula_is_exact():
    import recovery_owner_v3 as o
    assert o.protected_deadline(1000, 42, 5000) == 2902
    assert o.protected_deadline(1000, 42, 2000) == 2000


def test_cost_usage_keeps_each_missing_field_unknown(tmp_path, monkeypatch):
    import recovery_owner_v3 as o
    import recovery_study_v3 as s
    original = tmp_path / "original"; recovery = tmp_path / "recovery"
    monkeypatch.setattr(s, "ORIGINAL_ATTEMPT", original)
    p = recovery / "capture/x/physical/0001.json"
    s.write(p, {"physical_request_attempt": True,
                "response": {"choices": [{}], "usage": {"prompt_tokens": 5}}})
    ledger = o.cost_ledger(recovery)["by_stage"]["recovery_missing_capture"]
    assert ledger["usage"] == {"known": {"input": 5, "output": 0, "cached": 0},
                               "unknown": {"input": 0, "output": 1, "cached": 1}}


def test_v3_entries_all_import_coherent_study():
    import recovery_collect_v3 as capture
    import recovery_readout_v3 as readout
    import recovery_train_v3 as train
    import recovery_owner_v3 as owner
    import recovery_study_v3 as study
    import recovery_binding_v3 as binding
    assert capture.s is readout.s is train.s is owner.s is study
    assert readout.b is owner.b is binding


def test_actual_combined72_crosses_v3_verify_and_reaches_trainer_loader(tmp_path, monkeypatch):
    import recovery_study_v3 as s
    import qs_train as trainer

    attempt = tmp_path / "attempt"; plan = s.train_plan()
    template = s.read(s.ORIGINAL_ATTEMPT / "capture" / plan[0]["id"] / "TEACHER.json")
    episode = s.read(s.ORIGINAL_ATTEMPT / "capture" / plan[0]["id"] / "EPISODE.json")
    source_child = s.read(Path(template["actual_child_records"][0]))
    monkeypatch.setattr(s, "ATTEMPT", attempt); monkeypatch.setattr(s.v1, "ATTEMPT", attempt)
    for coordinate in plan[65:]:
        directory = attempt / "capture" / coordinate["id"]
        child = directory / "physical/0001.json"; s.write(child, source_child)
        teacher = copy.deepcopy(template); teacher.update(episode_id=coordinate["id"], coordinate=coordinate,
            actual_child_records=[str(child)], episode_path=str(directory / "EPISODE.json"))
        s.write(directory / "EPISODE.json", episode); s.write(directory / "TEACHER.json", teacher)
    values = s.build_corpus_ready()
    assert len(values) == 72 and s.read(attempt / "capture/CORPUS_READY.json")["identity"] == s.verify()["identity"]
    trainer.s = s; trainer.implementation.cache_clear(); module = trainer.implementation(); module.s = s
    class LoaderReached(RuntimeError): pass
    monkeypatch.setattr(module, "load_model", lambda output: (_ for _ in ()).throw(LoaderReached()))
    args = module.parse_args(["--mode", "train", "--output", str(attempt / "training"), "--deadline", "2000000000"])
    with pytest.raises(LoaderReached): module.run(args)
    assert (attempt / "training/RUN.json").exists()
