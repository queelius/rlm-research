"""Continue the exact authored objective from authenticated checkpoint4 through step32."""

from __future__ import annotations

import argparse
import json
import math
import os
from pathlib import Path
import random
import signal
import time
import traceback

import resume
import study


ORIGINAL_EVAL_BINDING = study.original_train.eval_binding


def eval_binding(checkpoint: Path, ready: dict, step: int) -> dict:
    value = ORIGINAL_EVAL_BINDING(checkpoint, ready, step)
    value["fixed_primary_step"] = study.LAST_STEP
    value["resume_parent_checkpoint"] = str(study.PARENT)
    value["resume_parent_step_commit_sha256"] = study.PARENT_COMMIT_SHA
    return value


def save_checkpoint(model, optimizer, output: Path, state: dict, ready: dict) -> dict:
    original = study.original_train.eval_binding
    study.original_train.eval_binding = eval_binding
    try:
        return study.original_train.save_checkpoint(model, optimizer, output, state, ready)
    finally:
        study.original_train.eval_binding = original


def run(output: Path, seconds: int) -> dict:
    if output.resolve() != study.OUTPUT.resolve() or output.exists() or seconds != study.OWNER_SECONDS:
        raise ValueError("exact unused output and 1500-second owner cap required")
    ready = study.verify()
    import torch
    from peft import PeftModel
    from transformers import AutoModelForCausalLM

    if not os.environ.get("CUDA_VISIBLE_DEVICES") or torch.cuda.device_count() != 1:
        raise ValueError("MAIN must assign exactly one GPU")
    output.mkdir(parents=True)
    started = time.monotonic()
    deadline = started + seconds
    completed, committed_steps = 4, []
    previous_handler = signal.signal(
        signal.SIGALRM,
        lambda *_: (_ for _ in ()).throw(TimeoutError("1500-second continuation owner cap")),
    )
    signal.setitimer(signal.ITIMER_REAL, seconds)
    study.write_x(output / "RUN.json", {
        "schema": "openai-mrcr-procedural-sft-continue32-run-v1",
        "ready_identity": ready["identity"], "ready_sha256": study.sha(study.READY),
        "corpus_sha256": study.CORPUS_SHA, "recipe": study.recipe(),
        "resume_parent_checkpoint": str(study.PARENT),
        "resume_parent_step_commit_sha256": study.PARENT_COMMIT_SHA,
        "started_epoch": time.time(), "deadline_seconds": seconds,
        "heldout_queries": 0, "generation_calls": 0, "gpu_authority": "MAIN",
    })
    try:
        torch.set_num_threads(4)
        base = AutoModelForCausalLM.from_pretrained(
            study.BASE, local_files_only=True, dtype=torch.bfloat16,
            attn_implementation="sdpa", device_map={"": "cuda:0"},
        )
        base.config.use_cache = False
        model = PeftModel.from_pretrained(
            base, study.PARENT, is_trainable=True, autocast_adapter_dtype=True,
        )
        model.train()
        model.gradient_checkpointing_enable(gradient_checkpointing_kwargs={"use_reentrant": False})
        model.enable_input_require_grads()
        optimizer, restored = resume.restore_state(model, study.PARENT)
        if restored["restored_step"] != 4:
            raise ValueError("continuation did not restore absolute Adam step4")
        study.write_x(output / "RESTORED_STATE.json", restored)
        restored_sha = study.sha(output / "RESTORED_STATE.json")
        parameters = [p for p in model.parameters() if p.requires_grad]
        initial = [p.detach().cpu().clone() for p in parameters]
        episodes = study.read(study.CORPUS)["episodes"]
        recipe = study.recipe()
        objective = study.training.learning()
        previous_commit_sha256 = study.PARENT_COMMIT_SHA
        metrics = []
        for step in range(study.FIRST_STEP, study.LAST_STEP + 1):
            order = list(range(32))
            random.Random(recipe["seed"] + step - 1).shuffle(order)
            metric = objective.update(
                model, optimizer, [episodes[index] for index in order], "cuda:0",
                deadline=deadline, terminal_weight=recipe["terminal_weight"],
            )
            completed = step
            if {int(value["step"]) for value in optimizer.state.values()} != {step}:
                raise ValueError("resumed Adam absolute step count mismatch")
            delta = math.sqrt(sum(
                float((p.detach().cpu() - before).double().square().sum())
                for p, before in zip(parameters, initial, strict=True)
            ))
            if not math.isfinite(delta) or delta <= 0:
                raise ValueError("resumed adapter did not change finitely")
            metric.update(
                step=step, example_order=[episodes[index]["episode_id"] for index in order],
                delta_l2_from_resume_checkpoint4=delta,
            )
            state = {
                "schema": "openai-mrcr-procedural-sft-state-v1",
                "step": step, "optimizer_steps": step,
                "additional_optimizer_steps": step - 4,
                "selection": recipe["selection"], "ready_identity": ready["identity"],
                "corpus_sha256": study.CORPUS_SHA,
                "base_manifest_sha256": ready["base_manifest_sha256"],
                "previous_step_commit_sha256": previous_commit_sha256,
                "resume_parent_checkpoint": str(study.PARENT),
                "resume_parent_step_commit_sha256": study.PARENT_COMMIT_SHA,
                "restored_state_sha256": restored_sha,
                "metric": metric, "elapsed_training_seconds": time.monotonic() - started,
            }
            commit = save_checkpoint(model, optimizer, output, state, ready)
            path = output / f"checkpoint-{step:04d}/STEP_COMMIT.json"
            previous_commit_sha256 = study.sha(path)
            committed_steps.append({"path": str(path), "sha256": previous_commit_sha256, "identity": commit["identity"]})
            metrics.append(metric)
            print(json.dumps({
                "step": step, "weighted_ce": metric["weighted_ce"],
                "action_objective": metric["action_objective"],
                "gradient_norm": metric["gradient_norm"],
                "delta_l2_from_resume_checkpoint4": delta, "step_commit_sha256": previous_commit_sha256,
            }, sort_keys=True), flush=True)
        primary = output / "checkpoint-0032"
        result = {
            "schema": "openai-mrcr-procedural-sft-continue32-result-v1",
            "status": "COMPLETED_32_TOTAL_UPDATES", "optimizer_steps": 32,
            "additional_optimizer_steps": 28, "selection": recipe["selection"],
            "primary_checkpoint": str(primary), "evaluation_binding": str(primary / "EVAL_BINDING.json"),
            "step_commits": committed_steps,
            "resume_parent_checkpoint": str(study.PARENT),
            "resume_parent_step_commit_sha256": study.PARENT_COMMIT_SHA,
            "restored_state_sha256": restored_sha,
            "ready_identity": ready["identity"], "corpus_sha256": study.CORPUS_SHA,
            "elapsed_training_seconds": time.monotonic() - started,
            "root_action_target_exposures_additional": 28 * ready["corpus"]["root_action_target_tokens"],
            "terminal_target_exposures_additional": 28 * ready["corpus"]["terminal_target_tokens"],
            "terminal_objective_weight": recipe["terminal_weight"],
            "child_loaded": False, "child_updated": False, "heldout_queries": 0,
            "generation_calls": 0, "metrics": metrics,
            "peak_memory_allocated": torch.cuda.max_memory_allocated(),
        }
        study.write_x(output / "RESULT.json", result)
        return result
    except BaseException as error:
        study.write_x(output / "FAILURE.json", {
            "type": type(error).__name__, "message": str(error),
            "traceback": traceback.format_exc(), "completed_optimizer_steps": completed,
            "committed_step_files": committed_steps,
            "elapsed_seconds": time.monotonic() - started, "no_retry": True,
        })
        raise
    finally:
        signal.setitimer(signal.ITIMER_REAL, 0)
        signal.signal(signal.SIGALRM, previous_handler)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("command", choices=("verify", "plan", "run"))
    parser.add_argument("--output", type=Path, default=study.OUTPUT)
    parser.add_argument("--seconds", type=int, default=study.OWNER_SECONDS)
    args = parser.parse_args()
    if args.command == "verify":
        value = {"identity": study.verify()["identity"]}
    elif args.command == "plan":
        value = study.plan()
    else:
        value = run(args.output, args.seconds)
    print(json.dumps(value, sort_keys=True))
