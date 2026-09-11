"""Fixed old-child correspondence controls. Preparation is strictly CPU-only."""

from __future__ import annotations

import argparse
import asyncio
import hashlib
import importlib.metadata
import importlib.util
import json
import os
import time
from collections import Counter
from copy import deepcopy
from functools import lru_cache
from pathlib import Path

import httpx
from tokenizers import Tokenizer

ROOT = Path(__file__).resolve().parent
SIDE = ROOT.parent
FIXED = SIDE / "fixed-leaf-composition-v1/driver.py"
OLD_VALIDATION = SIDE / "trec-leaf-validation-replication-v1/FROZEN_REPLAY_SPEC.json"
HISTORICAL_SELECTED = SIDE / "leaf-role-routing-v1/service-attempt-001/endpoint-selected.json"
BASE = Path(
    "/project/alex_phd/research-cache/models/Qwen--Qwen3-4B-Instruct-2507--cdbee75f17c01a7cc42f958dc650907174af0554"
)
ADAPTER = SIDE / "trec-leaf-sft-v1/outputs/attempt-001/checkpoint-0128"
SELECTION = ADAPTER.parent / "SELECTION.json"
SELECTED_SHA = "c32de1293c01bba5104eb1f123867649c71dd38e5194661ace4b17dcbbe66ba3"
CONFIG_SHA = "ec773bc3b9de58af98a7c4dce9a40af795a4d05cd47284dbbfb27eac99b74174"
PARTITION = "36e7d2e1ad83210f6420a0312ec46e8a8c70d764e9df0e6d631c67f6fd16c764"
SEEDS = [981261401, 981261402]
PLACEHOLDER = "__UNBOUND_OLD_SELECTED_CHILD__"

if (
    hashlib.sha256(FIXED.read_bytes()).hexdigest()
    != "9afd6c5d5219a6705c79839e99a87ca45e50c84fc7bdff197c97482f6cd8387a"
):
    raise ValueError("frozen fixed collector changed")
loader = importlib.util.spec_from_file_location("correspondence_owned_collector", FIXED)
fixed = importlib.util.module_from_spec(loader)
loader.loader.exec_module(fixed)
leaf = fixed.leaf
digest, file_hash, write_once = leaf.digest, leaf.file_hash, leaf.write_once
LABELS = list(leaf.LABELS)


@lru_cache(maxsize=1)
def tokenizer():
    return Tokenizer.from_file(str(BASE / "tokenizer.json"))


def selected_records():
    if (
        file_hash(OLD_VALIDATION)
        != "a51ce28adb11b97c9a0a31224ec3f3cded948fbfa06ed6a1e4934d6aea469333"
    ):
        raise ValueError("original validation300 manifest changed")
    original = json.loads(OLD_VALIDATION.read_text())["design"]
    records = original["records"]
    if (
        original["partition_id"] != PARTITION
        or len(records) != 300
        or [r["record_index"] for r in records] != list(range(1, 301))
        or [r["question_group_sha256"] for r in records]
        != sorted(r["question_group_sha256"] for r in records)
        or len({r["question_group_sha256"] for r in records}) != 300
    ):
        raise ValueError("wrong validation partition/order")
    # Read the already frozen validation-only snapshot, not source-test entries/files.
    return [{**deepcopy(r), "id": f"q{r['record_index']:04d}"} for r in records[:256]]


def build_spec(comparison: str) -> dict:
    if comparison not in ("representation", "rotation"):
        raise ValueError("unknown comparison")
    records = selected_records()
    contexts = [{"index": i, "records": records[i * 64 : (i + 1) * 64]} for i in range(4)]
    treatments = (
        ["anonymous", "indexed", "echo"] if comparison == "representation" else [0, 16, 32, 48]
    )
    plan, batches, coordinates = [], [], []
    for repeat, seed in enumerate(SEEDS):
        for cx in contexts:
            shift = (cx["index"] + repeat) % len(treatments)
            for position, treatment in enumerate(treatments[shift:] + treatments[:shift]):
                arm = treatment if comparison == "representation" else "anonymous"
                offset = 0 if comparison == "representation" else treatment
                order = list(range(offset, 64)) + list(range(offset))
                row = {
                    "comparison": comparison,
                    "context_index": cx["index"],
                    "repeat": repeat,
                    "seed": seed,
                    "arm": arm,
                    "offset": offset,
                    "treatment_order": position,
                    "batch_id": len(batches),
                    "dispatch_order": len(plan),
                }
                row["id"] = digest([ROOT.name, comparison, cx["index"], seed, arm, offset])
                row["coordinate_id"] = row["id"]
                plan.append(row)
                coordinates.append({**row})
                batches.append(
                    {
                        "questions": [cx["records"][i]["question"] for i in order],
                        "gold": {"arm": arm, "order": order, "records": deepcopy(cx["records"])},
                    }
                )
    design = {
        "comparison": comparison,
        "contexts": contexts,
        "plan": plan,
        "batches": batches,
        "coordinates": coordinates,
        "model_alias": PLACEHOLDER,
        "labels": LABELS,
        "definitions": leaf.DEFINITIONS,
        # Match the exact key order of saved runtime specs before CPU rendering.
        # Tool dictionaries are serialized into Qwen's physical prompt; their
        # key order is therefore observable even when JSON values are equal.
        "contract": json.loads(
            json.dumps(
                json.loads((SIDE / "trec-leaf-contract-probe-v1/CONTRACT.json").read_text()),
                sort_keys=True,
            )
        ),
        "max_tokens": 3072 if comparison == "representation" else 1024,
        "max_concurrent_calls": 4,
        "call_timeout_seconds": 60,
        "wall_time_cap_seconds": 300,
    }
    audit = json.loads((ROOT / "SEED_AUDIT.json").read_text())
    if audit["seeds"] != SEEDS or audit["exit_code"] != 1 or audit["matches"]:
        raise ValueError("fresh seed collision audit not satisfied")
    selection = json.loads(SELECTION.read_text())
    if (
        selection["selected"]["checkpoint"] != str(ADAPTER)
        or selection["selected"]["epoch"] != 2
        or selection["post_training_test_inspected"] is not False
        or file_hash(ADAPTER / "adapter_model.safetensors") != SELECTED_SHA
        or file_hash(ADAPTER / "adapter_config.json") != CONFIG_SHA
    ):
        raise ValueError("requires frozen old selected child")
    paths = [
        Path(__file__),
        ROOT / "test_driver.py",
        ROOT / "DESIGN.md",
        ROOT / "PLAN.md",
        ROOT / "SEED_AUDIT.json",
        ROOT / "CPU_QUALIFICATION.runtime-order-v2.json",
        ROOT / "README.md",
        OLD_VALIDATION,
        FIXED,
        leaf.ROOT / "driver.py",
        leaf.ROOT / "CONTRACT.json",
        SELECTION,
        ADAPTER / "adapter_model.safetensors",
        ADAPTER / "adapter_config.json",
        BASE / "tokenizer.json",
        BASE / "tokenizer_config.json",
        BASE / "local-research-manifest.json",
        SIDE / "trec-leaf-split-provenance-v1/PROPOSED_SPLIT.json",
        SIDE / "trec-leaf-split-provenance-v1/INVENTORY.json",
    ]
    if (BASE / "chat_template.jinja").exists():
        paths.append(BASE / "chat_template.jinja")
    spec = {
        "schema": ROOT.name,
        "comparison": comparison,
        "design": design,
        "source_file_sha256": {str(p): file_hash(p) for p in paths},
        "weights": {
            "adapter_path": str(ADAPTER),
            "adapter_sha256": SELECTED_SHA,
            "config_sha256": CONFIG_SHA,
            "base_path": str(BASE),
        },
        "provenance": {
            "partition_id": PARTITION,
            "source_test_file_read": False,
            "source_test_entries_accessed": False,
            "label_selected_cases": False,
            "validation_order": "unchanged validation720 record_index1..256, question-group-hash order",
            "unique_question_groups": 256,
            "source_validation_groups": 300,
            "validation_manifest_sha256": file_hash(OLD_VALIDATION),
            "caution": "New compositions of reused validation questions, not untouched test data.",
        },
        "plan_sha256": digest(plan),
        "request_sha256": {r["id"]: digest(make_request(design, r)) for r in plan},
    }
    return spec


def make_request(design: dict, row: dict) -> dict:
    body = leaf.make_request(design, {**row, "arm": "both"}, design["model_alias"])
    scoring = design["batches"][row["batch_id"]]["gold"]
    records = [scoring["records"][i] for i in scoring["order"]]
    if row["arm"] == "anonymous":
        return body
    ids = [r["id"] for r in records]
    value = {"type": "string", "enum": design["labels"]}
    if row["arm"] == "indexed":
        instruction = (
            "Return only a JSON object mapping every input ID to its one label. "
            "Include each input ID exactly once, with no missing or extra IDs. "
            "Emit entries in input order. Allowed labels: \n"
        )
    else:
        instruction = (
            "Return only a JSON object mapping every input ID to an object with "
            'exactly "question" and "label". For each entry, first copy the complete '
            'input question verbatim into "question", then emit its one label in "label". '
            "Include every input ID exactly once, with no missing or extra IDs. "
            "Emit entries in input order. Allowed labels: \n"
        )
        value = {
            "type": "object",
            "properties": {"question": {"type": "string"}, "label": value},
            "required": ["question", "label"],
            "additionalProperties": False,
        }
    prefix = instruction + ", ".join(design["labels"]) + ".\n"
    body["messages"][1]["content"] = (
        prefix
        + "\n"
        + design["definitions"]
        + "\n"
        + json.dumps({r["id"]: r["question"] for r in records})
    )
    body["structured_outputs"] = {
        "json": {
            "type": "object",
            "properties": {key: deepcopy(value) for key in ids},
            "required": ids,
            "additionalProperties": False,
        }
    }
    return body


def strict_object(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError("duplicate_json_key:" + key)
        result[key] = value
    return result


def reject_constant(value):
    raise ValueError("nonfinite_json:" + value)


def score_response(content: str | None, scoring: dict) -> dict:
    records, order, arm = scoring["records"], scoring["order"], scoring["arm"]
    n = len(records)
    predictions, copies, before, output_positions = [None] * n, [None] * n, [None] * n, [None] * n
    reason, raw = None, None
    try:
        raw = json.loads(content, object_pairs_hook=strict_object, parse_constant=reject_constant)
        if arm == "anonymous":
            if not isinstance(raw, list) or any(not isinstance(v, str) for v in raw):
                raise ValueError("wrong_representation")
            if len(raw) != n:
                raise ValueError("length_mismatch")
            for position, source in enumerate(order):
                predictions[source], output_positions[source] = raw[position], position + 1
        else:
            expected = {r["id"] for r in records}
            if not isinstance(raw, dict):
                raise ValueError("wrong_representation")
            if set(raw) != expected:
                raise ValueError("missing_or_extra_ids")
            for source, record in enumerate(records):
                value = raw[record["id"]]
                if arm == "echo":
                    if (
                        not isinstance(value, dict)
                        or set(value) != {"question", "label"}
                        or not isinstance(value["question"], str)
                    ):
                        raise ValueError("wrong_echo_shape")
                    copies[source] = value["question"] == record["question"]
                    before[source] = list(value) == ["question", "label"]
                    value = value["label"]
                if not isinstance(value, str):
                    raise ValueError("nonstring_label")
                predictions[source] = value
                output_positions[source] = list(raw).index(record["id"]) + 1
    except (ValueError, TypeError) as error:
        reason = str(error)
        predictions, copies, before, output_positions = (
            [None] * n,
            [None] * n,
            [None] * n,
            [None] * n,
        )
    aligned = reason is None
    invalid = sum(p not in LABELS for p in predictions) if aligned else 0
    return {
        "parse_status": "aligned" if aligned else reason,
        "raw_array_length": len(raw) if isinstance(raw, list) else None,
        "schema_valid": aligned and not invalid,
        "records": n,
        "aligned_records": n if aligned else 0,
        "predictions": predictions,
        "strict_correct": sum(
            p == r["gold_label"] for p, r in zip(predictions, records, strict=True)
        ),
        "noncanonical_labels": invalid,
        "copy_exact": copies,
        "echo_question_before_label": before,
        "output_positions": output_positions,
        "input_positions": [order.index(i) + 1 for i in range(n)],
    }


def score_coordinate(design: dict, coordinate: dict, records: list[dict]) -> dict:
    selected = [r for r in records if r["coordinate"]["id"] == coordinate["id"]]
    if len(selected) > 1:
        raise ValueError("duplicate call checkpoint")
    scoring = design["batches"][coordinate["batch_id"]]["gold"]
    record = selected[0] if selected else None
    score = record.get("score") if record else None
    item_rows = []
    if score is not None:
        for i, source in enumerate(scoring["records"]):
            item_rows.append(
                {
                    **source,
                    "source_position": i + 1,
                    "input_position": score["input_positions"][i],
                    "output_position": score["output_positions"][i],
                    "prediction": score["predictions"][i],
                    "aligned": score["aligned_records"] == len(scoring["records"]),
                    "canonical_correct": score["predictions"][i] == source["gold_label"],
                    "copy_exact": score["copy_exact"][i],
                    "echo_question_before_label": score["echo_question_before_label"][i],
                }
            )
    raw = record.get("raw_response", {}) if record else {}
    # Alias/protocol rejection can occur after raw usage arrived. Keep its observed
    # cost without admitting that response for scientific scoring.
    usage = (record.get("usage") or leaf.usage_metrics(raw.get("usage") or {})) if record else {}
    ids = raw.get("prompt_token_ids")
    decoded = tokenizer().decode(ids, skip_special_tokens=False) if isinstance(ids, list) else None
    request = record["request"] if record else None
    complete_input = (
        decoded is not None
        and request is not None
        and all(m["content"] in decoded for m in request["messages"])
        and len(ids) == raw.get("usage", {}).get("prompt_tokens")
    )
    qualification = json.loads((ROOT / "CPU_QUALIFICATION.runtime-order-v2.json").read_text())
    rendered = next(r for r in qualification["results"] if r["comparison"] == design["comparison"])
    expected_prompt = rendered["rendered_prompts"][coordinate["id"]]
    available = score is not None and score["schema_valid"]
    counts = {}
    for label in ["human being", "numeric value"]:
        gold = sum(r["gold_label"] == label for r in scoring["records"])
        predicted = sum(r["prediction"] == label for r in item_rows) if available else None
        counts[label] = {
            "gold_count": gold,
            "predicted_count": predicted,
            "strict": int(predicted == gold) if available else 0 if score is not None else None,
        }
    return {
        "coordinate": coordinate,
        "model_completed": score is not None,
        "schema_valid": available,
        "aligned_records": score["aligned_records"] if score else 0,
        "canonical_correct": score["strict_correct"] if score else 0,
        "record_results": item_rows,
        "counts": counts,
        "usage": usage,
        "model_called": bool(record and record.get("model_called")),
        "call_wall_seconds": record["ended"] - record["started"] if record else None,
        "physical_prompt": {
            "captured": isinstance(ids, list),
            "token_ids_sha256": digest(ids) if isinstance(ids, list) else None,
            "expected_cpu_token_ids_sha256": expected_prompt["token_ids_sha256"],
            "exact_cpu_template_match": digest(ids) == expected_prompt["token_ids_sha256"]
            if isinstance(ids, list)
            else None,
            "full_system_and_user_input_verified": complete_input,
        },
        "error": record.get("error") if record else None,
        "finish_reason": record.get("finish_reason") if record else None,
    }


# Only this privately loaded module instance is adapted. Frozen source files never change.
fixed.make_request = make_request
fixed.leaf.score_labels = score_response
fixed.score_coordinate = score_coordinate
collect_calls = fixed.collect_calls


def summarize(design: dict, records: list[dict]) -> dict:
    coordinates = [score_coordinate(design, c, records) for c in design["coordinates"]]
    cells = []
    keys = sorted({(r["arm"], r["offset"]) for r in design["plan"]})
    for arm, offset in keys:
        rows = [
            r
            for r in coordinates
            if (r["coordinate"]["arm"], r["coordinate"]["offset"]) == (arm, offset)
        ]
        items = [item for r in rows for item in r["record_results"]]
        aligned = [r for r in items if r["aligned"]]
        cells.append(
            {
                "arm": arm,
                "offset": offset,
                "planned_calls": len(rows),
                "model_completed_calls": sum(r["model_completed"] for r in rows),
                "dispatched_calls": sum(r["model_called"] for r in rows),
                "schema_valid_calls": sum(r["schema_valid"] for r in rows),
                "planned_assignments": len(rows) * 64,
                "aligned_assignments": len(aligned),
                "canonical_correct": sum(r["canonical_correct"] for r in aligned),
                "accuracy_among_aligned": sum(r["canonical_correct"] for r in aligned)
                / len(aligned)
                if aligned
                else None,
                "copy_exact": sum(r["copy_exact"] is True for r in items),
                "copy_observed": sum(r["copy_exact"] is not None for r in items),
                "echo_question_before_label": sum(
                    r["echo_question_before_label"] is True for r in items
                ),
                "physical_input_unverified_completed_calls": sum(
                    r["model_completed"]
                    and not r["physical_prompt"]["full_system_and_user_input_verified"]
                    for r in rows
                ),
                "physical_prompt_exact_cpu_matches": sum(
                    r["physical_prompt"]["exact_cpu_template_match"] is True for r in rows
                ),
                "truncated_calls": sum(r["finish_reason"] == "length" for r in rows),
                "input_position_quarters": [
                    {
                        "first": start,
                        "aligned": sum(start <= r["input_position"] < start + 16 for r in aligned),
                        "correct": sum(
                            r["canonical_correct"] and start <= r["input_position"] < start + 16
                            for r in aligned
                        ),
                    }
                    for start in [1, 17, 33, 49]
                ],
                "confusion": [
                    {"gold": g, "prediction": p, "count": n}
                    for (g, p), n in sorted(
                        Counter((r["gold_label"], r["prediction"]) for r in aligned).items()
                    )
                ],
                "usage": {
                    k: sum(r["usage"].get(k) or 0 for r in rows)
                    for k in [
                        "logical_input_tokens",
                        "cached_input_tokens",
                        "uncached_input_tokens",
                        "completion_tokens",
                    ]
                },
                "missing_usage_calls": {
                    k: sum(r["model_called"] and r["usage"].get(k) is None for r in rows)
                    for k in [
                        "logical_input_tokens",
                        "cached_input_tokens",
                        "uncached_input_tokens",
                        "completion_tokens",
                    ]
                },
                "call_wall_seconds_sum": sum(r["call_wall_seconds"] or 0 for r in rows),
                "counts_strict": {
                    label: sum(r["counts"][label]["strict"] or 0 for r in rows)
                    for label in ["human being", "numeric value"]
                },
            }
        )
    return {
        "comparison": design["comparison"],
        "cells": cells,
        "coordinates": coordinates,
        "caution": "Four compositions/256 unique reused validation questions; seeds and rotations are repeated measurements. Invalid cardinality/IDs are unaligned, not all semantically wrong. Count scores may hide cancelling errors. No voting or repair.",
    }


def validate_endpoint(descriptor: dict) -> None:
    if (
        descriptor.get("adapter", {}).get("model_sha256") != SELECTED_SHA
        or descriptor["adapter"].get("config_sha256") != CONFIG_SHA
        or descriptor["adapter"].get("path") != str(ADAPTER)
    ):
        raise ValueError("requires frozen old selected child c32de, not mixed-size A/B")
    leaf.verify_weights(descriptor)
    if (
        descriptor["base_model"]["path"] != str(BASE)
        or not descriptor.get("inference_only")
        or descriptor.get("vllm", {}).get("version") != "0.28.0"
        or descriptor["vllm"].get("max_model_len", 0) < 8192
        or not isinstance(descriptor["port"], int)
        or not 1024 <= descriptor["port"] <= 65535
    ):
        raise ValueError("requires an actual compatible local inference descriptor")


def validate_live_models(descriptor: dict, response: dict) -> None:
    cards = {r["id"]: r for r in response["data"]}
    card = cards.get(descriptor["model_alias"], {})
    if card.get("root") != str(ADAPTER) or card.get("parent") != str(BASE):
        raise ValueError("live alias/root/base differs from bound old selected child")
    if cards.get(str(BASE), {}).get("max_model_len", 0) < 8192:
        raise ValueError("live base context limit is not qualified")


def verify_inputs(spec: dict) -> None:
    for p, h in spec["source_file_sha256"].items():
        if file_hash(Path(p)) != h:
            raise ValueError("frozen source changed: " + p)
    if "endpoint_binding" in spec:
        binding = spec["endpoint_binding"]
        expected = bind_spec(Path(binding["unbound_spec_path"]), Path(binding["descriptor_path"]))
    else:
        expected = build_spec(spec["comparison"])
    if expected != spec:
        raise ValueError("frozen specification differs from actual inputs")


def bind_spec(unbound_path: Path, endpoint_path: Path) -> dict:
    spec = json.loads(unbound_path.read_text())
    if "endpoint_binding" in spec:
        raise ValueError("bind an unbound frozen comparison, not an old endpoint binding")
    verify_inputs(spec)
    descriptor = json.loads(endpoint_path.read_text())
    validate_endpoint(descriptor)
    spec["design"]["model_alias"] = descriptor["model_alias"]
    spec["endpoint_binding"] = {
        "unbound_spec_path": str(unbound_path.resolve()),
        "unbound_spec_sha256": file_hash(unbound_path),
        "descriptor_path": str(endpoint_path.resolve()),
        "descriptor_sha256": file_hash(endpoint_path),
        "descriptor": descriptor,
        "live_contact_during_binding": False,
    }
    spec["request_sha256"] = {
        r["id"]: digest(make_request(spec["design"], r)) for r in spec["design"]["plan"]
    }
    return spec


def qualify(spec: dict) -> dict:
    import xgrammar as xgr
    from transformers import AutoTokenizer
    from vllm.entrypoints.openai.chat_completion.protocol import ChatCompletionRequest

    hf = AutoTokenizer.from_pretrained(str(BASE), local_files_only=True, trust_remote_code=False)
    info = xgr.TokenizerInfo.from_huggingface(hf)
    compiler = xgr.GrammarCompiler(info, max_threads=1)
    schemas, prompts = {}, {}
    for row in spec["design"]["plan"]:
        body = make_request(spec["design"], row)
        before = digest(body)
        ChatCompletionRequest.model_validate(deepcopy(body))
        schema = body["structured_outputs"]["json"]
        key = digest(schema)
        if key not in schemas:
            compiler.compile_json_schema(json.dumps(schema))
            schemas[key] = {"type": schema["type"], "compiled": True}
        ids = hf.apply_chat_template(
            body["messages"],
            tools=body["tools"],
            add_generation_prompt=True,
            tokenize=True,
            return_dict=False,
        )
        if not isinstance(ids, list) or any(not isinstance(i, int) for i in ids):
            raise TypeError("CPU rendered prompt must be a flat integer token list")
        if len(ids) + body["max_tokens"] >= 8192:
            raise ValueError("rendered input plus requested cap exceeds model context")
        if digest(body) != before:
            raise ValueError("CPU schema validation mutated request")
        prompts[row["id"]] = {"tokens": len(ids), "token_ids_sha256": digest(ids)}
    return {
        "comparison": spec["comparison"],
        "requests_validated": len(prompts),
        "distinct_schemas_compiled": len(schemas),
        "schemas": schemas,
        "rendered_prompts": prompts,
        "max_input_tokens": max(p["tokens"] for p in prompts.values()),
        "versions": {
            p: importlib.metadata.version(p)
            for p in ["httpx", "vllm", "xgrammar", "transformers", "tokenizers"]
        },
        "live_model_calls": 0,
        "caution": "CPU grammar/protocol support verified; live enforcement remains a run-time observation.",
    }


async def run(bound_path: Path, output: Path) -> int:
    spec = json.loads(bound_path.read_text())
    verify_inputs(spec)
    if "endpoint_binding" not in spec:
        raise ValueError("run requires a newly bound truthful endpoint descriptor")
    descriptor = spec["endpoint_binding"]["descriptor"]
    url = f"http://{descriptor['host']}:{descriptor['port']}/v1"
    key = os.environ[descriptor["api_key_env"]]
    output.mkdir(parents=True, exist_ok=False)
    (output / "calls").mkdir()
    (output / "coordinates").mkdir()
    write_once(output / "SPEC.json", spec)
    write_once(output / "ENDPOINT.json", descriptor)
    started, deadline = time.time(), time.monotonic() + 300
    write_once(
        output / "ATTEMPT.json",
        {
            "started": started,
            "bound_spec_sha256": file_hash(bound_path),
            "url": url,
            "model_alias": descriptor["model_alias"],
            "adapter_sha256": SELECTED_SHA,
        },
    )
    records, reason = [], None
    try:
        async with asyncio.timeout(max(0.001, deadline - time.monotonic())):
            async with httpx.AsyncClient(
                headers={"Authorization": "Bearer " + key}, timeout=60, trust_env=False
            ) as client:
                version = await client.get(url.removesuffix("/v1") + "/version")
                version.raise_for_status()
                write_once(output / "VERSION_PREFLIGHT.json", version.json())
                if version.json().get("version") != "0.28.0":
                    raise ValueError("live vLLM version changed")
                response = await client.get(url + "/models")
                response.raise_for_status()
                write_once(output / "MODELS_PREFLIGHT.json", response.json())
                validate_live_models(descriptor, response.json())
                records, reason = await collect_calls(client, url, spec, output, deadline)
    except TimeoutError:
        reason = "wall_time_cap"
    except Exception as error:
        reason = "preflight_or_runtime_error:" + type(error).__name__
        write_once(
            output / "ERROR.json", {"type": type(error).__name__, "message": str(error)[:1200]}
        )
    finally:
        records = [json.loads(p.read_text()) for p in sorted((output / "calls").glob("*.json"))]
        write_once(output / "analysis.json", summarize(spec["design"], records))
        seen = {r["coordinate"]["id"] for r in records}
        write_once(
            output / "STATUS.json",
            {
                "planned": len(spec["design"]["plan"]),
                "recorded": len(records),
                "stop_reason": reason,
                "wall_seconds": time.time() - started,
                "unrun": [r["id"] for r in spec["design"]["plan"] if r["id"] not in seen],
            },
        )
    return 0 if reason is None and len(records) == len(spec["design"]["plan"]) else 2


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command", choices=["design", "preflight", "bind", "run"])
    parser.add_argument("--comparison", choices=["representation", "rotation"])
    parser.add_argument("--spec-path", type=Path)
    parser.add_argument("--frozen-spec", type=Path)
    parser.add_argument("--endpoint-descriptor", type=Path)
    parser.add_argument("--output-dir", type=Path)
    args = parser.parse_args()
    if args.command == "design":
        if not args.comparison:
            parser.error("design requires --comparison")
        spec = build_spec(args.comparison)
        if args.spec_path:
            write_once(args.spec_path, spec)
            print(
                json.dumps(
                    {
                        "frozen_spec": str(args.spec_path),
                        "sha256": file_hash(args.spec_path),
                        "live_model_calls": 0,
                    }
                )
            )
        else:
            print(json.dumps(spec, sort_keys=True, separators=(",", ":")))
    elif args.command == "preflight":
        if not args.spec_path:
            parser.error("preflight requires --spec-path")
        spec = json.loads(args.spec_path.read_text())
        verify_inputs(spec)
        print(json.dumps(qualify(spec), sort_keys=True))
    elif args.command == "bind":
        if not args.spec_path or not args.endpoint_descriptor or not args.comparison:
            parser.error("bind requires --comparison --endpoint-descriptor --spec-path NEW.json")
        frozen = args.frozen_spec or ROOT / (
            "SPEC-" + args.comparison.upper() + ".runtime-order-v2.json"
        )
        spec = bind_spec(frozen, args.endpoint_descriptor)
        if spec["comparison"] != args.comparison:
            raise ValueError("wrong comparison specification")
        write_once(args.spec_path, spec)
        print(
            json.dumps(
                {
                    "bound_spec": str(args.spec_path),
                    "sha256": file_hash(args.spec_path),
                    "live_model_calls": 0,
                }
            )
        )
    else:
        if not args.spec_path or not args.output_dir:
            parser.error("run requires --spec-path --output-dir NEW")
        raise SystemExit(asyncio.run(run(args.spec_path, args.output_dir)))


if __name__ == "__main__":
    main()
