"""Authenticate one fixed vector-credit checkpoint without any outcome selection."""

import math


def endpoint(study):
    import torch
    from safetensors.torch import load_file
    ready = study.verify(); root = study.OUTPUT; checkpoint = root / "checkpoint-0001"
    terminal = study.read(root / "OWNER_TERMINAL.json"); result = study.read(root / "RESULT.json")
    assert terminal["complete"] and terminal["owned_process_reaped"]
    assert terminal["subprocess_exit_code"] == 0 and terminal["result_sha256"] == study.sha(root / "RESULT.json")
    assert result["status"] == "UPDATED" and result["credit_mode"] == study.CREDIT_MODE
    assert result["optimizer_steps"] == 1 and result["ready_sha256"] == study.sha(study.READY)
    assert result["step_commit_sha256"] == study.sha(checkpoint / "STEP_COMMIT.json")
    commit = study.read(checkpoint / "STEP_COMMIT.json")
    assert commit["credit_mode"] == study.CREDIT_MODE and commit["optimizer_steps"] == 1
    assert commit["source_ready_sha256"] == study.sha(study.READY)
    assert commit["input_sha256"] == study.sha(study.INPUTS)
    for path, expected in commit["artifacts_sha256"].items(): assert study.sha(path) == expected, path
    state = study.read(checkpoint / "state.json"); initial_meta = study.read(root / "INITIAL.json")
    replay = study.read(root / "REPLAY.json")
    assert state["credit_mode"] == study.CREDIT_MODE and state["optimizer_steps"] == 1
    assert state["learning_rate"] == 1e-4 and state["denominator"] == 64
    assert state["groups"] == 16 and state["group_size"] == 4
    assert state["token_TIS_cap"] == 2.0 and state["token_TIS_biased"]
    assert state["fresh_AdamW"] and state["weight_decay"] == 0.0
    assert state["optimizer_state_empty_before_step"] and state["optimizer_state_steps"] == [1]
    assert initial_meta["disabled_enabled_HF_exact"] and initial_meta["disabled_enabled_max_error"] == 0.0
    assert replay["passed"] and len(replay["checks"]) == 64 and replay["denominator"] == 64
    assert all(row["passed"] for row in replay["checks"])
    assert replay["LoRA_A_gradient_norm"] == 0.0 and replay["LoRA_B_gradient_norm"] > 0
    initial = torch.load(root / "initial-trainable.pt", map_location="cpu", weights_only=True)
    gradient = torch.load(root / "gradients.pt", map_location="cpu", weights_only=True)
    updated = torch.load(checkpoint / "trainable.pt", map_location="cpu", weights_only=True)
    optimizer = torch.load(checkpoint / "optimizer.pt", map_location="cpu", weights_only=True)
    assert list(initial) == list(gradient) == list(updated)
    group = optimizer["param_groups"]; assert len(group) == 1
    assert group[0]["lr"] == 1e-4 and group[0]["weight_decay"] == 0.0
    assert group[0]["betas"] == (0.9, 0.999) and group[0]["eps"] == 1e-8
    errors = []
    for index, (name, start) in enumerate(initial.items()):
        grad = gradient[name]; end = updated[name]; slot = optimizer["state"][index]
        assert int(slot["step"]) == 1 and torch.isfinite(grad).all()
        assert torch.allclose(slot["exp_avg"], grad * 0.1, rtol=1e-5, atol=1e-9)
        assert torch.allclose(slot["exp_avg_sq"], grad.square() * 0.001, rtol=1e-5, atol=1e-11)
        expected = start - 1e-4 * (grad / (grad.abs() + 1e-8))
        error = float((end - expected).abs().max()); assert error <= 1e-7; errors.append(error)
        if ".lora_A." in name: assert torch.equal(start, end) and torch.count_nonzero(grad) == 0
        else: assert ".lora_B." in name and torch.count_nonzero(start) == 0
    disk = load_file(str(checkpoint / "adapter_model.safetensors"))
    remapped = {key.replace(".default.", "."): value for key, value in updated.items()}
    assert disk.keys() == remapped.keys() and all(torch.equal(disk[key], remapped[key]) for key in disk)
    with study.aliases({"study": study}, study.FLAT):
        core = study.load(f"vector_{study.CREDIT_MODE}_checkpoint_core", study.FLAT / "core.py")
    logps = study.read(root / "PRESTEP_LOGPS.json")
    rows = study.validate_inputs(study.read(study.INPUTS))
    weights, diagnostics = core.scorer._build_token_diagnostics(rows, logps["episodes"])
    assert weights == logps["detached_token_weights"]
    saved = study.read(root / "PRESTEP_QUALIFICATION.json")
    for key, value in diagnostics.items(): assert saved[key] == value, key
    delta = math.sqrt(math.fsum(float((updated[key].double() - value.double()).square().sum())
                                for key, value in initial.items()))
    assert math.isclose(delta, state["adapter_delta_l2"], rel_tol=1e-10) and delta > 0
    assert core.math.snapshot_digest(initial) == state["initial_trainable_identity"]
    assert core.math.snapshot_digest(updated) == state["updated_trainable_identity"]
    binding = study.read(checkpoint / "EVAL_BINDING.json")
    assert binding["alias"] == study.ALIAS and binding["base"] == str(study.BASE)
    assert binding["credit_mode"] == study.CREDIT_MODE
    assert binding["adapter_sha256"] == study.sha(checkpoint / "adapter_model.safetensors")
    assert binding["state_sha256"] == study.sha(checkpoint / "state.json")
    return {"eligible": True, "credit_mode": study.CREDIT_MODE, "checkpoint": str(checkpoint),
        "ready_identity": ready["identity"], "binding": binding,
        "binding_sha256": study.sha(checkpoint / "EVAL_BINDING.json"),
        "state_sha256": study.sha(checkpoint / "state.json"),
        "step_commit_sha256": study.sha(checkpoint / "STEP_COMMIT.json"),
        "result_sha256": study.sha(root / "RESULT.json"),
        "initial_trainable_identity": state["initial_trainable_identity"],
        "Adam_formula_max_error": max(errors), "all64_replays_pass": True,
        "fixed_sole_step1": True, "no_accuracy_qualification": True}

