"""One fresh-generation root-only TIS increment, with persistent authenticated AdamW."""

import argparse
import importlib.metadata
import json
import math
import os
import random
import signal
import subprocess
import sys
import time
import traceback
from pathlib import Path

import campaign_common as c


def optimizer_step(optimizer):
    values = {int(state["step"]) for state in optimizer.state.values() if "step" in state}
    if not optimizer.state:
        return 0
    if len(values) != 1 or len(optimizer.state) != sum(len(g["params"]) for g in optimizer.param_groups):
        raise ValueError("optimizer has inconsistent/missing parameter steps")
    return values.pop()


def make_optimizer(model, recipe):
    import torch
    trainable = [p for name, p in model.named_parameters() if p.requires_grad]
    if not trainable or any("lora_" not in name or p.dtype != torch.float32 for name, p in model.named_parameters() if p.requires_grad):
        raise ValueError("only FP32 root LoRA tensors may train")
    return torch.optim.AdamW(trainable, lr=recipe["learning_rate"], weight_decay=recipe["weight_decay"])


def restore_optimizer(optimizer, policy, parameter_names):
    import torch
    if not policy["step"]:
        if optimizer_step(optimizer) != 0:
            raise ValueError("initial generation needs fresh Adam state")
        return
    c.authenticate_policy(policy)
    path = Path(policy["path"])
    state = c.read(path / "state.json")
    if state["optimizer_parameter_names"] != parameter_names:
        raise ValueError("optimizer parameter order changed")
    before = [{k: v for k, v in group.items() if k != "params"} for group in optimizer.param_groups]
    optimizer.load_state_dict(torch.load(path / "optimizer.pt", map_location="cpu", weights_only=True))
    after = [{k: v for k, v in group.items() if k != "params"} for group in optimizer.param_groups]
    if before != after or optimizer_step(optimizer) != policy["step"]:
        raise ValueError("optimizer recipe or cursor differs from previous policy")
    rng = torch.load(path / "rng_state.pt", map_location="cpu", weights_only=False)
    random.setstate(rng["python"])
    torch.set_rng_state(rng["torch"])
    if rng["cuda"]:
        if not torch.cuda.is_available():
            raise ValueError("CUDA RNG checkpoint cannot resume on CPU")
        torch.cuda.set_rng_state_all(rng["cuda"])


def update_generation(model, optimizer, episodes, output, recipe, generation, input_identity):
    import torch
    output = Path(output)
    checkpoint = output / f"checkpoint-{generation['round']}"
    if (checkpoint / "state.json").exists():
        return {"policy": c.checkpoint_policy(output, generation, input_identity.get("input_binding", input_identity)), "recovered_checkpoint": True}
    if output.exists():
        raise ValueError("incomplete training attempt retained; diagnosis and new attempt identity required")
    policy = generation["previous_policy"]
    step = c.check_generation(generation, policy, optimizer_step(optimizer))
    math_helper = c.pilot_math()
    tis = math_helper.tis_module()
    if not episodes:
        raise ValueError("nonempty fresh mixed root episodes required")
    for episode in episodes:
        for turn in episode["turns"]:
            math_helper.validate_root_turn(turn, turn["call_model"], policy["adapter_sha256"], recipe["max_causal_tokens"])
    output.mkdir(parents=True)
    c.write_once(output / "INPUTS.json", input_identity)
    c.write_once(output / "GENERATION.json", generation)
    started = time.monotonic()
    model.train()
    model.config.use_cache = False
    model.enable_input_require_grads()
    model.gradient_checkpointing_enable(gradient_checkpointing_kwargs={"use_reentrant": False})
    for module in model.modules():
        if isinstance(module, torch.nn.Dropout):
            module.eval()
    trainable = [(name, p) for name, p in model.named_parameters() if p.requires_grad]
    if any("lora_" not in name or p.dtype != torch.float32 for name, p in trainable):
        raise ValueError("only FP32 root LoRA tensors may train")
    before = {name: p.detach().cpu().clone() for name, p in trainable}
    optimizer.zero_grad(set_to_none=True)
    captures = []
    for episode in episodes:
        if not episode["turns"]:
            raise ValueError("empty root actions")
        weight = 1 / (len(episodes) * len(episode["turns"]))
        for index, turn in enumerate(episode["turns"]):
            ids = torch.tensor([turn["input_ids"]], dtype=torch.long, device=model.device)
            result = model(input_ids=ids, attention_mask=torch.ones_like(ids), use_cache=False)
            loss, capture = tis.tis_action_loss(result.logits, turn, advantage=episode["advantage"], temperature=recipe["temperature"])
            if not torch.isfinite(loss):
                raise ValueError("nonfinite root-only loss")
            (loss * weight).backward()
            captures.append({**capture, "episode_id": episode["episode_id"], "turn": index,
                "source_trace_id": turn["source_trace_id"], "source_node_index": turn["source_node_index"],
                "role_depth": 0, "loss_weight": weight, "loss": float(loss.detach().cpu())})
            del ids, result, loss
    diagnostics = tis.distribution_summary(captures)
    c.write_once(output / "correction-capture.json", {"turns": captures, "diagnostics": diagnostics})
    if diagnostics["guard_failures"]:
        raise ValueError("distribution guards failed: " + ", ".join(diagnostics["guard_failures"]))
    gradient = float(torch.nn.utils.clip_grad_norm_([p for _, p in trainable], recipe["gradient_clip_norm"], error_if_nonfinite=True).cpu())
    if not math.isfinite(gradient) or gradient <= 0:
        raise ValueError("finite nonzero root-only gradient required")
    if time.monotonic() - started >= recipe["training_wall_cap_seconds"]:
        raise TimeoutError("training cap before optimizer step")
    c.write_once(output / "STEP_STARTED.json", {"generation_id": generation["generation_id"], "previous_optimizer_step": step - 1})
    optimizer.step()
    if model.device.type == "cuda":
        torch.cuda.synchronize()
    # Retain this actual step even if the overall envelope expires during serialization.
    signal.setitimer(signal.ITIMER_REAL, 0)
    elapsed = time.monotonic() - started
    if optimizer_step(optimizer) != step:
        raise ValueError("actual persistent Adam cursor failed to increment exactly once")
    delta = math.sqrt(sum(float((p.detach().cpu() - before[name]).double().square().sum()) for name, p in trainable))
    if not math.isfinite(delta) or delta <= 0 or any(not torch.isfinite(p).all() for _, p in trainable):
        raise ValueError("nonzero finite root parameter change required")
    checkpoint.mkdir()
    model.save_pretrained(checkpoint, safe_serialization=True)
    torch.save(optimizer.state_dict(), checkpoint / "optimizer.pt")
    torch.save({"python": random.getstate(), "torch": torch.get_rng_state(),
                "cuda": torch.cuda.get_rng_state_all() if model.device.type == "cuda" else []}, checkpoint / "rng_state.pt")
    metrics = {"episodes": len(episodes), "root_turns": len(captures), "root_action_tokens": diagnostics["action_tokens"],
        "child_loss_tokens": 0, "observation_loss_tokens": 0, "guard_failures": diagnostics["guard_failures"],
        "gradient_norm_before_clip": gradient, "trainable_parameter_delta_l2": delta, "optimization_seconds": elapsed,
        "trainable_parameter_count": sum(p.numel() for _, p in trainable),
        "peak_allocated_bytes": torch.cuda.max_memory_allocated() if model.device.type == "cuda" else 0,
        "peak_reserved_bytes": torch.cuda.max_memory_reserved() if model.device.type == "cuda" else 0}
    c.write_once(checkpoint / "state.json", {"generation": generation, "optimizer_steps": step,
        "optimizer_parameter_names": [name for name, _ in trainable], "input_identity": input_identity,
        "input_file_sha256": c.file_hash(output / "INPUTS.json"),
        "metrics": metrics, "correction_capture_sha256": c.file_hash(output / "correction-capture.json"),
        "files_sha256": {p.name: c.file_hash(p) for p in checkpoint.iterdir() if p.is_file()}})
    result = {"schema": "root-campaign-fresh-generation-result-v1", "policy": c.checkpoint_policy(output, generation),
              "generation_id": generation["generation_id"], "optimizer_steps": step, "metrics": metrics,
              "recovered_checkpoint": False, "diagnostics": diagnostics,
              "elapsed_with_checkpoint_seconds": time.monotonic() - started}
    c.write_once(output / "RESULT.json", result)
    return result


def authenticate_group(group_path, generation_path):
    campaign = c.verify_campaign()
    generation, group = c.read(generation_path), c.read(group_path)
    policy = generation["previous_policy"]
    c.check_generation(generation, policy, policy["step"])
    if generation["campaign_id"] != campaign["campaign_id"] or group["generation"] != generation:
        raise ValueError("stale group generation or another campaign")
    plans = c.read(c.ROOT / "inputs/PLANS.json")["training"][str(generation["round"])]
    if generation["coordinate_plan_sha256"] != c.digest(plans):
        raise ValueError("generation is not the declared fresh32")
    c.authenticate_policy(policy)
    manifest = c.read(group_path.parent / "MANIFEST.json")
    c.authenticate({group_path.parent / p: sha for p, sha in manifest["artifact_sha256"].items()})
    if manifest["recorded"] != 32 or manifest["planned"] != 32 or manifest["integrity_failures"]:
        raise ValueError("complete32 without integrity failures required")
    if group_path.name not in manifest["artifact_sha256"] or manifest["generation"] != generation:
        raise ValueError("group is not authenticated by current export")
    rows = c.read(group_path.parent / "EPISODES.json")
    if {r["episode_id"] for r in rows} != {r["id"] for r in plans} or any(r["split"] != "training" for r in rows):
        raise ValueError("nontraining, duplicate, or stale coordinates")
    helper = c.pilot_math()
    rebuilt = helper.recompute_group(rows)
    for key in ["dataset_id", "role_binding", "generation", "credit_policy"]:
        rebuilt[key] = group[key]
    rebuilt["group_id"] = c.digest({k: v for k, v in rebuilt.items() if k != "group_id"})
    if rebuilt != group:
        raise ValueError("mixed selection/advantages changed")
    binding = group["role_binding"]
    alias = binding["role_map"]["root"]
    if binding["campaign_policy"] != policy or binding["models"][binding["fixed_child"]]["adapter_sha256"] != c.CHILD_SHA:
        raise ValueError("rollout and training root/child differ")
    for row in group["episodes"]:
        for turn in row["turns"]:
            helper.validate_root_turn(turn, alias, policy["adapter_sha256"], c.read(c.ROOT / "RECIPE.json")["max_causal_tokens"])
            audit = turn["role_audit"]
            c.authenticate({audit["source_audit_path"]: audit["source_audit_sha256"]})
        if any(t["credited"] for t in row["all_role_evidence"] if t["role_depth"] == 1):
            raise ValueError("child actions received credit")
    result = subprocess.run([str(c.NATIVE_PYTHON), str(c.ROOT / "campaign_native.py"), "verify-export", "--output", str(group_path.parent)],
        check=True, text=True, capture_output=True, timeout=180,
        env={**os.environ, "CUDA_VISIBLE_DEVICES": "", "PYTHONDONTWRITEBYTECODE": "1"})
    proof = json.loads(result.stdout)
    if proof["group_sha256"] != c.file_hash(group_path):
        raise ValueError("native replay authenticated another group")
    recipe = c.read(c.ROOT / "RECIPE.json")
    base = Path(recipe["base_model"])
    c.authenticate({base / "local-research-manifest.json": recipe["base_manifest_sha256"]})
    c.authenticate({base / p: sha for p, sha in c.read(base / "local-research-manifest.json")["files"].items()})
    identity = {"generation": generation, "generation_file_sha256": c.file_hash(generation_path),
        "group_path": str(group_path), "group_sha256": c.file_hash(group_path), "group_id": group["group_id"],
        "export_manifest_sha256": c.file_hash(group_path.parent / "MANIFEST.json"), "native_replay": proof,
        "campaign_sha256": c.file_hash(c.ROOT / "CAMPAIGN.json"), "recipe_sha256": c.file_hash(c.ROOT / "RECIPE.json"),
        "role_binding": binding, "child_loaded_into_training_model": False}
    identity["input_identity"] = c.digest(identity)
    return group, generation, identity


def train(args):
    import torch
    from peft import PeftModel
    from transformers import AutoModelForCausalLM
    group, generation, identity = authenticate_group(args.group.resolve(), args.generation.resolve())
    if args.preflight:
        return identity
    if (args.output / f"checkpoint-{generation['round']}" / "state.json").exists():
        return {"policy": c.checkpoint_policy(args.output, generation, identity), "recovered_checkpoint": True}
    if args.output.exists():
        raise ValueError("partial training attempt requires diagnosis, not implicit retry")
    if not os.environ.get("CUDA_VISIBLE_DEVICES") or not torch.cuda.is_available() or torch.cuda.device_count() != 1:
        raise ValueError("parent must assign exactly one owned CUDA device")
    recipe = c.read(c.ROOT / "RECIPE.json")
    cap = min(recipe["training_wall_cap_seconds"], args.deadline - time.time())
    if cap <= 0:
        raise TimeoutError("campaign global deadline reached")
    def expired(_signum, _frame):
        raise TimeoutError("load/optimization or global cap reached before checkpoint")
    previous = signal.signal(signal.SIGALRM, expired)
    signal.setitimer(signal.ITIMER_REAL, cap)
    try:
        random.seed(c.SEED)
        torch.manual_seed(c.SEED)
        torch.cuda.manual_seed_all(c.SEED)
        torch.set_num_threads(4)
        torch.cuda.reset_peak_memory_stats()
        policy = generation["previous_policy"]
        base = AutoModelForCausalLM.from_pretrained(recipe["base_model"], local_files_only=True,
            dtype=torch.bfloat16, attn_implementation="sdpa", device_map={"": "cuda:0"})
        model = PeftModel.from_pretrained(base, policy["path"], is_trainable=True, autocast_adapter_dtype=True)
        converter = c.load("campaign_exact_tensor_audit", c.pilot_math().CONVERTER_PATH)
        audit = converter.audit_loaded_adapter(model, Path(policy["path"]))
        optimizer = make_optimizer(model, recipe)
        restore_optimizer(optimizer, policy, [n for n, p in model.named_parameters() if p.requires_grad])
        execution = {"input_binding": identity, "adapter_load_audit": audit,
            "runtime": {"python": sys.version, "torch": torch.__version__, "cuda": torch.version.cuda,
                "gpu": torch.cuda.get_device_name(), "cuda_visible_devices": os.environ["CUDA_VISIBLE_DEVICES"],
                "versions": {name: importlib.metadata.version(name) for name in ["peft", "transformers", "safetensors"]}}}
        return update_generation(model, optimizer, group["episodes"], args.output.resolve(), recipe, generation, execution)
    finally:
        signal.setitimer(signal.ITIMER_REAL, 0)
        signal.signal(signal.SIGALRM, previous)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--group", type=Path, required=True)
    parser.add_argument("--generation", type=Path, required=True)
    parser.add_argument("--output", type=Path)
    parser.add_argument("--deadline", type=float, default=float("inf"))
    parser.add_argument("--preflight", action="store_true")
    args = parser.parse_args()
    try:
        print(json.dumps(train(args), sort_keys=True, allow_nan=False))
    except BaseException as error:
        if args.output is not None:
            import uuid
            c.write_once(args.output.parent / f"TRAIN_FAILURE-{uuid.uuid4().hex}.json",
                {"type": type(error).__name__, "error": str(error), "traceback": traceback.format_exc(), "checkpoint_preserved": True})
        raise
