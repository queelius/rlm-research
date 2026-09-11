"""Single process HF sampling, owned by MAIN's externally bounded GPU parent."""

# ruff: noqa: E402
import time

ENTRY = time.monotonic()

import argparse
import hashlib
import importlib.metadata
import json
import os
import signal
import sys
from pathlib import Path

import pilot

ROOT = Path(__file__).resolve().parent


def prompt_ids(tokenizer, messages):
    return tokenizer.apply_chat_template(
        messages, tokenize=True, add_generation_prompt=True, return_dict=False
    )


def read(path):
    return json.loads(Path(path).read_text())


def sha(path):
    with Path(path).open("rb") as stream:
        return hashlib.file_digest(stream, "sha256").hexdigest()


def save(path, value):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists():
        raise ValueError("immutable output exists: " + str(path))
    temporary = path.with_suffix(path.suffix + ".partial")
    with temporary.open("x") as stream:
        json.dump(value, stream, ensure_ascii=False, allow_nan=False, separators=(",", ":"))
        stream.flush()
        os.fsync(stream.fileno())
    os.replace(temporary, path)


def verify():
    ready = read(ROOT / "READY.json")
    for path, expected in ready["source_sha256"].items():
        if sha(path) != expected:
            raise ValueError("frozen file changed: " + path)
    recipe = read(ROOT / "RECIPE.json")
    weights = read(ROOT / "WEIGHTS.json")
    for path, identity in weights["stat_identity"].items():
        st = Path(path).stat()
        if [st.st_size, st.st_mtime_ns, st.st_ino] != identity:
            raise ValueError("authenticated model stat changed: " + path)
    for key, expected in recipe["versions"].items():
        if importlib.metadata.version(key) != expected:
            raise ValueError("environment version changed: " + key)
    return recipe


def sample(model, tokenizer, request, output, deadline):
    import torch

    if time.monotonic() >= deadline:
        raise TimeoutError("work deadline")
    ids = prompt_ids(tokenizer, request["messages"])
    if "frozen_prompt_token_ids" in request and ids != request["frozen_prompt_token_ids"]:
        raise ValueError("native renderer differs from frozen static prompt")
    if len(ids) + request["max_new_tokens"] > 8192:
        raise ValueError("native context exceeds frozen cap")
    record = {
        "id": request["id"],
        "request": request,
        "prompt_token_ids": ids,
        "prompt_tokens": len(ids),
        "output_tokens": None,
        "seconds": None,
        "content": None,
        "started_epoch": time.time(),
    }
    save(output / "requests" / (request["id"] + ".json"), record)
    began = time.monotonic()
    try:
        torch.manual_seed(request["seed"])
        encoded = torch.tensor([ids], dtype=torch.long, device="cuda")
        with torch.inference_mode():
            generated = model.generate(
                input_ids=encoded,
                attention_mask=torch.ones_like(encoded),
                max_new_tokens=request["max_new_tokens"],
                pad_token_id=tokenizer.pad_token_id,
                **request["generation"],
            )
        continuation = generated[0, len(ids) :].tolist()
        eos = model.generation_config.eos_token_id
        eos = eos if isinstance(eos, list) else [eos]
        stopped = bool(continuation and continuation[-1] in eos)
        content_ids = continuation[:-1] if stopped else continuation
        record.update(
            generated_token_ids=continuation,
            output_tokens=len(continuation),
            content=tokenizer.decode(content_ids, skip_special_tokens=False),
            raw_generation=tokenizer.decode(continuation, skip_special_tokens=False),
            finish_reason="stop" if stopped else "length",
        )
    except BaseException as exc:
        record["error"] = {"type": type(exc).__name__, "message": str(exc)[:1500]}
        raise
    finally:
        record["seconds"] = time.monotonic() - began
        record["ended_epoch"] = time.time()
        save(output / "calls" / (request["id"] + ".json"), record)
    return record


def collect(model, tokenizer, coordinates, output, deadline):
    for coordinate in coordinates:
        calls = []
        try:
            for request in coordinate["static_requests"]:
                calls.append(sample(model, tokenizer, request, output, deadline))
            extracted = [
                next(call for call in calls if call["id"] == coordinate["id"] + f"-extract-{i}")
                for i in range(3)
            ]
            full, lossy = pilot.projections(extracted, coordinate["chunks"])
            ordinary_calls = [
                next(call for call in calls if call["id"] == coordinate["id"] + f"-ordinary-{i}")
                for i in range(3)
            ]
            reports = {
                "full": full,
                "lossy": lossy,
                "ordinary": {
                    "reports": [call["content"] for call in ordinary_calls],
                    "acquisition_call_ids": [call["id"] for call in ordinary_calls],
                },
            }
            save(output / "reports" / (coordinate["id"] + ".json"), reports)
            for arm in coordinate["parent_order"]:
                calls.append(
                    sample(
                        model,
                        tokenizer,
                        pilot.parent_request(coordinate, arm, reports[arm]),
                        output,
                        deadline,
                    )
                )
        finally:
            # Read persisted physical calls, including an interrupted call omitted by append.
            persisted = [
                read(p) for p in sorted((output / "calls").glob(coordinate["id"] + "-*.json"))
            ]
            save(
                output / "episodes" / (coordinate["id"] + ".json"),
                pilot.episode(coordinate, persisted),
            )


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--verify", action="store_true")
    parser.add_argument("--output", type=Path, default=ROOT / "outputs/attempt-001")
    args = parser.parse_args()
    recipe = verify()
    if args.verify:
        print(
            "Frozen inputs, source hashes, model stats and environment versions verified; no model loaded."
        )
        return
    gpu = os.environ.get("CUDA_VISIBLE_DEVICES", "")
    if not gpu or "," in gpu:
        raise ValueError("MAIN must assign exactly one device")
    output = args.output.resolve()
    if output.parent != ROOT / "outputs":
        raise ValueError("output must be a fresh direct child of owned outputs")
    output.mkdir(parents=True, exist_ok=False)
    coordinates = read(ROOT / "PLAN.json")
    model = None
    error = None

    def expired(*_):
        raise TimeoutError("1650s work cap including cold startup")

    def interrupted(*_):
        raise InterruptedError("parent termination")

    signal.signal(signal.SIGALRM, expired)
    signal.signal(signal.SIGTERM, interrupted)
    signal.setitimer(
        signal.ITIMER_REAL, max(0.001, ENTRY + recipe["work_seconds"] - time.monotonic())
    )
    save(
        output / "INPUTS.json",
        {
            "ready_sha256": sha(ROOT / "READY.json"),
            "recipe": recipe,
            "CUDA_VISIBLE_DEVICES": gpu,
            "argv": sys.argv,
            "started_epoch": time.time(),
            "python": sys.version,
            "executable": sys.executable,
            "cpu_affinity": sorted(os.sched_getaffinity(0)),
        },
    )
    try:
        import torch
        from transformers import AutoModelForCausalLM, AutoTokenizer

        if not torch.cuda.is_available() or torch.cuda.device_count() != 1:
            raise ValueError("exactly one assigned CUDA device required")
        torch.set_num_threads(4)
        torch.cuda.reset_peak_memory_stats()
        model_path = recipe["checkpoint"]["path"]
        tokenizer = AutoTokenizer.from_pretrained(
            model_path, local_files_only=True, trust_remote_code=False
        )
        start_load = time.monotonic()
        model = AutoModelForCausalLM.from_pretrained(
            model_path,
            local_files_only=True,
            trust_remote_code=False,
            dtype=torch.bfloat16,
            attn_implementation="sdpa",
            device_map={"": "cuda"},
        )
        model.eval()
        model.requires_grad_(False)
        save(
            output / "MODEL_LOADED.json",
            {
                "seconds": time.monotonic() - start_load,
                "class": type(model).__name__,
                "dtype": str(next(model.parameters()).dtype),
                "attention_backend": model.config._attn_implementation,
                "generation_config": model.generation_config.to_dict(),
                "cuda_runtime": torch.version.cuda,
                "device": torch.cuda.get_device_name(0),
                "adapter": None,
            },
        )
        collect(model, tokenizer, coordinates, output, ENTRY + recipe["work_seconds"])
    except BaseException as exc:
        error = {"type": type(exc).__name__, "message": str(exc)[:1500]}
    finally:
        signal.setitimer(signal.ITIMER_REAL, 0)
        memory = {}
        if "torch" in locals() and torch.cuda.is_available():
            memory = {
                "peak_allocated_bytes": torch.cuda.max_memory_allocated(),
                "peak_reserved_bytes": torch.cuda.max_memory_reserved(),
            }
            del model
            torch.cuda.empty_cache()
        calls = [read(p) for p in sorted((output / "calls").glob("*.json"))]
        episodes = [read(p) for p in sorted((output / "episodes").glob("*.json"))]
        indexed = {ep["id"]: ep for ep in episodes}
        outcomes = [indexed.get(c["id"], pilot.episode(c, [])) for c in coordinates]
        save(output / "OUTCOMES.json", outcomes)
        summary = {}
        for arm in ("ordinary", "lossy", "full", "direct_short", "direct_expanded"):
            endpoints = [ep["endpoints"][arm] for ep in outcomes]
            summary[arm] = {
                "correct": sum(bool(e["score"] and e["score"]["correct"]) for e in endpoints),
                "available": sum(e["score"] is not None for e in endpoints),
                "denominator": 8,
                "both_partitions_correct_worlds": sum(
                    all(
                        bool(
                            e["endpoints"][arm]["score"] and e["endpoints"][arm]["score"]["correct"]
                        )
                        for e in outcomes
                        if e["world_id"] == world
                    )
                    for world in sorted({c["world_id"] for c in coordinates})
                ),
            }
        status = {
            "complete": len(calls) == 88 and error is None,
            "planned_calls": 88,
            "physical_cost": pilot.cost(calls),
            "recorded_episodes": len(episodes),
            "summary": summary,
            "error": error,
            "elapsed_seconds_including_startup": time.monotonic() - ENTRY,
            "ended_epoch": time.time(),
            **memory,
        }
        paired = []
        for ep in outcomes:
            full, ordinary = ep["endpoints"]["full"]["score"], ep["endpoints"]["ordinary"]["score"]
            paired.append(
                {
                    "id": ep["id"],
                    "partition": ep["partition"],
                    "full_minus_ordinary_correct": int(full["correct"]) - int(ordinary["correct"])
                    if full and ordinary
                    else None,
                }
            )
        status["primary_pairs"] = paired
        save(output / "STATUS.json", status)
        print(json.dumps(status), flush=True)
    if not status["complete"]:
        raise SystemExit(2)


if __name__ == "__main__":
    main()
