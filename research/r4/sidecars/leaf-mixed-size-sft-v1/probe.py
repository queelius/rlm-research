"""Six matched greedy batch64 prompts: existing vLLM service versus selected HF PEFT."""

import argparse
import asyncio
import importlib.util
import json
import os
import signal
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent
SFT = ROOT.parent / "trec-leaf-sft-v1"
PARENT = ROOT.parent / "fixed-leaf-batch-extremes-v1/SPEC-B064.json"


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
        PARENT: "ed3056e2e9e058ea26ed73309de8963a288ecf813ea47ac5a0bf807f1fa7e297",
        SFT
        / "source/experiment.py": "c4a66731f544c57821b8f0bf81eb6f5785f12f943b61b8bc4e3916a1dcef041c",
    }
)
old = load("mixed_probe_sft", SFT / "source/experiment.py")


def build_requests():
    spec = data.read_json(PARENT)
    data.authenticate(spec["source_file_sha256"])
    leaf = load("mixed_probe_leaf", ROOT.parent / "trec-leaf-contract-probe-v1/driver.py")
    rows = []
    for batch in spec["design"]["batches"]:
        row = next(
            r
            for r in spec["design"]["plan"]
            if r["batch_id"] == batch["batch_id"] and r["arm"] == "sft_child"
        )
        body = leaf.make_request(
            spec["design"],
            {**row, "arm": "definitions"},
            "strict-rlm-qwen3-4b-role-sft-selected-v1",
        )
        body["temperature"] = 0
        rows.append(
            {
                "context_id": batch["context_id"],
                "gold": batch["gold"],
                "request": body,
                "request_sha256": data.digest(body),
            }
        )
    return {
        "requests": rows,
        "server": spec["server"],
        "model": spec["models"][rows[0]["request"]["model"]],
        "source_file_sha256": spec["source_file_sha256"],
    }


def prepare():
    spec = build_requests()
    tokenizer = data.load_tokenizer()
    for row in spec["requests"]:
        body = row["request"]
        prompt = tokenizer.apply_chat_template(
            body["messages"], tools=body["tools"], tokenize=False, add_generation_prompt=True
        )
        row["hf_prompt_ids"] = tokenizer.encode(prompt, add_special_tokens=False)
    spec["source_file_sha256"].update(
        {
            str(p): data.file_hash(p)
            for p in [
                Path(__file__),
                ROOT / "test_probe.py",
                PARENT,
                SFT / "RECIPE.json",
                SFT / "source/data.py",
                SFT / "source/experiment.py",
            ]
        }
    )
    spec["interpretation"] = (
        "Matched messages/tools, selected weights, greedy1024; HF FP32 LoRA versus vLLM BF16 cast and batching remain different. No schema."
    )
    spec["identity"] = data.digest(spec)
    data.write_once(ROOT / "PROBE_SPEC.json", spec)
    return {"requests": 6, "identity": spec["identity"], "gpu_calls": 0}


def bound():
    spec = data.read_json(ROOT / "PROBE_SPEC.json")
    if data.digest({k: v for k, v in spec.items() if k != "identity"}) != spec["identity"]:
        raise ValueError("probe identity changed")
    data.authenticate(spec["source_file_sha256"])
    data.authenticate(
        {Path(spec["model"]["path"]) / "adapter_model.safetensors": spec["model"]["adapter_sha256"]}
    )
    return spec


async def vllm(spec, output):
    import httpx

    semaphore = asyncio.Semaphore(4)
    async with httpx.AsyncClient(
        headers={"Authorization": "Bearer " + os.environ[spec["server"]["api_key_env"]]},
        timeout=120,
        trust_env=False,
    ) as client:
        cards = await client.get(spec["server"]["url"] + "/models")
        cards.raise_for_status()
        found = next(
            r for r in cards.json()["data"] if r["id"] == spec["requests"][0]["request"]["model"]
        )
        if (
            found["root"] != spec["model"]["path"]
            or found["parent"] != spec["server"]["base_model"]
        ):
            raise ValueError("actual serving alias/path/base changed")
        data.write_once(output / "MODELS.json", cards.json())

        async def one(row):
            async with semaphore:
                result = {
                    "context_id": row["context_id"],
                    "request": row["request"],
                    "started": time.time(),
                    "score": None,
                }
                try:
                    response = await client.post(
                        spec["server"]["url"] + "/chat/completions", json=row["request"]
                    )
                    result.update(http_status=response.status_code, raw_response_text=response.text)
                    response.raise_for_status()
                    raw = response.json()
                    if raw["model"] != row["request"]["model"]:
                        raise ValueError("response alias differs")
                    choice = raw["choices"][0]
                    content = (
                        None
                        if choice["message"].get("tool_calls")
                        else choice["message"].get("content")
                    )
                    result.update(
                        raw_response=raw,
                        score=old.score(content, row["gold"]),
                        prompt_ids_equal_hf=raw.get("prompt_token_ids") == row["hf_prompt_ids"]
                        if isinstance(raw.get("prompt_token_ids"), list)
                        else None,
                    )
                except Exception as error:
                    result["error"] = {"type": type(error).__name__, "message": str(error)}
                result["ended"] = time.time()
                data.write_once(output / (row["context_id"] + ".json"), result)
                return result

        return await asyncio.gather(*(one(row) for row in spec["requests"]))


def hf(spec, output):
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
    tokenizer = data.load_tokenizer()
    base = AutoModelForCausalLM.from_pretrained(
        data.BASE,
        local_files_only=True,
        dtype=torch.bfloat16,
        attn_implementation="sdpa",
        device_map={"": "cuda:0"},
    )
    model = PeftModel.from_pretrained(
        base, spec["model"]["path"], is_trainable=False, autocast_adapter_dtype=True
    )
    data.write_once(output / "LOAD_AUDIT.json", old.audit(model, Path(spec["model"]["path"])))
    model.eval()
    eos = model.generation_config.eos_token_id
    eos = set(eos if isinstance(eos, list) else [eos])
    results = []
    for start in range(0, 6, 2):
        rows = spec["requests"][start : start + 2]
        batch = {
            k: v.to(model.device)
            for k, v in data.generation_batch(
                [r["hf_prompt_ids"] for r in rows], tokenizer.pad_token_id
            ).items()
        }
        began = time.time()
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
        for row, ids in zip(rows, sequences, strict=True):
            content = tokenizer.decode(
                ids[:-1] if ids and ids[-1] in eos else ids, skip_special_tokens=False
            )
            result = {
                "context_id": row["context_id"],
                "prompt_token_ids": row["hf_prompt_ids"],
                "generated_token_ids": ids,
                "raw_generation": tokenizer.decode(ids, skip_special_tokens=False),
                "content": content,
                "finish_reason": "stop" if ids and ids[-1] in eos else "length",
                "score": old.score(content, row["gold"]),
                "batch_wall_seconds": time.time() - began,
            }
            data.write_once(output / (row["context_id"] + ".json"), result)
            results.append(result)
    return results


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command", choices=("prepare", "vllm", "hf"))
    args = parser.parse_args()
    if args.command == "prepare":
        print(json.dumps(prepare()))
        return
    spec = bound()
    output = ROOT / "probe-outputs" / (args.command + "-attempt-001")
    output.mkdir(parents=True, exist_ok=False)
    data.write_once(output / "SPEC.json", spec)

    def timeout(_sig, _frame):
        raise TimeoutError("600-second backend probe cap")

    signal.signal(signal.SIGALRM, timeout)
    signal.setitimer(signal.ITIMER_REAL, 600)
    try:
        results = asyncio.run(vllm(spec, output)) if args.command == "vllm" else hf(spec, output)
        summary = {
            "records": 384,
            "arrays": len(results),
            "valid_arrays": sum(r["score"]["array_valid"] for r in results if r["score"]),
            "canonical_correct": sum(sum(r["score"]["correct"]) for r in results if r["score"]),
            "runtime_failures": sum(r["score"] is None for r in results),
            "identity": spec["identity"],
        }
        data.write_once(output / "SUMMARY.json", summary)
        print(json.dumps(summary))
    finally:
        signal.setitimer(signal.ITIMER_REAL, 0)


if __name__ == "__main__":
    main()
