"""Four true-HF updates over four disjoint balanced AG News steps."""

import argparse
import importlib.util
import json
import os
from pathlib import Path
import random
import signal
import sys
import time

import numpy as np
import torch

import ag_runtime
import config


def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    previous = sys.modules.get(name)
    sys.modules[name] = module
    try:
        spec.loader.exec_module(module)
    finally:
        if previous is None:
            sys.modules.pop(name, None)
        else:
            sys.modules[name] = previous
    return module


# Preserve the proven implementation while binding its ordinary module imports to
# this sidecar's settings. No reference source is edited.
sys.modules["config"] = config
core = load("core", config.REFERENCE / "core.py")
sys.modules["core"] = core
rng_receipts = load("rng_receipts", config.REFERENCE / "rng_receipts.py")
sys.modules["rng_receipts"] = rng_receipts
reference = load("ag_reference_train_four", config.REFERENCE / "train_four.py")
core.v1.CATEGORIES = config.AG_VALUES
core.v1.local_reward = ag_runtime.local_reward


def verify_ready():
    ready = core.read(config.ROOT / "READY.json")
    if ready.get("status") != "CPU_READY_MAIN_REVIEW_REQUIRED_CONDITIONAL_ADMISSION":
        raise ValueError("unexpected AG training READY status")
    for raw, expected in ready["closure_sha256"].items():
        if core.sha(Path(raw)) != expected:
            raise ValueError("sealed AG source changed: " + raw)
    if core.v1.SAMPLES != config.DENOMINATOR or core.v1.BATCH != config.BATCH:
        raise ValueError("proven loss dimensions differ")
    return ready


def run(output: Path, cap_seconds: int):
    from peft import PeftModel
    from transformers import AutoModelForCausalLM, AutoTokenizer

    ready = verify_ready()
    if output != config.ROOT / "outputs/attempt-001" or output.exists():
        raise ValueError("exact unused attempt-001 required")
    if cap_seconds != config.CAP:
        raise ValueError("exact 4200-second cap required")
    if not os.environ.get("CUDA_VISIBLE_DEVICES") or not torch.cuda.is_available() or torch.cuda.device_count() != 1:
        raise ValueError("MAIN must assign exactly one GPU")
    steps = ag_runtime.load_training_inputs()
    gold = core.read(config.ROOT / "inputs/TRAIN_GOLD.json")
    all_ids = {row["group_id"] for groups in steps for row in groups}
    if set(gold) != all_ids or len(all_ids) != 128:
        raise ValueError("AG step/gold inventory differs")
    output.mkdir(parents=True)
    started = time.monotonic()
    core.write(output / "START.json", {
        "ready_identity": ready["identity"], "started_epoch": time.time(),
        "cap_seconds": config.CAP, "pid": os.getpid(),
        "starting_child_adapter_sha256": config.CHILD_SHA,
        "requested_updates": 4, "primary_checkpoint_step": 4,
        "training_dataset": "AG News train", "unique_training_records": 128,
        "step_inventories_disjoint": True,
    })

    def stop(sig, _frame):
        raise TimeoutError("AG four-step pilot interrupted by signal " + str(sig))

    old_handlers = {sig: signal.signal(sig, stop) for sig in (signal.SIGALRM, signal.SIGTERM, signal.SIGINT)}
    signal.setitimer(signal.ITIMER_REAL, config.CAP)
    completed, checkpoints, optimizer, model = 0, [], None, None
    try:
        random.seed(config.GLOBAL_SEED)
        np.random.seed(config.GLOBAL_SEED % 2**32)
        torch.manual_seed(config.GLOBAL_SEED)
        torch.cuda.manual_seed_all(config.GLOBAL_SEED)
        torch.set_num_threads(4)
        torch.backends.cuda.matmul.allow_tf32 = False
        torch.backends.cudnn.allow_tf32 = False
        torch.backends.cudnn.benchmark = False
        torch.cuda.reset_peak_memory_stats()
        sampler = torch.Generator(device="cuda:0").manual_seed(config.SAMPLER_SEED)
        tokenizer = AutoTokenizer.from_pretrained(config.BASE, local_files_only=True)
        base = AutoModelForCausalLM.from_pretrained(
            config.BASE, local_files_only=True, dtype=torch.bfloat16,
            attn_implementation="eager", device_map={"": "cuda:0"},
        )
        model = PeftModel.from_pretrained(base, config.CHILD, is_trainable=True, autocast_adapter_dtype=True)
        model.eval(); model.config.use_cache = False; model.gradient_checkpointing_disable()
        layers = core.install_eval_checkpoints(model)
        if core.sha(config.CHILD / "adapter_model.safetensors") != config.CHILD_SHA:
            raise ValueError("original c32 identity changed")
        initial = reference.parameter_snapshot(model)
        optimizer = torch.optim.AdamW(
            [parameter for _, parameter in reference.trainable_parameters(model)],
            lr=config.LR, weight_decay=0,
        )
        parent_identity, parent_commit = config.CHILD_SHA, None
        core.write(output / "ACTIVATION_STORAGE.json", {
            "decoder_layers": layers, "model_training": model.training,
            "builtin_gradient_checkpointing": model.is_gradient_checkpointing,
            "use_cache": model.config.use_cache, "batch_size": config.BATCH,
            "base_dtype": "bfloat16", "trainable_dtype": "float32",
        })
        with ((output / "GRAMMAR.stderr.log").open("w") as log, core.v1.GrammarClient(stderr=log) as worker):
            for step_number, groups in enumerate(steps, 1):
                result = reference.execute_update(
                    model, optimizer, worker, tokenizer, groups, gold, sampler, step_number,
                    output / "updates" / f"update-{step_number:04d}", parent_identity,
                    ready["identity"],
                )
                core.write(output / "updates" / f"update-{step_number:04d}" / "RESULT.json", result)
                if result["status"] != "UPDATED":
                    final = {
                        "status": result["status"], "completed_optimizer_steps": completed,
                        "current_step_applied": result["optimizer_step_applied"],
                        "primary_checkpoint_available": False, "checkpoints": checkpoints,
                        "elapsed_seconds": time.monotonic() - started,
                    }
                    core.write(output / "RESULT.json", final)
                    return final
                checkpoint, _ = reference.save_checkpoint(
                    model, optimizer, sampler, output, step_number, result, parent_identity,
                    parent_commit, ready["identity"], initial, started,
                )
                completed = step_number
                parent_commit = {"path": str(checkpoint / "STEP_COMMIT.json"), "sha256": core.sha(checkpoint / "STEP_COMMIT.json")}
                parent_identity = core.sha(checkpoint / "state.json")
                checkpoints.append({"step": step_number, "checkpoint": str(checkpoint), "state_sha256": parent_identity, "step_commit": parent_commit})
        final = {
            "status": "COMPLETED_FOUR_UPDATES", "completed_optimizer_steps": completed,
            "primary_checkpoint_available": True, "primary_checkpoint_step": 4,
            "primary_checkpoint": checkpoints[-1]["checkpoint"], "checkpoints": checkpoints,
            "elapsed_seconds": time.monotonic() - started,
            "peak_allocated_bytes": torch.cuda.max_memory_allocated(),
            "peak_reserved_bytes": torch.cuda.max_memory_reserved(),
        }
        core.write(output / "RESULT.json", final)
        return final
    except BaseException as error:
        steps_seen = sorted({int(value["step"]) for value in optimizer.state.values()}) if optimizer else []
        failure = {
            "status": "STOP_FAILED", "completed_optimizer_steps": completed,
            "observed_optimizer_state_steps": steps_seen, "primary_checkpoint_available": False,
            "checkpoints": checkpoints, "error_type": type(error).__name__, "error": str(error),
            "elapsed_seconds": time.monotonic() - started,
        }
        core.write(output / "FAILURE.json", failure); core.write(output / "RESULT.json", failure)
        raise
    finally:
        signal.setitimer(signal.ITIMER_REAL, 0)
        for sig, handler in old_handlers.items(): signal.signal(sig, handler)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--cap-seconds", type=int, required=True)
    args = parser.parse_args()
    print(json.dumps(run(args.output, args.cap_seconds), sort_keys=True))
