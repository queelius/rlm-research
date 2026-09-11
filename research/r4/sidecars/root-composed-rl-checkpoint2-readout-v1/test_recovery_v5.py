import json
from pathlib import Path


def write_json(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value))


def test_actual_source_binding_spec_and_all72_prefixes(tmp_path, monkeypatch):
    import readout_owner_v5 as owner
    import readout_study_v5 as meta

    monkeypatch.setenv("STRICT_RLM_CALIBRATION_API_KEY", "test-only-non-secret")
    decision = meta.checkpoint2_decision()
    binding = owner.collect.binding_for(decision["policy"])
    assert binding["campaign_policy"] == decision["policy"]
    assert binding["starting_binding"]["path"] == str(owner.source_study.ROOT / "START.json")

    binding_path = tmp_path / "BINDING.json"
    endpoint_path = tmp_path / "service/endpoint-original.json"
    owner.source_study.write(binding_path, binding)
    root_alias = binding["role_map"]["root"]
    root = binding["models"][root_alias]
    descriptor = {
        "model_alias": root_alias,
        "adapter": {"path": root["path"], "model_sha256": root["adapter_sha256"],
                    "config_sha256": root["config_sha256"]},
        "role_binding_sha256": owner.source_study.sha(binding_path),
        "base_model": {"manifest_sha256": owner.source_study.read(
            owner.source_study.ROOT / "RECIPE.json")["base_manifest_sha256"]},
    }
    owner.source_study.write(endpoint_path, descriptor)
    endpoint_path.with_name("inference.log").write_text("{'logprobs_mode': 'processed_logprobs'}\n")
    spec_path = tmp_path / "CAPTURE_SPEC.json"
    spec = owner.collect.prepare_spec("readout-rl_last", binding_path, endpoint_path,
                                      spec_path, 60.0, None)
    assert len(spec["plan"]) == 72

    public = {row["id"]: row for row in owner.source_study.data()[0]}
    gold = owner.source_study.data()[1]
    tasks = owner.source_study.read(owner.source_study.ROOT / "inputs/TASKS.json")
    prefixes = []
    for row in spec["plan"]:
        context = public[row["context_id"]]
        task = owner.native.make_task(context, tasks[row["task_name"]]["question"],
                                      gold[context["id"]]["answers"][row["family"]],
                                      row["task_name"])
        assert task.hash == tasks[row["task_name"]]["task_hash"]
        prefix = owner.native.first_prefix(task)
        assert prefix and all(type(token) is int for token in prefix)
        prefixes.append(prefix)
    assert len(prefixes) == 72


def test_v5_attempt_and_native_entry():
    import readout_owner_v5 as owner
    import readout_study_v5 as meta

    assert meta.ATTEMPT == meta.ROOT / "outputs/attempt-003"
    assert owner.collector_argv(Path("/stage"), 1.0)[0] == str(meta.NATIVE)
    assert owner.collector_argv(Path("/stage"), 1.0)[1] == str(
        owner.source_study.ROOT / "terminal_collect.py")
