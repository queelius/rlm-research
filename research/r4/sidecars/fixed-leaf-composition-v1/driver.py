"""Fixed, first-response leaf composition; CPU preparation never contacts a model."""

from __future__ import annotations

import argparse
import ast
import asyncio
import importlib.util
import json
import os
import time
from collections import Counter, defaultdict
from pathlib import Path

import httpx

ROOT = Path(__file__).resolve().parent
COMPOSITION = ROOT.parent / "leaf-composition-transfer-v1"
LEAF = ROOT.parent / "trec-leaf-contract-probe-v1"
CONTRACT = LEAF / "CONTRACT.json"
SFT = ROOT.parent / "trec-leaf-sft-v1"
ROLE = ROOT.parent / "leaf-role-routing-v1"
DATA_SHA = "1ea4640da5a8e3e305bee7f79d5abeecb02507d6bcc33d709d1c7209fd47bfc2"
HELPER_SHA = "a82baf0d9be7f5cbc756ced908c405f6aba4497b46a4ca56e15c8900798c8bce"
ALIASES = {
    "original_child": "strict-rlm-qwen3-4b-role-original-v1",
    "sft_child": "strict-rlm-qwen3-4b-role-sft-selected-v1",
}

loader = importlib.util.spec_from_file_location("fixed_original_leaf_helpers", LEAF / "driver.py")
leaf = importlib.util.module_from_spec(loader)
loader.loader.exec_module(leaf)
if leaf.file_hash(LEAF / "driver.py") != HELPER_SHA:
    raise ValueError("frozen leaf helper changed")


def layout_from_data(data: dict) -> dict:
    """Expand parent coordinates without changing their seeds, order or question selection."""
    batches = []
    batch_ids = defaultdict(list)
    tasks = {t["name"]: t for t in data["tasks"]}
    for context in data["contexts"]:
        for start in range(0, len(context["records"]), 5):
            records = context["records"][start : start + 5]
            batch_id = len(batches)
            batch_ids[context["id"]].append(batch_id)
            batches.append(
                {
                    "batch_id": batch_id,
                    "context_id": context["id"],
                    "record_indices": list(range(start + 1, start + len(records) + 1)),
                    "question_group_ids": [r["group_id"] for r in records],
                    "questions": [r["question"] for r in records],
                    "gold": [r["gold"] for r in records],
                }
            )
    plan = []
    for coordinate in data["plan"]:
        task = tasks[coordinate["task_name"]]
        if coordinate["arm"] not in ALIASES:
            raise ValueError("unknown frozen child-weight arm")
        for batch_index, batch_id in enumerate(batch_ids[task["context_id"]]):
            row = {
                "coordinate_id": coordinate["id"],
                "pair_id": coordinate["pair_id"],
                "task_name": task["name"],
                "context_id": task["context_id"],
                "arm": coordinate["arm"],
                "seed": coordinate["seed"],
                "repeat": coordinate["repeat"],
                "batch_id": batch_id,
                "batch_index": batch_index,
                "dispatch_order": len(plan),
            }
            row["id"] = leaf.digest([ROOT.name, coordinate["id"], batch_index])
            plan.append(row)
    return {
        "contexts": data["contexts"],
        "tasks": data["tasks"],
        "coordinates": data["plan"],
        "batches": batches,
        "plan": plan,
    }


def make_request(design: dict, row: dict) -> dict:
    return leaf.make_request(design, {**row, "arm": "definitions"}, ALIASES[row["arm"]])


def validate_binding(spec: dict, binding: dict) -> None:
    selected = spec["selection"]
    expected_roles = {"root": ALIASES["original_child"], "children": list(ALIASES.values())}
    if (
        binding.get("selection_path") != selected["path"]
        or binding.get("selection_sha256") != selected["sha256"]
        or binding.get("selected_epoch") != selected["epoch"]
        or binding.get("models") != spec["models"]
        or binding.get("role_map") != expected_roles
        or binding.get("post_training_test_consulted_for_binding") is not False
        or binding["models"][ALIASES["sft_child"]]["path"] != selected["checkpoint"]
    ):
        raise ValueError("role binding differs from frozen validation-selected weights")


def make_spec(binding_path: Path, server_dir: Path) -> dict:
    manifest_path = COMPOSITION / "prepared-v1/MANIFEST.json"
    data_path = COMPOSITION / "prepared-v1/DATA.json"
    manifest = json.loads(manifest_path.read_text())
    if leaf.digest({k: v for k, v in manifest.items() if k != "identity"}) != manifest["identity"]:
        raise ValueError("parent composition manifest identity changed")
    if leaf.file_hash(data_path) != DATA_SHA or manifest["data_sha256"] != DATA_SHA:
        raise ValueError("parent composition data changed")
    data = json.loads(data_path.read_text())
    if (
        len(data["contexts"]) != 6
        or len(data["tasks"]) != 12
        or len(data["plan"]) != 48
        or data["selected_groups"] != 384
        or data["source_question_overlap_with_sft_train_validation"]
        or data["model_outputs_inspected_for_context_or_query_selection"]
    ):
        raise ValueError("composition shape/provenance changed")
    groups = [r["group_id"] for context in data["contexts"] for r in context["records"]]
    if len(groups) != 384 or len(set(groups)) != 384:
        raise ValueError("composition questions must be disjoint by source group")
    for context in data["contexts"]:
        if len(context["records"]) != 64 or any(
            r["gold"] not in leaf.LABELS for r in context["records"]
        ):
            raise ValueError("invalid frozen context labels or cardinality")
    for task in data["tasks"]:
        context = next(c for c in data["contexts"] if c["id"] == task["context_id"])
        gold = sum(r["gold"] == task["label"] for r in context["records"])
        if task["label"] not in {"human being", "numeric value"} or ast.literal_eval(
            task["answer"]
        ) != [gold]:
            raise ValueError("frozen aggregate answer mismatch")
    design = layout_from_data(data)
    design.update(
        {
            "contract": json.loads(CONTRACT.read_text()),
            "definitions": leaf.DEFINITIONS,
            "labels": list(leaf.LABELS),
            "max_tokens": 256,
            "max_concurrent_calls": 4,
            "call_timeout_seconds": 30,
            "wall_time_cap_seconds": 900,
        }
    )
    if len(design["plan"]) != 624 or len({r["id"] for r in design["plan"]}) != 624:
        raise ValueError("expected624 unique leaf calls")
    selection_path = SFT / "outputs/attempt-001/SELECTION.json"
    selection = json.loads(selection_path.read_text())
    recipe_path = SFT / "RECIPE.json"
    recipe = json.loads(recipe_path.read_text())
    selected = Path(selection["selected"]["checkpoint"])
    if (
        selected.parent != selection_path.parent
        or selected.name not in {"checkpoint-0064", "checkpoint-0128"}
        or selection["post_training_test_inspected"] is not False
    ):
        raise ValueError("selection must be frozen before component-test inspection")
    models = {
        alias: {
            "path": str(path),
            "adapter_sha256": leaf.file_hash(path / "adapter_model.safetensors"),
            "config_sha256": leaf.file_hash(path / "adapter_config.json"),
        }
        for alias, path in [
            (ALIASES["original_child"], Path(recipe["adapter"])),
            (ALIASES["sft_child"], selected),
        ]
    }
    binding = json.loads(binding_path.read_text())
    endpoints = {
        arm: json.loads((server_dir / filename).read_text())
        for arm, filename in [
            ("original_child", "endpoint-original.json"),
            ("sft_child", "endpoint-selected.json"),
        ]
    }
    for arm, endpoint in endpoints.items():
        model = models[ALIASES[arm]]
        if (
            endpoint["model_alias"] != ALIASES[arm]
            or endpoint["adapter"]["path"] != model["path"]
            or endpoint["adapter"]["model_sha256"] != model["adapter_sha256"]
            or endpoint["adapter"]["config_sha256"] != model["config_sha256"]
            or endpoint["base_model"]["path"] != recipe["base"]
            or endpoint["host"] != "127.0.0.1"
            or endpoint["port"] != 18601
        ):
            raise ValueError("actual endpoint descriptor differs from bound weights")
    ready = json.loads((server_dir / "SERVER_READY.json").read_text())
    server_binding = json.loads((server_dir / "BINDING.json").read_text())
    server_config = json.loads((server_dir / "inference.json").read_text())
    if (
        set(ready["aliases"]) != set(models)
        or server_binding != binding
        or server_config["vllm"]["model"] != recipe["base"]
        or server_config["vllm"].get("lora_dtype") != "auto"
    ):
        raise ValueError("actual dual-LoRA service metadata disagrees with binding")
    sources = dict(manifest["source_sha256"])
    paths = [
        Path(__file__),
        ROOT / "test_driver.py",
        ROOT / "DESIGN.md",
        ROOT / "PLAN.md",
        manifest_path,
        data_path,
        LEAF / "driver.py",
        CONTRACT,
        selection_path,
        recipe_path,
        binding_path,
        server_dir / "endpoint-original.json",
        server_dir / "endpoint-selected.json",
        server_dir / "SERVER_READY.json",
        server_dir / "SERVER_START.json",
        server_dir / "BINDING.json",
        server_dir / "inference.json",
        Path(recipe["base"]) / "local-research-manifest.json",
    ]
    for model in models.values():
        paths.extend(
            [
                Path(model["path"]) / "adapter_model.safetensors",
                Path(model["path"]) / "adapter_config.json",
            ]
        )
    sources.update({str(p.resolve()): leaf.file_hash(p) for p in paths})
    spec = {
        "schema": ROOT.name,
        "design": design,
        "composition_identity": manifest["identity"],
        "selection": {
            "path": str(selection_path),
            "sha256": leaf.file_hash(selection_path),
            "checkpoint": str(selected),
            "epoch": selection["selected"]["epoch"],
        },
        "models": models,
        "source_file_sha256": sources,
        "source_binding": {
            "path": str(binding_path.resolve()),
            "sha256": leaf.file_hash(binding_path),
        },
        "server": {
            "directory": str(server_dir.resolve()),
            "pid": ready["pid"],
            "url": "http://127.0.0.1:18601/v1",
            "api_key_env": endpoints["original_child"]["api_key_env"],
            "base_model": recipe["base"],
            "model_dtype": server_config["vllm"]["dtype"],
            "lora_dtype": server_config["vllm"]["lora_dtype"],
            "dtype_caution": "FP32 checkpoint files are served with the parent's common BF16 inference cast, not exact FP32 adapter arithmetic.",
            "server_ready": ready,
            "preparation_live_contact": False,
        },
        "request_sha256": {r["id"]: leaf.digest(make_request(design, r)) for r in design["plan"]},
        "coordinate_plan_sha256": leaf.digest(design["coordinates"]),
        "call_plan_sha256": leaf.digest(design["plan"]),
        "primary_failure_policy": "Any noncanonical or malformed batch -> unavailable aggregate and strict0. Infrastructure or unrun -> null.",
        "unit_caution": "6 contexts/384 question groups;48 coordinates/3072 labels are repeated measurements.",
        "contract_caution": "Supplied fixed operator, reconstructed first-response leaf contract and256 output cap; not an exact full-RLM2048-token child replay.",
    }
    validate_binding(spec, binding)
    verify_inputs(spec)
    return spec


def verify_inputs(spec: dict) -> None:
    for path, expected in spec["source_file_sha256"].items():
        if leaf.file_hash(Path(path)) != expected:
            raise ValueError(f"frozen input changed: {path}")
    design = spec["design"]
    if (
        leaf.digest(design["coordinates"]) != spec["coordinate_plan_sha256"]
        or leaf.digest(design["plan"]) != spec["call_plan_sha256"]
    ):
        raise ValueError("frozen plan changed")
    for row in design["plan"]:
        if leaf.digest(make_request(design, row)) != spec["request_sha256"][row["id"]]:
            raise ValueError("frozen request changed")
    validate_binding(spec, json.loads(Path(spec["source_binding"]["path"]).read_text()))


def score_coordinate(design: dict, coordinate: dict, records: list[dict]) -> dict:
    task = next(t for t in design["tasks"] if t["name"] == coordinate["task_name"])
    context = next(c for c in design["contexts"] if c["id"] == task["context_id"])
    expected = [r for r in design["plan"] if r["coordinate_id"] == coordinate["id"]]
    selected = [r for r in records if r["coordinate"]["coordinate_id"] == coordinate["id"]]
    if len({r["coordinate"]["id"] for r in selected}) != len(selected):
        raise ValueError("duplicate call checkpoint")
    if not {r["coordinate"]["id"] for r in selected} <= {r["id"] for r in expected}:
        raise ValueError("unexpected call coordinate")
    rows = []
    for record in selected:
        if record.get("score") is None:
            continue
        batch = design["batches"][record["coordinate"]["batch_id"]]
        score = record["score"]
        for index, group, gold, prediction in zip(
            batch["record_indices"],
            batch["question_group_ids"],
            batch["gold"],
            score["predictions"],
            strict=True,
        ):
            rows.append(
                {
                    "record_index": index,
                    "question_group_id": group,
                    "gold": gold,
                    "prediction": prediction,
                    "aligned": score["parse_status"] == "aligned",
                    "canonical_correct": prediction == gold,
                }
            )
    full = len(selected) == len(expected) and bool(expected)
    errors = sum(record.get("score") is None for record in selected)
    contract_failures = sum(
        record.get("score") is not None and not record["score"]["schema_valid"]
        for record in selected
    )
    available = full and not errors and not contract_failures
    gold_count = sum(r["gold"] == task["label"] for r in context["records"])
    count = sum(r["prediction"] == task["label"] for r in rows) if available else None
    status = (
        "infrastructure_error"
        if errors
        else "incomplete"
        if not full
        else "model_contract_failure"
        if contract_failures
        else "aggregate_available"
    )
    reward = int(count == gold_count) if available else 0 if full and not errors else None
    return {
        "coordinate": coordinate,
        "status": status,
        "strict_reward": reward,
        "aggregate_available": available,
        "predicted_count": count,
        "gold_count": gold_count,
        "target_label": task["label"],
        "planned_calls": len(expected),
        "recorded_calls": len(selected),
        "infrastructure_errors": errors,
        "contract_failure_batches": contract_failures,
        "planned_records": len(context["records"]),
        "model_completed_records": len(rows),
        "aligned_records": sum(r["aligned"] for r in rows),
        "canonical_correct": sum(r["canonical_correct"] for r in rows),
        "record_results": sorted(rows, key=lambda r: r["record_index"]),
        "target_false_positives": [
            r["record_index"]
            for r in rows
            if r["aligned"] and r["prediction"] == task["label"] and r["gold"] != task["label"]
        ],
        "target_false_negatives": [
            r["record_index"]
            for r in rows
            if r["aligned"] and r["prediction"] != task["label"] and r["gold"] == task["label"]
        ],
        "usage": {
            key: sum(r.get("usage", {}).get(key) or 0 for r in selected)
            for key in ["logical_input_tokens", "cached_input_tokens", "completion_tokens"]
        },
        "missing_usage_calls": sum(
            r.get("usage", {}).get("logical_input_tokens") is None for r in selected
        ),
        "truncated_calls": sum(r.get("finish_reason") == "length" for r in selected),
    }


def summarize(design: dict, records: list[dict]) -> dict:
    results = [score_coordinate(design, c, records) for c in design["coordinates"]]
    cells = []
    for arm in ALIASES:
        selected = [r for r in results if r["coordinate"]["arm"] == arm]
        observable = [r for r in selected if r["strict_reward"] is not None]
        item_rows = [r for c in selected for r in c["record_results"]]
        confusion = Counter(
            (
                r["gold"],
                r["prediction"]
                if r["prediction"] in leaf.LABELS
                else "__invalid_or_noncanonical__",
            )
            for r in item_rows
        )
        cells.append(
            {
                "arm": arm,
                "planned_coordinates": len(selected),
                "observable_coordinates": len(observable),
                "strict_successes": sum(r["strict_reward"] for r in observable),
                "aggregate_available": sum(r["aggregate_available"] for r in selected),
                "status_counts": dict(Counter(r["status"] for r in selected)),
                "planned_record_assignments": sum(r["planned_records"] for r in selected),
                "model_completed_record_assignments": len(item_rows),
                "aligned_record_assignments": sum(r["aligned"] for r in item_rows),
                "canonical_correct_record_assignments": sum(
                    r["canonical_correct"] for r in item_rows
                ),
                "unique_question_groups_observed": len({r["question_group_id"] for r in item_rows}),
                "confusion": [
                    {"gold": a, "prediction": b, "count": n}
                    for (a, b), n in sorted(confusion.items())
                ],
                "usage": {
                    key: sum(r["usage"][key] for r in selected)
                    for key in ["logical_input_tokens", "cached_input_tokens", "completion_tokens"]
                },
            }
        )
    pairs = defaultdict(dict)
    for row in results:
        pairs[row["coordinate"]["pair_id"]][row["coordinate"]["arm"]] = row
    paired = []
    for pair_id, arms in pairs.items():
        if set(arms) != set(ALIASES):
            raise ValueError("unpaired parent design")
        left, right = arms["original_child"], arms["sft_child"]
        paired.append(
            {
                "pair_id": pair_id,
                "original_id": left["coordinate"]["id"],
                "sft_id": right["coordinate"]["id"],
                "strict_difference": right["strict_reward"] - left["strict_reward"]
                if left["strict_reward"] is not None and right["strict_reward"] is not None
                else None,
                "canonical_correct_difference": right["canonical_correct"]
                - left["canonical_correct"],
            }
        )
    return {
        "schema": ROOT.name + "-summary",
        "planned_calls": len(design["plan"]),
        "recorded_calls": len(records),
        "cells": cells,
        "paired": paired,
        "coordinates": results,
        "caution": "Fixed routine, no root model. Contexts and unique questions are the units; repeated calls are not independent.",
    }


async def collect_calls(
    client: httpx.AsyncClient, url: str, spec: dict, output: Path, deadline: float | None = None
) -> tuple[list[dict], str | None]:
    design = spec["design"]
    pending = iter(design["plan"])
    records = []
    completed_coordinates = set()
    stop = asyncio.Event()
    reason = None
    deadline = deadline or time.monotonic() + design["wall_time_cap_seconds"]
    coordinates = {c["id"]: c for c in design["coordinates"]}

    async def worker():
        while not stop.is_set():
            row = next(pending, None)
            if row is None:
                return
            body = make_request(design, row)
            if leaf.digest(body) != spec["request_sha256"][row["id"]]:
                raise ValueError("request hash changed before dispatch")
            batch = design["batches"][row["batch_id"]]
            record = {
                "coordinate": row,
                "request": body,
                "request_sha256": leaf.digest(body),
                "started": time.time(),
                "score": None,
                "usage": {},
                "model_called": False,
            }
            try:
                record["model_called"] = True
                response = await client.post(url + "/chat/completions", json=body)
                record["http_status"] = response.status_code
                record["raw_response_text"] = response.text
                response.raise_for_status()
                raw = response.json()
                record["raw_response"] = raw
                if raw.get("model") != body["model"]:
                    raise ValueError("provider response model differs from requested bound alias")
                choice = raw["choices"][0]
                message = choice["message"]
                record["finish_reason"] = choice["finish_reason"]
                record["tool_call_response"] = bool(message.get("tool_calls"))
                record["score"] = leaf.score_labels(
                    None if record["tool_call_response"] else message.get("content"), batch["gold"]
                )
                record["usage"] = leaf.usage_metrics(raw.get("usage") or {})
                record["capture"] = {
                    "prompt_token_ids": isinstance(raw.get("prompt_token_ids"), list),
                    "output_token_ids": isinstance(choice.get("token_ids"), list),
                    "logprobs_requested": False,
                    "tools_executed": False,
                }
            except asyncio.CancelledError:
                record["error"] = {"type": "CancelledError", "cost_unknown": True}
                raise
            except Exception as error:
                record["error"] = {"type": type(error).__name__, "message": str(error)[:1200]}
                stop.set()
            finally:
                record["ended"] = time.time()
                leaf.write_once(output / "calls" / (row["id"] + ".json"), record)
                records.append(record)
                cid = row["coordinate_id"]
                relevant = [r for r in records if r["coordinate"]["coordinate_id"] == cid]
                expected = [r for r in design["plan"] if r["coordinate_id"] == cid]
                if len(relevant) == len(expected) and cid not in completed_coordinates:
                    leaf.write_once(
                        output / "coordinates" / (cid + ".json"),
                        score_coordinate(design, coordinates[cid], relevant),
                    )
                    completed_coordinates.add(cid)
                if len(records) % 13 == 0 or record.get("error"):
                    print(
                        json.dumps(
                            {
                                "recorded": len(records),
                                "planned": len(design["plan"]),
                                "arm": row["arm"],
                                "error": record.get("error"),
                            }
                        ),
                        flush=True,
                    )

    try:
        async with asyncio.timeout(max(0.001, deadline - time.monotonic())):
            await asyncio.gather(*(worker() for _ in range(design["max_concurrent_calls"])))
    except TimeoutError:
        reason = "wall_time_cap"
    return records, reason or ("request_error" if stop.is_set() else None)


async def run(spec_path: Path, output: Path) -> int:
    spec = json.loads(spec_path.read_text())
    verify_inputs(spec)
    os.kill(spec["server"]["pid"], 0)
    key = os.environ[spec["server"]["api_key_env"]]
    output.mkdir(parents=True, exist_ok=False)
    (output / "calls").mkdir()
    (output / "coordinates").mkdir()
    leaf.write_once(output / "SPEC.json", spec)
    leaf.write_once(
        output / "BINDING.json", json.loads(Path(spec["source_binding"]["path"]).read_text())
    )
    started = time.time()
    deadline = time.monotonic() + spec["design"]["wall_time_cap_seconds"]
    leaf.write_once(
        output / "ATTEMPT.json",
        {"started": started, "spec_sha256": leaf.file_hash(spec_path), "server": spec["server"]},
    )
    records, reason = [], None
    try:
        async with httpx.AsyncClient(
            headers={"Authorization": "Bearer " + key},
            trust_env=False,
            timeout=spec["design"]["call_timeout_seconds"],
        ) as client:
            url = spec["server"]["url"]
            version = await client.get(url.removesuffix("/v1") + "/version")
            version.raise_for_status()
            if version.json().get("version") != "0.28.0":
                raise ValueError("live server is not qualified vLLM0.28")
            leaf.write_once(output / "VERSION_PREFLIGHT.json", version.json())
            response = await client.get(url + "/models")
            response.raise_for_status()
            cards = {r["id"]: r for r in response.json()["data"]}
            for alias, expected in spec["models"].items():
                if (
                    alias not in cards
                    or cards[alias].get("root") != expected["path"]
                    or cards[alias].get("parent") != spec["server"]["base_model"]
                ):
                    raise ValueError("live alias/path/base does not match frozen binding")
            leaf.write_once(output / "MODELS_PREFLIGHT.json", response.json())
            records, reason = await collect_calls(client, url, spec, output, deadline)
    except Exception as error:
        reason = "preflight_or_runtime_error:" + type(error).__name__
        leaf.write_once(
            output / "ERROR.json", {"type": type(error).__name__, "message": str(error)[:1200]}
        )
        raise
    finally:
        # Recover every atomically published record, even after a cancelled worker or exception.
        records = [json.loads(p.read_text()) for p in sorted((output / "calls").glob("*.json"))]
        leaf.write_once(output / "analysis.json", summarize(spec["design"], records))
        observed = {r["coordinate"]["id"] for r in records}
        leaf.write_once(
            output / "STATUS.json",
            {
                "planned": len(spec["design"]["plan"]),
                "recorded": len(records),
                "stop_reason": reason,
                "wall_seconds": time.time() - started,
                "unrun": [r["id"] for r in spec["design"]["plan"] if r["id"] not in observed],
            },
        )
    return 0 if reason is None and len(records) == len(spec["design"]["plan"]) else 2


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command", choices=["prepare", "preflight", "run"])
    parser.add_argument("--binding", type=Path, default=ROLE / "BOUND_WEIGHTS.json")
    parser.add_argument("--server-dir", type=Path, default=ROLE / "service-attempt-001")
    parser.add_argument("--spec-path", type=Path, default=ROOT / "SPEC.json")
    parser.add_argument("--output-dir", type=Path, default=ROOT / "outputs/attempt-001")
    args = parser.parse_args()
    if args.command == "prepare":
        spec = make_spec(args.binding.resolve(), args.server_dir.resolve())
        leaf.write_once(args.spec_path, spec)
        print(
            json.dumps(
                {
                    "prepared_calls": len(spec["design"]["plan"]),
                    "coordinates": 48,
                    "spec_sha256": leaf.file_hash(args.spec_path),
                    "live_model_calls": 0,
                }
            )
        )
    elif args.command == "preflight":
        spec = json.loads(args.spec_path.read_text())
        verify_inputs(spec)
        print(
            json.dumps(
                {
                    "cpu_preflight": True,
                    "planned_calls": len(spec["design"]["plan"]),
                    "spec_sha256": leaf.file_hash(args.spec_path),
                    "live_model_calls": 0,
                }
            )
        )
    else:
        raise SystemExit(asyncio.run(run(args.spec_path, args.output_dir)))


if __name__ == "__main__":
    main()
