"""Two matched fixed-24 continuation jobs from c32 with fresh Adam/RNG."""

import argparse
import importlib.metadata
import os
import platform
import random
import tempfile
import time
from pathlib import Path

import prepare
import study as s


def environment_metadata(torch):
    """Record the actual training runtime without requiring a GPU during CPU qualification."""
    def version(distribution):
        try:
            return importlib.metadata.version(distribution)
        except importlib.metadata.PackageNotFoundError:
            return None

    available = torch.cuda.is_available()
    return {
        "python": platform.python_version(),
        "torch": torch.__version__,
        "transformers": version("transformers"),
        "peft": version("peft"),
        "cuda": torch.version.cuda,
        "cuda_available": available,
        "device": torch.cuda.get_device_name(0) if available else None,
        "cuda_visible_devices": os.environ.get("CUDA_VISIBLE_DEVICES"),
    }


def fixed_selection(state):
    if state.get("step") != 24 or state.get("complete") is not True:
        raise ValueError("fixed endpoint requires true completed update24")
    return {
        "rule": "fixed true completed update24; no best/validation selection",
        "step": 24,
        "checkpoint": state.get("checkpoint"),
    }


def save_checkpoint(model, optimizer, output, state):
    import torch

    destination = output / f"checkpoint-{state['step']:04d}"
    if destination.exists():
        raise ValueError("checkpoint exists")
    staging = Path(tempfile.mkdtemp(prefix=f".checkpoint-{state['step']:04d}-", dir=output))
    model.save_pretrained(staging, safe_serialization=True)
    torch.save(optimizer.state_dict(), staging / "optimizer.pt")
    torch.save(
        {
            "torch": torch.get_rng_state(),
            "cuda": torch.cuda.get_rng_state_all(),
            "python": random.getstate(),
        },
        staging / "rng_state.pt",
    )
    state = {
        **state,
        "files_sha256": {path.name: s.sha(path) for path in staging.iterdir() if path.is_file()},
    }
    s.write(staging / "state.json", state)
    staging.rename(destination)
    return destination


def loss_sum(logits, labels):
    import torch.nn.functional as functional

    shifted = labels[:, 1:].contiguous()
    count = int((shifted != -100).sum())
    if not count:
        raise ValueError("zero supervised tokens")
    loss = functional.cross_entropy(
        logits[:, :-1].float().reshape(-1, logits.shape[-1]),
        shifted.reshape(-1),
        ignore_index=-100,
        reduction="sum",
    )
    return loss, count


def run_arm(arm, rows, output, deadline):
    import torch
    from peft import PeftModel
    from transformers import AutoModelForCausalLM

    recipe = s.recipe()
    if arm not in recipe["arms"] or len(rows) != 96:
        raise ValueError("exact arm/96 contexts required")
    output.mkdir(parents=True, exist_ok=False)
    seed = recipe["train_seed"]
    random.seed(seed)
    torch.manual_seed(seed)
    torch.cuda.manual_seed_all(seed)
    base = AutoModelForCausalLM.from_pretrained(
        s.BASE,
        local_files_only=True,
        dtype=torch.bfloat16,
        attn_implementation="sdpa",
        device_map={"": "cuda:0"},
    )
    model = PeftModel.from_pretrained(base, s.START, is_trainable=True, autocast_adapter_dtype=True)
    params = [parameter for parameter in model.parameters() if parameter.requires_grad]
    names = [name for name, parameter in model.named_parameters() if parameter.requires_grad]
    if (
        not params
        or any("lora_" not in name for name in names)
        or any(parameter.dtype != torch.float32 for parameter in params)
    ):
        raise ValueError("only FP32 c32 LoRA parameters may train")
    optimizer = torch.optim.AdamW(params, lr=recipe["lr"], weight_decay=0.0)
    if optimizer.state:
        raise ValueError("optimizer must be fresh")
    tokenizer = prepare.DATA.load_tokenizer()
    environment = environment_metadata(torch)
    s.write(
        output / "LOAD_AUDIT.json",
        {
            "start_adapter_sha256": s.C32_SHA,
            "environment": environment,
            "trainable_parameter_names": names,
            "trainable_parameters": sum(parameter.numel() for parameter in params),
            "optimizer": "fresh AdamW",
            "optimizer_state_initially_empty": True,
        },
    )
    model.train()
    model.config.use_cache = False
    model.gradient_checkpointing_enable(gradient_checkpointing_kwargs={"use_reentrant": False})
    model.enable_input_require_grads()
    metrics = []
    checkpoints = []
    started = time.monotonic()
    for step, cursor in enumerate(range(0, 96, 4), 1):
        if time.time() >= deadline:
            raise TimeoutError("training deadline before complete update")
        chunk = rows[cursor : cursor + 4]
        denominator = sum(row["target_tokens"] for row in chunk)
        optimizer.zero_grad(set_to_none=True)
        total = 0.0
        for row in chunk:
            batch = {
                key: value.to("cuda:0")
                for key, value in prepare.DATA.collate([row], tokenizer.pad_token_id).items()
            }
            labels = batch.pop("labels")
            result = model(**batch, use_cache=False)
            loss, _ = loss_sum(result.logits, labels)
            if not torch.isfinite(loss):
                raise ValueError("nonfinite SFT loss")
            (loss / denominator).backward()
            total += float(loss.detach())
        norm = torch.nn.utils.clip_grad_norm_(
            params, recipe["clip_grad_norm"], error_if_nonfinite=True
        )
        optimizer.step()
        torch.cuda.synchronize()
        metric = {
            "arm": arm,
            "step": step,
            "cursor": cursor + 4,
            "contexts": 4,
            "context_ids": [row["context_id"] for row in chunk],
            "target_tokens": denominator,
            "nll": total / denominator,
            "gradient_norm": float(norm),
            "peak_memory_allocated_bytes": torch.cuda.max_memory_allocated(),
            "elapsed_training_seconds": time.monotonic() - started,
        }
        metrics.append(metric)
        if step in recipe["checkpoint_steps"]:
            checkpoint = save_checkpoint(
                model,
                optimizer,
                output,
                {
                    "identity": s.verify()["identity"],
                    "arm": arm,
                    "step": step,
                    "cursor": cursor + 4,
                    "complete": step == 24,
                    "optimizer_origin": "fresh AdamW; c32 optimizer/RNG not restored",
                    "metric": metric,
                },
            )
            checkpoints.append(str(checkpoint))
            s.write(output / f"STEP-{step:02d}.json", {**metric, "checkpoint": str(checkpoint)})
    selected_path = output / "checkpoint-0024"
    selected = fixed_selection(
        {"step": 24, "complete": selected_path.is_dir(), "checkpoint": str(selected_path)}
    )
    selected.update(
        adapter_sha256=s.sha(selected_path / "adapter_model.safetensors"),
        config_sha256=s.sha(selected_path / "adapter_config.json"),
        state_sha256=s.sha(selected_path / "state.json"),
    )
    s.write(output / "SELECTION.json", selected)
    result = {
        "arm": arm,
        "complete": True,
        "steps": 24,
        "contexts": 96,
        "question_exposures": 1536,
        "target_tokens": sum(row["target_tokens"] for row in rows),
        "fresh_optimizer": True,
        "fresh_matched_rng_seed": seed,
        "selected": selected,
        "checkpoints": checkpoints,
        "training_seconds": time.monotonic() - started,
        "environment": environment,
        "peak_memory_allocated_bytes": torch.cuda.max_memory_allocated(),
    }
    s.write(output / "RESULT.json", result)
    del optimizer, model, base
    torch.cuda.empty_cache()
    return result


def run_all(output, deadline):
    if not os.environ.get("CUDA_VISIBLE_DEVICES"):
        raise ValueError("MAIN must assign one GPU")
    s.verify()
    rows = s.read(s.PREPARED / "TRAIN.json")
    output = Path(output)
    output.mkdir(parents=True, exist_ok=False)
    results = {arm: run_arm(arm, rows[arm], output / arm, deadline) for arm in ("full6", "abo")}
    s.write(output / "RESULT.json", {"complete": True, "arms": results})
    return results


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("command", choices=("verify", "run"))
    parser.add_argument("--output", type=Path, default=s.ATTEMPT / "training")
    parser.add_argument("--deadline", type=float, default=0)
    args = parser.parse_args()
    if args.command == "verify":
        print(s.verify()["identity"])
    else:
        print(run_all(args.output, args.deadline or time.time() + 2700))
