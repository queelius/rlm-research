"""Fresh B-only HF replay of two exact saved physical prompt templates."""

from __future__ import annotations

import argparse
import importlib.metadata
import importlib.util
import json
import os
import platform
import signal
import time
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parent
SIDE = ROOT.parent
MIXED_PATH = SIDE / "leaf-mixed-size-sft-v1/driver.py"
MIXED_SHA = "1a063bedc6882354736e822595472d8269211007aa92ff3fa8f3d487b7c5b708"
SST_PATH = SIDE / "leaf-sentiment-transfer-v1/driver.py"
SST_SHA = "eb9509ed00a85cd942d959407deb8c80f495f7fec2426f477265af48e407cb63"
PROBE = MIXED_PATH.parent / "PROBE_SPEC.json"
PROBE_SHA = "20765531fdeac3d832dcbc7673ea313fb4eff6c34dae63bd1d47d5dfd91c9608"
ARM = MIXED_PATH.parent / "B"
CHECKPOINT = ARM / "outputs/attempt-001/checkpoint-0204"
ADAPTER_SHA = "59ad854293142161f6b5e613dd5d1e3630fed600637106d5eae2cbcd764e9200"


def load_owned(name: str, path: Path, expected: str):
    import hashlib

    with path.open("rb") as stream:
        if hashlib.file_digest(stream, "sha256").hexdigest() != expected:
            raise ValueError("authenticated helper changed")
    loader = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(loader)
    loader.loader.exec_module(module)
    return module


mixed = load_owned("template_replay_owned_mixed_helpers", MIXED_PATH, MIXED_SHA)
sst = load_owned("template_replay_owned_authentication", SST_PATH, SST_SHA)
data = mixed.data
read, write_once, digest, file_hash = data.read_json, data.write_once, data.digest, data.file_hash


def environment() -> dict:
    return {
        "python": platform.python_version(),
        **{
            name: importlib.metadata.version(name)
            for name in ("torch", "transformers", "peft", "safetensors")
        },
    }


def check_identity(spec: dict) -> None:
    if spec["identity"] != digest({k: v for k, v in spec.items() if k != "identity"}):
        raise ValueError("outer identity changed")


def tool_parts(text: str):
    before, tail = text.split("<tools>\n", 1)
    tools, after = tail.split("\n</tools>", 1)
    return before, tools, after


def build_spec() -> dict:
    if file_hash(PROBE) != PROBE_SHA:
        raise ValueError("frozen probe changed")
    recipe = read(ARM / "RECIPE.json")
    if environment() != recipe["environment"]:
        raise ValueError("requires exact trained HF environment")
    state = read(CHECKPOINT / "state.json")
    sources = {}
    descriptor = {
        "adapter": {
            "path": str(CHECKPOINT),
            "model_sha256": ADAPTER_SHA,
            "config_sha256": state["files_sha256"]["adapter_config.json"],
        },
        "base_model": {
            "path": str(data.BASE),
            "manifest_sha256": "19619b44b0bd30bf5debe0960e6dfd6acc5be8287c581727456aa5d17699c18f",
        },
    }
    sst.authenticate_weight("B", descriptor, sources)
    prepared = read(ARM / "data.json")["transfer64"]
    probe = read(PROBE)
    if len(prepared) != 6 or len(probe["requests"]) != 6:
        raise ValueError("requires the same six frozen transfer contexts")
    tokenizer = data.load_tokenizer()
    training_tools = read(data.CONTRACT / "FROZEN_REPLAY_SPEC.json")["design"]["contract"]["tools"]
    rows, proof = [], []
    for index, (source, request) in enumerate(zip(prepared, probe["requests"], strict=True)):
        rendered = data.render(source["records"], tokenizer, "transfer64", 0, index)
        training_ids = rendered["prompt_ids"]
        prompt = request["request"]
        text = tokenizer.apply_chat_template(
            prompt["messages"], tools=prompt["tools"], tokenize=False, add_generation_prompt=True
        )
        probe_ids = tokenizer.encode(text, add_special_tokens=False)
        if (
            training_ids != source["training_template_prompt_ids"]
            or probe_ids != source["prompt_ids"]
            or probe_ids != request["hf_prompt_ids"]
            or rendered["messages"] != prompt["messages"]
            or rendered["messages"] != source["messages"]
            or rendered["gold"] != source["gold"]
            or source["gold"] != request["gold"]
            or training_tools != prompt["tools"]
        ):
            raise ValueError("saved/reconstructed physical template or semantic input changed")
        tr = tokenizer.decode(training_ids, skip_special_tokens=False)
        pr = tokenizer.decode(probe_ids, skip_special_tokens=False)
        tb, tt, ta = tool_parts(tr)
        pb, pt, pa = tool_parts(pr)
        if (
            tb != pb
            or ta != pa
            or json.loads(tt) != json.loads(pt)
            or list(json.loads(tt)) != ["type", "function"]
            or list(json.loads(pt)) != ["function", "type"]
            or training_ids == probe_ids
            or len(training_ids) != len(probe_ids)
        ):
            raise ValueError("difference is not exactly declared tool-key serialization")
        proof.append(
            {
                "context_id": request["context_id"],
                "training_render_exact": True,
                "probe_render_exact": True,
                "only_tool_key_serialization_differs": True,
                "prompt_tokens": len(probe_ids),
                "training_prompt_sha256": digest(training_ids),
                "probe_prompt_sha256": digest(probe_ids),
                "different_token_positions_0based": [
                    i
                    for i, (a, b) in enumerate(zip(training_ids, probe_ids, strict=True))
                    if a != b
                ],
            }
        )
        conditions = ["probe", "training"] if index % 2 == 0 else ["training", "probe"]
        for condition in conditions:
            ids = probe_ids if condition == "probe" else training_ids
            row = {
                "source_row_id": source["id"],
                "context_id": request["context_id"],
                "context_index": index,
                "microbatch_index": index,
                "condition": condition,
                "gold": source["gold"],
                "group_ids": source["group_ids"],
                "records": source["records"],
                "messages": source["messages"],
                "prompt_ids": ids,
            }
            row["id"] = digest([ROOT.name, ADAPTER_SHA, source["id"], condition, ids])
            rows.append(row)
    sources.update(
        {
            str(p): file_hash(p)
            for p in [
                Path(__file__),
                ROOT / "test_driver.py",
                ROOT / "DESIGN.md",
                ROOT / "PLAN.md",
                ROOT / "README.md",
                MIXED_PATH,
                SST_PATH,
                PROBE,
            ]
        }
    )
    spec = {
        "schema": ROOT.name,
        "checkpoint": str(CHECKPOINT),
        "adapter_sha256": ADAPTER_SHA,
        "checkpoint_authentication": descriptor,
        "environment": recipe["environment"],
        "rows": rows,
        "reconstruction": proof,
        "source_sha256": sources,
        "generation": {
            "do_sample": False,
            "max_new_tokens": 1024,
            "microbatch": 2,
            "use_cache": True,
            "base_dtype": "bfloat16",
            "adapter_autocast_dtype": True,
            "adapter_dtype": "float32",
            "attn_implementation": "sdpa",
        },
        "global_cap_seconds": 900,
        "seed": recipe["train_seed"],
        "fresh_calls": 12,
        "caution": "Six reused frozen test compositions/384 unique questions; fresh paired completions, no historical arm or repair.",
    }
    spec["identity"] = digest(spec)
    return spec


def verify_spec(spec: dict) -> None:
    check_identity(spec)
    data.authenticate(spec["source_sha256"])
    if spec != build_spec():
        raise ValueError("frozen replay differs from authenticated saved templates")


class AuditedModel:
    """A single-generate boundary wrapper, not a separate inference implementation."""

    def __init__(self, model, rows, pad_id, output, synchronize):
        self.model = model
        self.rows = rows
        self.pad_id = pad_id
        self.output = output
        self.synchronize = synchronize
        self.calls = 0

    def __getattr__(self, name):
        return getattr(self.model, name)

    def generate(self, **kwargs):
        if self.calls:
            raise ValueError("retry or multiple generation calls forbidden for this microbatch")
        actual = {k: kwargs[k].detach().cpu().tolist() for k in ("input_ids", "attention_mask")}
        expected = data.generation_batch([r["prompt_ids"] for r in self.rows], self.pad_id)
        if any(actual[k] != expected[k].tolist() for k in actual):
            raise ValueError("actual dispatched HF prompt differs from outer spec")
        if (
            kwargs.get("do_sample") is not False
            or kwargs.get("max_new_tokens") != 1024
            or kwargs.get("pad_token_id") != self.pad_id
            or kwargs.get("use_cache") is not True
        ):
            raise ValueError("decoder contract changed")
        self.calls += 1
        write_once(
            self.output / "GENERATE_INPUT.json",
            {
                **actual,
                "row_ids": [r["id"] for r in self.rows],
                "do_sample": False,
                "max_new_tokens": 1024,
                "use_cache": True,
                "logical_input_tokens": sum(len(r["prompt_ids"]) for r in self.rows),
                "padded_input_tokens": sum(len(r) for r in actual["input_ids"]),
            },
        )
        started = time.monotonic()
        try:
            generated = self.model.generate(**kwargs)
            self.synchronize()
        except BaseException as error:
            write_once(
                self.output / "GENERATE_ERROR.json",
                {
                    "type": type(error).__name__,
                    "wall_seconds": time.monotonic() - started,
                    "output_cost_unknown": True,
                },
            )
            raise
        write_once(
            self.output / "GENERATE_TIME.json",
            {"wall_seconds": time.monotonic() - started, "shared_microbatch_rows": len(self.rows)},
        )
        return generated


def summarize(spec: dict, output: Path) -> dict:
    coordinates = []
    for row in spec["rows"]:
        folder = output / "batches" / f"{row['microbatch_index']:02d}"
        path = folder / (row["id"] + ".json")
        result = read(path) if path.exists() else None
        score = result["score"] if result else None
        valid = bool(score and score["array_valid"])
        raw = None
        if result:
            try:
                raw = json.loads(result["content"])
            except (ValueError, TypeError):
                pass
        predictions = score["predictions"] if valid else [None] * 64
        coordinates.append(
            {
                "id": row["id"],
                "context_id": row["context_id"],
                "condition": row["condition"],
                "completed": result is not None,
                "array_valid": valid,
                "raw_array_length": len(raw) if isinstance(raw, list) else None,
                "aligned_records": 64 if valid else 0,
                "canonical_correct": sum(score["correct"]) if valid else 0,
                "strict_reward": int(valid and all(score["correct"])) if result else None,
                "finish_reason": result["finish_reason"] if result else None,
                "logical_input_tokens": len(row["prompt_ids"])
                if (folder / "GENERATE_INPUT.json").exists()
                else None,
                "completion_tokens": len(result["generated_token_ids"]) if result else None,
                "items": [
                    {
                        "group_id": g,
                        "position": i + 1,
                        "gold": gold,
                        "prediction": pred,
                        "aligned": valid,
                        "correct": pred == gold,
                    }
                    for i, (g, gold, pred) in enumerate(
                        zip(row["group_ids"], row["gold"], predictions, strict=True)
                    )
                ],
            }
        )
    cells = []
    for condition in ("probe", "training"):
        selected = [r for r in coordinates if r["condition"] == condition]
        aligned = [i for r in selected for i in r["items"] if i["aligned"]]
        cells.append(
            {
                "condition": condition,
                "planned_calls": 6,
                "completed_calls": sum(r["completed"] for r in selected),
                "valid_arrays": sum(r["array_valid"] for r in selected),
                "strict_successes": sum(r["strict_reward"] or 0 for r in selected),
                "aligned_records": len(aligned),
                "canonical_correct": sum(i["correct"] for i in aligned),
                "truncated_calls": sum(r["finish_reason"] == "length" for r in selected),
                "raw_lengths": [r["raw_array_length"] for r in selected],
                "position_quartiles": [
                    {
                        "first": start,
                        "aligned": sum(start <= i["position"] < start + 16 for i in aligned),
                        "correct": sum(
                            i["correct"] and start <= i["position"] < start + 16 for i in aligned
                        ),
                    }
                    for start in [1, 17, 33, 49]
                ],
                "confusion": [
                    {"gold": g, "prediction": p, "count": n}
                    for (g, p), n in sorted(
                        Counter((i["gold"], i["prediction"]) for i in aligned).items()
                    )
                ],
                "logical_input_tokens_observed": sum(
                    r["logical_input_tokens"] or 0 for r in selected
                ),
                "completion_tokens_observed": sum(r["completion_tokens"] or 0 for r in selected),
            }
        )
    pairs = []
    for index in range(6):
        selected = {
            r["condition"]: r
            for r in coordinates
            if r["context_id"] == spec["rows"][index * 2]["context_id"]
        }
        p, t = selected["probe"], selected["training"]
        observable = p["completed"] and t["completed"]
        aligned = p["array_valid"] and t["array_valid"]
        pairs.append(
            {
                "context_id": p["context_id"],
                "valid_array_difference": int(t["array_valid"]) - int(p["array_valid"])
                if observable
                else None,
                "strict_difference": t["strict_reward"] - p["strict_reward"]
                if observable
                else None,
                "canonical_correct_difference_when_jointly_aligned": t["canonical_correct"]
                - p["canonical_correct"]
                if aligned
                else None,
            }
        )
    return {
        "identity": spec["identity"],
        "cells": cells,
        "paired": pairs,
        "coordinates": coordinates,
        "caution": spec["caution"]
        + " Unaligned outputs are not64 semantic errors; infrastructure remains null. Per-batch generation time is shared, not additive per row.",
    }


def run(spec_path: Path, output: Path) -> int:
    spec = read(spec_path)
    output.mkdir(parents=True, exist_ok=False)
    (output / "batches").mkdir()
    write_once(output / "SPEC.json", spec)
    started = time.monotonic()

    def timeout(_sig, _frame):
        raise TimeoutError("900-second global replay cap")

    previous = signal.signal(signal.SIGALRM, timeout)
    signal.setitimer(signal.ITIMER_REAL, 900)
    reason = None
    try:
        verify_spec(spec)
        import torch
        from peft import PeftModel
        from transformers import AutoModelForCausalLM

        if (
            not os.environ.get("CUDA_VISIBLE_DEVICES")
            or not torch.cuda.is_available()
            or torch.cuda.device_count() != 1
        ):
            raise ValueError("parent must assign exactly one released GPU")
        torch.set_num_threads(4)
        torch.manual_seed(spec["seed"])
        torch.cuda.manual_seed_all(spec["seed"])
        torch.cuda.reset_peak_memory_stats()
        load_started = time.monotonic()
        tokenizer = data.load_tokenizer()
        base = AutoModelForCausalLM.from_pretrained(
            data.BASE,
            local_files_only=True,
            dtype=torch.bfloat16,
            attn_implementation="sdpa",
            device_map={"": "cuda:0"},
        )
        model = PeftModel.from_pretrained(
            base, CHECKPOINT, is_trainable=False, autocast_adapter_dtype=True
        )
        audit = mixed.old.audit(model, CHECKPOINT)
        lora = [p for name, p in model.named_parameters() if "lora_" in name]
        if not lora or any(p.dtype != torch.float32 or p.requires_grad for p in lora):
            raise ValueError("requires exact inference-only FP32 adapter cast")
        write_once(
            output / "LOAD_AUDIT.json",
            {
                **audit,
                "environment": environment(),
                "base_dtype": "bfloat16",
                "attn_implementation": "sdpa",
                "adapter_dtype": "float32",
                "adapter_trainable": False,
                "model_loads": 1,
                "load_seconds": time.monotonic() - load_started,
                "gpu": torch.cuda.get_device_name(),
                "cuda": torch.version.cuda,
            },
        )
        for index in range(6):
            rows = spec["rows"][index * 2 : index * 2 + 2]
            folder = output / "batches" / f"{index:02d}"
            folder.mkdir()
            write_once(
                folder / "OUTER_BINDING.json",
                {
                    "identity": spec["identity"],
                    "rows": [
                        {
                            "id": r["id"],
                            "condition": r["condition"],
                            "prompt_ids_sha256": digest(r["prompt_ids"]),
                        }
                        for r in rows
                    ],
                    "checkpoint_sha256": ADAPTER_SHA,
                },
            )
            wrapped = AuditedModel(
                model, rows, tokenizer.pad_token_id, folder, torch.cuda.synchronize
            )
            mixed.evaluate_long(wrapped, tokenizer, rows, folder, spec["identity"], CHECKPOINT)
            if wrapped.calls != 1:
                raise ValueError("fresh microbatch did not generate exactly once")
            completed = [read(folder / (r["id"] + ".json")) for r in rows]
            costs = read(folder / "GENERATE_INPUT.json")
            write_once(
                folder / "COST.json",
                {
                    "logical_input_tokens": costs["logical_input_tokens"],
                    "padded_input_tokens": costs["padded_input_tokens"],
                    "completion_tokens": sum(len(r["generated_token_ids"]) for r in completed),
                    "generation_seconds": read(folder / "GENERATE_TIME.json")["wall_seconds"],
                },
            )
            print(json.dumps({"completed": (index + 1) * 2, "planned": 12}), flush=True)
        write_once(
            output / "MEMORY.json",
            {
                "peak_allocated_bytes": torch.cuda.max_memory_allocated(),
                "peak_reserved_bytes": torch.cuda.max_memory_reserved(),
            },
        )
    except BaseException as error:
        reason = type(error).__name__ + ":" + str(error)
        write_once(
            output / "ERROR.json", {"type": type(error).__name__, "message": str(error)[:1500]}
        )
    finally:
        signal.setitimer(signal.ITIMER_REAL, 0)
        signal.signal(signal.SIGALRM, previous)
        summary = summarize(spec, output)
        write_once(output / "analysis.json", summary)
        completed = sum(r["completed"] for r in summary["coordinates"])
        write_once(
            output / "STATUS.json",
            {
                "completed": completed,
                "planned": 12,
                "stop_reason": reason,
                "wall_seconds": time.monotonic() - started,
                "unrun_or_unavailable": [
                    r["id"] for r in summary["coordinates"] if not r["completed"]
                ],
            },
        )
    return 0 if reason is None and completed == 12 else 2


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command", choices=["prepare", "verify", "run"])
    parser.add_argument("--spec-path", type=Path, default=ROOT / "SPEC.json")
    parser.add_argument("--output-dir", type=Path)
    args = parser.parse_args()
    if args.command == "prepare":
        write_once(args.spec_path, build_spec())
        print(
            json.dumps(
                {
                    "spec": str(args.spec_path),
                    "sha256": file_hash(args.spec_path),
                    "live_model_calls": 0,
                }
            )
        )
    elif args.command == "verify":
        verify_spec(read(args.spec_path))
        print(json.dumps({"verified": str(args.spec_path), "live_model_calls": 0}))
    else:
        if not args.output_dir:
            parser.error("run requires --output-dir NEW_DIR")
        raise SystemExit(run(args.spec_path, args.output_dir))


if __name__ == "__main__":
    main()
