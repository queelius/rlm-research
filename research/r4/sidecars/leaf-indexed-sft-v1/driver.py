"""Indexed authoritative leaf SFT using a privately loaded, pinned mixed-size loop."""

from __future__ import annotations

import argparse
import gc
import hashlib
import importlib.util
import json
import math
import os
import sys
import time
import traceback
import uuid
from pathlib import Path

ROOT = Path(__file__).resolve().parent
SIDECARS = ROOT.parent
MIXED = SIDECARS / "leaf-mixed-size-sft-v1"
SFT = SIDECARS / "trec-leaf-sft-v1"
PINNED = {
    MIXED
    / "driver.py": "1a063bedc6882354736e822595472d8269211007aa92ff3fa8f3d487b7c5b708",
    MIXED
    / "B/RECIPE.json": "cb5a3e64168931239ab8fa1e651738506324b0c279ea2277a7eaecc4238d9718",
    MIXED
    / "B/MANIFEST.json": "ae230378c83b548ea8ad27c6f128cdb8c37f76f6a9acd3454ec7b69751401847",
    SIDECARS
    / "leaf-correspondence-controls-v1/driver.py": "6fa2846b144f863cea79f2c82ee9e6d07d00104aba4f01dc8d95ec51fd1a49c8",
}
for path, want in PINNED.items():
    if hashlib.sha256(path.read_bytes()).hexdigest() != want:
        raise ValueError(f"pinned source changed: {path}")
spec = importlib.util.spec_from_file_location(
    "indexed_private_mixed_loop", MIXED / "driver.py"
)
mixed = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = mixed
spec.loader.exec_module(mixed)
data = mixed.data

INSTRUCTION = (
    "Return only a JSON object mapping every input ID to its one label. "
    "Include each input ID exactly once, with no missing or extra IDs. "
    "Emit entries in input order. Allowed labels: \n"
)


def unique_object(pairs):
    value = {}
    for key, item in pairs:
        if key in value:
            raise ValueError("duplicate ID")
        value[key] = item
    return value


def score(content, row):
    if row["representation"] == "anonymous":
        return mixed.old.score(content, row["gold"])
    status = "valid"
    try:
        parsed = json.loads(content, object_pairs_hook=unique_object)
    except (ValueError, TypeError):
        parsed = None
    if "<tool_call>" in (content or ""):
        status = "tool_call"
    elif not isinstance(parsed, dict):
        status = "invalid_json_or_duplicate_ids"
    elif set(parsed) != set(row["record_ids"]):
        status = "id_coverage_mismatch"
    elif any(
        not isinstance(v, str) or v not in data.LABELS.values() for v in parsed.values()
    ):
        status = "noncanonical_label"
    predictions = (
        [parsed[key] for key in row["record_ids"]]
        if status == "valid"
        else [None] * len(row["gold"])
    )
    return {
        "array_valid": status == "valid",
        "status": status,
        "predictions": predictions,
        "correct": [a == b for a, b in zip(predictions, row["gold"], strict=True)],
        "emitted_id_order": list(parsed) if isinstance(parsed, dict) else None,
        "input_order_emitted": list(parsed) == row["record_ids"]
        if isinstance(parsed, dict)
        else False,
    }


def render(records, tokenizer, split, epoch, batch_id, representation):
    row = data.render(records, tokenizer, split, epoch, batch_id)
    ids = [f"q{i + 1:04d}" for i in range(len(records))]
    row.update(
        id=f"{split}-{representation}-e{epoch}-b{batch_id:04d}",
        representation=representation,
        record_ids=ids,
    )
    if representation == "anonymous":
        return row
    if representation != "indexed":
        raise ValueError("unknown representation")
    frozen = data.read_json(
        SFT / "../trec-leaf-contract-probe-v1/FROZEN_REPLAY_SPEC.json"
    )["design"]
    contract = frozen["contract"]
    # Replace the array contract in full; keep generic system/tools/definitions unchanged.
    row["messages"][1]["content"] = (
        INSTRUCTION
        + ", ".join(frozen["labels"])
        + ".\n\n"
        + frozen["definitions"]
        + "\n"
        + json.dumps(dict(zip(ids, [r["question"] for r in records], strict=True)))
    )
    row["target"] = json.dumps(dict(zip(ids, row["gold"], strict=True)))
    prompt = tokenizer.apply_chat_template(
        row["messages"],
        tools=contract["tools"],
        tokenize=False,
        add_generation_prompt=True,
    )
    full = tokenizer.apply_chat_template(
        row["messages"] + [{"role": "assistant", "content": row["target"]}],
        tools=contract["tools"],
        tokenize=False,
        add_generation_prompt=False,
    )
    prompt_ids = tokenizer.encode(prompt, add_special_tokens=False)
    full_ids = tokenizer.encode(full, add_special_tokens=False)
    if tokenizer.eos_token_id not in full_ids[len(prompt_ids) :]:
        raise ValueError("missing native terminator")
    row.update(
        prompt=prompt,
        prompt_ids=prompt_ids,
        native_target_suffix=full[len(prompt) :],
        **data.causal_example(prompt_ids, full_ids),
    )
    return row


def prepare():
    if (ROOT / "prepared").exists():
        raise ValueError("preparation requires unused destination")
    recipe, previous, bmanifest = mixed.bound("B")
    partitions = data.load_partitions()
    tokenizer = data.load_tokenizer()
    epochs = []
    for epoch, batches in enumerate(
        mixed.allocate(partitions["train"], (1, 5, 16, 64)), 1
    ):
        rows = []
        for i, batch in enumerate(batches):
            row = render(batch["records"], tokenizer, "train", epoch, i, "indexed")
            row.update(
                {key: batch[key] for key in ("nominal_size", "bucket", "residual")}
            )
            oldrow = previous["train"][epoch - 1][i]
            if (
                row["group_ids"] != oldrow["group_ids"]
                or row["nominal_size"] != oldrow["nominal_size"]
            ):
                raise ValueError("B training allocation/order changed")
            rows.append(row)
        epochs.append(rows)
    prepared = {"train": epochs}
    for split in ("validation", "test"):
        prepared[split] = []
        for representation in ("anonymous", "indexed"):
            for i, oldrow in enumerate(previous[split]):
                row = render(oldrow["records"], tokenizer, split, 0, i, representation)
                if representation == "anonymous" and (
                    row["prompt_ids"] != oldrow["prompt_ids"]
                    or row["gold"] != oldrow["gold"]
                ):
                    raise ValueError("original fixed5 readout changed")
                prepared[split].append(row)
    composition_path = SIDECARS / "leaf-composition-transfer-v1/prepared-v1/DATA.json"
    data.authenticate(
        {
            composition_path: "1ea4640da5a8e3e305bee7f79d5abeecb02507d6bcc33d709d1c7209fd47bfc2"
        }
    )
    contexts = data.read_json(composition_path)["contexts"]
    prepared["transfer64"] = [
        render(c["records"], tokenizer, "transfer64", 0, i, rep)
        for rep in ("anonymous", "indexed")
        for i, c in enumerate(contexts)
    ]
    for rows in [
        *epochs,
        prepared["validation"],
        prepared["test"],
        prepared["transfer64"],
    ]:
        for row in rows:
            cap = 3072 if row in prepared["transfer64"] else 256
            if len(row["prompt_ids"]) + cap > 8192:
                raise ValueError("evaluation input/output context cap exceeded")
    baselines = {}
    for name, attempt, expected in [
        (
            "old_sft",
            SFT / "outputs/attempt-001",
            "c32de1293c01bba5104eb1f123867649c71dd38e5194661ace4b17dcbbe66ba3",
        ),
        (
            "Bfinal",
            MIXED / "B/outputs/attempt-001",
            "59ad854293142161f6b5e613dd5d1e3630fed600637106d5eae2cbcd764e9200",
        ),
    ]:
        result = data.read_json(attempt / "RESULT.json")
        checkpoint = Path(result["selected"]["checkpoint"])
        data.authenticate({checkpoint / "adapter_model.safetensors": expected})
        saved = data.read_json(checkpoint / "state.json")
        data.authenticate({checkpoint / k: v for k, v in saved["files_sha256"].items()})
        selection = data.read_json(attempt / "SELECTION.json")
        if selection["selected"]["checkpoint"] != str(checkpoint):
            raise ValueError("baseline selected checkpoint differs")
        baselines[name] = {
            "checkpoint": str(checkpoint),
            "adapter_sha256": expected,
            "result_path": str(attempt / "RESULT.json"),
            "result_sha256": data.file_hash(attempt / "RESULT.json"),
            "selection_path": str(attempt / "SELECTION.json"),
            "selection_sha256": data.file_hash(attempt / "SELECTION.json"),
            "checkpoint_state_sha256": data.file_hash(checkpoint / "state.json"),
        }
    sources = dict(recipe["source_hashes"])
    sources.update(
        {
            str(p): data.file_hash(p)
            for p in [
                *PINNED,
                Path(__file__),
                ROOT / "test_driver.py",
                ROOT / "launch.py",
                ROOT / "test_launch.py",
                ROOT / "DESIGN.md",
                composition_path,
            ]
        }
    )
    recipe.update(
        schema="leaf-indexed-sft-v1",
        arm="indexed",
        source_hashes=sources,
        questions_per_array=[1, 5, 16, 64],
        selection="Fixed final epoch2; validation monitored, never selects checkpoint",
        representation="Batch-local q0001..qNNNN input and output maps; no grammar in SFT",
        evaluation="Both natural anonymous/indexed fixed5 readouts; matched free HF3072 final64 old/B/new",
        training_wall_seconds=3600,
        overall_wall_seconds=5400,
        baseline_bindings=baselines,
        prior_B_manifest_identity=bmanifest["identity"],
        compute_matched_to_B=False,
    )
    manifest = {
        "schema": "indexed-sft-prepared-v1",
        "epochs": [mixed.stats(r) for r in epochs],
        "record_exposures": 10130,
        "split_counts": {k: len(v) for k, v in partitions.items()},
        "optimizer_steps": sum(math.ceil(len(r) / 16) for r in epochs),
        "comparison_models": ["old_sft", "Bfinal", "indexed_final"],
        "evaluation_representations": ["anonymous", "indexed"],
        "evaluation_cap_fixed5": 256,
        "evaluation_cap64": 3072,
        "training_template_and_all_evaluation_tools_identical": True,
        "historical_evaluation_caution": "Fresh physical prompt-ID matched comparisons, not pooled with older probe/native calls.",
    }
    (ROOT / "prepared").mkdir()
    data.write_once(ROOT / "prepared/RECIPE.json", recipe)
    data.write_once(ROOT / "prepared/data.json", prepared)
    manifest.update(
        recipe_sha256=data.file_hash(ROOT / "prepared/RECIPE.json"),
        data_sha256=data.file_hash(ROOT / "prepared/data.json"),
    )
    manifest["identity"] = data.digest(manifest)
    data.write_once(ROOT / "prepared/MANIFEST.json", manifest)
    return manifest


def bound(_arm=None):
    manifest = data.read_json(ROOT / "prepared/MANIFEST.json")
    if (
        data.digest({k: v for k, v in manifest.items() if k != "identity"})
        != manifest["identity"]
    ):
        raise ValueError("prepared identity changed")
    data.authenticate(
        {
            ROOT / "prepared/RECIPE.json": manifest["recipe_sha256"],
            ROOT / "prepared/data.json": manifest["data_sha256"],
        }
    )
    recipe = data.read_json(ROOT / "prepared/RECIPE.json")
    data.authenticate(recipe["source_hashes"])
    return recipe, data.read_json(ROOT / "prepared/data.json"), manifest


def evaluate_rows(
    model,
    tokenizer,
    rows,
    output,
    identity,
    adapter,
    *,
    with_nll=False,
    max_new_tokens=256,
):
    import torch

    output.mkdir(exist_ok=True)
    binding = {
        "identity": identity,
        "adapter_sha256": data.file_hash(adapter / "adapter_model.safetensors"),
        "rows": [r["id"] for r in rows],
        "greedy": True,
        "microbatch": 2,
        "max_new_tokens": max_new_tokens,
        "with_nll": with_nll,
        "score": "strict per declared representation; no repair or schema",
    }
    evaluation_identity = data.digest(binding)
    if (output / "MANIFEST.json").exists():
        if data.read_json(output / "MANIFEST.json") != binding:
            raise ValueError("evaluation binding changed")
    else:
        data.write_once(output / "MANIFEST.json", binding)
    model.eval()
    model.gradient_checkpointing_disable()
    eos = model.generation_config.eos_token_id
    eos = set(eos if isinstance(eos, list) else [eos])
    results = []
    for start in range(0, len(rows), 2):
        chunk = rows[start : start + 2]
        paths = [output / (r["id"] + ".json") for r in chunk]
        if all(p.exists() for p in paths):
            results.extend(data.read_json(p) for p in paths)
            continue
        batch = {
            k: v.to(model.device)
            for k, v in data.generation_batch(
                [r["prompt_ids"] for r in chunk], tokenizer.pad_token_id
            ).items()
        }
        started = time.monotonic()
        with torch.inference_mode():
            generated = model.generate(
                **batch,
                do_sample=False,
                max_new_tokens=max_new_tokens,
                pad_token_id=tokenizer.pad_token_id,
                use_cache=True,
            )
        sequences = data.continuations(
            generated, batch["input_ids"].shape[1], eos, tokenizer.pad_token_id
        )
        elapsed = time.monotonic() - started
        for row, ids, path in zip(chunk, sequences, paths, strict=True):
            content = tokenizer.decode(
                ids[:-1] if ids and ids[-1] in eos else ids, skip_special_tokens=False
            )
            scored = score(content, row)
            result = {
                "id": row["id"],
                "evaluation_identity": evaluation_identity,
                "representation": row["representation"],
                "gold": row["gold"],
                "group_ids": row["group_ids"],
                "record_ids": row["record_ids"],
                "prompt_token_ids": row["prompt_ids"],
                "content": content,
                "raw_generation": tokenizer.decode(ids, skip_special_tokens=False),
                "generated_token_ids": ids,
                "finish_reason": "stop" if ids and ids[-1] in eos else "length",
                "prompt_tokens": len(row["prompt_ids"]),
                "generated_tokens": len(ids),
                "batch_generation_seconds": elapsed,
                "score": scored,
                "outcomes": [
                    {"group_id": g, "gold": gold, "prediction": pred, "correct": ok}
                    for g, gold, pred, ok in zip(
                        row["group_ids"],
                        row["gold"],
                        scored["predictions"],
                        scored["correct"],
                        strict=True,
                    )
                ],
            }
            if path.exists():
                result = data.read_json(path)
            else:
                data.write_once(path, result)
            results.append(result)
    if any(r["evaluation_identity"] != evaluation_identity for r in results):
        raise ValueError("stored evaluation identity changed")
    nll = None
    if with_nll:
        total = count = 0
        with torch.inference_mode():
            for start in range(0, len(rows), 2):
                batch = {
                    k: v.to(model.device)
                    for k, v in data.collate(
                        rows[start : start + 2], tokenizer.pad_token_id
                    ).items()
                }
                labels = batch.pop("labels")
                loss, n = mixed.old.loss_sum(
                    model(**batch, use_cache=False).logits, labels
                )
                total += float(loss)
                count += n
        nll = total / count
        if not math.isfinite(nll):
            raise ValueError("nonfinite validation NLL")
    summary = {
        **mixed.old.summarize(results, nll),
        "evaluation_identity": evaluation_identity,
        "unique_groups": len({g for r in rows for g in r["group_ids"]}),
        "by_representation": {},
    }
    for rep in ("anonymous", "indexed"):
        selected = [r for r in results if r["representation"] == rep]
        if selected:
            summary["by_representation"][rep] = {
                **mixed.old.summarize(selected, None),
                "truncated_arrays": sum(
                    r["finish_reason"] == "length" for r in selected
                ),
                "exact_arrays": sum(all(r["score"]["correct"]) for r in selected),
                "position_quartiles": mixed.position_metrics(selected),
            }
    if (output / "SUMMARY.json").exists():
        return data.read_json(output / "SUMMARY.json")
    data.write_once(output / "SUMMARY.json", summary)
    return summary


def evaluate_long(model, tokenizer, rows, output, identity, checkpoint):
    return evaluate_rows(
        model, tokenizer, rows, output, identity, checkpoint, max_new_tokens=3072
    )


def baseline(name, attempt, recipe, prepared, identity):
    import torch
    from peft import PeftModel
    from transformers import AutoModelForCausalLM

    binding = recipe["baseline_bindings"][name]
    checkpoint = Path(binding["checkpoint"])
    data.authenticate(
        {
            checkpoint / "adapter_model.safetensors": binding["adapter_sha256"],
            checkpoint / "state.json": binding["checkpoint_state_sha256"],
            binding["result_path"]: binding["result_sha256"],
            binding["selection_path"]: binding["selection_sha256"],
        }
    )
    state = data.read_json(checkpoint / "state.json")
    data.authenticate({checkpoint / k: v for k, v in state["files_sha256"].items()})
    gc.collect()
    torch.cuda.empty_cache()
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
    audit = mixed.old.audit(model, checkpoint)
    target = attempt / name
    target.mkdir(exist_ok=True)
    data.write_once(target / f"load-audit-{uuid.uuid4().hex}.json", audit)
    tokenizer = data.load_tokenizer()
    answer = {
        "checkpoint": str(checkpoint),
        "adapter_sha256": binding["adapter_sha256"],
        "test": evaluate_rows(
            model, tokenizer, prepared["test"], target / "test", identity, checkpoint
        ),
        "transfer64": evaluate_long(
            model,
            tokenizer,
            prepared["transfer64"],
            target / "transfer64",
            identity,
            checkpoint,
        ),
    }
    del model, base
    gc.collect()
    torch.cuda.empty_cache()
    return answer


def train(attempt, resume=False):
    import torch

    recipe, prepared, manifest = bound()
    if (
        not os.environ.get("CUDA_VISIBLE_DEVICES")
        or not torch.cuda.is_available()
        or torch.cuda.device_count() != 1
    ):
        raise ValueError("parent must assign exactly one released GPU")
    # Only this private imported module is changed; frozen sources/processes are untouched.
    mixed.bound = bound
    mixed.old.evaluate = evaluate_rows
    mixed.evaluate_long = evaluate_long
    result_path = attempt / "RESULT.json"
    if result_path.exists():
        if not resume:
            raise ValueError("completed training needs explicit comparison resume")
        result = data.read_json(result_path)
        if result["identity"] != manifest["identity"]:
            raise ValueError("attempt identity changed")
        mixed.old.checkpoint_state(
            Path(result["selected"]["checkpoint"]),
            manifest["identity"],
            [len(e) for e in prepared["train"]],
        )
    else:
        result = mixed.train("indexed", attempt, resume)
    if (attempt / "COMPARISON.json").exists():
        raise ValueError("complete comparison cannot be rerun")
    comparisons = {
        "indexed_final": {
            "checkpoint": result["selected"]["checkpoint"],
            "test": result["test"],
            "transfer64": result["transfer64"],
        }
    }
    for name in ("old_sft", "Bfinal"):
        comparisons[name] = baseline(
            name, attempt, recipe, prepared, manifest["identity"]
        )
    complete = {
        "identity": manifest["identity"],
        "fixed_final_epoch": 2,
        "models": comparisons,
        "no_test_selection": True,
        "same_prepared_prompt_ids_across_weights": True,
        "training_result_sha256": data.file_hash(result_path),
    }
    data.write_once(attempt / "COMPARISON.json", complete)
    return complete


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command", choices=("prepare", "preflight", "train"))
    parser.add_argument("--attempt", type=Path, default=ROOT / "outputs/attempt-001")
    parser.add_argument("--resume", action="store_true")
    args = parser.parse_args()
    if args.command == "prepare":
        result = prepare()
    elif args.command == "preflight":
        result = bound()[2]
    else:
        try:
            result = train(args.attempt, args.resume)
        except BaseException as error:
            if args.attempt.exists():
                data.write_once(
                    args.attempt / f"FAILURE-{uuid.uuid4().hex}.json",
                    {
                        "type": type(error).__name__,
                        "message": str(error),
                        "traceback": traceback.format_exc(),
                    },
                )
            raise
    print(json.dumps(result, sort_keys=True))


if __name__ == "__main__":
    main()
