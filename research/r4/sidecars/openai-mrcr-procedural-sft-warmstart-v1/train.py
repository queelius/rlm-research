"""One fixed four-update procedural SFT dose. MAIN alone may launch this on one GPU."""

from __future__ import annotations

import argparse
import json
import math
import os
from pathlib import Path
import random
import time
import traceback

import training


ROOT = Path(__file__).resolve().parent
READY = ROOT / "READY_TRAINING.json"
CORPUS = ROOT / "TEACHER_CORPUS_V2.json"
BASE_MANIFEST = training.BASE / "local-research-manifest.json"


def read(path: Path):
    return json.loads(Path(path).read_text())


def verify() -> dict:
    ready = read(READY)
    if ready.get("identity") != training.digest(
        {key: value for key, value in ready.items() if key != "identity"}
    ):
        raise ValueError("training READY identity changed")
    for path, expected in ready.get("closure_sha256", {}).items():
        if training.sha(Path(path)) != expected:
            raise ValueError("training closure changed: " + path)
    corpus = read(CORPUS)
    if training.validate_corpus(corpus) != ready["corpus"]:
        raise ValueError("teacher corpus contract changed")
    return ready


def eval_binding(checkpoint: Path, ready: dict, step: int) -> dict:
    return {
        "schema": "openai-mrcr-procedural-sft-root-only-binding-v1",
        "policy_alias": f"Qwen3-4B-Instruct-2507-mrcr-procedural-sft-step{step}",
        "root": {
            "base_model": str(training.BASE),
            "base_manifest_sha256": training.sha(BASE_MANIFEST),
            "adapter": str(checkpoint),
            "adapter_model_sha256": training.sha(checkpoint / "adapter_model.safetensors"),
            "adapter_config_sha256": training.sha(checkpoint / "adapter_config.json"),
        },
        "child": {
            "base_model": str(training.BASE),
            "base_manifest_sha256": training.sha(BASE_MANIFEST),
            "adapter": None,
        },
        "root_only_update": True,
        "step": step,
        "fixed_primary_step": 4,
        "training_ready_identity": ready["identity"],
    }


def save_checkpoint(model, optimizer, output: Path, state: dict, ready: dict) -> dict:
    import torch

    checkpoint = output / f"checkpoint-{state['step']:04d}"
    checkpoint.mkdir(parents=False, exist_ok=False)
    model.save_pretrained(checkpoint, safe_serialization=True)
    torch.save(optimizer.state_dict(), checkpoint / "optimizer.pt")
    torch.save(
        {
            "python": random.getstate(),
            "numpy": __import__("numpy").random.get_state(),
            "torch_cpu": torch.get_rng_state(),
            "torch_cuda": torch.cuda.get_rng_state_all(),
        },
        checkpoint / "rng.pt",
    )
    training.write_x(
        checkpoint / "EVAL_BINDING.json", eval_binding(checkpoint, ready, state["step"])
    )
    return training.commit_checkpoint(checkpoint, state)


def run(output: Path, seconds: int) -> dict:
    ready = verify()
    started = time.monotonic()
    deadline = started + seconds
    import numpy as np
    import torch
    from peft import LoraConfig, get_peft_model
    from transformers import AutoModelForCausalLM

    if (
        not os.environ.get("CUDA_VISIBLE_DEVICES")
        or not torch.cuda.is_available()
        or torch.cuda.device_count() != 1
    ):
        raise ValueError("MAIN must assign exactly one GPU")
    output = output.resolve()
    output.mkdir(parents=True, exist_ok=False)
    completed = 0
    training.write_x(
        output / "RUN.json",
        {
            "schema": "openai-mrcr-procedural-sft-run-v1",
            "ready_identity": ready["identity"],
            "ready_sha256": training.sha(READY),
            "corpus_sha256": training.sha(CORPUS),
            "recipe": training.recipe(),
            "started_epoch": time.time(),
            "deadline_seconds": seconds,
            "gpu_authority": "MAIN",
        },
    )
    try:
        manifest = read(BASE_MANIFEST)
        for filename, expected in manifest["files"].items():
            if training.sha(training.BASE / filename) != expected:
                raise ValueError("base model file changed: " + filename)
        recipe = training.recipe()
        seed = recipe["seed"]
        random.seed(seed)
        np.random.seed(seed)
        torch.manual_seed(seed)
        torch.cuda.manual_seed_all(seed)
        base = AutoModelForCausalLM.from_pretrained(
            training.BASE,
            local_files_only=True,
            dtype=torch.bfloat16,
            attn_implementation="sdpa",
            device_map={"": "cuda:0"},
        )
        base.config.use_cache = False
        adapter = recipe["adapter"]
        model = get_peft_model(
            base,
            LoraConfig(
                r=adapter["rank"],
                lora_alpha=adapter["alpha"],
                target_modules=adapter["target_modules"],
                lora_dropout=adapter["dropout"],
                bias=adapter["bias"],
                task_type="CAUSAL_LM",
            ),
            autocast_adapter_dtype=True,
        )
        model.train()
        model.gradient_checkpointing_enable(gradient_checkpointing_kwargs={"use_reentrant": False})
        model.enable_input_require_grads()
        params = [parameter for parameter in model.parameters() if parameter.requires_grad]
        named = [(name, parameter) for name, parameter in model.named_parameters() if parameter.requires_grad]
        if len(params) != 504 or [id(parameter) for _, parameter in named] != [
            id(parameter) for parameter in params
        ]:
            raise ValueError("expected exact504 rank8 Qwen3 LoRA parameters")
        if any(parameter.dtype != torch.float32 for parameter in params):
            raise ValueError("all trainable LoRA parameters must be FP32")
        if any("lora_" not in name for name, _ in named):
            raise ValueError("non-LoRA parameter is trainable")
        optimizer = torch.optim.AdamW(
            params, lr=recipe["learning_rate"], weight_decay=recipe["weight_decay"]
        )
        if optimizer.state:
            raise ValueError("optimizer is not fresh")
        initial = [parameter.detach().cpu().clone() for parameter in params]
        corpus = read(CORPUS)
        episodes = corpus["episodes"]
        objective = training.learning()
        previous_commit_sha256 = None
        metrics = []
        for step in range(1, recipe["updates"] + 1):
            order = list(range(32))
            random.Random(seed + step - 1).shuffle(order)
            metric = objective.update(
                model,
                optimizer,
                [episodes[index] for index in order],
                "cuda:0",
                deadline=deadline,
                terminal_weight=recipe["terminal_weight"],
            )
            completed = step
            optimizer_steps = {int(value["step"]) for value in optimizer.state.values()}
            if optimizer_steps != {step}:
                raise ValueError("Adam step count mismatch")
            delta = math.sqrt(
                sum(
                    float((parameter.detach().cpu() - before).square().sum())
                    for parameter, before in zip(params, initial, strict=True)
                )
            )
            if not math.isfinite(delta) or delta <= 0:
                raise ValueError("adapter did not change finitely")
            metric.update(
                step=step,
                example_order=[episodes[index]["episode_id"] for index in order],
                delta_l2_from_start=delta,
            )
            state = {
                "schema": "openai-mrcr-procedural-sft-state-v1",
                "step": step,
                "optimizer_steps": step,
                "selection": recipe["selection"],
                "ready_identity": ready["identity"],
                "corpus_sha256": training.sha(CORPUS),
                "base_manifest_sha256": training.sha(BASE_MANIFEST),
                "previous_step_commit_sha256": previous_commit_sha256,
                "metric": metric,
                "elapsed_training_seconds": time.monotonic() - started,
            }
            commit = save_checkpoint(model, optimizer, output, state, ready)
            previous_commit_sha256 = training.sha(
                output / f"checkpoint-{step:04d}/STEP_COMMIT.json"
            )
            metrics.append(metric)
            print(
                json.dumps(
                    {
                        "step": step,
                        "weighted_ce": metric["weighted_ce"],
                        "gradient_norm": metric["gradient_norm"],
                        "delta_l2_from_start": delta,
                        "commit_identity": commit["identity"],
                    },
                    sort_keys=True,
                ),
                flush=True,
            )
        result = training.result_for(output)
        result.update(
            {
                "ready_identity": ready["identity"],
                "corpus_sha256": training.sha(CORPUS),
                "elapsed_training_seconds": time.monotonic() - started,
                "peak_memory_allocated": torch.cuda.max_memory_allocated(),
                "root_action_target_exposures": 4 * ready["corpus"]["root_action_target_tokens"],
                "terminal_target_exposures": 4 * ready["corpus"]["terminal_target_tokens"],
                "terminal_objective_weight": recipe["terminal_weight"],
                "child_loaded": False,
                "child_updated": False,
                "metrics": metrics,
            }
        )
        training.write_x(output / "RESULT.json", result)
        return result
    except BaseException as error:
        training.write_x(
            output / "FAILURE.json",
            {
                "type": type(error).__name__,
                "message": str(error),
                "traceback": traceback.format_exc(),
                "completed_optimizer_steps": completed,
                "elapsed_seconds": time.monotonic() - started,
                "no_retry": True,
            },
        )
        raise


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("command", choices=("verify", "run"))
    parser.add_argument("--output", type=Path, default=ROOT / "outputs/attempt-001")
    parser.add_argument("--seconds", type=int, default=600)
    args = parser.parse_args()
    if args.command == "verify":
        print(verify()["identity"])
    else:
        value = run(args.output, args.seconds)
        print(json.dumps(value, sort_keys=True))
