import json
from pathlib import Path


def write_json(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value))


def test_exact_checkpoint2_generates_original_window4():
    import continuation_study as study

    policy = study.checkpoint2_policy()
    generation = study.common.generation(4, policy)
    assert generation["candidate_window"] == 4
    assert generation["round"] == 3
    assert generation["previous_policy"] == policy
    assert generation["coordinate_plan_sha256"] == study.digest(study.source_study.candidate_plan(4))


def test_generic_sparse_trainer_accepts_dynamic_paths(tmp_path):
    import continuation_train as train

    group = tmp_path / "window-04/export/GROUP.json"
    generation = tmp_path / "window-04/GENERATION.json"
    checkpoint = tmp_path / "checkpoint-2"
    args = train.parse_args(["--group", str(group), "--generation", str(generation),
                             "--checkpoint", str(checkpoint), "--output", str(tmp_path / "training"),
                             "--deadline", "123", "--preflight"])
    assert args.group == group and args.generation == generation and args.checkpoint == checkpoint


def test_budget_inventory_and_window_order():
    import continuation_owner as owner

    assert owner.budget(10) == {"started": 10, "work": 11710, "owned": 11980, "outer": 12010}
    rows = owner.planned_inventory(Path("/out"))
    assert len(rows) == 120
    assert [row["window"] for row in rows[::24]] == [4, 5, 6, 7, 8]
    assert len({row["coordinate"]["id"] for row in rows}) == 120


def test_source_binding_spec_and_export_replay_fixture(tmp_path, monkeypatch):
    import continuation_owner as owner
    import continuation_study as study

    monkeypatch.setenv("STRICT_RLM_CALIBRATION_API_KEY", "test-only-non-secret")
    policy = study.checkpoint2_policy()
    generation = study.common.generation(4, policy)
    binding = owner.collect.binding_for(policy)
    assert binding["campaign_policy"] == policy
    assert binding["starting_binding"]["path"] == str(study.source_study.ROOT / "START.json")
    binding_path = tmp_path / "BINDING.json"
    endpoint_path = tmp_path / "service/endpoint-original.json"
    study.source_study.write(binding_path, binding)
    alias = binding["role_map"]["root"]
    root = binding["models"][alias]
    descriptor = {"model_alias": alias,
                  "adapter": {"path": root["path"], "model_sha256": root["adapter_sha256"],
                              "config_sha256": root["config_sha256"]},
                  "role_binding_sha256": study.source_study.sha(binding_path),
                  "base_model": {"manifest_sha256": study.source_study.read(
                      study.source_study.ROOT / "RECIPE.json")["base_manifest_sha256"]}}
    study.source_study.write(endpoint_path, descriptor)
    endpoint_path.with_name("inference.log").write_text("{'logprobs_mode': 'processed_logprobs'}\n")
    spec_path = tmp_path / "CAPTURE_SPEC.json"
    spec = owner.collect.prepare_spec("window-4", binding_path, endpoint_path, spec_path,
                                      60.0, generation)
    assert spec["plan"] == study.source_study.candidate_plan(4)
    assert len(spec["plan"]) == 24


def test_noop_advances_window_not_adam():
    import continuation_study as study

    policy = study.checkpoint2_policy()
    cursor = study.common.transition(3, policy, 4, None)
    assert cursor["completed_windows"] == 4
    assert cursor["optimizer_steps"] == 2
    assert cursor["policy"] == policy


def test_source_trainer_replays_existing_authenticated_group():
    import continuation_study as study

    stage = study.SOURCE / "outputs/attempt-003/window-03"
    group, generation, identity = study.source_train.authenticate_group(
        stage / "collection/export/GROUP.json", stage / "GENERATION.json")
    assert generation["candidate_window"] == 3
    assert len(group["episodes"]) == 11
    assert identity["native_replay"]["replayed"] == 24


def test_separate_readout_is_fixed72_and_conditional(tmp_path, monkeypatch):
    import continuation_readout_owner as readout
    import continuation_study as study

    assert readout.budget(1) == {"started": 1, "work": 2401, "owned": 2671, "outer": 2701}
    assert len(readout.planned_inventory(tmp_path)) == 72
    monkeypatch.setattr(study, "READOUT_ATTEMPT", tmp_path / "skip")
    monkeypatch.setattr(study, "verify_prepared", lambda: {"identity": "fixture"})
    monkeypatch.setattr(study, "final_policy", lambda: {"run": False, "reason": "no final"})
    result = readout.execute(study.READOUT_ATTEMPT)
    assert result["skipped"] is True and result["physical_requests"] == 0
