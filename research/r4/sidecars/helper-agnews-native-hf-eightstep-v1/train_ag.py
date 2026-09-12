"""One HF load for this step, carrying authenticated Adam/RNG from its parent."""

import os
import random
import time
from pathlib import Path

import core
import numpy as np
import torch
import train_step


def main():
    from peft import PeftModel
    from transformers import AutoModelForCausalLM

    if not os.environ.get("CUDA_VISIBLE_DEVICES") or torch.cuda.device_count() != 1:
        raise ValueError("MAIN must provide exactly one GPU")
    step = int(os.environ["RLM_AG_EIGHT_STEP"])
    view = core.step_view(step)
    ready = core.verify()
    parent_receipt = core.read(core.ATTEMPT / f"parent-inputs/step-{step:03d}.json")
    if parent_receipt["parent_policy"] != view.PARENT:
        raise ValueError("precollection parent receipt differs")
    if core.read(view.ATTEMPT / "service/BINDING.json") != view.binding():
        raise ValueError("actual native served binding differs from exact HF parent")
    source = core.numeric_source(view)
    load_inputs = core.patched_function(
        source,
        "load_inputs",
        [('dataset["c32_adapter_sha256"]', 'dataset["parent_adapter_sha256"]')],
    )
    records, masks = load_inputs()
    dataset = core.read(view.ATTEMPT / "qualification-inputs/DATASET.json")
    if dataset["parent_policy"] != view.PARENT or dataset["step"] != step:
        raise ValueError("prepared actions carry another parent policy")
    started = time.monotonic()
    torch.set_num_threads(4)
    torch.cuda.reset_peak_memory_stats()
    if step == 1:
        random.seed(view.SEED)
        np.random.seed(view.SEED % (2**32))
        torch.manual_seed(view.SEED)
        torch.cuda.manual_seed_all(view.SEED)
    core.write_x(
        view.ATTEMPT / "HF_START.json",
        {
            "started_epoch": time.time(),
            "step": step,
            "parent_policy": view.PARENT,
            "ready_identity": ready["identity"],
            "single_hf_model_load_this_step": True,
            "optimizer_steps": step - 1,
            "rng_restored_after_construction": step > 1,
        },
    )
    base = AutoModelForCausalLM.from_pretrained(
        core.original.BASE_MODEL,
        local_files_only=True,
        dtype=torch.bfloat16,
        attn_implementation="sdpa",
        device_map={"": "cuda:0"},
    )
    model = PeftModel.from_pretrained(
        base, view.CHILD_START, is_trainable=True, autocast_adapter_dtype=True
    )
    optimizer = train_step.make_optimizer(model)
    if step > 1:
        train_step.restore_training_state(model, optimizer, view.CHILD_START, step - 1)
    core.write_x(
        view.ATTEMPT / "PRESTEP_OPTIMIZER.json",
        {
            "completed_steps": step - 1,
            "state_steps": train_step.optimizer_steps(optimizer),
            "parameter_layout": train_step.optimizer_layout(model),
            "parent_optimizer_sha256": view.PARENT.get("optimizer_sha256"),
            "parent_rng_sha256": view.PARENT.get("rng_sha256"),
            "fresh_optimizer": step == 1,
        },
    )
    result = train_step.update_once(model, optimizer, records, masks, view.ATTEMPT, step - 1)
    result.update(
        step=step,
        ready_identity=ready["identity"],
        elapsed_seconds=time.monotonic() - started,
        peak_allocated_bytes=torch.cuda.max_memory_allocated(),
        peak_reserved_bytes=torch.cuda.max_memory_reserved(),
    )
    if result["status"] == "UPDATED":
        checkpoint = view.ATTEMPT / f"checkpoint-{step:04d}"
        train_step.save_training_state(model, optimizer, checkpoint, step)
        state = {key: value for key, value in result.items() if key != "gradient_replay"}
        state.update(
            schema="agnews-eightstep-checkpoint-v1",
            parent_policy=view.PARENT,
            source_c32_adapter_sha256=core.original.CHILD_SHA,
            training_data_manifest_sha256=core.sha(core.DATA / "inputs/MANIFEST.json"),
            objective=ready["policy"],
            single_hf_model_load_this_step=True,
            qualification_sha256=core.sha(view.ATTEMPT / "PRESTEP_QUALIFICATION.json"),
            gradient_replay_sha256=core.sha(view.ATTEMPT / "GRADIENT_REPLAY_CHECK.json"),
            collection_sha256=core.sha(view.ATTEMPT / "COLLECTION.json"),
            dataset_sha256=core.sha(view.ATTEMPT / "qualification-inputs/DATASET.json"),
            files_sha256={
                name: core.sha(checkpoint / name)
                for name in (
                    "adapter_model.safetensors",
                    "adapter_config.json",
                    "optimizer.pt",
                    "rng_state.pt",
                    "OPTIMIZER_LAYOUT.json",
                )
            },
        )
        core.write_x(checkpoint / "state.json", state)
        endpoint_parent = {
            "step": step,
            "checkpoint": str(checkpoint),
            "adapter_sha256": core.sha(checkpoint / "adapter_model.safetensors"),
            "config_sha256": core.sha(checkpoint / "adapter_config.json"),
            "state_sha256": core.sha(checkpoint / "state.json"),
            "source_c32_adapter_sha256": core.original.CHILD_SHA,
            "optimizer_steps": step,
        }
        core.write_x(checkpoint / "EVAL_BINDING.json", core.binding_from_parent(endpoint_parent))
        files = list(checkpoint.iterdir()) + [
            view.ATTEMPT / name
            for name in (
                "PRESTEP_QUALIFICATION.json",
                "GRADIENT_REPLAY_CHECK.json",
                "COLLECTION.json",
                "PREPARED.json",
                "CAPTURE.json",
                "ENGINE_ATTESTATION.json",
                "PRESTEP_OPTIMIZER.json",
                "OPTIMIZER_INTENT.json",
                "OPTIMIZER_STEP.json",
                "service/BINDING.json",
                "service/SERVICE_STOPPED.json",
                "qualification-inputs/DATASET.json",
                "qualification-inputs/MASKS.npz",
                "qualification-inputs/MASK_MANIFEST.json",
            )
        ]
        files.append(core.ATTEMPT / f"parent-inputs/step-{step:03d}.json")
        for row in records:
            files.extend(Path(row[key]) for key in ("raw_request_path", "raw_response_path"))
        core.write_x(
            checkpoint / "STEP_COMMIT.json",
            {
                "schema": "agnews-eightstep-commit-v1",
                "status": "UPDATED",
                "step": step,
                "optimizer_steps": step,
                "ready_identity": ready["identity"],
                "parent_step_commit_sha256": view.PARENT["step_commit_sha256"],
                "files_sha256": {str(path): core.sha(path) for path in sorted(set(files))},
            },
        )
        result.update(
            checkpoint=str(checkpoint),
            state_sha256=core.sha(checkpoint / "state.json"),
            step_commit_sha256=core.sha(checkpoint / "STEP_COMMIT.json"),
        )
    core.write_x(view.ATTEMPT / "RESULT.json", result)
    print({key: value for key, value in result.items() if key != "gradient_replay"})


if __name__ == "__main__":
    main()
