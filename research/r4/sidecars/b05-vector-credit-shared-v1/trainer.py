"""One fixed native G4 batch, one fresh zero-B LoRA update, parameterized only by credit mode."""

import math
import os
from pathlib import Path
import random
import signal
import time
import traceback


def norm(values):
    return math.sqrt(math.fsum(float(value.double().square().sum()) for value in values))


def dependencies(study):
    with study.aliases({"study": study}, study.FLAT):
        model_core = study.load(f"vector_credit_{study.CREDIT_MODE}_model_core", study.FLAT / "core.py")
    credit = study.load(f"vector_credit_{study.CREDIT_MODE}_math", study.SHARED / "credit.py")
    assert model_core.scorer.study is study and model_core.scorer.math_core is model_core.math
    return model_core, credit


def preflight(study):
    ready = study.verify(); rows = study.validate_inputs(study.read(study.INPUTS))
    dependencies(study)
    return ready, rows


def run(study, output, seconds):
    ready, rows = preflight(study); model_core, credit = dependencies(study)
    output = Path(output)
    assert output == study.OUTPUT and seconds == study.SCIENCE_SECONDS
    if not os.environ.get("CUDA_VISIBLE_DEVICES"):
        raise RuntimeError("CPU_ENTRY_VERIFIED: MAIN must assign one GPU before training")
    import numpy as np
    import torch
    from transformers import AutoModelForCausalLM
    assert torch.cuda.device_count() == 1
    output.mkdir(parents=True)
    assert {path.name for path in output.iterdir()} <= {"OWNER_START.json", "train.stdout", "train.stderr"}
    started = time.monotonic(); steps = 0; model = None
    def timeout(_sig, _frame): raise TimeoutError("vector-credit one-step science cap")
    signal.signal(signal.SIGALRM, timeout); signal.alarm(seconds)
    study.write_x(output / "START.json", {"ready_sha256": study.sha(study.READY),
        "input_sha256": study.sha(study.INPUTS), "credit_mode": study.CREDIT_MODE,
        "init_seed": study.INIT_SEED, "seed": study.SEED, "numpy_seed": study.NP_SEED,
        "science_seconds": seconds})
    try:
        torch.set_num_threads(4); random.seed(study.SEED); np.random.seed(study.NP_SEED)
        torch.manual_seed(study.SEED); torch.cuda.manual_seed_all(study.SEED)
        torch.backends.cuda.matmul.allow_tf32 = False; torch.backends.cudnn.allow_tf32 = False
        base = AutoModelForCausalLM.from_pretrained(str(study.BASE), local_files_only=True,
            torch_dtype=torch.bfloat16, attn_implementation="sdpa", device_map={"": "cuda:0"})
        base.config.use_cache = False; model = model_core.initialize(base); model.train()
        for module in model.modules():
            if isinstance(module, torch.nn.Dropout): module.eval()
        model.gradient_checkpointing_enable(gradient_checkpointing_kwargs={"use_reentrant": False})
        model.enable_input_require_grads()
        initial = model_core.math.snapshot_trainable(model)
        assert all(value.dtype == torch.float32 for value in initial.values())
        torch.save(initial, output / "initial-trainable.pt")
        model_core.save_rng(output / "initial-rng.pt", torch); model.save_pretrained(output / "initial-adapter")
        first = rows[0]["root_turns"][0]
        enabled = model_core.selected_logprobs(model, first, require_grad=False)
        with model.disable_adapter(): disabled = model_core.selected_logprobs(model, first, require_grad=False)
        assert torch.equal(enabled, disabled)
        study.write_x(output / "INITIAL.json", {"start": "released_base_new_zero_B_LoRA",
            "init_seed": study.INIT_SEED, "config_source_sha256": study.sha(study.CONFIG_SOURCE),
            "all_B_exact_zero": True, "all_A_nonzero": True,
            "trainable_identity": model_core.math.snapshot_digest(initial),
            "trainable_parameters": sum(value.numel() for value in initial.values()),
            "initial_tensor_file_sha256": study.sha(output / "initial-trainable.pt"),
            "initial_rng_sha256": study.sha(output / "initial-rng.pt"),
            "disabled_enabled_HF_exact": True, "disabled_enabled_max_error": 0.0,
            "precision": "BF16 base / FP32 LoRA", "dropout_disabled": True,
            "attention": "sdpa", "no_KV_cache": True, "model_training": True})
        baseline = model_core.scorer._all_logprobs(model, rows)
        weights, qualification = model_core.scorer._build_token_diagnostics(rows, baseline)
        qualification.update({"denominator": 64, "groups": 16, "all_actions": 64,
            "credit_mode": study.CREDIT_MODE, "native_HF_equality_required": False,
            "exact_sequence_IS_claim": False, "token_TIS_cap": 2.0,
            "policy_scope": "biased token-TIS on native boolean decision tokens only"})
        study.write_x(output / "PRESTEP_QUALIFICATION.json", qualification)
        study.write_x(output / "PRESTEP_LOGPS.json", {"episodes": baseline,
            "detached_token_weights": weights,
            "native_logprobs": [[row["root_turns"][0]["old_logprobs"]] for row in rows]})
        named = {name: parameter for name, parameter in model.named_parameters() if parameter.requires_grad}
        model.zero_grad(set_to_none=True); checks = []; perrow = []; objective = 0.0
        for index, row in enumerate(rows):
            coefficients = row["credit_coefficients"]
            advantages = row[study.CREDIT_MODE + "_advantages"]
            active = any(any(value != 0 for value in coeff) and
                         sum(coeff[j] * advantages[j] for j in range(row["candidate_count"])) != 0
                         for coeff in coefficients)
            values = model_core.selected_logprobs(model, row["root_turns"][0], require_grad=active)
            replay = model_core.replay_check(values.detach().cpu().tolist(), baseline[index][0])
            replay.update({"episode_id": row["episode_id"], "full_action_tokens": values.numel(),
                "credited_tokens": sum(any(value > 0 for value in coeff) for coeff in coefficients),
                "active_gradient": active})
            checks.append(replay)
            if not replay["passed"]:
                study.write_x(output / "REPLAY.json", {"passed": False, "checks": checks,
                                                        "optimizer_steps": 0})
                raise ValueError("HF gradient replay mismatch; no optimizer step")
            if active:
                term = credit.credit_loss(values, weights[index][0], advantages, coefficients,
                    candidates=row["candidate_count"], denominator=64)
                objective += float(term.detach()); term.backward(); del term
            perrow.append({"episode_id": row["episode_id"], "semantic_valid": row["semantic_valid"],
                "active_gradient": active, "reward": row[study.CREDIT_MODE + "_reward"],
                "advantages": advantages, "candidate_count": row["candidate_count"],
                "credited_tokens": replay["credited_tokens"],
                "boundary_overlap_token_indices": row["credit_receipt"]["boundary_overlap_token_indices"],
                "cross_decision_token_indices": row["credit_receipt"]["cross_decision_token_indices"]})
            del values
        assert len(checks) == len(perrow) == 64 and all(check["passed"] for check in checks)
        preclip = float(torch.nn.utils.clip_grad_norm_(list(named.values()), 1.0))
        assert math.isfinite(preclip) and preclip > 0
        gradients = {name: parameter.grad.detach().cpu().clone() if parameter.grad is not None
            else torch.zeros_like(parameter, device="cpu") for name, parameter in named.items()}
        assert all(torch.isfinite(value).all() for value in gradients.values())
        a_norm = norm(value for name, value in gradients.items() if ".lora_A." in name)
        b_norm = norm(value for name, value in gradients.items() if ".lora_B." in name)
        assert a_norm == 0.0 and b_norm > 0
        torch.save(gradients, output / "gradients.pt")
        study.write_x(output / "REPLAY.json", {"passed": True, "checks": checks, "rows": perrow,
            "optimizer_steps": 0, "credit_mode": study.CREDIT_MODE, "objective": objective,
            "denominator": 64, "preclip_gradient_norm": preclip, "clip": 1.0,
            "LoRA_A_gradient_norm": a_norm, "LoRA_B_gradient_norm": b_norm,
            "selected_loss_tokens": sum(row["credited_tokens"] for row in perrow),
            "active_actions": sum(row["active_gradient"] for row in perrow),
            "invalid_actions": sum(not row["semantic_valid"] for row in perrow)})
        model_core.restore_rng(output / "initial-rng.pt", torch)
        branch = model_core.math.apply_fresh_adam_branch(
            model, initial, gradients, learning_rate=study.LEARNING_RATE); steps = 1
        updated = model_core.math.snapshot_trainable(model)
        delta = norm(updated[name].double() - initial[name].double() for name in initial)
        assert math.isfinite(delta) and delta > 0
        checkpoint = output / "checkpoint-0001"; checkpoint.mkdir(); model.save_pretrained(checkpoint)
        torch.save(branch["optimizer"].state_dict(), checkpoint / "optimizer.pt")
        model_core.save_rng(checkpoint / "rng.pt", torch)
        torch.save(updated, checkpoint / "trainable.pt")
        state = {"schema": "b05-vector-credit-state-v1", "status": "UPDATED",
            "credit_mode": study.CREDIT_MODE, "optimizer_steps": 1,
            "start": "released_base_new_zero_B_LoRA", "base": str(study.BASE),
            "initial_config_sha256": study.sha(study.CONFIG_SOURCE), "init_seed": study.INIT_SEED,
            "learning_rate": study.LEARNING_RATE, "denominator": 64, "groups": 16,
            "group_size": 4, "reward": study.REWARD_DESCRIPTION,
            "baseline": "other three samples in same root/candidate group; G4 RLOO",
            "per_candidate_weight": "1/candidate_count", "gradient_clip": 1.0,
            "token_TIS_cap": 2.0, "token_TIS_biased": True, "sequence_IS_unbiased": False,
            "loss_scope": "whole native token intersecting one boolean; inseparable comma/space retained; cross-decision zero",
            "invalid_policy": "zero reward and zero token mask; retained /64 and enters peer RLOO baseline",
            "fresh_AdamW": True, "weight_decay": 0.0,
            "optimizer_state_empty_before_step": branch["optimizer_state_empty_before_step"],
            "optimizer_state_steps": branch["optimizer_state_steps"],
            "initial_trainable_identity": model_core.math.snapshot_digest(initial),
            "updated_trainable_identity": model_core.math.snapshot_digest(updated),
            "adapter_delta_l2": delta, "source_input_sha256": study.sha(study.INPUTS),
            "source_rollout_result_sha256": study.sha(study.ROLLOUT / "outputs/attempt-001/RESULT.json"),
            "elapsed_seconds": time.monotonic() - started,
            "peak_allocated_bytes": torch.cuda.max_memory_allocated(),
            "selected_loss_tokens": study.read(output / "REPLAY.json")["selected_loss_tokens"]}
        study.write_x(checkpoint / "state.json", state)
        binding = {"schema": "b05-vector-credit-checkpoint-binding-v1", "alias": study.ALIAS,
            "base": str(study.BASE), "checkpoint": str(checkpoint), "credit_mode": study.CREDIT_MODE,
            "adapter_sha256": study.sha(checkpoint / "adapter_model.safetensors"),
            "adapter_config_sha256": study.sha(checkpoint / "adapter_config.json"),
            "state_sha256": study.sha(checkpoint / "state.json"),
            "source_ready_sha256": study.sha(study.READY), "selection": "fixed sole step1; not outcome-selected"}
        study.write_x(checkpoint / "EVAL_BINDING.json", binding)
        artifact_paths = [checkpoint / name for name in ("adapter_model.safetensors", "adapter_config.json",
            "optimizer.pt", "rng.pt", "trainable.pt", "state.json", "EVAL_BINDING.json")]
        artifact_paths += [output / name for name in ("initial-trainable.pt", "initial-rng.pt", "INITIAL.json",
            "PRESTEP_QUALIFICATION.json", "PRESTEP_LOGPS.json", "REPLAY.json", "gradients.pt")]
        artifacts = {str(path): study.sha(path) for path in artifact_paths}
        study.write_x(checkpoint / "STEP_COMMIT.json", {"schema": "b05-vector-credit-step1-commit-v1",
            "credit_mode": study.CREDIT_MODE, "optimizer_steps": 1,
            "source_ready_sha256": study.sha(study.READY), "input_sha256": study.sha(study.INPUTS),
            "artifacts_sha256": artifacts})
        study.write_x(output / "RESULT.json", {"status": "UPDATED", "credit_mode": study.CREDIT_MODE,
            "optimizer_steps": 1, "checkpoint": str(checkpoint),
            "state_sha256": study.sha(checkpoint / "state.json"),
            "step_commit_sha256": study.sha(checkpoint / "STEP_COMMIT.json"),
            "binding_sha256": study.sha(checkpoint / "EVAL_BINDING.json"), "adapter_delta_l2": delta,
            "elapsed_seconds": time.monotonic() - started, "ready_sha256": study.sha(study.READY)})
    except BaseException as error:
        if not (output / "RESULT.json").exists():
            study.write_x(output / "RESULT.json", {"status": "FAILED", "credit_mode": study.CREDIT_MODE,
                "optimizer_steps": steps, "error": {"type": type(error).__name__, "message": str(error),
                "traceback": traceback.format_exc()}, "elapsed_seconds": time.monotonic() - started,
                "ready_sha256": study.sha(study.READY)})
        raise
    finally:
        signal.alarm(0)
        if model is not None: del model
        import gc
        gc.collect(); torch.cuda.empty_cache()
