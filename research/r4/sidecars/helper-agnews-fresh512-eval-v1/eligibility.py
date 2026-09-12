"""Authenticate exact c32, RL8 and SFT8 before any heldout model call."""

import copy
import math
from pathlib import Path

import study

SFT = study.SIDE / "helper-agnews-sft-eightstep-v1"
SFT_READY_SHA = "088f4b7e366582365f62d226fac9e3677957e0f32c54e534f5d000ea3bce9753"
RL_REPAIR_SHA = "e9dcccfdcb45a092d5ad85d4a161266f85c3f8f3cbe2f3a494aaec46edeaabb5"


def binding_check(binding, checkpoint):
    expected = {
        "path": str(checkpoint),
        "adapter_sha256": study.sha(checkpoint / "adapter_model.safetensors"),
        "config_sha256": study.sha(checkpoint / "adapter_config.json"),
    }
    if binding["models"][study.CHILD_ALIAS] != expected:
        raise ValueError("endpoint native child binding differs from exact checkpoint")
    source = study.read(study.rl.original.SOURCE_BINDING)
    if binding["fixed_child"] != study.CHILD_ALIAS or binding["role_map"] != source["role_map"]:
        raise ValueError("endpoint role map changed")
    for alias, model in source["models"].items():
        if alias != study.CHILD_ALIAS and binding["models"][alias] != model:
            raise ValueError("endpoint root/base binding changed")


def optimizer_counter(path, step):
    verifier = study.rl.load_bound(
        "fresh512_actual_adam_counter",
        study.SIDE / "helper-hf-fourstep-unseen-eval-v1/fourstep_panel_study.py",
        {},
    )
    verifier.verify_optimizer_steps(path, step)


def rl_endpoint():
    ready = study.rl.verify()
    repair_path = study.RL / "READY_V2.json"
    repair = study.read(repair_path)
    launch_path = study.RL / "V2_LAUNCH_AFTER_000.json"
    launch = study.read(launch_path)
    if (
        study.sha(repair_path) != RL_REPAIR_SHA
        or launch["repair_ready_sha256"] != RL_REPAIR_SHA
        or launch["original_ready_identity"] != ready["identity"]
        or launch["admission_sha256"] != repair["admission_sha256"]
        or launch["optimizer_or_probability_changes"] is not False
    ):
        raise ValueError("RL additive admission-repair launch lineage differs")
    for path, expected in repair["closure_sha256"].items():
        if study.sha(path) != expected:
            raise ValueError("RL repair closure differs: " + path)
    final = study.read(study.rl.ATTEMPT / "FINAL_RESULT.json")
    parent = study.rl.parent_for(9)
    if (
        final.get("status") != "UPDATED_STEP8"
        or final.get("completed_steps") != 8
        or final.get("primary_endpoint_eligible") is not True
        or final.get("errors")
        or final.get("endpoint") != parent
        or final.get("ready_identity") != ready["identity"]
    ):
        raise ValueError("fixed complete RL step8 endpoint required")
    for step in range(1, 9):
        view = study.rl.step_view(step)
        checkpoint = view.ATTEMPT / f"checkpoint-{step:04d}"
        state = study.read(checkpoint / "state.json")
        qualification = study.read(view.ATTEMPT / "PRESTEP_QUALIFICATION.json")
        replay = study.read(view.ATTEMPT / "GRADIENT_REPLAY_CHECK.json")
        if (
            state["objective"] != ready["policy"]
            or state["training_data_manifest_sha256"]
            != study.sha(study.DATA / "inputs/MANIFEST.json")
            or not qualification.get("all_finite")
            or not qualification.get("all_supported")
            or qualification.get("gate_failures")
            or qualification.get("ess", 0) < 102.4
            or qualification.get("max_normalized_weight", 1) > 0.1
            or qualification.get("computed_before_this_optimizer_step") is not True
            or replay.get("token_tolerance") != 1e-5
            or replay.get("sequence_tolerance") != 1e-4
        ):
            raise ValueError("RL full objective/likelihood gate differs")
        for key in ("gradient_norm_before_clip", "adapter_delta_l2"):
            if not math.isfinite(state.get(key, math.nan)) or state[key] <= 0:
                raise ValueError("nonpositive/nonfinite RL update evidence")
        for row in replay["episodes"]:
            if (
                not row.get("passed")
                or not row.get("support")
                or not math.isfinite(row["max_token_error"])
                or row["max_token_error"] > 1e-5
                or not math.isfinite(row["sequence_error"])
                or row["sequence_error"] > 1e-4
            ):
                raise ValueError("individual RL replay gate differs")
        source = study.rl.numeric_source(view)
        loader = study.rl.patched_function(
            source,
            "load_inputs",
            [('dataset["c32_adapter_sha256"]', 'dataset["parent_adapter_sha256"]')],
        )
        records, masks = loader()
        expected_ids = [row["episode_id"] for row in records]
        if (
            qualification["episode_ids"] != expected_ids
            or [row["episode_id"] for row in replay["episodes"]] != expected_ids
        ):
            raise ValueError("RL exact qualified action order differs")
        computed = study.rl.original.numeric_modules().leaf.importance_diagnostics(
            qualification["current_token_logprobs"],
            [row["old_logprobs"] for row in records],
            [True] * 128,
            ess_fraction_min=0.8,
            max_normalized_weight_limit=0.1,
        )
        for key in (
            "ratios",
            "log_ratios",
            "ess",
            "max_normalized_weight",
            "gate_passed",
            "gate_failures",
        ):
            if computed[key] != qualification[key]:
                raise ValueError("RL importance rederivation differs: " + key)
        masks.close()
        optimizer_counter(checkpoint / "optimizer.pt", step)
    checkpoint = Path(parent["checkpoint"])
    binding = study.read(checkpoint / "EVAL_BINDING.json")
    binding_check(binding, checkpoint)
    return {
        "eligible": True,
        "arm": "rl_step8",
        "checkpoint": str(checkpoint),
        "binding": binding,
        "binding_sha256": study.sha(checkpoint / "EVAL_BINDING.json"),
        "state_sha256": study.sha(checkpoint / "state.json"),
        "step_commit_sha256": study.sha(checkpoint / "STEP_COMMIT.json"),
        "training_result_sha256": study.sha(study.rl.ATTEMPT / "FINAL_RESULT.json"),
        "training_ready_sha256": study.sha(study.RL / "READY.json"),
        "training_launch_ready_sha256": RL_REPAIR_SHA,
        "training_launch_receipt_sha256": study.sha(launch_path),
        "selection": "none; fixed completed step8",
    }


def qualify(arm):
    if arm == "c32":
        parent = study.rl.initial_parent()
        binding = study.rl.binding_from_parent(parent)
        binding_check(binding, Path(parent["checkpoint"]))
        return {
            "eligible": True,
            "arm": arm,
            "checkpoint": parent["checkpoint"],
            "binding": binding,
            "original_c32_sha256": study.rl.original.CHILD_SHA,
            "selection": "fixed original c32",
        }
    if arm == "rl_step8":
        return rl_endpoint()
    if arm == "sft_step8":
        if study.sha(SFT / "READY_V2.json") != SFT_READY_SHA:
            raise ValueError("actual sealed SFT READY differs")
        source = study.rl.load_bound("fresh512_actual_sft_endpoint", SFT / "sft_study_v2.py", {})
        receipt = source.endpoint()
        checkpoint = Path(receipt["checkpoint"])
        descriptor = receipt["binding"]
        if (
            descriptor["checkpoint"] != str(checkpoint)
            or descriptor["adapter_sha256"] != study.sha(checkpoint / "adapter_model.safetensors")
            or descriptor["config_sha256"] != study.sha(checkpoint / "adapter_config.json")
            or descriptor["state_sha256"] != receipt["state_sha256"]
            or descriptor["fixed_child"] != study.CHILD_ALIAS
            or descriptor["optimizer_steps"] != 8
            or descriptor["step"] != 8
            or descriptor["root_unchanged"] is not True
            or descriptor["source_c32_adapter_sha256"] != study.rl.original.CHILD_SHA
        ):
            raise ValueError("SFT endpoint descriptor does not authenticate exact final child")
        binding = copy.deepcopy(study.read(study.rl.original.SOURCE_BINDING))
        binding["models"][study.CHILD_ALIAS] = {
            "path": str(checkpoint),
            "adapter_sha256": descriptor["adapter_sha256"],
            "config_sha256": descriptor["config_sha256"],
        }
        binding["fixed_endpoint_evaluation"] = {
            "arm": arm,
            "step": 8,
            "endpoint_descriptor_sha256": receipt["binding_sha256"],
        }
        binding_check(binding, checkpoint)
        for step in range(1, 9):
            optimizer_counter(source.ATTEMPT / f"checkpoint-{step:04d}/optimizer.pt", step)
        return {
            **receipt,
            "arm": arm,
            "binding": binding,
            "endpoint_descriptor": descriptor,
            "native_binding_digest": study.digest(binding),
        }
    raise ValueError("unknown endpoint arm")


def fixed_endpoints(arm):
    path = study.ROOT / "ENDPOINTS_FIXED.json"
    receipt = study.read(path)
    selected = receipt.get("trained_endpoints", {})
    if (
        receipt.get("authority") != "MAIN"
        or receipt.get("fixed_step") != 8
        or receipt.get("data_manifest_sha256") != study.sha(study.DATA / "inputs/MANIFEST.json")
        or receipt.get("heldout512_consulted_before_fix") is not False
        or not selected
        or not set(selected) <= {"rl_step8", "sft_step8"}
        or (arm != "c32" and arm not in selected)
    ):
        raise ValueError("MAIN must fix completed trained endpoints before heldout model queries")
    qualified = {}
    for name, expected in selected.items():
        current = qualify(name)
        if (
            current["state_sha256"] != expected.get("state_sha256")
            or current["step_commit_sha256"] != expected.get("step_commit_sha256")
            or current["binding_sha256"] != expected.get("binding_sha256")
            or current["checkpoint"] != expected.get("checkpoint")
        ):
            raise ValueError("fixed trained endpoint changed: " + name)
        qualified[name] = current
    return {
        "fixed_receipt_path": str(path),
        "fixed_receipt_sha256": study.sha(path),
        "selected_endpoints": qualified,
        "arm_eligibility": qualify("c32") if arm == "c32" else qualified[arm],
    }
