"""One fresh c32 collection, then paired RLOO and other-31 one-step updates."""

import argparse
import copy
import json
import math
import os
import random
from pathlib import Path
import shutil
import signal
import time

import numpy as np
import torch

import pair_math
import source
import study


def _stage_alarm(stage, cap, overall_deadline):
    remaining = max(1, int(overall_deadline - time.monotonic()))
    seconds = min(cap, remaining)

    def stop(_sig, _frame):
        raise TimeoutError(stage + " exceeded its sealed deadline")

    signal.signal(signal.SIGALRM, stop)
    signal.setitimer(signal.ITIMER_REAL, seconds)
    return seconds


def _collect(implementation, model, worker, tokenizer, groups, gold, generator, output, ready):
    directory = output / "shared-collection"
    directory.mkdir(parents=True)
    order = list(range(32))
    random.Random(study.PERMUTATION_SEED).shuffle(order)
    ordered = [groups[index] for index in order]
    implementation.core.write(
        directory / "START.json",
        {
            "ready_identity": ready["identity"],
            "parent_adapter_sha256": implementation.CHILD_SHA,
            "permutation_seed": study.PERMUTATION_SEED,
            "group_source_indices": order,
            "group_ids": [group["group_id"] for group in ordered],
            "planned_actions": 128,
            "optimizer_created": False,
        },
    )
    implementation.save_rng(directory / "START_RNG.pt", generator)
    records = []
    for index, group in enumerate(ordered):
        destination = directory / "groups" / f"group-{index:03d}"
        record = implementation.core.v1.rollout_group(
            model, worker, tokenizer, group, index, generator, destination
        )
        rewards = [
            implementation.core.v1.local_reward(
                content, group["public_record"]["id"], gold[group["group_id"]], terminated
            )
            for content, terminated in zip(
                record["contents"], record["terminated"], strict=True
            )
        ]
        record.update(
            rewards=rewards,
            shared_group_index=index,
            source_group_index=order[index],
            all_actions_retained=True,
        )
        implementation.core.write(destination / "ROLLOUT.json", record)
        implementation.save_rng(destination / "AFTER_GROUP_RNG.pt", generator)
        records.append(record)
        implementation.core.write(
            output / "PROGRESS.json",
            {"stage": "collection", "completed_groups": index + 1, "planned_groups": 32},
        )
    if len(records) != 32 or sum(len(record["completion_ids"]) for record in records) != 128:
        raise ValueError("shared fresh action inventory differs")
    paired = pair_math.paired_advantages([record["rewards"] for record in records])
    commits = {}
    all_failure_ids = []
    action_inventory = []
    for index, (group, record, advantages) in enumerate(
        zip(ordered, records, paired, strict=True)
    ):
        destination = directory / "groups" / f"group-{index:03d}"
        record.update(
            paired_advantages=advantages,
            shared_actions_for_branches=["rloo", "other31"],
        )
        implementation.core.write(destination / "ROLLOUT.json", record)
        if advantages["all_failure"]:
            all_failure_ids.append(group["group_id"])
        commit = implementation.commit_files(
            destination / "GROUP_COMMIT.json",
            [
                destination / "ROLLOUT.json",
                destination / "MASKS.npz",
                destination / "AFTER_GROUP_RNG.pt",
            ],
            {
                "ready_identity": ready["identity"],
                "parent_identity": implementation.CHILD_SHA,
                "group_index": index,
                "group_id": group["group_id"],
                "actions_shared_by_both_branches": True,
            },
        )
        commits[str(destination / "GROUP_COMMIT.json")] = implementation.core.sha(
            destination / "GROUP_COMMIT.json"
        )
        action_inventory.append(
            {
                "group_id": group["group_id"],
                "completion_ids": record["completion_ids"],
                "rewards": record["rewards"],
                "rollout_sha256": implementation.core.sha(destination / "ROLLOUT.json"),
                "masks_sha256": record["masks_sha256"],
                "commit_sha256": implementation.core.sha(destination / "GROUP_COMMIT.json"),
            }
        )
    implementation.save_rng(directory / "AFTER_COLLECTION_RNG.pt", generator)
    collection = {
        "schema": "helper-hf-other31-shared-fresh-collection-v1",
        "groups": 32,
        "actions": 128,
        "freshly_sampled": True,
        "optimizer_created_during_collection": False,
        "parent_adapter_sha256": implementation.CHILD_SHA,
        "temperature": 1.0,
        "permutation_seed": study.PERMUTATION_SEED,
        "group_source_indices": order,
        "correct": math.fsum(value for record in records for value in record["rewards"]),
        "mixed_groups": sum(len(set(record["rewards"])) > 1 for record in records),
        "all_failure_group_ids": all_failure_ids,
        "all_failure_actions_retained": 4 * len(all_failure_ids),
        "group_commit_sha256": commits,
        "action_inventory": action_inventory,
        "after_collection_rng_sha256": implementation.core.sha(
            directory / "AFTER_COLLECTION_RNG.pt"
        ),
    }
    implementation.core.write(directory / "COLLECTION.json", collection)
    return ordered, records, collection


def _branch(
    implementation,
    model,
    worker,
    generator,
    ordered,
    records,
    snapshot,
    branch,
    output,
    ready,
    shared_sha,
    collection,
):
    pair_math.assert_snapshot(model, snapshot)
    directory = output / "branches" / branch
    directory.mkdir(parents=True)
    optimizer = torch.optim.AdamW(
        [parameter for _, parameter in implementation.trainable_parameters(model)],
        lr=1e-5,
        weight_decay=0,
    )
    if optimizer.state:
        raise ValueError("fresh branch optimizer unexpectedly has state")
    implementation.core.write(
        directory / "START.json",
        {
            "branch": branch,
            "baseline": study.BASELINES[branch],
            "ready_identity": ready["identity"],
            "parent_adapter_sha256": implementation.CHILD_SHA,
            "shared_collection_sha256": shared_sha,
            "fresh_optimizer_state_empty": True,
            "sequence_reduction": "sum",
            "denominator": 128,
        },
    )
    optimizer.zero_grad(set_to_none=True)
    qualifications = []
    nonzero_groups = 0
    all_failure_actions = []
    inventory = {row["group_id"]: row for row in collection["action_inventory"]}
    if len(inventory) != 32:
        raise ValueError("shared collection inventory differs")
    for index, (group, record) in enumerate(zip(ordered, records, strict=True)):
        destination = directory / "groups" / f"group-{index:03d}"
        destination.mkdir(parents=True)
        shared = output / "shared-collection/groups" / f"group-{index:03d}"
        expected = inventory.get(group["group_id"])
        if expected is None:
            raise ValueError("shared group absent from inventory")
        saved_record = implementation.core.read(shared / "ROLLOUT.json")
        if saved_record != record:
            raise ValueError("shared rollout changed")
        if (
            implementation.core.sha(shared / "ROLLOUT.json")
            != expected["rollout_sha256"]
            or implementation.core.sha(shared / "MASKS.npz") != expected["masks_sha256"]
            or record["completion_ids"] != expected["completion_ids"]
            or record["rewards"] != expected["rewards"]
        ):
            raise ValueError("shared action or mask inventory changed")
        shutil.copyfile(shared / "MASKS.npz", destination / "MASKS.npz")
        advantages = record["paired_advantages"][branch]
        if any(advantages):
            nonzero_groups += 1
        if record["paired_advantages"]["all_failure"]:
            all_failure_actions.extend(
                {
                    "group_id": group["group_id"],
                    "action_index": action_index,
                    "reward": record["rewards"][action_index],
                    "advantage": advantages[action_index],
                }
                for action_index in range(4)
            )
        result = implementation.core.v1.replay_group(
            model, worker, group, record, advantages, destination
        )
        result.update(
            branch=branch,
            baseline=study.BASELINES[branch],
            shared_rollout=str(shared / "ROLLOUT.json"),
            shared_rollout_sha256=implementation.core.sha(shared / "ROLLOUT.json"),
            shared_masks_sha256=implementation.core.sha(shared / "MASKS.npz"),
        )
        implementation.core.write(destination / "REPLAY.json", result)
        qualifications.append(result)
        implementation.core.write(
            output / "PROGRESS.json",
            {"stage": branch, "completed_groups": index + 1, "planned_groups": 32},
        )
        if not result["passed"]:
            optimizer.zero_grad(set_to_none=True)
            raise RuntimeError(branch + " exact on-policy probability gate failed")
    qualification = {
        "schema": "helper-hf-other31-branch-qualification-v1",
        "branch": branch,
        "baseline": study.BASELINES[branch],
        "all32_passed": True,
        "computed_before_step": True,
        "shared_collection_sha256": shared_sha,
        "same_actions_and_masks_for_both_branches": True,
        "true_onpolicy_c32_before_step": True,
        "importance_weights_used": False,
        "sequence_reduction": "sum",
        "denominator": 128,
        "nonzero_groups": nonzero_groups,
        "all_failure_actions": all_failure_actions,
        "groups": qualifications,
    }
    implementation.core.write(directory / "QUALIFICATION.json", qualification)
    if nonzero_groups == 0:
        result = {"status": "NO_UPDATE_ZERO_SIGNAL", "branch": branch, "optimizer_steps": 0}
        implementation.core.write(directory / "RESULT.json", result)
        return result, optimizer
    norm = float(
        torch.nn.utils.clip_grad_norm_(
            [parameter for _, parameter in implementation.trainable_parameters(model)],
            1.0,
            error_if_nonfinite=True,
        ).cpu()
    )
    if not math.isfinite(norm) or norm <= 0:
        raise RuntimeError(branch + " nonfinite or zero gradient")
    optimizer.step()
    delta = implementation.adapter_delta(model, snapshot)
    if not math.isfinite(delta) or delta <= 0:
        raise RuntimeError(branch + " nonfinite or zero adapter delta")
    checkpoint = directory / "checkpoint-0001"
    checkpoint.mkdir()
    model.save_pretrained(checkpoint, safe_serialization=True)
    torch.save(optimizer.state_dict(), checkpoint / "optimizer.pt")
    implementation.save_rng(checkpoint / "rng_state.pt", generator)
    optimizer_steps = sorted({int(value["step"]) for value in optimizer.state.values()})
    if optimizer_steps != [1]:
        raise ValueError("branch optimizer state does not show exact step1")
    state = {
        "schema": "helper-hf-onpolicy-other31-paired-state-v1",
        "branch": branch,
        "baseline": study.BASELINES[branch],
        "step": 1,
        "optimizer_state_steps": optimizer_steps,
        "optimizer": "fresh AdamW for this branch only",
        "learning_rate": 1e-5,
        "weight_decay": 0,
        "gradient_clip_norm": 1.0,
        "gradient_norm_before_clip": norm,
        "adapter_delta_l2_from_c32": delta,
        "starting_adapter_sha256": implementation.CHILD_SHA,
        "shared_collection_sha256": shared_sha,
        "qualification_sha256": implementation.core.sha(directory / "QUALIFICATION.json"),
        "all_failure_actions_retained": len(all_failure_actions),
        "nonzero_groups": nonzero_groups,
        "sequence_reduction": "sum",
        "denominator": 128,
        "temperature": 1.0,
        "seed_namespace": study.plan()["seeds"],
        "files_sha256": {
            path.name: implementation.core.sha(path)
            for path in checkpoint.iterdir()
            if path.is_file()
        },
    }
    implementation.core.write(checkpoint / "state.json", state)
    child = {
        "path": str(checkpoint),
        "adapter_sha256": implementation.core.sha(checkpoint / "adapter_model.safetensors"),
        "config_sha256": implementation.core.sha(checkpoint / "adapter_config.json"),
    }
    source_binding = implementation.core.read(study.SOURCE_BINDING)
    binding = implementation.core.v1.changed_binding(
        source_binding,
        child,
        {
            "experiment": study.ROOT.name,
            "branch": branch,
            "step": 1,
            "baseline": study.BASELINES[branch],
            "shared_collection_sha256": shared_sha,
            "root_unchanged": True,
            "state_sha256": implementation.core.sha(checkpoint / "state.json"),
            "source_child": source_binding["models"][source_binding["fixed_child"]],
        },
    )
    implementation.core.write(checkpoint / "EVAL_BINDING.json", binding)
    commit = implementation.commit_files(
        checkpoint / "STEP_COMMIT.json",
        list(checkpoint.iterdir()) + [directory / "QUALIFICATION.json"],
        {
            "branch": branch,
            "step": 1,
            "ready_identity": ready["identity"],
            "shared_collection_sha256": shared_sha,
            "status": "UPDATED",
        },
    )
    result = {
        "status": "UPDATED",
        "branch": branch,
        "optimizer_steps": 1,
        "baseline": study.BASELINES[branch],
        "checkpoint": str(checkpoint),
        "checkpoint_state_sha256": implementation.core.sha(checkpoint / "state.json"),
        "step_commit_sha256": implementation.core.sha(checkpoint / "STEP_COMMIT.json"),
        "shared_collection_sha256": shared_sha,
        "gradient_norm_before_clip": norm,
        "adapter_delta_l2_from_c32": delta,
        "nonzero_groups": nonzero_groups,
        "all_failure_actions_retained": len(all_failure_actions),
    }
    implementation.core.write(directory / "RESULT.json", result)
    return result, optimizer


def run(output, cap_seconds):
    from peft import PeftModel
    from transformers import AutoModelForCausalLM, AutoTokenizer

    ready = study.verify()
    if output.resolve() != study.OUTPUT.resolve() or output.exists() or cap_seconds != study.CAP:
        raise ValueError("exact unused attempt-001 and2700-second cap required")
    if (
        not os.environ.get("CUDA_VISIBLE_DEVICES")
        or not torch.cuda.is_available()
        or torch.cuda.device_count() != 1
    ):
        raise ValueError("MAIN must assign exactly one GPU")
    output.mkdir(parents=True)
    started = time.monotonic()
    overall_deadline = started + study.CAP
    implementation = source.load()
    if (
        implementation.core.v1.TEMPERATURE != 1.0
        or implementation.core.v1.SAMPLES != 128
        or implementation.core.v1.BATCH != 4
        or implementation.CHILD_SHA
        != "c32de1293c01bba5104eb1f123867649c71dd38e5194661ace4b17dcbbe66ba3"
    ):
        raise ValueError("sealed source policy differs")
    groups = implementation.core.read(study.ROOT / "inputs/GROUPS.json")
    gold = implementation.core.read(study.ROOT / "inputs/TRAIN_GOLD.json")
    if len(groups) != 32 or {group["group_id"] for group in groups} != set(gold):
        raise ValueError("training-only inventory differs")
    implementation.core.write(
        output / "START.json",
        {
            "ready_identity": ready["identity"],
            "started_epoch": time.time(),
            "pid": os.getpid(),
            "cap_seconds": study.CAP,
            "stage_caps_seconds": study.STAGE_CAPS,
            "planned_shared_actions": 128,
            "planned_branches": ["rloo", "other31"],
            "optimizer_steps_per_branch": 1,
        },
    )
    completed = []
    first_optimizer = None
    try:
        random.seed(study.GLOBAL_SEED)
        np.random.seed(study.GLOBAL_SEED % 2**32)
        torch.manual_seed(study.GLOBAL_SEED)
        torch.cuda.manual_seed_all(study.GLOBAL_SEED)
        torch.set_num_threads(4)
        torch.backends.cuda.matmul.allow_tf32 = False
        torch.backends.cudnn.allow_tf32 = False
        torch.backends.cudnn.benchmark = False
        torch.cuda.reset_peak_memory_stats()
        generator = torch.Generator(device="cuda:0").manual_seed(study.SAMPLER_SEED)
        tokenizer = AutoTokenizer.from_pretrained(study.BASE, local_files_only=True)
        base = AutoModelForCausalLM.from_pretrained(
            study.BASE,
            local_files_only=True,
            dtype=torch.bfloat16,
            attn_implementation="eager",
            device_map={"": "cuda:0"},
        )
        model = PeftModel.from_pretrained(
            base, study.CHILD, is_trainable=True, autocast_adapter_dtype=True
        )
        model.eval()
        model.config.use_cache = False
        model.gradient_checkpointing_disable()
        decoder_layers = implementation.core.install_eval_checkpoints(model)
        if implementation.core.sha(study.CHILD / "adapter_model.safetensors") != implementation.CHILD_SHA:
            raise ValueError("original c32 adapter changed")
        initial = pair_math.snapshot_trainable(model)
        initial_digest = pair_math.snapshot_digest(initial)
        torch.save(initial, output / "C32_TRAINABLE_SNAPSHOT.pt")
        implementation.core.write(
            output / "C32_SNAPSHOT.json",
            {
                "tensor_identity_sha256": initial_digest,
                "serialized_sha256": implementation.core.sha(output / "C32_TRAINABLE_SNAPSHOT.pt"),
                "trainable_parameters": sorted(initial),
                "decoder_layers": decoder_layers,
            },
        )
        with (
            (output / "GRAMMAR.stderr.log").open("w") as log,
            implementation.core.v1.GrammarClient(stderr=log) as worker,
        ):
            _stage_alarm("collection", study.STAGE_CAPS["collection"], overall_deadline)
            ordered, records, collection = _collect(
                implementation, model, worker, tokenizer, groups, gold, generator, output, ready
            )
            shared_path = output / "shared-collection/COLLECTION.json"
            shared_sha = implementation.core.sha(shared_path)
            implementation.restore_rng(
                output / "shared-collection/AFTER_COLLECTION_RNG.pt", generator
            )
            _stage_alarm("rloo", study.STAGE_CAPS["rloo"], overall_deadline)
            rloo, first_optimizer = _branch(
                implementation,
                model,
                worker,
                generator,
                ordered,
                records,
                initial,
                "rloo",
                output,
                ready,
                shared_sha,
                collection,
            )
            completed.append("rloo")
            del first_optimizer
            first_optimizer = None
            pair_math.restore_snapshot(model, initial)
            implementation.restore_rng(
                output / "shared-collection/AFTER_COLLECTION_RNG.pt", generator
            )
            if pair_math.snapshot_digest(pair_math.snapshot_trainable(model)) != initial_digest:
                raise ValueError("restored c32 tensor identity differs")
            implementation.core.write(
                output / "BRANCH_RESTORE.json",
                {
                    "after_branch": "rloo",
                    "before_branch": "other31",
                    "bit_identical_c32": True,
                    "tensor_identity_sha256": initial_digest,
                    "rng_restored_sha256": implementation.core.sha(
                        output / "shared-collection/AFTER_COLLECTION_RNG.pt"
                    ),
                    "fresh_second_optimizer": True,
                },
            )
            _stage_alarm("other31", study.STAGE_CAPS["other31"], overall_deadline)
            other31, second_optimizer = _branch(
                implementation,
                model,
                worker,
                generator,
                ordered,
                records,
                initial,
                "other31",
                output,
                ready,
                shared_sha,
                collection,
            )
            completed.append("other31")
            del second_optimizer
        both_updated = all(row["status"] == "UPDATED" for row in (rloo, other31))
        final = {
            "status": (
                "COMPLETED_PAIRED_ONE_STEP"
                if both_updated
                else "COMPLETED_WITH_NO_UPDATE_BRANCH"
            ),
            "shared_collection": str(shared_path),
            "shared_collection_sha256": shared_sha,
            "shared_actions": collection["actions"],
            "branches": {"rloo": rloo, "other31": other31},
            "completed_branches": completed,
            "optimizer_steps": {"rloo": rloo["optimizer_steps"], "other31": other31["optimizer_steps"]},
            "elapsed_seconds": time.monotonic() - started,
            "peak_allocated_bytes": torch.cuda.max_memory_allocated(),
            "peak_reserved_bytes": torch.cuda.max_memory_reserved(),
        }
        implementation.core.write(output / "RESULT.json", final)
        return final
    except BaseException as error:
        failure = {
            "status": "STOP_FAILED",
            "completed_branches": completed,
            "error_type": type(error).__name__,
            "error": str(error),
            "elapsed_seconds": time.monotonic() - started,
        }
        implementation.core.write(output / "FAILURE.json", failure)
        implementation.core.write(output / "RESULT.json", failure)
        raise
    finally:
        signal.setitimer(signal.ITIMER_REAL, 0)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--cap-seconds", type=int, required=True)
    arguments = parser.parse_args()
    print(json.dumps(run(arguments.output, arguments.cap_seconds), sort_keys=True))
