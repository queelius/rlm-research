"""Conditional updated AG256 arm over the exact existing V2 native collector."""

import argparse
import copy
import json
import math

import ag_study as study

ATTEMPT = study.ROOT / "eval/outputs/attempt-001"
CAP, OUTER_CAP = 600, 700
source = study.load("ag_native_updated_eval_v2", study.EVAL / "owner_v2.py")


def plan():
    return {
        "schema": "agnews-native-hf-updated-eval-ready-v1",
        "output": str(ATTEMPT),
        "owner_cap_seconds": CAP,
        "external_cap_seconds": OUTER_CAP,
        "command": [
            str(study.NATIVE),
            str(study.ROOT / "eval_owner.py"),
            "run",
            "--outer-seconds",
            str(CAP),
        ],
        "physical_calls": 64,
        "records": 256,
        "batch": 4,
        "temperature": 0,
        "schedule_sha256": study.digest(source.study.schedule()),
        "baseline_ready": str(study.EVAL / "READY_C32_V2.json"),
        "baseline_ready_sha256": study.sha(study.EVAL / "READY_C32_V2.json"),
        "baseline_source_reuse": "only fully qualified same runtime; otherwise fresh c32",
        "training_status_required": "UPDATED and complete owner and full128 probability gates",
    }


def qualify():
    training = study.verify()
    output = study.ATTEMPT
    result = study.read(output / "RESULT.json")
    terminal = study.read(output / "OWNER_TERMINAL.json")
    checkpoint = output / "checkpoint-0001"
    state = study.read(checkpoint / "state.json")
    commit = study.read(checkpoint / "STEP_COMMIT.json")
    qualification = study.read(output / "PRESTEP_QUALIFICATION.json")
    replay = study.read(output / "GRADIENT_REPLAY_CHECK.json")
    if (
        result.get("status") != "UPDATED"
        or result.get("optimizer_steps") != 1
        or result.get("ready_identity") != training["identity"]
        or not terminal.get("complete")
        or terminal.get("errors")
        or terminal.get("optimizer_steps") != 1
        or not terminal.get("released_before_hf")
        or terminal.get("result_sha256") != study.sha(output / "RESULT.json")
        or result.get("checkpoint") != str(checkpoint)
        or result.get("state_sha256") != study.sha(checkpoint / "state.json")
        or result.get("step_commit_sha256") != study.sha(checkpoint / "STEP_COMMIT.json")
    ):
        raise ValueError("exact fully completed one-step result required")
    if (
        state.get("step") != 1
        or state.get("optimizer_state_steps") != [1]
        or state.get("starting_child_adapter_sha256") != study.CHILD_SHA
        or state.get("objective") != training["policy"]
        or state.get("ready_identity") != training["identity"]
        or commit.get("status") != "UPDATED"
        or commit.get("optimizer_steps") != 1
        or commit.get("ready_identity") != training["identity"]
    ):
        raise ValueError("checkpoint policy/step identity differs")
    for key in ("gradient_norm_before_clip", "adapter_delta_l2"):
        if not math.isfinite(state.get(key, math.nan)) or state.get(key, 0) <= 0:
            raise ValueError("nonpositive/nonfinite update evidence")
    for path, expected in commit["files_sha256"].items():
        if study.sha(path) != expected:
            raise ValueError("step-committed artifact changed")
    required = {
        str(checkpoint / name)
        for name in (
            "adapter_model.safetensors",
            "adapter_config.json",
            "optimizer.pt",
            "rng_state.pt",
            "state.json",
            "EVAL_BINDING.json",
        )
    }
    required.update(
        str(output / name)
        for name in (
            "PRESTEP_QUALIFICATION.json",
            "GRADIENT_REPLAY_CHECK.json",
            "COLLECTION.json",
            "PREPARED.json",
            "CAPTURE.json",
            "ENGINE_ATTESTATION.json",
        )
    )
    if not required <= set(commit["files_sha256"]):
        raise ValueError("full checkpoint/source commit inventory required")
    for name, expected in state["files_sha256"].items():
        if study.sha(checkpoint / name) != expected:
            raise ValueError("checkpoint tensor/optimizer artifact changed")
    if (
        not qualification.get("gate_passed")
        or qualification.get("gate_failures")
        or not qualification.get("all_finite")
        or not qualification.get("all_supported")
        or qualification.get("ess", 0) < 102.4
        or qualification.get("max_normalized_weight", 1) > 0.1
        or qualification.get("computed_before_optimizer_creation") is not True
        or len(qualification.get("episode_ids", [])) != 128
        or not replay.get("all128_passed")
        or len(replay.get("episodes", [])) != 128
        or replay.get("computed_before_optimizer_step") is not True
        or replay.get("token_tolerance") != 1e-5
        or replay.get("sequence_tolerance") != 1e-4
    ):
        raise ValueError("full exact pre-step/replay qualification required")
    for row in replay["episodes"]:
        if (
            not row.get("passed")
            or not row.get("support")
            or not math.isfinite(row.get("max_token_error", math.nan))
            or row["max_token_error"] > 1e-5
            or not math.isfinite(row.get("sequence_error", math.nan))
            or row["sequence_error"] > 1e-4
        ):
            raise ValueError("a per-action replay gate failed")
    trained = study.load("ag_native_readout_input_audit", study.ROOT / "train_ag.py")
    records, _masks = trained.load_inputs()
    expected_ids = [row["episode_id"] for row in records]
    if (
        qualification["episode_ids"] != expected_ids
        or [row["episode_id"] for row in replay["episodes"]] != expected_ids
    ):
        raise ValueError("qualified episode identity/order differs")
    recomputed = study.numeric_modules().leaf.importance_diagnostics(
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
        if recomputed[key] != qualification[key]:
            raise ValueError("importance qualification rederivation differs")
    if (
        state["qualification_sha256"] != study.sha(output / "PRESTEP_QUALIFICATION.json")
        or state["gradient_replay_sha256"] != study.sha(output / "GRADIENT_REPLAY_CHECK.json")
        or state["collection_sha256"] != study.sha(output / "COLLECTION.json")
        or state["dataset_sha256"] != study.sha(output / "qualification-inputs/DATASET.json")
    ):
        raise ValueError("checkpoint source lineage hashes differ")
    verifier = study.load(
        "ag_native_optimizer_state_verifier",
        study.SIDE / "helper-hf-fourstep-unseen-eval-v1/fourstep_panel_study.py",
    )
    verifier.verify_optimizer_steps(checkpoint / "optimizer.pt", 1)
    binding = study.read(checkpoint / "EVAL_BINDING.json")
    expected_binding = study.child_binding(checkpoint, study.sha(checkpoint / "state.json"))
    if binding != expected_binding:
        raise ValueError("child binding differs beyond authenticated update")
    return {
        "eligible": True,
        "training_ready_identity": training["identity"],
        "training_ready_sha256": study.sha(study.ROOT / "READY.json"),
        "state_sha256": study.sha(checkpoint / "state.json"),
        "step_commit_sha256": study.sha(checkpoint / "STEP_COMMIT.json"),
        "binding": binding,
        "binding_sha256": study.sha(checkpoint / "EVAL_BINDING.json"),
        "selection": "none; exact single step1",
    }


def verify(require_training=True):
    ready = study.read(study.ROOT / "EVAL_READY.json")
    if (
        study.digest({key: value for key, value in ready.items() if key != "identity"})
        != ready["identity"]
    ):
        raise ValueError("eval READY identity differs")
    for key, value in plan().items():
        if ready.get(key) != value:
            raise ValueError("eval plan changed")
    for path, expected in ready["closure_sha256"].items():
        if study.sha(path) != expected:
            raise ValueError("eval closure changed: " + path)
    if require_training:
        qualify()
    return ready


def build():
    collector = source.collector("c32")
    collector.study.ATTEMPT = ATTEMPT
    collector.study.verify = verify

    def binding():
        receipt = qualify()
        study.write_x(ATTEMPT / "ELIGIBILITY.json", receipt)
        return copy.deepcopy(receipt["binding"])

    collector.study.binding = binding
    original = collector.summarize

    def summarize(calls, gold, expected=True):
        result = original(calls, gold, expected)
        result.update(
            arm="ag_native_hf_step1_seed2",
            primary_step=1,
            eligibility_sha256=study.sha(ATTEMPT / "ELIGIBILITY.json"),
            training_result_sha256=study.sha(study.ATTEMPT / "RESULT.json"),
        )
        result["cost_accounting"] = {
            "totals_are_observed_subtotals": True,
            "unknown_usage_calls": {
                field: sum(call.get(field) is None for call in calls)
                for field in ("prompt_tokens", "completion_tokens", "cached_prompt_tokens")
            },
            "unattempted_calls": 64 - len(calls),
        }
        return result

    collector.summarize = summarize
    return collector


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("command", choices=("verify", "qualify", "run"))
    parser.add_argument("--outer-seconds", type=int, default=CAP)
    args = parser.parse_args()
    if args.command == "qualify":
        print(json.dumps(qualify(), sort_keys=True))
    elif args.command == "verify":
        print(verify(False)["identity"])
    else:
        if args.outer_seconds != CAP:
            raise ValueError("exact600 eval owner cap required")
        verify()
        terminal = build().execute(args.outer_seconds)
        print(json.dumps(terminal, sort_keys=True))
        raise SystemExit(0 if terminal["complete"] else 1)
