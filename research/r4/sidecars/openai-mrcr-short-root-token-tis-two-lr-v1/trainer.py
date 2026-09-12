"""One saved-batch token-TIS gradient, applied to two independent LR branches."""

from __future__ import annotations

import argparse
import json
import math
import os
from pathlib import Path
import random
import signal
import time

import math_core
import study


TOKEN_TOLERANCE = 1e-5
SEQUENCE_TOLERANCE = 1e-4


def selected_logprobs(model, turn: dict, *, require_grad: bool):
    import torch

    positions, targets = study.positions_and_targets(turn)
    ids = torch.tensor([turn["input_ids"]], dtype=torch.long, device=model.device)
    selected = torch.tensor(positions, dtype=torch.long, device=model.device)
    context = torch.enable_grad() if require_grad else torch.no_grad()
    with context:
        logits = model(
            input_ids=ids,
            attention_mask=torch.ones_like(ids),
            use_cache=False,
            logits_to_keep=selected,
        ).logits.float() / study.TEMPERATURE
        target = torch.tensor(targets, dtype=torch.long, device=logits.device)
        values = torch.log_softmax(logits.reshape(-1, logits.shape[-1]), dim=-1).gather(
            1, target[:, None]
        ).squeeze(1)
    return values


def replay_check(actual, expected):
    if len(actual) != len(expected):
        return {"passed": False, "max_token_error": None, "sequence_error": None}
    token = max(abs(float(a) - float(b)) for a, b in zip(actual, expected, strict=True))
    sequence = abs(math.fsum(map(float, actual)) - math.fsum(map(float, expected)))
    return {
        "passed": token <= TOKEN_TOLERANCE and sequence <= SEQUENCE_TOLERANCE,
        "max_token_error": token,
        "sequence_error": sequence,
    }


def save_rng(path, torch_module) -> None:
    import numpy as np

    torch_module.save(
        {
            "python": random.getstate(),
            "numpy": np.random.get_state(),
            "torch": torch_module.get_rng_state(),
            "cuda": torch_module.cuda.get_rng_state_all(),
        },
        path,
    )


def restore_rng(path, torch_module) -> None:
    import numpy as np

    value = torch_module.load(path, map_location="cpu", weights_only=False)
    random.setstate(value["python"])
    np.random.set_state(value["numpy"])
    torch_module.set_rng_state(value["torch"])
    torch_module.cuda.set_rng_state_all(value["cuda"])


def _trajectory_diagnostics(current, native):
    log_ratios = []
    for current_turns, native_turns in zip(current, native, strict=True):
        log_ratios.append(
            math.fsum(value for turn in current_turns for value in turn)
            - math.fsum(value for turn in native_turns for value in turn)
        )
    ratios = [math.exp(value) for value in log_ratios]
    total = math.fsum(ratios)
    square = math.fsum(value * value for value in ratios)
    normalized = [value / total for value in ratios]
    return {
        "log_ratios": log_ratios,
        "ratios": ratios,
        "ess": total * total / square,
        "ess_fraction": total * total / square / len(ratios),
        "max_normalized_weight": max(normalized),
        "diagnostic_only": True,
        "optimizer_gate": False,
        "long_trajectory_variance_retained": True,
    }


def _persist_likelihoods(output, label, episodes, values, *, baseline=None):
    directory = output / "likelihood" / label
    directory.mkdir(parents=True)
    inventory = []
    all_deltas = []
    by_advantage = {"positive": [], "negative": [], "zero": []}
    for index, (episode, turns) in enumerate(zip(episodes, values, strict=True)):
        if len(turns) != len(episode["root_turns"]):
            raise ValueError("likelihood root-turn inventory differs")
        turn_rows = []
        episode_deltas = []
        for turn_index, (turn, current) in enumerate(
            zip(episode["root_turns"], turns, strict=True)
        ):
            if len(current) != len(turn["old_logprobs"]):
                raise ValueError("likelihood action-token inventory differs")
            row = {
                "turn_index": turn_index,
                "action_tokens": len(current),
                "input_ids_sha256": _ids_sha(turn["input_ids"]),
                "action_ids_sha256": _ids_sha(turn["action_ids"]),
                "logprobs": current,
            }
            if label == "baseline":
                row["native_logprobs"] = turn["old_logprobs"]
            else:
                reference = baseline[index][turn_index]
                deltas = [
                    float(now) - float(old)
                    for now, old in zip(current, reference, strict=True)
                ]
                row["delta_from_baseline"] = deltas
                episode_deltas.extend(deltas)
                all_deltas.extend(deltas)
            turn_rows.append(row)
        path = directory / f"{index:02d}-{episode['episode_id']}.json"
        record = {
            "schema": "mrcr-root-token-logprobs-v1",
            "condition": label,
            "episode_index": index,
            "episode_id": episode["episode_id"],
            "group_id": episode["group_id"],
            "reward": episode["reward"],
            "advantage": episode["advantage"],
            "root_turns": turn_rows,
            "root_action_tokens": sum(row["action_tokens"] for row in turn_rows),
        }
        if episode_deltas:
            record["movement"] = _movement_summary(episode_deltas)
            key = "positive" if episode["advantage"] > 0 else "negative" if episode["advantage"] < 0 else "zero"
            by_advantage[key].extend(episode_deltas)
        study.write_x(path, record)
        inventory.append({"path": str(path), "sha256": study.sha(path)})
    summary = {
        "schema": "mrcr-root-likelihood-inventory-v1",
        "condition": label,
        "episodes": len(episodes),
        "root_turns": sum(len(row["root_turns"]) for row in episodes),
        "root_action_tokens": sum(
            len(turn["old_logprobs"]) for row in episodes for turn in row["root_turns"]
        ),
        "files": inventory,
    }
    if all_deltas:
        summary["movement_all_tokens"] = _movement_summary(all_deltas)
        summary["movement_by_advantage_sign"] = {
            key: _movement_summary(rows) if rows else None for key, rows in by_advantage.items()
        }
    path = directory / "INVENTORY.json"
    study.write_x(path, summary)
    return summary, study.sha(path)


def _ids_sha(values):
    import hashlib

    return hashlib.sha256(json.dumps(values, separators=(",", ":")).encode()).hexdigest()


def _movement_summary(values):
    return {
        "tokens": len(values),
        "mean_delta": math.fsum(values) / len(values),
        "mean_absolute_delta": math.fsum(abs(value) for value in values) / len(values),
        "min_delta": min(values),
        "max_delta": max(values),
        "positive_tokens": sum(value > 0 for value in values),
        "negative_tokens": sum(value < 0 for value in values),
        "zero_tokens": sum(value == 0 for value in values),
    }


def _all_logprobs(model, episodes):
    return [
        [
            selected_logprobs(model, turn, require_grad=False).float().cpu().tolist()
            for turn in episode["root_turns"]
        ]
        for episode in episodes
    ]


def _build_token_diagnostics(episodes, baseline):
    weights = []
    episode_rows = []
    all_uncapped = []
    all_capped = []
    for episode, current_turns in zip(episodes, baseline, strict=True):
        native_turns = [turn["old_logprobs"] for turn in episode["root_turns"]]
        result = math_core.token_tis(current_turns, native_turns, cap=study.TOKEN_TIS_CAP)
        split = []
        cursor = 0
        for turn in current_turns:
            split.append(result["weights"][cursor : cursor + len(turn)])
            cursor += len(turn)
        if cursor != result["tokens"]:
            raise ValueError("token-TIS split differs")
        weights.append(split)
        all_uncapped.extend(result["uncapped_weights"])
        all_capped.extend(result["weights"])
        episode_rows.append(
            {
                "episode_id": episode["episode_id"],
                "group_id": episode["group_id"],
                "reward": episode["reward"],
                "advantage": episode["advantage"],
                "tokens": result["tokens"],
                "capped_tokens": result["capped_tokens"],
                "capped_fraction": result["capped_fraction"],
                "token_ess": result["token_ess"],
                "token_ess_fraction": result["token_ess_fraction"],
                "mean_weight": result["weight_mean"],
            }
        )
    total = math.fsum(all_capped)
    square = math.fsum(value * value for value in all_capped)
    diagnostics = {
        "schema": "mrcr-root-detached-token-tis-qualification-v1",
        "episodes": len(episodes),
        "groups": len({row["group_id"] for row in episodes}),
        "root_turns": sum(len(row["root_turns"]) for row in episodes),
        "root_action_tokens": len(all_capped),
        "cap": study.TOKEN_TIS_CAP,
        "capped_tokens": sum(value > study.TOKEN_TIS_CAP for value in all_uncapped),
        "capped_fraction": sum(value > study.TOKEN_TIS_CAP for value in all_uncapped) / len(all_capped),
        "uncapped_min": min(all_uncapped),
        "uncapped_max": max(all_uncapped),
        "capped_min": min(all_capped),
        "capped_max": max(all_capped),
        "capped_weight_mean": total / len(all_capped),
        "token_ess": total * total / square,
        "token_ess_fraction": total * total / square / len(all_capped),
        "self_normalized": False,
        "surrogate_unbiased": False,
        "bias_boundary": "Per-token cap controls variance but is not unbiased sequence IS.",
        "finite_support_gate_passed": True,
        "episodes_detail": episode_rows,
        "full_trajectory_diagnostics": _trajectory_diagnostics(
            baseline, [[turn["old_logprobs"] for turn in row["root_turns"]] for row in episodes]
        ),
    }
    return weights, diagnostics


def _checkpoint_branch(
    model,
    branch_name,
    learning_rate,
    branch_info,
    initial,
    output,
    ready,
    data,
    diagnostics_sha,
    gradient_sha,
    initial_rng,
    episodes,
    baseline,
    started,
):
    import torch

    directory = output / "branches" / branch_name
    checkpoint = directory / "checkpoint-0001"
    checkpoint.mkdir(parents=True)
    post = _all_logprobs(model, episodes)
    post_summary, post_inventory_sha = _persist_likelihoods(
        output, branch_name, episodes, post, baseline=baseline
    )
    model.save_pretrained(checkpoint, safe_serialization=True)
    optimizer = branch_info["optimizer"]
    torch.save(optimizer.state_dict(), checkpoint / "optimizer.pt")
    save_rng(checkpoint / "rng_state.pt", torch)
    updated = math_core.snapshot_trainable(model)
    delta_l2 = math.sqrt(
        math.fsum(
            float((updated[name].double() - initial[name].double()).square().sum())
            for name in initial
        )
    )
    core = [
        checkpoint / "adapter_model.safetensors",
        checkpoint / "adapter_config.json",
        checkpoint / "optimizer.pt",
        checkpoint / "rng_state.pt",
    ]
    state = {
        "schema": "mrcr-root-token-tis-independent-step1-state-v1",
        "branch": branch_name,
        "step": 1,
        "optimizer_steps": 1,
        "optimizer_state_steps": branch_info["optimizer_state_steps"],
        "optimizer_state_empty_before_step": branch_info["optimizer_state_empty_before_step"],
        "learning_rate": learning_rate,
        "weight_decay": 0.0,
        "starting_identity_sha256": branch_info["starting_identity_sha256"],
        "adapter_delta_l2": delta_l2,
        "same_saved_gradient_for_both_branches": True,
        "seed": study.SEED,
        "numpy_seed": study.NP_SEED,
        "episodes": 24,
        "groups": 6,
        "root_turns": 74,
        "root_action_tokens": 15602,
        "child_loss_tokens": 0,
        "environment_loss_tokens": 0,
        "new_generation_calls": 0,
        "heldout_queries": 0,
        "objective": "detached capped token-TIS sequence-SUM/24",
        "token_tis_cap": study.TOKEN_TIS_CAP,
        "self_normalized": False,
        "surrogate_unbiased": False,
        "inputs_sha256": study.sha(study.INPUTS),
        "token_tis_diagnostics_sha256": diagnostics_sha,
        "saved_gradient_sha256": gradient_sha,
        "initial_rng_sha256": study.sha(initial_rng),
        "postupdate_likelihood_inventory_sha256": post_inventory_sha,
        "postupdate_movement": post_summary["movement_all_tokens"],
        "elapsed_seconds": time.monotonic() - started,
        "files_sha256": {path.name: study.sha(path) for path in core},
    }
    study.write_x(checkpoint / "state.json", state)
    root_alias = f"mrcr-root-token-tis-{branch_name}-step1"
    binding = {
        "schema": "mrcr-root-hf-child-fixed-binding-v1",
        "base_model": {
            "path": str(study.BASE),
            "revision": "cdbee75f17c01a7cc42f958dc650907174af0554",
        },
        "role_map": {
            "root": root_alias,
            "children": ["Qwen3-4B-Instruct-2507-no-research-adapter"],
        },
        "models": {
            root_alias: {
                "path": str(checkpoint),
                "adapter_sha256": study.sha(checkpoint / "adapter_model.safetensors"),
                "config_sha256": study.sha(checkpoint / "adapter_config.json"),
            },
            "Qwen3-4B-Instruct-2507-no-research-adapter": {
                "path": str(study.BASE),
                "adapter": None,
            },
        },
        "root_only_update": {
            "branch": branch_name,
            "step": 1,
            "optimizer_sha256": study.sha(checkpoint / "optimizer.pt"),
            "rng_sha256": study.sha(checkpoint / "rng_state.pt"),
            "state_sha256": study.sha(checkpoint / "state.json"),
            "fixed_child": True,
            "source_short32_ready_v2_sha256": data["source"]["short32_ready_v2_sha256"],
        },
    }
    study.write_x(checkpoint / "EVAL_BINDING.json", binding)
    committed = core + [checkpoint / "state.json", checkpoint / "EVAL_BINDING.json"]
    commit = {
        "schema": "mrcr-root-token-tis-independent-step1-commit-v1",
        "status": "UPDATED",
        "branch": branch_name,
        "optimizer_steps": 1,
        "ready_identity": ready["identity"],
        "files_sha256": {str(path): study.sha(path) for path in committed},
    }
    study.write_x(checkpoint / "STEP_COMMIT.json", commit)
    return {
        "status": "UPDATED",
        "branch": branch_name,
        "optimizer_steps": 1,
        "checkpoint": str(checkpoint),
        "state_sha256": study.sha(checkpoint / "state.json"),
        "step_commit_sha256": study.sha(checkpoint / "STEP_COMMIT.json"),
        "adapter_delta_l2": delta_l2,
        "postupdate_likelihood_inventory_sha256": post_inventory_sha,
    }, updated


def run(output: Path, cap_seconds: int):
    import numpy as np
    import torch
    from peft import LoraConfig, get_peft_model
    from transformers import AutoModelForCausalLM

    if output.resolve() != study.OUTPUT.resolve() or output.exists():
        raise ValueError("exact unused attempt-001 output required")
    if cap_seconds != study.CAP_SECONDS:
        raise ValueError("exact 900-second cap required")
    if not os.environ.get("CUDA_VISIBLE_DEVICES") or torch.cuda.device_count() != 1:
        raise ValueError("MAIN must assign exactly one GPU")
    ready, data, episodes = study.load_sealed_inputs()
    output.mkdir(parents=True)
    started = time.monotonic()
    completed = []
    study.write_x(
        output / "START.json",
        {
            "ready_identity": ready["identity"],
            "started_epoch": time.time(),
            "pid": os.getpid(),
            "cap_seconds": cap_seconds,
            "planned_branches": [name for name, _ in study.BRANCHES],
            "optimizer_steps_per_branch": 1,
            "new_generation_calls": 0,
            "heldout_queries": 0,
        },
    )
    previous = signal.signal(
        signal.SIGALRM,
        lambda *_: (_ for _ in ()).throw(TimeoutError("900-second token-TIS cap")),
    )
    signal.setitimer(signal.ITIMER_REAL, cap_seconds)
    try:
        random.seed(study.SEED)
        np.random.seed(study.NP_SEED)
        torch.manual_seed(study.SEED)
        torch.cuda.manual_seed_all(study.SEED)
        torch.set_num_threads(4)
        torch.backends.cuda.matmul.allow_tf32 = False
        torch.backends.cudnn.allow_tf32 = False
        torch.backends.cudnn.benchmark = False
        torch.cuda.reset_peak_memory_stats()
        base = AutoModelForCausalLM.from_pretrained(
            study.BASE,
            local_files_only=True,
            dtype=torch.bfloat16,
            attn_implementation="sdpa",
            device_map={"": "cuda:0"},
        )
        config = LoraConfig(
            r=8,
            lora_alpha=16,
            lora_dropout=0.0,
            bias="none",
            task_type="CAUSAL_LM",
            target_modules=[
                "q_proj", "k_proj", "v_proj", "o_proj", "gate_proj", "up_proj", "down_proj"
            ],
        )
        model = get_peft_model(base, config)
        model.train()
        model.config.use_cache = False
        for module in model.modules():
            if isinstance(module, torch.nn.Dropout):
                module.eval()
        model.enable_input_require_grads()
        model.gradient_checkpointing_enable(
            gradient_checkpointing_kwargs={"use_reentrant": False}
        )
        trainable = [
            (name, parameter) for name, parameter in model.named_parameters() if parameter.requires_grad
        ]
        if (
            not trainable
            or any("lora_" not in name or parameter.dtype != torch.float32 for name, parameter in trainable)
            or not bool(getattr(model, "is_gradient_checkpointing", False))
        ):
            raise ValueError("exact FP32 rank8 LoRA training state differs")
        initial = math_core.snapshot_trainable(model)
        initial_identity = math_core.snapshot_digest(initial)
        torch.save(initial, output / "INITIAL_TRAINABLE.pt")
        save_rng(output / "INITIAL_RNG.pt", torch)

        baseline = _all_logprobs(model, episodes)
        with model.disable_adapter():
            disabled = selected_logprobs(model, episodes[0]["root_turns"][0], require_grad=False)
        enabled = torch.tensor(baseline[0][0], dtype=torch.float32)
        zero_effect_error = float((enabled - disabled.float().cpu()).abs().max())
        if zero_effect_error > TOKEN_TOLERANCE:
            raise ValueError("initial zero-effect LoRA differs from base")
        baseline_summary, baseline_inventory_sha = _persist_likelihoods(
            output, "baseline", episodes, baseline
        )
        weights, diagnostics = _build_token_diagnostics(episodes, baseline)
        diagnostics.update(
            {
                "zero_effect_adapter_max_logprob_error": zero_effect_error,
                "baseline_likelihood_inventory_sha256": baseline_inventory_sha,
                "optimizer_gate": "finite/support only; full-trajectory ESS retained as diagnostic",
                "optimizer_steps": 0,
            }
        )
        study.write_x(output / "TOKEN_TIS_DIAGNOSTICS.json", diagnostics)
        diagnostics_sha = study.sha(output / "TOKEN_TIS_DIAGNOSTICS.json")

        model.zero_grad(set_to_none=True)
        checks = []
        objective = 0.0
        for episode_index, episode in enumerate(episodes):
            row = []
            for turn_index, turn in enumerate(episode["root_turns"]):
                values = selected_logprobs(model, turn, require_grad=True)
                check = replay_check(
                    values.detach().float().cpu().tolist(), baseline[episode_index][turn_index]
                )
                row.append(check)
                term = next(
                    iter(
                        math_core.token_tis_terms(
                            [[values]],
                            [[weights[episode_index][turn_index]]],
                            [episode["advantage"]],
                            denominator=study.DENOMINATOR,
                        )
                    )
                )
                objective += float(term.detach().cpu())
                term.backward()
                del values, term
            checks.append(
                {
                    "episode_id": episode["episode_id"],
                    "turns": row,
                    "passed": all(item["passed"] for item in row),
                }
            )
        replay = {
            "schema": "mrcr-root-token-tis-gradient-replay-v1",
            "computed_before_optimizer_steps": True,
            "optimizer_steps": 0,
            "episodes": checks,
            "all24_passed": len(checks) == 24 and all(row["passed"] for row in checks),
            "objective_value_before_step": objective,
            "fixed_denominator": study.DENOMINATOR,
        }
        study.write_x(output / "GRADIENT_REPLAY_CHECK.json", replay)
        if not replay["all24_passed"]:
            result = {
                "status": "NO_UPDATE_GRADIENT_REPLAY_FAILED",
                "optimizer_steps": 0,
                "gradient_replay_sha256": study.sha(output / "GRADIENT_REPLAY_CHECK.json"),
            }
            study.write_x(output / "RESULT.json", result)
            return result
        gradient_norm = float(
            torch.nn.utils.clip_grad_norm_(
                [parameter for _, parameter in trainable], 1.0, error_if_nonfinite=True
            ).cpu()
        )
        if not math.isfinite(gradient_norm) or gradient_norm <= 0:
            raise ValueError("token-TIS gradient is nonfinite or zero")
        gradients = {
            name: parameter.grad.detach().cpu().clone() for name, parameter in trainable
        }
        if set(gradients) != set(initial):
            raise ValueError("saved gradient inventory differs")
        torch.save(gradients, output / "CLIPPED_GRADIENTS.pt")
        gradient_sha = study.sha(output / "CLIPPED_GRADIENTS.pt")

        branch_results = {}
        branch_snapshots = {}
        for branch_name, learning_rate in study.BRANCHES:
            restore_rng(output / "INITIAL_RNG.pt", torch)
            info = math_core.apply_fresh_adam_branch(
                model, initial, gradients, learning_rate=learning_rate
            )
            if info["starting_identity_sha256"] != initial_identity:
                raise ValueError("branch did not start from identical trainable state")
            result, updated = _checkpoint_branch(
                model,
                branch_name,
                learning_rate,
                info,
                initial,
                output,
                ready,
                data,
                diagnostics_sha,
                gradient_sha,
                output / "INITIAL_RNG.pt",
                episodes,
                baseline,
                started,
            )
            branch_results[branch_name] = result
            branch_snapshots[branch_name] = updated
            completed.append(branch_name)
        relation = math_core.ten_x_dose_relation(
            initial, branch_snapshots["lr1e-5"], branch_snapshots["lr1e-4"]
        )
        if not relation["passed"]:
            raise ValueError("independent AdamW branches do not show expected 10x dose")
        study.write_x(output / "BRANCH_RELATION.json", relation)
        result = {
            "schema": "mrcr-root-token-tis-two-independent-lr-result-v1",
            "status": "UPDATED_TWO_INDEPENDENT_BRANCHES",
            "branches": branch_results,
            "branch_optimizer_steps": {name: 1 for name, _ in study.BRANCHES},
            "sequential_updates": False,
            "same_initial_trainable_identity_sha256": initial_identity,
            "same_saved_gradient_sha256": gradient_sha,
            "token_tis_diagnostics_sha256": diagnostics_sha,
            "baseline_likelihood_inventory_sha256": baseline_inventory_sha,
            "branch_relation_sha256": study.sha(output / "BRANCH_RELATION.json"),
            "new_generation_calls": 0,
            "heldout_queries": 0,
            "elapsed_seconds": time.monotonic() - started,
            "peak_allocated_bytes": torch.cuda.max_memory_allocated(),
            "peak_reserved_bytes": torch.cuda.max_memory_reserved(),
            "ready_identity": ready["identity"],
        }
        study.write_x(output / "RESULT.json", result)
        return result
    except BaseException as error:
        if output.exists() and not (output / "FAILURE.json").exists():
            study.write_x(
                output / "FAILURE.json",
                {
                    "error_type": type(error).__name__,
                    "error": str(error),
                    "completed_branches": completed,
                    "elapsed_seconds": time.monotonic() - started,
                },
            )
        raise
    finally:
        signal.setitimer(signal.ITIMER_REAL, 0)
        signal.signal(signal.SIGALRM, previous)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--cap-seconds", type=int, required=True)
    args = parser.parse_args()
    print(json.dumps(run(args.output, args.cap_seconds), sort_keys=True))
