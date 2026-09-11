"""Two record-exposure-matched mixed-cardinality supervised leaf curricula."""

from __future__ import annotations

import argparse
import importlib.metadata
import importlib.util
import math
import os
import platform
import random
import signal
import sys
import time
import traceback
import uuid
from pathlib import Path

ROOT = Path(__file__).resolve().parent
SFT = ROOT.parent / "trec-leaf-sft-v1"
SIZES = {"A": (1, 5, 16, 32), "B": (1, 5, 16, 64)}


def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


data = load("data", SFT / "source/data.py")
data.authenticate(
    {
        SFT / "source/data.py": "b5aa353e2173c3fd48ecc36ce0596c9c3328767a7d82c8d22c57b4e0a32f0b8f",
        SFT / "source/experiment.py": (
            "c4a66731f544c57821b8f0bf81eb6f5785f12f943b61b8bc4e3916a1dcef041c"
        ),
        SFT / "RECIPE.json": "556a69539f4d90df2c6b97341c343fbfb80d135dfcf3f92f17427dbb8bdab702",
    }
)
old = load("mixed_sft_authenticated_training_helpers", SFT / "source/experiment.py")


def allocate(rows, sizes):
    if len({r["group_id"] for r in rows}) != len(rows):
        raise ValueError("duplicate training group")
    epochs = []
    for epoch in range(2):
        ordered = sorted(rows, key=lambda r: r["group_id"])
        random.Random(981260700 + epoch).shuffle(ordered)
        quotas = [len(rows) // 4] * 4
        for extra in range(len(rows) % 4):
            quotas[(epoch + extra) % 4] += 1
        batches, cursor = [], 0
        for bucket, (size, count) in enumerate(zip(sizes, quotas, strict=True)):
            selected = ordered[cursor : cursor + count]
            cursor += count
            for start in range(0, count, size):
                records = selected[start : start + size]
                batches.append(
                    {
                        "bucket": bucket,
                        "nominal_size": size,
                        "residual": len(records) != size,
                        "records": records,
                    }
                )
        random.Random(981261700 + epoch).shuffle(batches)
        epochs.append(batches)
    return epochs


def final_selection(candidates):
    if len(candidates) != 2 or [r["epoch"] for r in candidates] != [1, 2]:
        raise ValueError("both completed epochs required")
    return candidates[-1]


def stats(rows):
    return {
        "arrays": len(rows),
        "records": sum(len(r["gold"]) for r in rows),
        "optimizer_steps": math.ceil(len(rows) / 16),
        "prompt_tokens": sum(len(r["prompt_ids"]) for r in rows),
        "target_tokens": sum(sum(t != -100 for t in r["labels"][1:]) for r in rows),
        "input_tokens_unpadded": sum(len(r["input_ids"]) for r in rows),
        "input_tokens_padded_microbatch2": sum(
            len(rows[i : i + 2]) * max(len(r["input_ids"]) for r in rows[i : i + 2])
            for i in range(0, len(rows), 2)
        ),
        "max_length": max(len(r["input_ids"]) for r in rows),
        "sizes": [
            {
                "nominal_size": size,
                "records": sum(len(r["gold"]) for r in rows if r["nominal_size"] == size),
                "arrays": sum(r["nominal_size"] == size for r in rows),
                "residual_cardinalities": [
                    len(r["gold"]) for r in rows if r["nominal_size"] == size and r["residual"]
                ],
            }
            for size in sorted({r["nominal_size"] for r in rows})
        ],
    }


def prepare(arm):
    destination = ROOT / arm
    if destination.exists():
        raise ValueError("curriculum preparation requires unused destination")
    recipe = data.read_json(SFT / "RECIPE.json")
    data.authenticate(recipe["source_hashes"])
    partitions = data.load_partitions()
    tokenizer = data.load_tokenizer()
    epochs = []
    for epoch, batches in enumerate(allocate(partitions["train"], SIZES[arm]), 1):
        rows = []
        for index, batch in enumerate(batches):
            rendered = data.render(batch["records"], tokenizer, "train", epoch, index)
            rows.append(
                {**rendered, **{k: batch[k] for k in ("nominal_size", "bucket", "residual")}}
            )
        epochs.append(rows)
    evaluation = {}
    for split in ("validation", "test"):
        ordered = sorted(partitions[split], key=lambda r: r["group_id"])
        # Exactly the original frozen fixed5 evaluation order and grouping.
        original = data.read_json(SFT / "prepared-v1/data.json")
        evaluation[split] = original[split]
        if {g for r in evaluation[split] for g in r["group_ids"]} != {
            r["group_id"] for r in ordered
        }:
            raise ValueError("fixed evaluation source groups differ")
    extra = {}
    ordered = sorted(partitions["test"], key=lambda r: r["group_id"])
    for size in (1, 5, 16, 32, 64):
        extra[str(size)] = [
            data.render(ordered[i : i + size], tokenizer, f"test-size{size}", 0, i // size)
            for i in range(0, len(ordered), size)
        ]
    composition_path = ROOT.parent / "leaf-composition-transfer-v1/prepared-v1/DATA.json"
    data.authenticate(
        {composition_path: "1ea4640da5a8e3e305bee7f79d5abeecb02507d6bcc33d709d1c7209fd47bfc2"}
    )
    composition = data.read_json(composition_path)
    transfer = [
        data.render(c["records"], tokenizer, "transfer64", 0, i)
        for i, c in enumerate(composition["contexts"])
    ]
    probe_path = ROOT / "PROBE_SPEC.json"
    probe = data.read_json(probe_path)
    if probe["identity"] != "2672884bf83451246e92a0f2659964db5d8c137165d7d6800c61d3b2c8818c7f":
        raise ValueError("matched greedy comparison identity changed")
    if data.digest({k: v for k, v in probe.items() if k != "identity"}) != probe["identity"]:
        raise ValueError("matched greedy comparison bytes changed")
    for row, request in zip(transfer, probe["requests"], strict=True):
        if row["messages"] != request["request"]["messages"] or row["gold"] != request["gold"]:
            raise ValueError("curriculum final64 messages/gold differ from matched probe")
        row["training_template_prompt_ids"] = row["prompt_ids"]
        row["prompt_ids"] = request["hf_prompt_ids"]
        row["prompt"] = tokenizer.decode(row["prompt_ids"], skip_special_tokens=False)
        row["evaluation_template_caution"] = (
            "Matched serving-request tools use function/type key order; training retains "
            "exact prior-SFT type/function order. Semantic messages/tools are identical."
        )
        # Evaluation-only prompts must not masquerade as valid supervised causal rows.
        for key in ("input_ids", "labels", "native_target_suffix"):
            row.pop(key)
    prepared = {"train": epochs, **evaluation, "test_by_size": extra, "transfer64": transfer}
    sources = dict(recipe["source_hashes"])
    sources.update(
        {
            str(p): data.file_hash(p)
            for p in [
                Path(__file__),
                ROOT / "test_driver.py",
                ROOT / "DESIGN.md",
                composition_path,
                probe_path,
                SFT / "RECIPE.json",
                SFT / "prepared-v1/data.json",
                SFT / "prepared-v1/MANIFEST.json",
                SFT / "outputs/attempt-001/baseline-test/SUMMARY.json",
            ]
        }
    )
    data.authenticate(
        {
            SFT / "prepared-v1/data.json": data.read_json(SFT / "prepared-v1/MANIFEST.json")[
                "data_sha256"
            ]
        }
    )
    recipe.update(
        schema=ROOT.name,
        arm=arm,
        source_hashes=sources,
        questions_per_array=list(SIZES[arm]),
        selection="Fixed final epoch2; validation monitored, never used for checkpoint selection",
        shuffle_seed=981260700,
        shuffle_algorithm=(
            "Per-epoch seeded record shuffle; balanced rotating residual quota; "
            "separate array-order shuffle"
        ),
        evaluation="Same original fixed5 validation/test; optional queued test-by-size greedy1024",
        max_new_tokens_by_size=1024,
    )
    destination.mkdir()
    data.write_once(destination / "RECIPE.json", recipe)
    data.write_once(destination / "data.json", prepared)
    manifest = {
        "arm": arm,
        "recipe_sha256": data.file_hash(destination / "RECIPE.json"),
        "data_sha256": data.file_hash(destination / "data.json"),
        "epochs": [stats(rows) for rows in epochs],
        "split_counts": {k: len(v) for k, v in partitions.items()},
        "record_exposures": 10130,
        "compute_matched_to_all5": False,
        "validation_test_selection": "Final epoch2 fixed in advance; no test selection",
    }
    manifest["identity"] = data.digest(manifest)
    data.write_once(destination / "MANIFEST.json", manifest)
    for path in destination.iterdir():
        path.chmod(0o444)
    return manifest


def bound(arm):
    path = ROOT / arm
    manifest = data.read_json(path / "MANIFEST.json")
    if data.digest({k: v for k, v in manifest.items() if k != "identity"}) != manifest["identity"]:
        raise ValueError("prepared identity changed")
    data.authenticate(
        {
            path / "RECIPE.json": manifest["recipe_sha256"],
            path / "data.json": manifest["data_sha256"],
        }
    )
    recipe = data.read_json(path / "RECIPE.json")
    data.authenticate(recipe["source_hashes"])
    return recipe, data.read_json(path / "data.json"), manifest


def supervised_step(model, optimizer, rows, pad_id):
    import torch

    denominator = sum(sum(t != -100 for t in row["labels"][1:]) for row in rows)
    optimizer.zero_grad(set_to_none=True)
    total = 0.0
    for start in range(0, len(rows), 2):
        batch = {
            k: v.to(model.device) for k, v in data.collate(rows[start : start + 2], pad_id).items()
        }
        labels = batch.pop("labels")
        logits = model(**batch, use_cache=False).logits
        loss, count = old.loss_sum(logits, labels)
        if not torch.isfinite(loss) or count <= 0:
            raise ValueError("nonfinite or empty supervised loss")
        (loss / denominator).backward()
        total += float(loss.detach())
    gradient = torch.nn.utils.clip_grad_norm_(
        [p for p in model.parameters() if p.requires_grad], 1.0, error_if_nonfinite=True
    )
    optimizer.step()
    return {
        "action_tokens": denominator,
        "nll": total / denominator,
        "gradient_norm": float(gradient),
    }


def position_metrics(results):
    output = []
    for start in range(0, 64, 16):
        records = [
            (r["gold"][i], r["score"]["predictions"][i], r["score"]["correct"][i])
            for r in results
            for i in range(start, min(start + 16, len(r["gold"])))
        ]
        output.append(
            {
                "positions_1based": [start + 1, start + 16],
                "records": len(records),
                "correct": sum(r[2] for r in records),
                "predicted_entity": sum(r[1] == "entity" for r in records),
                "gold_entity": sum(r[0] == "entity" for r in records),
            }
        )
    return output


def evaluate_long(model, tokenizer, rows, output, identity, checkpoint):
    import torch

    output.mkdir(exist_ok=True)
    binding = {
        "identity": identity,
        "adapter_sha256": data.file_hash(checkpoint / "adapter_model.safetensors"),
        "row_ids": [r["id"] for r in rows],
        "greedy": True,
        "max_new_tokens": 1024,
        "microbatch": 2,
    }
    binding["evaluation_identity"] = data.digest(binding)
    if (output / "MANIFEST.json").exists():
        if data.read_json(output / "MANIFEST.json") != binding:
            raise ValueError("long evaluation identity changed")
    else:
        data.write_once(output / "MANIFEST.json", binding)
    model.eval()
    model.gradient_checkpointing_disable()
    eos = model.generation_config.eos_token_id
    eos = set(eos if isinstance(eos, list) else [eos])
    results = []
    for start in range(0, len(rows), 2):
        chunk = rows[start : start + 2]
        if all((output / (r["id"] + ".json")).exists() for r in chunk):
            results.extend(data.read_json(output / (r["id"] + ".json")) for r in chunk)
            continue
        batch = {
            k: v.to(model.device)
            for k, v in data.generation_batch(
                [r["prompt_ids"] for r in chunk], tokenizer.pad_token_id
            ).items()
        }
        with torch.inference_mode():
            generated = model.generate(
                **batch,
                do_sample=False,
                max_new_tokens=1024,
                pad_token_id=tokenizer.pad_token_id,
                use_cache=True,
            )
        sequences = data.continuations(
            generated, batch["input_ids"].shape[1], eos, tokenizer.pad_token_id
        )
        for row, ids in zip(chunk, sequences, strict=True):
            content = tokenizer.decode(
                ids[:-1] if ids and ids[-1] in eos else ids, skip_special_tokens=False
            )
            result = {
                "id": row["id"],
                "evaluation_identity": binding["evaluation_identity"],
                "gold": row["gold"],
                "group_ids": row["group_ids"],
                "prompt_token_ids": row["prompt_ids"],
                "generated_token_ids": ids,
                "content": content,
                "raw_generation": tokenizer.decode(ids, skip_special_tokens=False),
                "finish_reason": "stop" if ids and ids[-1] in eos else "length",
                "score": old.score(content, row["gold"]),
            }
            path = output / (row["id"] + ".json")
            if path.exists():
                result = data.read_json(path)
            else:
                data.write_once(path, result)
            results.append(result)
    if any(r["evaluation_identity"] != binding["evaluation_identity"] for r in results):
        raise ValueError("stored long evaluation row identity changed")
    summary = {
        "evaluation_identity": binding["evaluation_identity"],
        "arrays": len(results),
        "records": sum(len(r["gold"]) for r in results),
        "valid_arrays": sum(r["score"]["array_valid"] for r in results),
        "canonical_correct": sum(sum(r["score"]["correct"]) for r in results),
        "truncated_arrays": sum(r["finish_reason"] == "length" for r in results),
        "position_quartiles": position_metrics(results),
        "primary": "Strict full-array canonical score; no repair/fallback",
    }
    if not (output / "SUMMARY.json").exists():
        data.write_once(output / "SUMMARY.json", summary)
    return summary


def train(arm, attempt, resume):
    import torch
    from peft import PeftModel
    from safetensors.torch import load_file
    from transformers import AutoModelForCausalLM

    recipe, prepared, manifest = bound(arm)
    environment = {
        "python": platform.python_version(),
        **{
            n: importlib.metadata.version(n)
            for n in ("torch", "transformers", "peft", "safetensors")
        },
    }
    if environment != recipe["environment"]:
        raise ValueError("pinned training environment changed")
    if (
        not os.environ.get("CUDA_VISIBLE_DEVICES")
        or not torch.cuda.is_available()
        or torch.cuda.device_count() != 1
    ):
        raise ValueError("parent must assign exactly one released GPU")
    if attempt.exists() != resume:
        raise ValueError("existing attempt requires explicit resume; fresh attempt must not exist")
    attempt.mkdir(parents=True, exist_ok=resume)
    identity = manifest["identity"]
    if (attempt / "INPUTS.json").exists():
        if data.read_json(attempt / "INPUTS.json")["identity"] != identity:
            raise ValueError("attempt identity changed")
    else:
        data.write_once(attempt / "INPUTS.json", manifest)
    if (attempt / "RESULT.json").exists():
        raise ValueError("completed attempt cannot be relaunched")
    lengths = [len(e) for e in prepared["train"]]
    checkpoints = sorted(attempt.glob("checkpoint-[0-9][0-9][0-9][0-9]"))
    restored = checkpoints[-1] if checkpoints else None
    state = (
        old.checkpoint_state(restored, identity, lengths)
        if restored
        else {
            "identity": identity,
            "step": 0,
            "epoch": 0,
            "cursor": 0,
            "training_seconds": 0.0,
            "step_metrics": [],
        }
    )
    random.seed(recipe["train_seed"])
    torch.manual_seed(recipe["train_seed"])
    torch.cuda.manual_seed_all(recipe["train_seed"])
    torch.set_num_threads(4)
    torch.cuda.reset_peak_memory_stats()
    tokenizer = data.load_tokenizer()
    base = AutoModelForCausalLM.from_pretrained(
        data.BASE,
        local_files_only=True,
        dtype=torch.bfloat16,
        attn_implementation="sdpa",
        device_map={"": "cuda:0"},
    )
    adapter = restored or data.ADAPTER
    model = PeftModel.from_pretrained(base, adapter, is_trainable=True, autocast_adapter_dtype=True)
    audit = old.audit(model, adapter)
    trainable = [(n, p) for n, p in model.named_parameters() if p.requires_grad]
    if not trainable or any("lora_" not in n or p.dtype != torch.float32 for n, p in trainable):
        raise ValueError("only original FP32 LoRA tensors may train")
    data.write_once(
        attempt / f"load-audit-{uuid.uuid4().hex}.json",
        {
            **audit,
            "adapter": str(adapter),
            "gpu": torch.cuda.get_device_name(),
            "cuda": torch.version.cuda,
            "environment": environment,
        },
    )
    optimizer = torch.optim.AdamW([p for _, p in trainable], lr=recipe["lr"], weight_decay=0.0)
    if restored:
        optimizer.load_state_dict(
            torch.load(restored / "optimizer.pt", map_location="cuda:0", weights_only=True)
        )
        rng = torch.load(restored / "rng_state.pt", map_location="cpu", weights_only=True)
        torch.set_rng_state(rng["torch"])
        torch.cuda.set_rng_state_all(rng["cuda"])
        random.setstate(rng["python"])
        if {int(v["step"]) for v in optimizer.state.values() if "step" in v} != {state["step"]}:
            raise ValueError("optimizer actual step differs")
    candidates = []
    for epoch, rows in enumerate(prepared["train"]):
        epoch_step = sum(math.ceil(n / 16) for n in lengths[: epoch + 1])
        checkpoint = attempt / f"checkpoint-{epoch_step:04d}"
        validation_path = attempt / f"epoch-{epoch + 1}-validation"
        if epoch >= state["epoch"]:
            model.train()
            model.config.use_cache = False
            model.enable_input_require_grads()
            model.gradient_checkpointing_enable(
                gradient_checkpointing_kwargs={"use_reentrant": False}
            )
            for cursor in range(state["cursor"], len(rows), 16):
                started = time.monotonic()
                remaining = recipe["training_wall_seconds"] - state["training_seconds"]
                if remaining <= 0:
                    raise TimeoutError("3600-second optimization cap exhausted")

                def timeout(_sig, _frame):
                    raise TimeoutError("3600-second optimization cap; saved checkpoints retained")

                signal.signal(signal.SIGALRM, timeout)
                signal.setitimer(signal.ITIMER_REAL, remaining)
                chunk = rows[cursor : cursor + 16]
                metrics = supervised_step(model, optimizer, chunk, tokenizer.pad_token_id)
                torch.cuda.synchronize()
                signal.setitimer(signal.ITIMER_REAL, 0)
                next_cursor = cursor + len(chunk)
                finished = next_cursor == len(rows)
                state = {
                    **state,
                    "step": state["step"] + 1,
                    "epoch": epoch + 1 if finished else epoch,
                    "cursor": 0 if finished else next_cursor,
                    "training_seconds": state["training_seconds"] + time.monotonic() - started,
                    "step_metrics": state["step_metrics"]
                    + [
                        {
                            **metrics,
                            "step": state["step"] + 1,
                            "epoch": epoch + 1,
                            "arrays": len(chunk),
                            "group_ids": [g for r in chunk for g in r["group_ids"]],
                            "prompt_tokens": sum(len(r["prompt_ids"]) for r in chunk),
                            "padded_input_tokens": sum(
                                len(chunk[i : i + 2])
                                * max(len(r["input_ids"]) for r in chunk[i : i + 2])
                                for i in range(0, len(chunk), 2)
                            ),
                        }
                    ],
                }
                old.validate_cursor(state, identity, lengths)
                if state["step"] % 16 == 0 or finished:
                    old.save_checkpoint(model, optimizer, attempt, state)
                print(
                    __import__("json").dumps(
                        {k: state[k] for k in ("step", "epoch", "cursor", "training_seconds")}
                    ),
                    flush=True,
                )
        if (validation_path / "SUMMARY.json").exists():
            validation = data.read_json(validation_path / "SUMMARY.json")
        elif state["epoch"] == epoch + 1 and state["cursor"] == 0:
            validation = old.evaluate(
                model,
                tokenizer,
                prepared["validation"],
                validation_path,
                identity,
                checkpoint,
                with_nll=True,
            )
        else:
            raise ValueError("missing validation from an earlier completed epoch")
        candidates.append(
            {"epoch": epoch + 1, "checkpoint": str(checkpoint), "validation": validation}
        )
    selected = final_selection(candidates)
    decision = {
        "identity": identity,
        "rule": recipe["selection"],
        "selected": selected,
        "candidates": candidates,
        "post_training_test_inspected": False,
    }
    if not (attempt / "SELECTION.json").exists():
        data.write_once(attempt / "SELECTION.json", decision)
    elif data.read_json(attempt / "SELECTION.json") != decision:
        raise ValueError("final checkpoint declaration changed")
    test = old.evaluate(
        model,
        tokenizer,
        prepared["test"],
        attempt / "final-test",
        identity,
        Path(selected["checkpoint"]),
        with_nll=False,
    )
    transfer = evaluate_long(
        model,
        tokenizer,
        prepared["transfer64"],
        attempt / "final-transfer64",
        identity,
        Path(selected["checkpoint"]),
    )
    starting, final = (
        load_file(data.ADAPTER / "adapter_model.safetensors"),
        load_file(Path(selected["checkpoint"]) / "adapter_model.safetensors"),
    )
    delta = math.sqrt(
        sum(float((final[k] - starting[k]).double().square().sum()) for k in starting)
    )
    actual_steps = {int(v["step"]) for v in optimizer.state.values() if "step" in v}
    actual_exposures = sum(len(r["group_ids"]) for r in state["step_metrics"])
    if actual_steps != {state["step"]} or actual_exposures != 10130:
        raise ValueError("actual optimizer steps or record exposures differ")
    if not math.isfinite(delta) or delta <= 0:
        raise ValueError("finite nonzero adapter delta required; checkpoints retained")
    result = {
        "identity": identity,
        "selected": selected,
        "test": test,
        "transfer64": transfer,
        "baseline_test": data.read_json(SFT / "outputs/attempt-001/baseline-test/SUMMARY.json"),
        "optimizer_steps": state["step"],
        "training_seconds": state["training_seconds"],
        "actual_optimizer_steps": sorted(
            {int(v["step"]) for v in optimizer.state.values() if "step" in v}
        ),
        "parameter_delta_l2": delta,
        "peak_allocated_bytes": torch.cuda.max_memory_allocated(),
        "peak_reserved_bytes": torch.cuda.max_memory_reserved(),
        "record_exposures": actual_exposures,
        "compute": manifest["epochs"],
    }
    data.write_once(attempt / "RESULT.json", result)
    return result


def evaluate(arm, size):
    import torch
    from peft import PeftModel
    from transformers import AutoModelForCausalLM

    _, prepared, manifest = bound(arm)
    attempt = ROOT / arm / "outputs/attempt-001"
    checkpoint = Path(data.read_json(attempt / "SELECTION.json")["selected"]["checkpoint"])
    old.checkpoint_state(checkpoint, manifest["identity"], [len(e) for e in prepared["train"]])
    if (
        not os.environ.get("CUDA_VISIBLE_DEVICES")
        or not torch.cuda.is_available()
        or torch.cuda.device_count() != 1
    ):
        raise ValueError("parent must assign exactly one released GPU")
    torch.set_num_threads(4)
    base = AutoModelForCausalLM.from_pretrained(
        data.BASE,
        local_files_only=True,
        dtype=torch.bfloat16,
        attn_implementation="sdpa",
        device_map={"": "cuda:0"},
    )
    model = PeftModel.from_pretrained(
        base, checkpoint, is_trainable=False, autocast_adapter_dtype=True
    )
    old.audit(model, checkpoint)
    return evaluate_long(
        model,
        data.load_tokenizer(),
        prepared["test_by_size"][str(size)],
        attempt / f"test-size{size}",
        manifest["identity"],
        checkpoint,
    )


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command", choices=("prepare", "preflight", "train", "evaluate"))
    parser.add_argument("--arm", choices=("A", "B"), required=True)
    parser.add_argument("--resume", action="store_true")
    parser.add_argument("--size", type=int, choices=(1, 5, 16, 32, 64), default=64)
    args = parser.parse_args()
    if args.command == "prepare":
        result = prepare(args.arm)
    elif args.command == "preflight":
        result = bound(args.arm)[2]
    elif args.command == "evaluate":
        result = evaluate(args.arm, args.size)
    else:
        attempt = ROOT / args.arm / "outputs/attempt-001"
        try:
            result = train(args.arm, attempt, args.resume)
        except BaseException as error:
            signal.setitimer(signal.ITIMER_REAL, 0)
            if attempt.exists():
                data.write_once(
                    attempt / f"FAILURE-{uuid.uuid4().hex}.json",
                    {
                        "type": type(error).__name__,
                        "message": str(error),
                        "traceback": traceback.format_exc(),
                    },
                )
            raise
    print(__import__("json").dumps(result, sort_keys=True))


if __name__ == "__main__":
    main()
