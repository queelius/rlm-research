"""GPU qualification: no optimizer construction or step."""
import argparse
import json
import math
import os
from pathlib import Path
import signal
import sys
import time

import sparse_math
import sparse_study as study

sys.path.insert(0, str(study.SOURCE))
import terminal_common as common  # noqa: E402
import terminal_train as original  # noqa: E402

TOLERANCE = {
    "max_action_logprob_absolute": 0.005,
    "loss_absolute": 0.002,
    "gradient_relative_l2": 0.01,
    "gradient_cosine_minimum": 0.99995,
}


def _grad_vector(model):
    import torch
    values = [p.grad.detach().float().reshape(-1).cpu() for name, p in model.named_parameters()
              if p.requires_grad and p.grad is not None]
    if not values:
        raise ValueError("missing LoRA gradients")
    return torch.cat(values)


def _prepare(model):
    import torch
    model.train()
    model.config.use_cache = False
    model.enable_input_require_grads()
    model.gradient_checkpointing_enable(gradient_checkpointing_kwargs={"use_reentrant": False})
    for module in model.modules():
        if isinstance(module, torch.nn.Dropout):
            module.eval()
    trainable = [(name, p) for name, p in model.named_parameters() if p.requires_grad]
    if any("lora_" not in name or p.dtype != torch.float32 for name, p in trainable):
        raise ValueError("qualification must use only FP32 LoRA")


def run(args):
    import torch
    from peft import PeftModel
    from transformers import AutoModelForCausalLM
    if args.group.resolve() != study.GROUP.resolve() or args.generation.resolve() != study.GENERATION.resolve() or args.checkpoint.resolve() != study.CHECKPOINT.resolve():
        raise ValueError("exact frozen qualification inputs only")
    if not os.environ.get("CUDA_VISIBLE_DEVICES") or not torch.cuda.is_available() or torch.cuda.device_count() != 1:
        raise ValueError("owner must assign exactly one CUDA device")
    inputs = study.verify_inputs()
    group, generation, identity = original.authenticate_group(args.group, args.generation)
    cap = min(900.0, args.deadline - time.time())
    if cap <= 0:
        raise TimeoutError("qualification deadline reached")
    previous = signal.signal(signal.SIGALRM, lambda *_: (_ for _ in ()).throw(TimeoutError("qualification cap")))
    signal.setitimer(signal.ITIMER_REAL, cap)
    started = time.monotonic()
    try:
        recipe = study.read(study.SOURCE / "RECIPE.json")
        base = AutoModelForCausalLM.from_pretrained(recipe["base_model"], local_files_only=True,
            dtype=torch.bfloat16, attn_implementation="sdpa", device_map={"": "cuda:0"})
        model = PeftModel.from_pretrained(base, args.checkpoint, is_trainable=True, autocast_adapter_dtype=True)
        _prepare(model)
        turns = [(turn, episode["advantage"]) for episode in group["episodes"] for turn in episode["turns"]]
        short, short_advantage = min(turns, key=lambda row: len(row[0]["input_ids"]))
        longest, long_advantage = max(turns, key=lambda row: len(row[0]["input_ids"]))
        tis = common.c.pilot_math().tis_module()
        ids = torch.tensor([short["input_ids"]], dtype=torch.long, device=model.device)
        model.zero_grad(set_to_none=True)
        full = model(input_ids=ids, attention_mask=torch.ones_like(ids), use_cache=False).logits
        full_loss, full_capture = tis.tis_action_loss(full, short, advantage=short_advantage, temperature=recipe["temperature"])
        full_loss.backward()
        full_grad = _grad_vector(model)
        model.zero_grad(set_to_none=True)
        positions = torch.tensor(sparse_math.position_list(short), dtype=torch.long, device=model.device)
        selected = model(input_ids=ids, attention_mask=torch.ones_like(ids), use_cache=False, logits_to_keep=positions).logits
        sparse_loss, sparse_capture = sparse_math.selected_tis_loss(selected, short, advantage=short_advantage, temperature=recipe["temperature"], tis=tis)
        sparse_loss.backward()
        sparse_grad = _grad_vector(model)
        logprob_difference = float(torch.tensor(full_capture["hf_old_logprobs"]).sub(torch.tensor(sparse_capture["hf_old_logprobs"])).abs().max())
        loss_difference = abs(float(full_loss.detach().cpu()) - float(sparse_loss.detach().cpu()))
        gradient_difference = float(torch.linalg.vector_norm(full_grad - sparse_grad))
        gradient_norm = float(torch.linalg.vector_norm(full_grad))
        relative = gradient_difference / gradient_norm if gradient_norm else math.inf
        cosine = float(torch.nn.functional.cosine_similarity(full_grad, sparse_grad, dim=0))
        short_passed = (logprob_difference <= TOLERANCE["max_action_logprob_absolute"] and
            loss_difference <= TOLERANCE["loss_absolute"] and relative <= TOLERANCE["gradient_relative_l2"] and
            cosine >= TOLERANCE["gradient_cosine_minimum"])
        del ids, full, selected, full_grad, sparse_grad, full_loss, sparse_loss
        model.zero_grad(set_to_none=True)
        torch.cuda.empty_cache(); torch.cuda.reset_peak_memory_stats(); long_started = time.monotonic()
        ids = torch.tensor([longest["input_ids"]], dtype=torch.long, device=model.device)
        positions = torch.tensor(sparse_math.position_list(longest), dtype=torch.long, device=model.device)
        result = model(input_ids=ids, attention_mask=torch.ones_like(ids), use_cache=False, logits_to_keep=positions)
        loss, capture = sparse_math.selected_tis_loss(result.logits, longest, advantage=long_advantage, temperature=recipe["temperature"], tis=tis)
        loss.backward(); torch.cuda.synchronize()
        long_seconds = time.monotonic() - long_started
        long_passed = math.isfinite(float(loss.detach().cpu())) and all(p.grad is None or torch.isfinite(p.grad).all() for p in model.parameters() if p.requires_grad)
        receipt = {
            "schema": "root-composed-rl-sparse-head-qualification-v1",
            "passed": bool(short_passed and long_passed),
            "optimizer_steps": 0,
            "tolerance": TOLERANCE,
            "short_equivalence": {"passed": short_passed, "sequence_tokens": len(short["input_ids"]), "action_tokens": len(short["old_logprobs"]), "max_logprob_absolute_difference": logprob_difference, "loss_absolute_difference": loss_difference, "gradient_relative_l2_difference": relative, "gradient_cosine": cosine},
            "longest_sparse": {"passed": bool(long_passed), "sequence_tokens": len(longest["input_ids"]), "selected_positions": len(positions), "forward_backward_seconds": long_seconds, "peak_allocated_bytes": torch.cuda.max_memory_allocated(), "peak_reserved_bytes": torch.cuda.max_memory_reserved(), "finite_loss": math.isfinite(float(loss.detach().cpu()))},
            "checkpoint1_state_sha256": inputs["checkpoint1_state_sha256"],
            "group_sha256": inputs["group_sha256"],
            "generation_sha256": inputs["generation_sha256"],
            "input_identity": identity["input_identity"],
            "elapsed_seconds": time.monotonic() - started,
        }
        study.write(args.output / "QUALIFICATION_RESULT.json", receipt)
        return receipt
    finally:
        signal.setitimer(signal.ITIMER_REAL, 0)
        signal.signal(signal.SIGALRM, previous)


def parse_args(argv=None):
    parser = argparse.ArgumentParser()
    parser.add_argument("--group", type=Path, required=True)
    parser.add_argument("--generation", type=Path, required=True)
    parser.add_argument("--checkpoint", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--deadline", type=float, required=True)
    return parser.parse_args(argv)


if __name__ == "__main__":
    print(json.dumps(run(parse_args()), sort_keys=True, allow_nan=False))
