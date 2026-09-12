"""One model load, four fresh on-policy collections, one carried AdamW optimizer."""

import argparse
import json
import math
import os
import random
import signal
import time
from pathlib import Path

import core
import numpy as np
import torch
from config import (
    BASE,
    BATCH,
    CAP,
    CHILD,
    CHILD_SHA,
    CLIP,
    DENOMINATOR,
    GLOBAL_SEED,
    GROUPS,
    LR,
    PERMUTATION_SEED_BASE,
    ROOT,
    SAMPLER_SEED,
    SOURCE_BINDING,
    UPDATES,
)
from rng_receipts import commit_files, save_rng, verify_commit


def trainable_parameters(model):
    pairs = [(name, value) for name, value in model.named_parameters() if value.requires_grad]
    if not pairs or any(
        "lora_" not in name or value.dtype != torch.float32 for name, value in pairs
    ):
        raise ValueError("only FP32 LoRA parameters may train")
    return pairs


def parameter_snapshot(model):
    return {name: value.detach().cpu().clone() for name, value in trainable_parameters(model)}


def adapter_delta(model, before):
    return math.sqrt(
        math.fsum(
            float((value.detach().cpu() - before[name]).double().square().sum())
            for name, value in trainable_parameters(model)
        )
    )


def execute_update(
    model,
    optimizer,
    worker,
    tokenizer,
    groups,
    gold,
    generator,
    step,
    directory,
    parent_identity,
    ready_identity,
):
    """Collect all groups before replay; no state/optimizer mutation on a failed gate."""
    if directory.exists() or len(groups) != GROUPS:
        raise ValueError("unused update directory and exact group inventory required")
    core.v1.assert_eval_policy(model)
    directory.mkdir(parents=True)
    started = time.monotonic()
    order = list(range(len(groups)))
    random.Random(PERMUTATION_SEED_BASE + step).shuffle(order)
    ordered = [groups[index] for index in order]
    before = parameter_snapshot(model)
    core.write(
        directory / "START.json",
        {
            "step": step,
            "parent_identity": parent_identity,
            "ready_identity": ready_identity,
            "permutation_seed": PERMUTATION_SEED_BASE + step,
            "group_source_indices": order,
            "group_ids": [group["group_id"] for group in ordered],
            "started_epoch": time.time(),
            "sampling_seed_namespace": SAMPLER_SEED,
        },
    )
    save_rng(directory / "START_RNG.pt", generator)
    optimizer.zero_grad(set_to_none=True)
    rollouts = []
    for index, group in enumerate(ordered):
        destination = directory / "groups" / f"group-{index:03d}"
        record = core.v1.rollout_group(
            model, worker, tokenizer, group, index, generator, destination
        )
        rewards = [
            core.v1.local_reward(
                content, group["public_record"]["id"], gold[group["group_id"]], terminated
            )
            for content, terminated in zip(record["contents"], record["terminated"], strict=True)
        ]
        record.update(rewards=rewards, advantages=core.v1.rloo_advantages(rewards))
        core.write(destination / "ROLLOUT.json", record)
        save_rng(destination / "AFTER_GROUP_RNG.pt", generator)
        commit_files(
            destination / "GROUP_COMMIT.json",
            [destination / name for name in ("ROLLOUT.json", "MASKS.npz", "AFTER_GROUP_RNG.pt")],
            {
                "parent_identity": parent_identity,
                "ready_identity": ready_identity,
                "step": step,
                "group_index": index,
                "group_id": group["group_id"],
                "sampling_seed_namespace": SAMPLER_SEED,
                "sampler_state_scope": "after this completed group",
            },
        )
        rollouts.append(record)
        core.write(
            directory.parent.parent / "PROGRESS.json",
            {
                "stage": "collection",
                "step": step,
                "completed_groups": index + 1,
                "completed_optimizer_steps": step - 1,
                "update_elapsed_seconds": time.monotonic() - started,
            },
        )
        print(
            json.dumps({"stage": "collection", "step": step, "group": index, "rewards": rewards}),
            flush=True,
        )
    if any(
        not torch.equal(value.detach().cpu(), before[name])
        for name, value in trainable_parameters(model)
    ):
        raise ValueError("adapter changed during frozen-policy collection")
    mixed = sum(bool(any(record["advantages"])) for record in rollouts)
    collection = {
        "groups": len(rollouts),
        "samples": len(rollouts) * BATCH,
        "correct": sum(sum(record["rewards"]) for record in rollouts),
        "terminated": sum(sum(record["terminated"]) for record in rollouts),
        "mixed_reward_groups": mixed,
        "optimizer_steps_at_collection": step - 1,
        "collection_seconds": time.monotonic() - started,
        "fresh_actions": True,
        "parent_identity": parent_identity,
        "start_sha256": core.sha(directory / "START.json"),
        "start_rng_sha256": core.sha(directory / "START_RNG.pt"),
        "group_commit_sha256": {
            str(path): core.sha(path)
            for path in sorted((directory / "groups").glob("*/GROUP_COMMIT.json"))
        },
    }
    core.write(directory / "COLLECTION.json", collection)
    qualifications = []
    for index, (group, record) in enumerate(zip(ordered, rollouts, strict=True)):
        destination = directory / "groups" / f"group-{index:03d}"
        verify_commit(destination / "GROUP_COMMIT.json", parent_identity)
        result = core.v1.replay_group(
            model, worker, group, record, record["advantages"], destination
        )
        qualifications.append(result)
        core.write(
            directory.parent.parent / "PROGRESS.json",
            {
                "stage": "replay",
                "step": step,
                "completed_groups": index + 1,
                "completed_optimizer_steps": step - 1,
                "update_elapsed_seconds": time.monotonic() - started,
            },
        )
        if not result["passed"]:
            optimizer.zero_grad(set_to_none=True)
            qualification = {
                "all_passed": False,
                "computed_before_step": True,
                "failed_group": index,
                "groups": qualifications,
            }
            core.write(directory / "QUALIFICATION.json", qualification)
            return {
                "status": "STOP_PROBABILITY_GATE",
                "qualification": qualification,
                "collection": collection,
                "optimizer_step_applied": False,
            }
    qualification = {
        "all_passed": True,
        "computed_before_step": True,
        "groups": qualifications,
        "historical_behavior_probabilities_used": False,
        "parent_identity": parent_identity,
        "step": step,
    }
    core.write(directory / "QUALIFICATION.json", qualification)
    if mixed == 0:
        return {
            "status": "STOP_ZERO_ADVANTAGE",
            "qualification": qualification,
            "collection": collection,
            "optimizer_step_applied": False,
        }
    if any(
        not torch.equal(value.detach().cpu(), before[name])
        for name, value in trainable_parameters(model)
    ):
        raise ValueError("adapter changed before qualified optimizer step")
    norm = float(
        torch.nn.utils.clip_grad_norm_(
            [p for _, p in trainable_parameters(model)], CLIP, error_if_nonfinite=True
        ).cpu()
    )
    if not math.isfinite(norm) or norm <= 0:
        optimizer.zero_grad(set_to_none=True)
        return {
            "status": "STOP_ZERO_GRADIENT",
            "qualification": qualification,
            "collection": collection,
            "optimizer_step_applied": False,
            "gradient_norm_before_clip": norm,
        }
    optimizer.step()
    delta = adapter_delta(model, before)
    result = {
        "status": "UPDATED",
        "qualification": qualification,
        "collection": collection,
        "optimizer_step_applied": True,
        "gradient_norm_before_clip": norm,
        "adapter_delta_l2": delta,
        "update_elapsed_seconds": time.monotonic() - started,
        "helper_loss_tokens": sum(sum(map(len, record["completion_ids"])) for record in rollouts),
    }
    if not math.isfinite(delta) or delta <= 0:
        result["status"] = "FAILED_AFTER_STEP_NONFINITE_OR_ZERO_DELTA"
    return result


def verify_ready():
    ready = core.read(ROOT / "READY.json")
    if ready["status"] != "CPU_READY_MAIN_REVIEW_REQUIRED":
        raise ValueError("unexpected four-step READY status")
    for raw, expected in ready["closure_sha256"].items():
        if core.sha(Path(raw)) != expected:
            raise ValueError("sealed four-step input changed: " + raw)
    if core.v1.SAMPLES != DENOMINATOR or core.v1.BATCH != BATCH:
        raise ValueError("qualified core loss/sampling dimensions differ")
    return ready


def save_checkpoint(
    model,
    optimizer,
    generator,
    output,
    step,
    result,
    parent_identity,
    parent_commit,
    ready_identity,
    initial,
    started,
):
    checkpoint = output / f"checkpoint-{step:04d}"
    checkpoint.mkdir()
    model.save_pretrained(checkpoint, safe_serialization=True)
    torch.save(optimizer.state_dict(), checkpoint / "optimizer.pt")
    save_rng(checkpoint / "rng_state.pt", generator)
    update = output / "updates" / f"update-{step:04d}"
    optimizer_steps = sorted({int(value["step"]) for value in optimizer.state.values()})
    if optimizer_steps != [step]:
        raise ValueError("AdamW state does not reflect the exact cumulative step")
    state = {
        "schema": "helper-hf-onpolicy-fourstep-state-v1",
        "step": step,
        "cumulative_optimizer_steps": step,
        "ready_identity": ready_identity,
        "parent_identity": parent_identity,
        "parent_step_commit": parent_commit,
        "starting_child": str(CHILD),
        "starting_child_adapter_sha256": CHILD_SHA,
        "optimizer": "one fresh AdamW carried across updates",
        "learning_rate": LR,
        "weight_decay": 0,
        "gradient_clip_norm": CLIP,
        "gradient_norm_before_clip": result["gradient_norm_before_clip"],
        "adapter_delta_l2_from_parent": result["adapter_delta_l2"],
        "adapter_delta_l2_from_c32": adapter_delta(model, initial),
        "optimizer_parameter_names": [name for name, _ in trainable_parameters(model)],
        "optimizer_state_steps": optimizer_steps,
        "temperature": 1.0,
        "loss_reduction": "sequence sum; mean over all128 freshly sampled actions",
        "root_loss_tokens": 0,
        "environment_loss_tokens": 0,
        "helper_loss_tokens": result["helper_loss_tokens"],
        "mixed_reward_groups": result["collection"]["mixed_reward_groups"],
        "seed_namespace": {
            "global": GLOBAL_SEED,
            "sampler": SAMPLER_SEED,
            "permutation_base": PERMUTATION_SEED_BASE,
        },
        "activation_storage": "eval-mode per-decoder nonreentrant checkpoint",
        "rng_state_scope": "complete current global and sampling RNG after this update",
        "elapsed_seconds": time.monotonic() - started,
        "peak_allocated_bytes": torch.cuda.max_memory_allocated(),
        "peak_reserved_bytes": torch.cuda.max_memory_reserved(),
        "qualification_path": str(update / "QUALIFICATION.json"),
        "qualification_sha256": core.sha(update / "QUALIFICATION.json"),
        "collection_path": str(update / "COLLECTION.json"),
        "collection_sha256": core.sha(update / "COLLECTION.json"),
        "files_sha256": {
            path.name: core.sha(path) for path in checkpoint.iterdir() if path.is_file()
        },
    }
    core.write(checkpoint / "state.json", state)
    child = {
        "path": str(checkpoint),
        "adapter_sha256": core.sha(checkpoint / "adapter_model.safetensors"),
        "config_sha256": core.sha(checkpoint / "adapter_config.json"),
    }
    source = core.read(SOURCE_BINDING)
    binding = core.v1.changed_binding(
        source,
        child,
        {
            "experiment": ROOT.name,
            "step": step,
            "cumulative_optimizer_steps": step,
            "root_unchanged": True,
            "state_sha256": core.sha(checkpoint / "state.json"),
            "optimizer_sha256": core.sha(checkpoint / "optimizer.pt"),
            "rng_sha256": core.sha(checkpoint / "rng_state.pt"),
            "source_child": source["models"][source["fixed_child"]],
        },
    )
    core.write(checkpoint / "EVAL_BINDING.json", binding)
    commit = commit_files(
        checkpoint / "STEP_COMMIT.json",
        list(checkpoint.iterdir()) + [update / "QUALIFICATION.json", update / "COLLECTION.json"],
        {
            "step": step,
            "cumulative_optimizer_steps": step,
            "parent_identity": parent_identity,
            "parent_step_commit": parent_commit,
            "ready_identity": ready_identity,
            "status": "UPDATED",
        },
    )
    return checkpoint, commit


def run(output, cap_seconds):
    from peft import PeftModel
    from transformers import AutoModelForCausalLM, AutoTokenizer

    ready = verify_ready()
    if output != ROOT / "outputs/attempt-001" or output.exists() or cap_seconds != CAP:
        raise ValueError("exact unused attempt-001 and3300-second cap required")
    if (
        not os.environ.get("CUDA_VISIBLE_DEVICES")
        or not torch.cuda.is_available()
        or torch.cuda.device_count() != 1
    ):
        raise ValueError("MAIN must assign exactly one GPU")
    groups = core.read(ROOT / "inputs/GROUPS.json")
    gold = core.read(ROOT / "inputs/TRAIN_GOLD.json")
    if len(groups) != GROUPS or {g["group_id"] for g in groups} != set(gold):
        raise ValueError("wrong training-only inventory")
    output.mkdir(parents=True)
    started = time.monotonic()
    core.write(
        output / "START.json",
        {
            "ready_identity": ready["identity"],
            "started_epoch": time.time(),
            "cap_seconds": CAP,
            "pid": os.getpid(),
            "starting_child_adapter_sha256": CHILD_SHA,
            "requested_updates": UPDATES,
            "primary_checkpoint_step": 4,
        },
    )

    def stop(sig, _frame):
        raise TimeoutError("four-step pilot interrupted by signal " + str(sig))

    old_handlers = {
        sig: signal.signal(sig, stop) for sig in (signal.SIGALRM, signal.SIGTERM, signal.SIGINT)
    }
    signal.setitimer(signal.ITIMER_REAL, CAP)
    completed, checkpoints, optimizer, model = 0, [], None, None
    try:
        random.seed(GLOBAL_SEED)
        np.random.seed(GLOBAL_SEED % 2**32)
        torch.manual_seed(GLOBAL_SEED)
        torch.cuda.manual_seed_all(GLOBAL_SEED)
        torch.set_num_threads(4)
        torch.backends.cuda.matmul.allow_tf32 = False
        torch.backends.cudnn.allow_tf32 = False
        torch.backends.cudnn.benchmark = False
        torch.cuda.reset_peak_memory_stats()
        sampler = torch.Generator(device="cuda:0").manual_seed(SAMPLER_SEED)
        tokenizer = AutoTokenizer.from_pretrained(BASE, local_files_only=True)
        base = AutoModelForCausalLM.from_pretrained(
            BASE,
            local_files_only=True,
            dtype=torch.bfloat16,
            attn_implementation="eager",
            device_map={"": "cuda:0"},
        )
        model = PeftModel.from_pretrained(
            base, CHILD, is_trainable=True, autocast_adapter_dtype=True
        )
        model.eval()
        model.config.use_cache = False
        model.gradient_checkpointing_disable()
        layers = core.install_eval_checkpoints(model)
        if core.sha(CHILD / "adapter_model.safetensors") != CHILD_SHA:
            raise ValueError("original c32 identity changed")
        initial = parameter_snapshot(model)
        optimizer = torch.optim.AdamW(
            [p for _, p in trainable_parameters(model)], lr=LR, weight_decay=0
        )
        parent_identity, parent_commit = CHILD_SHA, None
        core.write(
            output / "ACTIVATION_STORAGE.json",
            {
                "decoder_layers": layers,
                "model_training": model.training,
                "builtin_gradient_checkpointing": model.is_gradient_checkpointing,
                "use_cache": model.config.use_cache,
                "batch_size": BATCH,
                "base_dtype": "bfloat16",
                "trainable_dtype": "float32",
            },
        )
        with (
            (output / "GRAMMAR.stderr.log").open("w") as log,
            core.v1.GrammarClient(stderr=log) as worker,
        ):
            for step in range(1, UPDATES + 1):
                result = execute_update(
                    model,
                    optimizer,
                    worker,
                    tokenizer,
                    groups,
                    gold,
                    sampler,
                    step,
                    output / "updates" / f"update-{step:04d}",
                    parent_identity,
                    ready["identity"],
                )
                core.write(output / "updates" / f"update-{step:04d}" / "RESULT.json", result)
                if result["status"] != "UPDATED":
                    final = {
                        "status": result["status"],
                        "completed_optimizer_steps": completed,
                        "current_step_applied": result["optimizer_step_applied"],
                        "primary_checkpoint_available": False,
                        "checkpoints": checkpoints,
                        "elapsed_seconds": time.monotonic() - started,
                    }
                    core.write(output / "RESULT.json", final)
                    return final
                checkpoint, _commit = save_checkpoint(
                    model,
                    optimizer,
                    sampler,
                    output,
                    step,
                    result,
                    parent_identity,
                    parent_commit,
                    ready["identity"],
                    initial,
                    started,
                )
                completed = step
                parent_commit = {
                    "path": str(checkpoint / "STEP_COMMIT.json"),
                    "sha256": core.sha(checkpoint / "STEP_COMMIT.json"),
                }
                parent_identity = core.sha(checkpoint / "state.json")
                checkpoints.append(
                    {
                        "step": step,
                        "checkpoint": str(checkpoint),
                        "state_sha256": parent_identity,
                        "step_commit": parent_commit,
                    }
                )
                print(
                    json.dumps(
                        {
                            "stage": "committed_update",
                            "step": step,
                            "gradient_norm": result["gradient_norm_before_clip"],
                            "delta": result["adapter_delta_l2"],
                        }
                    ),
                    flush=True,
                )
        final = {
            "status": "COMPLETED_FOUR_UPDATES",
            "completed_optimizer_steps": completed,
            "primary_checkpoint_available": True,
            "primary_checkpoint_step": 4,
            "primary_checkpoint": checkpoints[-1]["checkpoint"],
            "checkpoints": checkpoints,
            "elapsed_seconds": time.monotonic() - started,
            "peak_allocated_bytes": torch.cuda.max_memory_allocated(),
            "peak_reserved_bytes": torch.cuda.max_memory_reserved(),
        }
        core.write(output / "RESULT.json", final)
        return final
    except BaseException as error:
        # Optimizer state reveals an applied-but-not-committed step after interruption.
        steps = (
            sorted({int(value["step"]) for value in optimizer.state.values()}) if optimizer else []
        )
        failure = {
            "status": "STOP_FAILED",
            "completed_optimizer_steps": completed,
            "observed_optimizer_state_steps": steps,
            "primary_checkpoint_available": False,
            "checkpoints": checkpoints,
            "error_type": type(error).__name__,
            "error": str(error),
            "elapsed_seconds": time.monotonic() - started,
        }
        core.write(output / "FAILURE.json", failure)
        core.write(output / "RESULT.json", failure)
        raise
    finally:
        signal.setitimer(signal.ITIMER_REAL, 0)
        for sig, handler in old_handlers.items():
            signal.signal(sig, handler)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--cap-seconds", type=int, required=True)
    args = parser.parse_args()
    print(json.dumps(run(args.output, args.cap_seconds), sort_keys=True))
