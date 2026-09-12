"""One HF load: exact score qualification, bounded replay, one AdamW update."""

import math
import os
import random
import time
from collections import Counter

import ag_study as study
import numpy as np
import torch


def rng_seed():
    random.seed(study.SEED)
    np.random.seed(study.SEED % (2**32))
    torch.manual_seed(study.SEED)
    torch.cuda.manual_seed_all(study.SEED)


def qualify_model(model, records, masks):
    modules = study.numeric_modules()
    model.eval()
    model.config.use_cache = False
    current, supported = [], []
    for row in records:
        values = modules.train._selected_logprobs(
            model, row, masks[row["mask_key"]], require_grad=False
        )
        sequence = values.detach().float().cpu().tolist()
        current.append(sequence)
        supported.append(len(sequence) == len(row["old_logprobs"]))
    result = modules.leaf.importance_diagnostics(
        current,
        [row["old_logprobs"] for row in records],
        supported,
        ess_fraction_min=0.8,
        max_normalized_weight_limit=0.1,
    )
    result.update(
        current_token_logprobs=current,
        episode_ids=[row["episode_id"] for row in records],
        computed_before_optimizer_creation=True,
        optimizer_steps=0,
        behavior="fresh c32 native batch-invariant T.5 chosen-token logprobs",
        target="c32 HF BF16 SDPA/dropout-off exact ordered-grammar T.5",
        raw_importance_weights_unclipped_and_not_self_normalized=True,
    )
    return result


def gradient_update(model, records, masks, qualification, output):
    modules = study.numeric_modules()
    output.mkdir(parents=True, exist_ok=True)
    if not qualification["gate_passed"]:
        return {"status": "NO_UPDATE_LIKELIHOOD_GATE_FAILED", "optimizer_steps": 0}
    advantages = modules.leaf.rloo_advantages(
        [row["reward"] for row in records], [row["group_id"] for row in records], reward_scale=4
    )
    model.train()
    model.config.use_cache = False
    for module in model.modules():
        if isinstance(module, torch.nn.Dropout):
            module.eval()
    model.enable_input_require_grads()
    model.gradient_checkpointing_enable(gradient_checkpointing_kwargs={"use_reentrant": False})
    if not model.is_gradient_checkpointing:
        raise ValueError("gradient checkpointing must be active")
    trainable = [(name, value) for name, value in model.named_parameters() if value.requires_grad]
    if not trainable or any(
        "lora_" not in name or value.dtype != torch.float32 for name, value in trainable
    ):
        raise ValueError("only FP32 LoRA may update")
    before = {name: value.detach().cpu().clone() for name, value in trainable}
    model.zero_grad(set_to_none=True)
    replay, captures = [], []
    for index, row in enumerate(records):
        values = modules.train._selected_logprobs(
            model, row, masks[row["mask_key"]], require_grad=True
        )
        actual = values.detach().float().cpu().tolist()
        check = modules.fast.replay_difference(
            actual, qualification["current_token_logprobs"][index]
        )
        replay.append({"episode_id": row["episode_id"], **check})
        if check["passed"]:
            loss = modules.fast.objective_term(
                values, qualification["ratios"][index], advantages[index], 128
            )
            loss.backward()
            captures.append(
                {
                    "episode_id": row["episode_id"],
                    "group_id": row["group_id"],
                    "reward": row["reward"],
                    "advantage": advantages[index],
                    "importance_ratio": qualification["ratios"][index],
                    "sequence_loss_over128": float(loss.detach().cpu()),
                }
            )
            del loss
        del values
    receipt = {
        "schema": "agnews-native-hf-gradient-replay-v1",
        "all128_passed": len(replay) == 128 and all(row["passed"] for row in replay),
        "computed_before_optimizer_step": True,
        "optimizer_steps": 0,
        "token_tolerance": 1e-5,
        "sequence_tolerance": 1e-4,
        "training_mode": True,
        "dropout_modules_eval": True,
        "gradient_checkpointing_active": bool(model.is_gradient_checkpointing),
        "episodes": replay,
        "batch_denominator": 128,
        "max_token_error": max(row["max_token_error"] for row in replay),
        "max_sequence_error": max(row["sequence_error"] for row in replay),
    }
    study.write_x(output / "GRADIENT_REPLAY_CHECK.json", receipt)
    study.write_x(output / "CAPTURE.json", captures)
    if not receipt["all128_passed"]:
        model.zero_grad(set_to_none=True)
        return {
            "status": "NO_UPDATE_GRADIENT_REPLAY_FAILED",
            "optimizer_steps": 0,
            "gradient_replay": receipt,
        }
    if not any(advantages):
        return {
            "status": "NO_UPDATE_ZERO_ADVANTAGE",
            "optimizer_steps": 0,
            "gradient_replay": receipt,
        }
    gradient = float(
        torch.nn.utils.clip_grad_norm_(
            [value for _, value in trainable], 1, error_if_nonfinite=True
        ).cpu()
    )
    if not math.isfinite(gradient) or gradient <= 0:
        return {
            "status": "NO_UPDATE_ZERO_GRADIENT",
            "optimizer_steps": 0,
            "gradient_replay": receipt,
        }
    # The optimizer does not exist until every saved-action replay has passed.
    optimizer = torch.optim.AdamW([value for _, value in trainable], lr=1e-5, weight_decay=0)
    if optimizer.state:
        raise ValueError("fresh AdamW unexpectedly has state")
    study.write_x(
        output / "OPTIMIZER_INTENT.json", {"intended_steps": 1, "all128_replay_passed": True}
    )
    optimizer.step()
    if torch.cuda.is_available():
        torch.cuda.synchronize()
    study.write_x(output / "OPTIMIZER_STEP.json", {"completed_steps": 1})
    state = optimizer.state_dict()
    steps = sorted({int(value["step"].item()) for value in state["state"].values()})
    if steps != [1]:
        raise ValueError("optimizer is not exactly one update")
    delta = math.sqrt(
        sum(
            float((value.detach().cpu() - before[name]).double().square().sum())
            for name, value in trainable
        )
    )
    if not math.isfinite(delta) or delta <= 0:
        raise ValueError("adapter failed to change")
    torch.save(state, output / "optimizer.pt")
    return {
        "status": "UPDATED",
        "optimizer_steps": 1,
        "optimizer_state_steps": steps,
        "gradient_norm_before_clip": gradient,
        "adapter_delta_l2": delta,
        "gradient_replay": receipt,
        "batch_denominator": 128,
        "mixed_reward_groups": sum(
            len({row["reward"] for row in records if row["group_id"] == group}) > 1
            for group in {row["group_id"] for row in records}
        ),
    }


def numeric_update(model, records, masks, output):
    output.mkdir(parents=True, exist_ok=True)
    qualification = qualify_model(model, records, masks)
    study.write_x(output / "PRESTEP_QUALIFICATION.json", qualification)
    return gradient_update(model, records, masks, qualification, output)


def load_inputs():
    output = study.ATTEMPT
    stopped = study.read(output / "service/SERVICE_STOPPED.json")
    if not stopped.get("all_owned_process_identities_exited") or not stopped.get("ports_free"):
        raise ValueError("native service must fully release before HF")
    attestation = study.read(output / "ENGINE_ATTESTATION.json")
    if attestation.get("actual_kernel_marker") != "batch_invariant.py / matmul_persistent":
        raise ValueError("actual batch-invariant kernel receipt missing")
    prepared = study.read(output / "PREPARED.json")
    inputs = output / "qualification-inputs"
    for field, path in (
        ("dataset_sha256", inputs / "DATASET.json"),
        ("masks_sha256", inputs / "MASKS.npz"),
        ("mask_manifest_sha256", inputs / "MASK_MANIFEST.json"),
        ("collection_sha256", output / "COLLECTION.json"),
    ):
        if prepared[field] != study.sha(path):
            raise ValueError("CPU mask handoff changed: " + field)
    dataset = study.read(inputs / "DATASET.json")
    records = dataset["records"]
    masks = np.load(inputs / "MASKS.npz", allow_pickle=False)
    collection = study.read(output / "COLLECTION.json")
    schedule = study.schedule()
    if (
        len(records) != 128
        or dataset["c32_adapter_sha256"] != study.CHILD_SHA
        or [row["episode_id"] for row in records] != [row["coordinate_id"] for row in schedule]
    ):
        raise ValueError("dataset inventory changed")
    gold = study.read(study.HOST_GOLD)
    group_sizes = Counter(record["group_id"] for record in records)
    if len(group_sizes) != 32 or set(group_sizes.values()) != {4}:
        raise ValueError("exact32 groups of4 sampled actions required")
    for record, collected, scheduled in zip(records, collection["records"], schedule, strict=True):
        if any(record.get(key) != value for key, value in collected.items()):
            raise ValueError("prepared data changed a collected action")
        ids = scheduled["requested_ids"]
        prompt = scheduled["body"]["token_ids"]
        schema = scheduled["body"]["sampling_params"]["structured_outputs"]["json"]
        if (
            record["group_id"] != study.digest({"prompt_ids": prompt, "schema": schema})
            or record["input_ids"] != prompt + record["action_ids"]
            or record["prompt_length"] != len(prompt)
            or record["selected_positions"] != list(range(len(prompt), len(record["input_ids"])))
            or record["requested_ids"] != ids
        ):
            raise ValueError("exact prompt/action/loss-mask grouping differs")
        correct = sum(
            record["prediction"][key] == gold[record["context_id"]]["labels"][key] for key in ids
        )
        if (
            record["correct_count"] != correct
            or record["reward"] != correct / 4
            or record["temperature"] != 0.5
            or len(ids) != 4
        ):
            raise ValueError("reward/temperature rederivation differs")
        for key in ("raw_request_path", "raw_response_path"):
            if study.sha(record[key]) != record[key.replace("path", "sha256")]:
                raise ValueError("native raw source changed")
        array = masks[record["mask_key"]]
        if (
            list(array.shape) != record["mask_shape"]
            or study.hashlib.sha256(array.tobytes()).hexdigest() != record["mask_raw_sha256"]
        ):
            raise ValueError("packed grammar mask changed")
    return records, masks


def run():
    from peft import PeftModel
    from transformers import AutoModelForCausalLM

    if not os.environ.get("CUDA_VISIBLE_DEVICES") or torch.cuda.device_count() != 1:
        raise ValueError("MAIN must assign exactly one GPU")
    ready = study.verify()
    records, masks = load_inputs()
    started = time.monotonic()
    rng_seed()
    torch.set_num_threads(4)
    torch.cuda.reset_peak_memory_stats()
    study.write_x(
        study.ATTEMPT / "HF_START.json",
        {
            "ready_identity": ready["identity"],
            "started_epoch": time.time(),
            "seed": study.SEED,
            "numpy_legacy_seed": study.SEED % (2**32),
            "optimizer_steps": 0,
            "single_hf_model_load": True,
        },
    )
    base = AutoModelForCausalLM.from_pretrained(
        study.BASE_MODEL,
        local_files_only=True,
        dtype=torch.bfloat16,
        attn_implementation="sdpa",
        device_map={"": "cuda:0"},
    )
    model = PeftModel.from_pretrained(
        base, study.CHILD_START, is_trainable=True, autocast_adapter_dtype=True
    )
    result = numeric_update(model, records, masks, study.ATTEMPT)
    result.update(
        ready_identity=ready["identity"],
        elapsed_seconds=time.monotonic() - started,
        peak_allocated_bytes=torch.cuda.max_memory_allocated(),
        peak_reserved_bytes=torch.cuda.max_memory_reserved(),
    )
    if result["status"] == "UPDATED":
        checkpoint = study.ATTEMPT / "checkpoint-0001"
        checkpoint.mkdir()
        model.save_pretrained(checkpoint, safe_serialization=True)
        (study.ATTEMPT / "optimizer.pt").rename(checkpoint / "optimizer.pt")
        torch.save(
            {
                "python": random.getstate(),
                "numpy": np.random.get_state(),
                "torch": torch.get_rng_state(),
                "cuda": torch.cuda.get_rng_state_all(),
            },
            checkpoint / "rng_state.pt",
        )
        state = {key: value for key, value in result.items() if key != "gradient_replay"}
        state.update(
            schema="agnews-native-hf-checkpoint-v1",
            step=1,
            starting_child_adapter_sha256=study.CHILD_SHA,
            qualification_sha256=study.sha(study.ATTEMPT / "PRESTEP_QUALIFICATION.json"),
            gradient_replay_sha256=study.sha(study.ATTEMPT / "GRADIENT_REPLAY_CHECK.json"),
            collection_sha256=study.sha(study.ATTEMPT / "COLLECTION.json"),
            dataset_sha256=study.sha(study.ATTEMPT / "qualification-inputs/DATASET.json"),
            objective=ready["policy"],
            single_hf_model_load=True,
            files_sha256={
                name: study.sha(checkpoint / name)
                for name in (
                    "adapter_model.safetensors",
                    "adapter_config.json",
                    "optimizer.pt",
                    "rng_state.pt",
                )
            },
        )
        study.write_x(checkpoint / "state.json", state)
        study.write_x(
            checkpoint / "EVAL_BINDING.json",
            study.child_binding(checkpoint, study.sha(checkpoint / "state.json")),
        )
        files = [
            checkpoint / name
            for name in (
                "adapter_model.safetensors",
                "adapter_config.json",
                "optimizer.pt",
                "rng_state.pt",
                "state.json",
                "EVAL_BINDING.json",
            )
        ]
        files += [
            study.ATTEMPT / name
            for name in (
                "PRESTEP_QUALIFICATION.json",
                "GRADIENT_REPLAY_CHECK.json",
                "COLLECTION.json",
                "PREPARED.json",
                "CAPTURE.json",
                "ENGINE_ATTESTATION.json",
            )
        ]
        study.write_x(
            checkpoint / "STEP_COMMIT.json",
            {
                "status": "UPDATED",
                "step": 1,
                "optimizer_steps": 1,
                "ready_identity": ready["identity"],
                "files_sha256": {str(path): study.sha(path) for path in files},
            },
        )
        result.update(
            checkpoint=str(checkpoint),
            state_sha256=study.sha(checkpoint / "state.json"),
            step_commit_sha256=study.sha(checkpoint / "STEP_COMMIT.json"),
        )
    study.write_x(study.ATTEMPT / "RESULT.json", result)
    print({key: value for key, value in result.items() if key != "gradient_replay"})


if __name__ == "__main__":
    run()
