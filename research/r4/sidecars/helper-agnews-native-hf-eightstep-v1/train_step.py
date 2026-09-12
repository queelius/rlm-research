"""Persistent-Adam exact-likelihood helper update with bounded per-action graphs."""

import math
import random
from pathlib import Path

import core
import numpy as np
import torch


def make_optimizer(model):
    parameters = trainable_parameters(model)
    return torch.optim.AdamW([parameter for _, parameter in parameters], lr=1e-5, weight_decay=0)


def modules():
    return core.original.numeric_modules()


def trainable_parameters(model):
    values = [
        (name, parameter) for name, parameter in model.named_parameters() if parameter.requires_grad
    ]
    if not values or any(
        "lora_" not in name or parameter.dtype != torch.float32 for name, parameter in values
    ):
        raise ValueError("only ordered FP32 LoRA parameters may update")
    return values


def optimizer_steps(optimizer):
    return sorted({int(state["step"].item()) for state in optimizer.state.values()})


def optimizer_layout(model):
    return [
        {"name": name, "shape": list(value.shape), "dtype": str(value.dtype)}
        for name, value in trainable_parameters(model)
    ]


def validate_optimizer(model, optimizer, completed_steps):
    parameters = trainable_parameters(model)
    if len(optimizer.param_groups) != 1:
        raise ValueError("exact one AdamW parameter group required")
    group = optimizer.param_groups[0]
    if (
        group["lr"] != 1e-5
        or group["weight_decay"] != 0
        or [id(value) for value in group["params"]] != [id(value) for _, value in parameters]
    ):
        raise ValueError("optimizer configuration or parameter order differs")
    expected = [] if completed_steps == 0 else [completed_steps]
    if optimizer_steps(optimizer) != expected:
        raise ValueError("optimizer counters do not match prior committed step")
    if completed_steps and len(optimizer.state) != len(parameters):
        raise ValueError("incomplete optimizer moment inventory")
    for state in optimizer.state.values():
        if any(
            not torch.isfinite(value).all() for value in state.values() if torch.is_tensor(value)
        ):
            raise ValueError("nonfinite optimizer state")


def save_training_state(model, optimizer, checkpoint, completed_steps):
    checkpoint = Path(checkpoint)
    checkpoint.mkdir(parents=True, exist_ok=False)
    validate_optimizer(model, optimizer, completed_steps)
    model.save_pretrained(checkpoint, safe_serialization=True)
    torch.save(optimizer.state_dict(), checkpoint / "optimizer.pt")
    core.write_x(checkpoint / "OPTIMIZER_LAYOUT.json", optimizer_layout(model))
    torch.save(
        {
            "python": random.getstate(),
            "numpy": np.random.get_state(),
            "torch": torch.get_rng_state(),
            "cuda": torch.cuda.get_rng_state_all(),
        },
        checkpoint / "rng_state.pt",
    )


def restore_training_state(model, optimizer, checkpoint, completed_steps):
    from peft import set_peft_model_state_dict
    from safetensors.torch import load_file

    checkpoint = Path(checkpoint)
    if core.read(checkpoint / "OPTIMIZER_LAYOUT.json") != optimizer_layout(model):
        raise ValueError("saved optimizer parameter names/shapes/dtypes differ")
    # Caller authenticates the complete parent commit before this local checkpoint read.
    restored = set_peft_model_state_dict(model, load_file(checkpoint / "adapter_model.safetensors"))
    if restored.unexpected_keys:
        raise ValueError("unexpected saved LoRA parameter keys")
    optimizer.load_state_dict(
        torch.load(checkpoint / "optimizer.pt", map_location="cpu", weights_only=False)
    )
    validate_optimizer(model, optimizer, completed_steps)
    rng = torch.load(checkpoint / "rng_state.pt", map_location="cpu", weights_only=False)
    random.setstate(rng["python"])
    np.random.set_state(rng["numpy"])
    torch.set_rng_state(rng["torch"])
    if len(rng["cuda"]) != torch.cuda.device_count():
        raise ValueError("saved/current CUDA RNG device count differs")
    if rng["cuda"]:
        torch.cuda.set_rng_state_all(rng["cuda"])


def update_once(model, optimizer, records, masks, output, completed_steps):
    output = Path(output)
    output.mkdir(parents=True, exist_ok=True)
    validate_optimizer(model, optimizer, completed_steps)
    if len(records) != 128 or len({row["episode_id"] for row in records}) != 128:
        raise ValueError("exact fresh128 action inventory required")
    source = core.load_bound(
        "ag_eight_qualified_scores", core.SOURCE / "train_ag.py", {"ag_study": core.original}
    )
    qualification = source.qualify_model(model, records, masks)
    qualification.update(
        computed_before_optimizer_creation=False,
        computed_before_this_optimizer_step=True,
        optimizer_steps=completed_steps,
        behavior="fresh exact authenticated parent native batch-invariant T.5 policy",
        target="same parent checkpoint HF BF16/FP32LoRA SDPA/dropout-off exact grammar T.5",
    )
    core.write_x(output / "PRESTEP_QUALIFICATION.json", qualification)
    stopped = {"optimizer_steps": completed_steps, "optimizer_steps_this_stage": 0}
    if not qualification["gate_passed"]:
        return {**stopped, "status": "NO_UPDATE_LIKELIHOOD_GATE_FAILED"}
    numeric = modules()
    advantages = numeric.leaf.rloo_advantages(
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
        raise ValueError("nonreentrant gradient checkpointing required")
    parameters = trainable_parameters(model)
    before = {name: parameter.detach().cpu().clone() for name, parameter in parameters}
    optimizer.zero_grad(set_to_none=True)
    replay, captures = [], []
    for index, row in enumerate(records):
        values = numeric.train._selected_logprobs(
            model, row, masks[row["mask_key"]], require_grad=True
        )
        actual = values.detach().float().cpu().tolist()
        check = numeric.fast.replay_difference(
            actual, qualification["current_token_logprobs"][index]
        )
        replay.append({"episode_id": row["episode_id"], **check})
        if check["passed"]:
            loss = numeric.fast.objective_term(
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
        "schema": "agnews-eightstep-gradient-replay-v1",
        "all128_passed": len(replay) == 128 and all(row["passed"] for row in replay),
        "computed_before_optimizer_step": True,
        "optimizer_steps": completed_steps,
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
    core.write_x(output / "GRADIENT_REPLAY_CHECK.json", receipt)
    core.write_x(output / "CAPTURE.json", captures)
    if not receipt["all128_passed"]:
        optimizer.zero_grad(set_to_none=True)
        return {**stopped, "status": "NO_UPDATE_GRADIENT_REPLAY_FAILED", "gradient_replay": receipt}
    if not any(advantages):
        return {**stopped, "status": "NO_UPDATE_ZERO_ADVANTAGE", "gradient_replay": receipt}
    gradient = float(
        torch.nn.utils.clip_grad_norm_(
            [value for _, value in parameters], 1, error_if_nonfinite=True
        ).cpu()
    )
    if not math.isfinite(gradient) or gradient <= 0:
        return {**stopped, "status": "NO_UPDATE_ZERO_GRADIENT", "gradient_replay": receipt}
    core.write_x(
        output / "OPTIMIZER_INTENT.json",
        {
            "previous_steps": completed_steps,
            "intended_steps": completed_steps + 1,
            "all128_replay_passed": True,
        },
    )
    optimizer.step()
    if torch.cuda.is_available():
        torch.cuda.synchronize()
    core.write_x(output / "OPTIMIZER_STEP.json", {"completed_steps": completed_steps + 1})
    validate_optimizer(model, optimizer, completed_steps + 1)
    delta = math.sqrt(
        sum(
            float((value.detach().cpu() - before[name]).double().square().sum())
            for name, value in parameters
        )
    )
    if not math.isfinite(delta) or delta <= 0:
        raise ValueError("adapter failed to change after the optimizer step")
    return {
        "status": "UPDATED",
        "optimizer_steps": completed_steps + 1,
        "optimizer_steps_this_stage": 1,
        "optimizer_state_steps": optimizer_steps(optimizer),
        "gradient_norm_before_clip": gradient,
        "adapter_delta_l2": delta,
        "gradient_replay": receipt,
        "batch_denominator": 128,
        "mixed_reward_groups": sum(
            len({row["reward"] for row in records if row["group_id"] == group}) > 1
            for group in {row["group_id"] for row in records}
        ),
    }
