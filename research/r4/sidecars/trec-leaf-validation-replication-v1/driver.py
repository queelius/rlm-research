"""Clean validation replication of frozen leaf request contracts; never starts a server."""

from __future__ import annotations

import argparse
import asyncio
import hashlib
import importlib.util
import json
import os
import re
import time
import unicodedata
from collections import Counter
from pathlib import Path

import httpx

ROOT = Path(__file__).resolve().parent
OLD = ROOT.parent / "trec-leaf-contract-probe-v1"
SPLIT = ROOT.parent / "trec-leaf-split-provenance-v1/PROPOSED_SPLIT.json"
INVENTORY = SPLIT.with_name("INVENTORY.json")
TRAIN = Path(
    "/project/alex_phd/research-cache/2026-09-08-literature/trec-context8.6NYSkv/train_5500.label"
)
POOL = TRAIN.with_name("oolong__trec_coarse_validated.jsonl")
DEFAULT_ENDPOINT = (
    ROOT.parents[1]
    / "operations/2026-09-08-resume/inference-frozen-contract-attempt-001/endpoint.json"
)
STEP0_SHA = "e5be32e83aa00893f7c75074d79843b8a7f88cc4cf794fab75ca00c7b48e05a8"
PARTITION = "36e7d2e1ad83210f6420a0312ec46e8a8c70d764e9df0e6d631c67f6fd16c764"
OLD_SHA = "a82baf0d9be7f5cbc756ced908c405f6aba4497b46a4ca56e15c8900798c8bce"


def file_hash(path: Path) -> str:
    with path.open("rb") as stream:
        return hashlib.file_digest(stream, "sha256").hexdigest()


if file_hash(OLD / "driver.py") != OLD_SHA:
    raise ValueError("frozen leaf72 helper source changed")
_spec = importlib.util.spec_from_file_location("frozen_leaf72_helpers", OLD / "driver.py")
base = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(base)
ARMS, LABELS = base.ARMS, base.LABELS
make_request, score_labels = base.make_request, base.score_labels
digest, write_once, usage_metrics = base.digest, base.write_once, base.usage_metrics
ALIASES = {
    "description": "description and abstract concept",
    "abstract concept": "description and abstract concept",
}
COARSE = dict(zip(("HUM", "LOC", "ABBR", "ENTY", "DESC", "NUM"), LABELS, strict=True))


def question_group(question: str) -> str:
    normalized = " ".join(re.findall(r"\w+", unicodedata.normalize("NFKC", question).casefold()))
    return hashlib.sha256(normalized.encode()).hexdigest()


def make_design() -> dict:
    expected = {
        SPLIT: "3f5f648488d512d2052b9f3d57c02e030af8e939ca363998c07a556a47d7f457",
        INVENTORY: "5ad3bc2e9d2e440500a918b3ed7d41d163a29dceaf26cc31b41c2f488ffd660b",
        ROOT / "DESIGN.md": "9949f4802db5abd8e0eac35001d29a95bd07c6faf06b8c13e8a8778a1c3948af",
        OLD / "driver.py": OLD_SHA,
        OLD / "CONTRACT.json": "cb50c6fddff7ea62a96936a7fcb58da84307248028adb420d7b1ab971a74bea7",
    }
    if any(file_hash(path) != sha for path, sha in expected.items()):
        raise ValueError("frozen source hash changed")
    inventory = json.loads(INVENTORY.read_text())
    for path in (TRAIN, POOL):
        expected[path] = inventory["source_file_sha256"][str(path)]
        if file_hash(path) != expected[path]:
            raise ValueError("authenticated source train/pool hash changed")
    split = json.loads(SPLIT.read_text())
    if split["partition_id"] != PARTITION:
        raise ValueError("wrong question partition")
    # Access validation only. No source-test question, label file or split entries are used.
    selected = sorted(split["validation"], key=lambda r: r["question_group_sha256"])
    if len(selected) != 300 or len({r["question_group_sha256"] for r in selected}) != 300:
        raise ValueError("validation must contain exactly 300 unique declared groups")
    source_lines = TRAIN.read_bytes().splitlines()
    pool_groups = {
        question_group(json.loads(line)["input"]) for line in POOL.read_text().splitlines()
    }
    prior_groups = {
        group
        for context in inventory["old_contexts"].values()
        for group in context["question_group_sha256"]
    }
    records = []
    for index, row in enumerate(selected, 1):
        line_number = row["source_line_1based"][0]
        fine, _, question = (
            source_lines[line_number - 1]
            .replace(b"\xf0", b" ")
            .strip()
            .decode("utf-8")
            .partition(" ")
        )
        coarse = fine.split(":")[0]
        if coarse != row["coarse"] or question_group(question) != row["question_group_sha256"]:
            raise ValueError("source representative/label disagrees with frozen partition")
        if row["question_group_sha256"] in pool_groups | prior_groups:
            raise ValueError("validation group overlaps inspected OOLONG input")
        records.append(
            {
                "record_index": index,
                "question_group_sha256": row["question_group_sha256"],
                "source_line_1based": line_number,
                "source_all_group_lines": row["source_line_1based"],
                "source": "official_trec_train",
                "question": question,
                "coarse": coarse,
                "gold_label": COARSE[coarse],
            }
        )
    if Counter(r["coarse"] for r in records) != Counter(
        {"ABBR": 5, "DESC": 59, "ENTY": 59, "HUM": 59, "LOC": 59, "NUM": 59}
    ):
        raise ValueError("validation class inventory changed")
    batches = [
        {
            "batch_id": start // 5,
            "record_indices": [r["record_index"] for r in records[start : start + 5]],
            "questions": [r["question"] for r in records[start : start + 5]],
            "question_group_sha256": [
                r["question_group_sha256"] for r in records[start : start + 5]
            ],
        }
        for start in range(0, len(records), 5)
    ]
    seeds = [980260100, 980260101, 980260102]
    plan = []
    for repetition, seed in enumerate(seeds):
        for batch in batches:
            shift = (batch["batch_id"] + repetition) % len(ARMS)
            for order, arm in enumerate(ARMS[shift:] + ARMS[:shift]):
                row = {
                    "batch_id": batch["batch_id"],
                    "arm": arm,
                    "seed": seed,
                    "repetition": repetition,
                    "arm_order": order,
                    "dispatch_order": len(plan),
                }
                row["id"] = digest(
                    [ROOT.name, PARTITION, batch["question_group_sha256"], arm, seed]
                )
                plan.append(row)
    return {
        "schema": "trec-leaf-validation-design-v1",
        "study": ROOT.name,
        "analysis_split": "clean_source_train_validation_exploratory",
        "partition_id": PARTITION,
        "records": records,
        "batches": batches,
        "plan": plan,
        "seeds": seeds,
        "plan_sha256": digest(plan),
        "contract": json.loads((OLD / "CONTRACT.json").read_text()),
        "definitions": base.DEFINITIONS,
        "labels": list(LABELS),
        "max_tokens": 256,
        "max_concurrent_calls": 4,
        "call_timeout_seconds": 30,
        "wall_time_cap_seconds": 600,
        "planned_calls": len(plan),
        "planned_record_labels": sum(len(batches[r["batch_id"]]["record_indices"]) for r in plan),
        "source_file_sha256": {str(path): sha for path, sha in expected.items()}
        | {str(Path(__file__)): file_hash(Path(__file__))},
        "provenance": {
            "source_test_file_read": False,
            "source_test_split_entries_used": False,
            "validation_intersects_prior_pool": 0,
            "validation_intersects_old_contexts": 0,
            "normalization": split["normalization"],
            "trec_data_license": "unknown",
            "source_test_disjointness": "inherited from authenticated partition audit; not re-read",
        },
    }


def verify_original_weights(descriptor: dict) -> None:
    if descriptor["adapter"]["model_sha256"] != STEP0_SHA:
        raise ValueError("this recipe requires the original step0 adapter")
    base.verify_weights(descriptor)
    if descriptor.get("vllm", {}).get("version") != "0.28.0":
        raise ValueError(
            "use the actual current inference descriptor, not a stale planned endpoint"
        )


def bind_spec(descriptor_path: Path) -> dict:
    descriptor = json.loads(descriptor_path.read_text())
    verify_original_weights(descriptor)
    design = make_design()
    return {
        "schema": "trec-leaf-validation-bound-spec-v1",
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
    def cell(arm: str, seed: int | None = None) -> dict:
        def matches(row):
            return row["arm"] == arm and (seed is None or row["seed"] == seed)

        planned = [r for r in design["plan"] if matches(r)]
        rows = [r for r in records if matches(r["coordinate"])]
        completed = [r for r in rows if r["score"] is not None]
        labels = [z for r in completed for z in r["record_results"]]
        denominator = sum(r["score"]["records"] for r in completed)
        planned_denominator = sum(
            len(design["batches"][r["batch_id"]]["record_indices"]) for r in planned
        )
        correct = sum(z["prediction"] == z["gold_label"] for z in labels)
        alias_correct = sum(
            ALIASES.get(z["prediction"], z["prediction"]) == z["gold_label"] for z in labels
        )
        confusion = Counter(
            (
                z["gold_label"],
                z["prediction"] if z["prediction"] in LABELS else "__invalid_or_noncanonical__",
            )
            for z in labels
        )
        classwise = [
            {
                "label": label,
                "observed": sum(z["gold_label"] == label for z in labels),
                "correct": sum(
                    z["gold_label"] == label and z["prediction"] == label for z in labels
                ),
            }
            for label in LABELS
        ]
        for item in classwise:
            item["accuracy"] = item["correct"] / item["observed"] if item["observed"] else None
        acc = [c["accuracy"] for c in classwise if c["accuracy"] is not None]
        return {
            "arm": arm,
            "seed": seed,
            "planned_calls": len(planned),
            "recorded_calls": len(rows),
            "model_completed_calls": len(completed),
            "execution_errors": len(rows) - len(completed),
            "unrecorded_calls": len(planned) - len(rows),
            "planned_record_labels": planned_denominator,
            "observed_record_labels": denominator,
            "strict_correct_record_labels": correct,
            "accuracy_per_model_completed_record": correct / denominator if denominator else None,
            "correct_over_planned_record_labels": correct / planned_denominator
            if planned_denominator
            else None,
            "schema_valid_calls": sum(r["score"]["schema_valid"] for r in completed),
            "truncated_calls": sum(r.get("finish_reason") == "length" for r in completed),
            "alias_sensitivity_correct": alias_correct,
            "alias_map": ALIASES,
            "alias_sensitivity_accuracy": alias_correct / denominator if denominator else None,
            "macro_accuracy_observed_classes": sum(acc) / len(acc) if acc else None,
            "classwise": classwise,
            "confusion": [
                {"gold": a, "prediction": b, "count": n} for (a, b), n in sorted(confusion.items())
            ],
            "reported_logical_input_tokens": sum(
                r["usage"].get("logical_input_tokens") or 0 for r in rows
            ),
            "reported_completion_tokens": sum(
                r["usage"].get("completion_tokens") or 0 for r in rows
            ),
            "missing_usage_calls": sum(
                r["usage"].get("logical_input_tokens") is None for r in rows
            ),
        }

    indexed = {}
    for r in records:
        if r["score"] is not None:
            for z in r["record_results"]:
                indexed[(z["record_index"], r["coordinate"]["seed"], r["coordinate"]["arm"])] = z
    pairs = []
    for first, second in (
        ("baseline", "definitions"),
        ("baseline", "schema"),
        ("definitions", "both"),
        ("schema", "both"),
    ):
        groups = []
        for source in design["records"]:
            changes = []
            for seed in design["seeds"]:
                a = indexed.get((source["record_index"], seed, first))
                b = indexed.get((source["record_index"], seed, second))
                if a is None or b is None:
                    continue
                changes.append(
                    {
                        "seed": seed,
                        "from_prediction": a["prediction"],
                        "to_prediction": b["prediction"],
                        "delta_correct": int(b["prediction"] == b["gold_label"])
                        - int(a["prediction"] == a["gold_label"]),
                        "alias_delta_correct": int(
                            ALIASES.get(b["prediction"], b["prediction"]) == b["gold_label"]
                        )
                        - int(ALIASES.get(a["prediction"], a["prediction"]) == a["gold_label"]),
                    }
                )
            if changes:
                groups.append(
                    {
                        "record_index": source["record_index"],
                        "question_group_sha256": source.get("question_group_sha256"),
                        "paired_repetitions": len(changes),
                        "mean_delta_correct": sum(c["delta_correct"] for c in changes)
                        / len(changes),
                        "changes": changes,
                    }
                )
        pairs.append(
            {
                "from_arm": first,
                "to_arm": second,
                "observed_paired_question_groups": len(groups),
                "question_mean_delta": sum(g["mean_delta_correct"] for g in groups) / len(groups)
                if groups
                else None,
                "question_groups": groups,
            }
        )
    return {
        "schema": "trec-leaf-validation-summary-v1",
        "planned": len(design["plan"]),
        "recorded": len(records),
        "unique_question_groups": len(design["records"]),
        "shared_batches": len(design["batches"]),
        "cells": [cell(a) for a in ARMS],
        "per_seed_cells": [cell(a, s) for s in design["seeds"] for a in ARMS],
        "paired_question_contrasts": pairs,
        "caution": "Validation, not source test; repeated labels share questions/batches. No independence-based CI, silent aliases, tools or RL training admission.",
    }


async def run(spec_path: Path, output: Path) -> None:
    spec = json.loads(spec_path.read_text())
    design, descriptor = spec["design"], spec["endpoint_descriptor"]
    if design != make_design():
        raise ValueError("inputs differ from frozen design")
    if (
        file_hash(Path(spec["source_endpoint_descriptor"]["path"]))
        != spec["source_endpoint_descriptor"]["sha256"]
    ):
        raise ValueError("endpoint descriptor changed")
    verify_original_weights(descriptor)
    for row in design["plan"]:
        if (
            digest(make_request(design, row, descriptor["model_alias"]))
            != spec["request_sha256"][row["id"]]
        ):
            raise ValueError("request specification changed")
    api_key = os.environ[descriptor["api_key_env"]]
    url = f"http://{descriptor['host']}:{descriptor['port']}/v1"
    output.mkdir(parents=True, exist_ok=False)
    (output / "calls").mkdir()
    write_once(output / "SPEC.json", spec)
    started = time.time()
    identity = {
        "model_alias": descriptor["model_alias"],
        "base_revision": descriptor["base_model"]["revision"],
        "adapter_sha256": descriptor["adapter"]["model_sha256"],
    }
    write_once(
        output / "ATTEMPT.json",
        {
            "started": started,
            "spec_sha256": file_hash(spec_path),
            "endpoint": url,
            "model_identity": identity,
        },
    )
    records, pending, stop = [], iter(design["plan"]), asyncio.Event()
    reason = None
    async with httpx.AsyncClient(
        headers={"Authorization": "Bearer " + api_key},
        timeout=design["call_timeout_seconds"],
        trust_env=False,
    ) as client:
        version = await client.get(url.removesuffix("/v1") + "/version")
        version.raise_for_status()
        if version.json().get("version") != "0.28.0":
            raise ValueError("live API differs from qualified vLLM0.28")
        write_once(output / "VERSION_PREFLIGHT.json", version.json())
        models = await client.get(url + "/models")
        models.raise_for_status()
        if descriptor["model_alias"] not in {m["id"] for m in models.json()["data"]}:
            raise ValueError("assigned original alias is not loaded")
        write_once(output / "MODELS_PREFLIGHT.json", models.json())

        async def worker() -> None:
            while not stop.is_set():
                row = next(pending, None)
                if row is None:
                    return
                batch = design["batches"][row["batch_id"]]
                source = [design["records"][i - 1] for i in batch["record_indices"]]
                gold = [r["gold_label"] for r in source]
                body = make_request(design, row, descriptor["model_alias"])
                record = {
                    "coordinate": row,
                    "request": body,
                    "request_sha256": digest(body),
                    "started": time.time(),
                    "score": None,
                    "usage": {},
                    "record_results": [],
                    "model_identity": identity,
                    "source_groups": [
                        {
                            "question_group_sha256": r["question_group_sha256"],
                            "source_line_1based": r["source_line_1based"],
                        }
                        for r in source
                    ],
                }
                try:
                    response = await client.post(url + "/chat/completions", json=body)
                    record.update(http_status=response.status_code, raw_response_text=response.text)
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
                    record["score"], record["usage"] = score, usage_metrics(raw.get("usage") or {})
                    record["record_results"] = [
                        {
                            "record_index": r["record_index"],
                            "question_group_sha256": r["question_group_sha256"],
                            "source_line_1based": r["source_line_1based"],
                            "gold_label": g,
                            "prediction": p,
                            "strict_correct": g == p,
                        }
                        for r, g, p in zip(source, gold, score["predictions"], strict=True)
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
                                "seed": row["seed"],
                                "strict_correct": record["score"]["strict_correct"]
                                if record["score"]
                                else None,
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
                    "planned": len(design["plan"]),
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
    parser.add_argument("--endpoint-descriptor", type=Path, default=DEFAULT_ENDPOINT)
    parser.add_argument("--spec-path", type=Path)
    parser.add_argument("--output-dir", type=Path)
    args = parser.parse_args()
    if args.mode == "design":
        print(json.dumps(make_design(), sort_keys=True, indent=2))
    elif args.mode == "bind":
        if not args.spec_path:
            parser.error("bind requires a new --spec-path")
        write_once(args.spec_path, bind_spec(args.endpoint_descriptor))
        print(json.dumps({"spec": str(args.spec_path), "sha256": file_hash(args.spec_path)}))
    else:
        if not args.spec_path or not args.output_dir:
            parser.error("run requires --spec-path and new --output-dir")
        asyncio.run(run(args.spec_path, args.output_dir))


if __name__ == "__main__":
    main()
