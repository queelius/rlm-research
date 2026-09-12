"""One-load, eight-update answer-only SFT on the frozen broader AG schedule."""

from __future__ import annotations

import math
import os
import random
import time
from pathlib import Path

import numpy as np
import sft_study as study


def trainable_parameters(model):
    values = [(name, value) for name, value in model.named_parameters() if value.requires_grad]
    if not values or any("lora_" not in name or value.dtype.__str__() != "torch.float32" for name, value in values):
        raise ValueError("only FP32 LoRA parameters may train")
    return values


def make_optimizer(model):
    import torch

    return torch.optim.AdamW(
        [value for _, value in trainable_parameters(model)], lr=study.LR, weight_decay=0
    )


def optimizer_steps(optimizer):
    return sorted({int(value["step"].item()) for value in optimizer.state.values()})


def validate_optimizer(model, optimizer, completed):
    parameters = trainable_parameters(model)
    group = optimizer.param_groups
    if (
        len(group) != 1
        or group[0]["lr"] != study.LR
        or group[0]["weight_decay"] != 0
        or [id(value) for value in group[0]["params"]] != [id(value) for _, value in parameters]
    ):
        raise ValueError("optimizer configuration differs")
    expected = [] if completed == 0 else [completed]
    if optimizer_steps(optimizer) != expected:
        raise ValueError("optimizer counter differs")


def collate(rows, pad_id):
    import torch

    width = max(len(row["input_ids"]) for row in rows)
    values = {}
    for name, pad in (("input_ids", pad_id), ("labels", -100), ("attention_mask", 0)):
        values[name] = torch.tensor(
            [
                (
                    row[name]
                    if name in row
                    else [1] * len(row["input_ids"])
                )
                + [pad] * (width - len(row["input_ids"]))
                for row in rows
            ],
            dtype=torch.long,
        )
    values["label_token_mask"] = torch.tensor(
        [row["label_token_mask"] + [False] * (width - len(row["input_ids"])) for row in rows],
        dtype=torch.bool,
    )
    return values


def save_checkpoint(model, optimizer, step, metrics):
    import torch

    destination = study.ATTEMPT / f"checkpoint-{step:04d}"
    destination.mkdir(parents=True, exist_ok=False)
    validate_optimizer(model, optimizer, step)
    model.save_pretrained(destination, safe_serialization=True)
    torch.save(optimizer.state_dict(), destination / "optimizer.pt")
    torch.save(
        {
            "python": random.getstate(),
            "numpy": np.random.get_state(),
            "torch": torch.get_rng_state(),
            "cuda": torch.cuda.get_rng_state_all(),
        },
        destination / "rng_state.pt",
    )
    files = {
        name: study.sha(destination / name)
        for name in ("adapter_model.safetensors", "adapter_config.json", "optimizer.pt", "rng_state.pt")
    }
    state = {
        "schema": "agnews-eightstep-answer-only-sft-state-v1",
        "status": "UPDATED",
        "step": step,
        "optimizer_steps": step,
        "optimizer_state_steps": optimizer_steps(optimizer),
        "starting_adapter": str(study.CHILD_START),
        "starting_adapter_sha256": study.CHILD_SHA,
        "training_data_manifest_sha256": study.DATA_MANIFEST_SHA256,
        "ready_identity": study.verify()["identity"],
        "step_metrics": metrics,
        "files_sha256": files,
        "fresh_optimizer_at_step0": True,
        "carried_optimizer_across_steps": True,
        "root_unchanged": True,
    }
    study.write_x(destination / "state.json", state)
    binding = {
        "schema": "agnews-eightstep-answer-only-sft-eval-binding-v1",
        "fixed_child": study.CHILD_ALIAS,
        "checkpoint": str(destination),
        "adapter_sha256": files["adapter_model.safetensors"],
        "config_sha256": files["adapter_config.json"],
        "state_sha256": study.sha(destination / "state.json"),
        "step": step,
        "optimizer_steps": step,
        "source_c32_adapter_sha256": study.CHILD_SHA,
        "root_unchanged": True,
    }
    study.write_x(destination / "EVAL_BINDING.json", binding)
    commit_paths = list(destination.iterdir())
    study.write_x(
        destination / "STEP_COMMIT.json",
        {
            "schema": "agnews-eightstep-answer-only-sft-commit-v1",
            "status": "UPDATED",
            "step": step,
            "optimizer_steps": step,
            "ready_identity": study.verify()["identity"],
            "parent_step_commit_sha256": (
                study.sha(study.ATTEMPT / f"checkpoint-{step - 1:04d}/STEP_COMMIT.json")
                if step > 1
                else None
            ),
            "files_sha256": {str(path): study.sha(path) for path in commit_paths},
        },
    )
    return destination


def run():
    import torch
    import torch.nn.functional as functional
    from peft import PeftModel
    from transformers import AutoModelForCausalLM

    if not os.environ.get("CUDA_VISIBLE_DEVICES") or torch.cuda.device_count() != 1:
        raise ValueError("MAIN must provide exactly one visible GPU")
    ready = study.verify()
    if study.ATTEMPT.exists():
        raise ValueError("refusing existing SFT attempt")
    study.ATTEMPT.mkdir(parents=True)
    random.seed(study.SEED)
    np.random.seed(study.SEED % (2**32))
    torch.manual_seed(study.SEED)
    torch.cuda.manual_seed_all(study.SEED)
    torch.set_num_threads(4)
    torch.cuda.reset_peak_memory_stats()
    started = time.monotonic()
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
    parameters = trainable_parameters(model)
    optimizer = make_optimizer(model)
    validate_optimizer(model, optimizer, 0)
    study.write_x(
        study.ATTEMPT / "LOAD_AUDIT.json",
        {
            "ready_identity": ready["identity"],
            "base": str(study.BASE_MODEL),
            "starting_adapter": str(study.CHILD_START),
            "starting_adapter_sha256": study.sha(study.CHILD_START / "adapter_model.safetensors"),
            "trainable_names": [name for name, _ in parameters],
            "trainable_parameters": sum(value.numel() for _, value in parameters),
            "base_dtype": str(next(base.parameters()).dtype),
            "gpu": torch.cuda.get_device_name(),
            "cuda": torch.version.cuda,
            "fresh_optimizer": True,
        },
    )
    model.train()
    model.config.use_cache = False
    for module in model.modules():
        if isinstance(module, torch.nn.Dropout):
            module.eval()
    model.enable_input_require_grads()
    model.gradient_checkpointing_enable(gradient_checkpointing_kwargs={"use_reentrant": False})
    metrics = []
    for step, rows in enumerate(study.teacher_schedule(), 1):
        before = {name: value.detach().cpu().clone() for name, value in parameters}
        optimizer.zero_grad(set_to_none=True)
        denominator = sum(row["supervised_tokens"] for row in rows)
        loss_sum = label_loss_sum = structure_loss_sum = 0.0
        for row in rows:
            batch = {key: value.to(model.device) for key, value in collate([row], study.tokenizer().pad_token_id).items()}
            labels = batch.pop("labels")
            label_mask = batch.pop("label_token_mask")[:, 1:]
            logits = model(**batch, use_cache=False).logits[:, :-1].float()
            targets = labels[:, 1:]
            losses = functional.cross_entropy(
                logits.reshape(-1, logits.shape[-1]), targets.reshape(-1), ignore_index=-100, reduction="none"
            ).reshape_as(targets)
            supervised = targets != -100
            total = losses[supervised].sum()
            (total / denominator).backward()
            loss_sum += float(total.detach())
            label_loss_sum += float(losses[supervised & label_mask].sum().detach())
            structure_loss_sum += float(losses[supervised & ~label_mask].sum().detach())
            del logits, losses, total, batch, labels
        gradient = float(torch.nn.utils.clip_grad_norm_([value for _, value in parameters], 1, error_if_nonfinite=True))
        if not math.isfinite(gradient) or gradient <= 0:
            raise ValueError("nonfinite or zero SFT gradient")
        optimizer.step()
        torch.cuda.synchronize()
        validate_optimizer(model, optimizer, step)
        delta = math.sqrt(sum(float((value.detach().cpu() - before[name]).double().square().sum()) for name, value in parameters))
        if not math.isfinite(delta) or delta <= 0:
            raise ValueError("adapter failed to change")
        metric = {
            "step": step,
            "teacher_maps": len(rows),
            "unique_records": sum(len(row["requested_ids"]) for row in rows),
            "supervised_tokens": denominator,
            "label_tokens": sum(sum(row["label_token_mask"]) for row in rows),
            "mean_nll": loss_sum / denominator,
            "label_nll_sum": label_loss_sum,
            "structure_nll_sum": structure_loss_sum,
            "gradient_norm_before_clip": gradient,
            "adapter_delta_l2": delta,
            "context_ids": [row["context_id"] for row in rows],
            "step_input_sha256": study.digest(rows),
            "elapsed_seconds": time.monotonic() - started,
        }
        metrics.append(metric)
        checkpoint = save_checkpoint(model, optimizer, step, metrics)
        print({"step": step, "checkpoint": str(checkpoint), "mean_nll": metric["mean_nll"]}, flush=True)
    result = {
        "schema": "agnews-eightstep-answer-only-sft-result-v1",
        "status": "UPDATED_STEP8",
        "complete": True,
        "optimizer_steps": 8,
        "checkpoint": str(study.ATTEMPT / "checkpoint-0008"),
        "step_commit_sha256": study.sha(study.ATTEMPT / "checkpoint-0008/STEP_COMMIT.json"),
        "state_sha256": study.sha(study.ATTEMPT / "checkpoint-0008/state.json"),
        "starting_adapter_sha256": study.CHILD_SHA,
        "training_data_manifest_sha256": study.DATA_MANIFEST_SHA256,
        "teacher_maps": 256,
        "unique_records": 1024,
        "supervised_tokens": sum(row["supervised_tokens"] for rows in study.teacher_schedule() for row in rows),
        "elapsed_seconds": time.monotonic() - started,
        "peak_allocated_bytes": torch.cuda.max_memory_allocated(),
        "peak_reserved_bytes": torch.cuda.max_memory_reserved(),
        "root_unchanged": True,
        "claim_boundary": "ordinary answer-only SFT data-signal control; no RL superiority comparison",
    }
    study.write_x(study.ATTEMPT / "RESULT.json", result)
    return result


def main():
    print(run())


if __name__ == "__main__":
    main()
