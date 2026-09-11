"""Train-only first-leaf-response proxy. Never starts a model server or executes tools."""

from __future__ import annotations

import argparse
import asyncio
import hashlib
import importlib.metadata
import json
import os
import time
import uuid
from collections import Counter
from copy import deepcopy
from pathlib import Path
from typing import Any

import httpx

ROOT = Path(__file__).resolve().parent
MAP = ROOT.parent / "trec-train-process-audit-v1/CONTEXT8_LABEL_MAP.json"
MAP_SHA = "cbb3612d2c147983234ff230202325fc259d746ff1ba09f99a6595999688ff57"
ARMS = ("baseline", "definitions", "schema", "both")
LABELS = (
    "human being",
    "location",
    "abbreviation",
    "entity",
    "description and abstract concept",
    "numeric value",
)
DEFINITIONS = (
    "Classify the type of answer requested, not words mentioned in the question.\n"
    "human being: a person, an organization or group of people, or a person's role, "
    "title or description.\n"
    "location: a geographic place, including a city, country, state, mountain or other place.\n"
    "abbreviation: a shortened form, or the expanded wording represented by a shortened form.\n"
    "entity: a nonhuman, nongeographic thing or name, including objects, organisms, works, "
    "events, substances, methods or synonymous terms.\n"
    "description and abstract concept: a definition, explanation, reason or manner of doing "
    "something, rather than a particular name or number.\n"
    "numeric value: a quantity, count, measurement, date, duration, rank or numerical code.\n"
)


def digest(value: Any) -> str:
    return hashlib.sha256(
        json.dumps(value, sort_keys=True, separators=(",", ":")).encode()
    ).hexdigest()


def file_hash(path: Path) -> str:
    with path.open("rb") as stream:
        return hashlib.file_digest(stream, "sha256").hexdigest()


def write_once(path: Path, value: Any) -> None:
    """Atomic publication without overwriting an existing checkpoint."""
    temporary = path.with_name(path.name + ".pending-" + uuid.uuid4().hex)
    try:
        with temporary.open("x") as stream:
            json.dump(value, stream, sort_keys=True, indent=2, allow_nan=False)
            stream.write("\n")
            stream.flush()
            os.fsync(stream.fileno())
        os.link(temporary, path)
    finally:
        temporary.unlink(missing_ok=True)


def make_design() -> dict[str, Any]:
    if file_hash(MAP) != MAP_SHA:
        raise ValueError("frozen train label map changed")
    mapping = json.loads(MAP.read_text())
    contract = json.loads((ROOT / "CONTRACT.json").read_text())
    if mapping["context_window_id"] != 8 or mapping["heldout_context_accessed"]:
        raise ValueError("only audited training context8 is allowed")
    records = mapping["records"]
    batches = [
        {
            "batch_id": k // 5,
            "record_indices": [r["record_index"] for r in records[k : k + 5]],
            "questions": [r["question"] for r in records[k : k + 5]],
        }
        for k in range(0, 89, 5)
    ]
    seed = int(digest([ROOT.name, "fresh-train-leaf-v1"])[:8], 16) % (2**31 - 1)
    plan = []
    for batch in batches:
        shift = batch["batch_id"] % 4
        order = ARMS[shift:] + ARMS[:shift]
        for position, arm in enumerate(order):
            row = {
                "batch_id": batch["batch_id"],
                "arm": arm,
                "seed": seed,
                "arm_order": position,
                "dispatch_order": len(plan),
            }
            row["id"] = digest([ROOT.name, batch, arm, seed])
            plan.append(row)
    return {
        "schema": "trec-leaf-factorial-design-v1",
        "study": ROOT.name,
        "analysis_split": "training_development_only",
        "context_window_id": 8,
        "context_sha256": mapping["context_utf8_sha256"],
        "contract": contract,
        "definitions": DEFINITIONS,
        "labels": list(LABELS),
        "seed": seed,
        "batches": batches,
        "plan": plan,
        "plan_sha256": digest(plan),
        "max_tokens": 256,
        "max_concurrent_calls": 4,
        "call_timeout_seconds": 30,
        "wall_time_cap_seconds": 600,
        "planned_calls": 72,
        "planned_record_labels": 356,
        "source_file_sha256": {
            str(p): file_hash(p) for p in [Path(__file__), ROOT / "CONTRACT.json", MAP]
        },
        "versions": {p: importlib.metadata.version(p) for p in ["httpx", "vllm", "xgrammar"]},
        "interpretation": (
            "Isolated first-response leaf proxy with reconstructed native contract; "
            "not a full RLM replay or heldout transfer."
        ),
    }


def make_request(design: dict, row: dict, model: str) -> dict:
    contract = design["contract"]
    batch = design["batches"][row["batch_id"]]
    prefix = contract["baseline_user_prefix"]
    if row["arm"] in ("definitions", "both"):
        prefix += "\n" + design["definitions"] + "\n"
    body = {
        "model": model,
        "messages": [
            deepcopy(contract["system_message"]),
            {"role": "user", "content": prefix + json.dumps(batch["questions"])},
        ],
        "tools": deepcopy(contract["tools"]),
        **contract["request_settings"],
        "max_tokens": design["max_tokens"],
        "seed": row["seed"],
    }
    if row["arm"] in ("schema", "both"):
        n = len(batch["questions"])
        body["structured_outputs"] = {
            "json": {
                "type": "array",
                "items": {"type": "string", "enum": design["labels"]},
                "minItems": n,
                "maxItems": n,
            }
        }
    return body


def score_labels(content: str | None, gold: list[str]) -> dict:
    status = "aligned"
    try:
        raw = json.loads(content) if isinstance(content, str) else None
    except ValueError:
        raw = None
    if not isinstance(raw, list) or any(not isinstance(v, str) for v in raw):
        status = "invalid_json"
    elif len(raw) != len(gold):
        status = "length_mismatch"
    predictions = raw if status == "aligned" else [None] * len(gold)
    invalid = sum(v not in LABELS for v in predictions) if status == "aligned" else 0
    return {
        "parse_status": status,
        "raw_array_length": len(raw) if isinstance(raw, list) else None,
        "schema_valid": status == "aligned" and invalid == 0,
        "predictions": predictions,
        "noncanonical_labels": invalid,
        "strict_correct": sum(a == b for a, b in zip(predictions, gold, strict=True)),
        "records": len(gold),
    }


def usage_metrics(usage: dict) -> dict:
    prompt = usage.get("prompt_tokens")
    cached = (usage.get("prompt_tokens_details") or {}).get("cached_tokens")
    return {
        "logical_input_tokens": prompt,
        "cached_input_tokens": cached,
        "uncached_input_tokens": prompt - cached
        if prompt is not None and cached is not None
        else None,
        "completion_tokens": usage.get("completion_tokens"),
    }


def verify_weights(descriptor: dict) -> None:
    if descriptor["base_model"]["revision"] != "cdbee75f17c01a7cc42f958dc650907174af0554":
        raise ValueError("the qualified 4B base revision is required")
    base = Path(descriptor["base_model"]["path"])
    adapter = Path(descriptor["adapter"]["path"])
    expected = {
        base / "local-research-manifest.json": descriptor["base_model"]["manifest_sha256"],
        adapter / "adapter_config.json": descriptor["adapter"]["config_sha256"],
        adapter / "adapter_model.safetensors": descriptor["adapter"]["model_sha256"],
    }
    if any(file_hash(p) != h for p, h in expected.items()):
        raise ValueError("descriptor weight bytes changed")
    if descriptor["host"] != "127.0.0.1" or importlib.metadata.version("vllm") != "0.28.0":
        raise ValueError("only the qualified local vLLM0.28 service is prepared")


def bind_spec(descriptor_path: Path) -> dict:
    descriptor = json.loads(descriptor_path.read_text())
    verify_weights(descriptor)
    design = make_design()
    return {
        "schema": "trec-leaf-bound-spec-v1",
        "design": design,
        "endpoint_descriptor": descriptor,
        "source_endpoint_descriptor": {
            "path": str(descriptor_path.resolve()),
            "sha256": file_hash(descriptor_path),
        },
        "request_sha256": {
            r["id"]: digest(make_request(design, r, descriptor["model_alias"]))
            for r in design["plan"]
        },
    }


def summarize(design: dict, records: list[dict]) -> dict:
    cells = []
    for arm in ARMS:
        rows = [r for r in records if r["coordinate"]["arm"] == arm]
        observed = [r for r in rows if r["score"] is not None]
        denominator = sum(r["score"]["records"] for r in observed)
        correct = sum(r["score"]["strict_correct"] for r in observed)
        confusion = Counter(
            (
                z["gold_label"],
                z["prediction"] if z["prediction"] in LABELS else "__invalid_or_noncanonical__",
            )
            for r in observed
            for z in r["record_results"]
        )
        cells.append(
            {
                "arm": arm,
                "planned_calls": 18,
                "recorded_calls": len(rows),
                "model_completed_calls": len(observed),
                "execution_errors": len(rows) - len(observed),
                "schema_valid_calls": sum(r["score"]["schema_valid"] for r in observed),
                "strict_correct_record_labels": correct,
                "observed_record_labels": denominator,
                "accuracy_per_model_completed_record": correct / denominator
                if denominator
                else None,
                "correct_over_all_89_planned_records": correct / 89,
                "truncated_calls": sum(r.get("finish_reason") == "length" for r in observed),
                "reported_logical_input_tokens": sum(
                    r["usage"].get("logical_input_tokens") or 0 for r in rows
                ),
                "reported_completion_tokens": sum(
                    r["usage"].get("completion_tokens") or 0 for r in rows
                ),
                "missing_usage_calls": sum(
                    r["usage"].get("logical_input_tokens") is None for r in rows
                ),
                "confusion": [
                    {"gold": a, "prediction": b, "count": n}
                    for (a, b), n in sorted(confusion.items())
                ],
            }
        )
    return {
        "schema": "trec-leaf-summary-v1",
        "planned": len(design["plan"]),
        "recorded": len(records),
        "cells": cells,
        "caution": (
            "One previously observed training context; 356 labels are not independent contexts. "
            "No silent aliases, no tool execution, no extra logprob request."
        ),
    }


async def run(spec_path: Path, output: Path) -> None:
    spec = json.loads(spec_path.read_text())
    design = spec["design"]
    descriptor = spec["endpoint_descriptor"]
    if design != make_design():
        raise ValueError("current inputs differ from frozen design")
    if (
        file_hash(Path(spec["source_endpoint_descriptor"]["path"]))
        != spec["source_endpoint_descriptor"]["sha256"]
    ):
        raise ValueError("endpoint descriptor changed")
    verify_weights(descriptor)
    for row in design["plan"]:
        if (
            digest(make_request(design, row, descriptor["model_alias"]))
            != spec["request_sha256"][row["id"]]
        ):
            raise ValueError("request specification changed")
    api_key = os.environ[descriptor["api_key_env"]]
    url = f"http://{descriptor['host']}:{descriptor['port']}/v1"
    mapping = json.loads(MAP.read_text())
    output.mkdir(parents=True, exist_ok=False)
    (output / "calls").mkdir()
    write_once(output / "SPEC.json", spec)
    started = time.time()
    write_once(
        output / "ATTEMPT.json",
        {
            "started": started,
            "spec_sha256": file_hash(spec_path),
            "endpoint": url,
            "model": descriptor["model_alias"],
        },
    )
    records: list[dict] = []
    pending = iter(design["plan"])
    stop = asyncio.Event()
    reason = None
    async with httpx.AsyncClient(
        headers={"Authorization": "Bearer " + api_key},
        timeout=design["call_timeout_seconds"],
        trust_env=False,
    ) as client:
        version = await client.get(url.removesuffix("/v1") + "/version")
        version.raise_for_status()
        if version.json().get("version") != "0.28.0":
            raise ValueError("live server API version differs from CPU-qualified vLLM0.28")
        write_once(output / "VERSION_PREFLIGHT.json", version.json())
        models = await client.get(url + "/models")
        models.raise_for_status()
        if descriptor["model_alias"] not in {m["id"] for m in models.json()["data"]}:
            raise ValueError("assigned alias is not loaded")
        write_once(output / "MODELS_PREFLIGHT.json", models.json())

        async def worker() -> None:
            while not stop.is_set():
                row = next(pending, None)
                if row is None:
                    return
                body = make_request(design, row, descriptor["model_alias"])
                batch = design["batches"][row["batch_id"]]
                gold = [mapping["records"][i - 1]["gold_label"] for i in batch["record_indices"]]
                record = {
                    "coordinate": row,
                    "request": body,
                    "request_sha256": digest(body),
                    "started": time.time(),
                    "score": None,
                    "usage": {},
                    "record_results": [],
                }
                try:
                    response = await client.post(url + "/chat/completions", json=body)
                    record["http_status"] = response.status_code
                    record["raw_response_text"] = response.text
                    response.raise_for_status()
                    raw = response.json()
                    record["raw_response"] = raw
                    choice = raw["choices"][0]
                    message = choice["message"]
                    record["finish_reason"] = choice["finish_reason"]
                    record["tool_call_response"] = bool(message.get("tool_calls"))
                    score = score_labels(
                        None if record["tool_call_response"] else message.get("content"), gold
                    )
                    record["score"] = score
                    record["usage"] = usage_metrics(raw.get("usage") or {})
                    record["record_results"] = [
                        {
                            "record_index": i,
                            "gold_label": g,
                            "prediction": p,
                            "strict_correct": g == p,
                        }
                        for i, g, p in zip(
                            batch["record_indices"], gold, score["predictions"], strict=True
                        )
                    ]
                    record["capture"] = {
                        "prompt_token_ids": isinstance(raw.get("prompt_token_ids"), list),
                        "output_token_ids": isinstance(choice.get("token_ids"), list),
                        "logprobs_requested": False,
                    }
                except asyncio.CancelledError:
                    record["error"] = {"type": "CancelledError", "cost_unknown": True}
                    raise
                except Exception as error:
                    record["error"] = {"type": type(error).__name__, "message": str(error)}
                    stop.set()
                finally:
                    record["ended"] = time.time()
                    write_once(output / "calls" / (row["id"] + ".json"), record)
                    records.append(record)
                    print(
                        json.dumps(
                            {
                                "recorded": len(records),
                                "arm": row["arm"],
                                "batch": row["batch_id"],
                                "score": record["score"],
                                "error": record.get("error"),
                            }
                        ),
                        flush=True,
                    )

        try:
            async with asyncio.timeout(design["wall_time_cap_seconds"]):
                await asyncio.gather(*(worker() for _ in range(design["max_concurrent_calls"])))
        except TimeoutError:
            reason = "wall_time_cap"
        except asyncio.CancelledError:
            reason = "cancelled"
            raise
        finally:
            write_once(output / "analysis.json", summarize(design, records))
            write_once(
                output / "STATUS.json",
                {
                    "planned": 72,
                    "recorded": len(records),
                    "stop_reason": reason or ("request_error" if stop.is_set() else None),
                    "wall_seconds": time.time() - started,
                    "unrun": [
                        r["id"]
                        for r in design["plan"]
                        if r["id"] not in {z["coordinate"]["id"] for z in records}
                    ],
                },
            )


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("mode", choices=("design", "bind", "run"))
    parser.add_argument("--endpoint-descriptor", type=Path)
    parser.add_argument("--spec-path", type=Path)
    parser.add_argument("--output-dir", type=Path)
    args = parser.parse_args()
    if args.mode == "design":
        print(json.dumps(make_design(), sort_keys=True, indent=2))
    elif args.mode == "bind":
        if not args.endpoint_descriptor or not args.spec_path:
            parser.error("bind requires --endpoint-descriptor and new --spec-path")
        write_once(args.spec_path, bind_spec(args.endpoint_descriptor))
        print(json.dumps({"spec": str(args.spec_path), "sha256": file_hash(args.spec_path)}))
    else:
        if not args.spec_path or not args.output_dir:
            parser.error("run requires --spec-path and new --output-dir")
        asyncio.run(run(args.spec_path, args.output_dir))


if __name__ == "__main__":
    main()
