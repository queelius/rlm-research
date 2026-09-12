"""CPU-only broader AG source selection; no model inference or trainer."""

import copy
import importlib.metadata
import importlib.util
import json
import os
import subprocess
import sys
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent
SIDE = ROOT.parent
OLD_PREPARE = SIDE / "helper-agnews-data-vs-mechanics-v1/prepare.py"
spec = importlib.util.spec_from_file_location("broader_ag_existing_selection", OLD_PREPARE)
old = importlib.util.module_from_spec(spec)
spec.loader.exec_module(old)
NAMESPACE = "agnews-native-hf-eightstep-dose-v1|20260912"
old.NAMESPACE = NAMESPACE
FROZEN = SIDE / "helper-agnews-data-vs-mechanics-v1/inputs"
EVAL_PREPARE = SIDE / "helper-agnews-heldout-eval-v1/prepare_eval.py"
spec = importlib.util.spec_from_file_location("broader_ag_existing_prompt_seam", EVAL_PREPARE)
prompt_source = importlib.util.module_from_spec(spec)
spec.loader.exec_module(prompt_source)


def freeze_selection(
    rows,
    excluded,
    excluded_ids,
    *,
    steps_count=8,
    train_per_step_label=32,
    heldout_per_label=128,
):
    word_groups = defaultdict(list)
    for row in rows:
        word_groups[old.word_norm(row["text"])].append(row)
    duplicates = [group for group in word_groups.values() if len(group) > 1]
    singletons = [group[0] for group in word_groups.values() if len(group) == 1]
    train, heldout, audit = old.select_rows(
        singletons,
        excluded,
        excluded_ids=excluded_ids,
        train_per_label=steps_count * train_per_step_label,
        heldout_per_label=heldout_per_label,
    )
    by_label = defaultdict(list)
    for row in train:
        by_label[row["label_id"]].append(row)
    for group in by_label.values():
        group.sort(key=lambda row: old.text_sha(NAMESPACE + "|candidate|" + row["source_id"]))
    steps = []
    for index in range(steps_count):
        step = [
            row
            for label in old.AG_LABELS
            for row in by_label[label][
                index * train_per_step_label : (index + 1) * train_per_step_label
            ]
        ]
        steps.append(order_records(step, f"step-{index + 1:03d}"))
    selected = [row for step in steps for row in step] + heldout
    for row in selected:
        row["word_normalized_sha256"] = old.text_sha(old.word_norm(row["text"]))
    if len({row["source_id"] for row in selected}) != len(selected):
        raise ValueError("selected source IDs overlap")
    for normalizer in (old.whitespace_norm, old.word_norm):
        norms = [normalizer(row["text"]) for row in selected]
        if len(set(norms)) != len(selected) or set(norms) & excluded:
            raise ValueError("selected normalization/exposure overlap")
    audit.update(
        original_source_rows=len(rows),
        word_duplicate_groups_rejected=len(duplicates),
        word_duplicate_rows_rejected=sum(map(len, duplicates)),
        word_duplicate_conflicting_label_groups=sum(
            len({row["label_id"] for row in group}) > 1 for group in duplicates
        ),
        whitespace_duplicate_groups_on_original=sum(
            count > 1
            for count in Counter(old.whitespace_norm(row["text"]) for row in rows).values()
        ),
        selected_source_id_overlap=0,
        selected_normalized_overlap=0,
        selected_exclusion_overlap=0,
    )
    return steps, heldout, audit


def order_records(rows, role):
    return sorted(
        rows, key=lambda row: old.text_sha(NAMESPACE + "|" + role + "|" + row["source_id"])
    )


def context_bound(lengths):
    if not lengths or max(lengths) + 1024 > 8192:
        raise ValueError("exact prompt plus1024 exceeds8192 context bound")
    return {
        "min_prompt_tokens": min(lengths),
        "max_prompt_tokens": max(lengths),
        "max_completion_tokens": 1024,
        "max_prompt_plus_completion": max(lengths) + 1024,
        "actual_context_cap_required": 8192,
        "truncated_or_replaced_records": 0,
    }


def extract_public(value, texts, ids):
    if isinstance(value, dict):
        for key, item in value.items():
            if key in ("text", "question", "article") and isinstance(item, str):
                texts.add(item)
            if key in ("id", "source_id", "group_id") and isinstance(item, str):
                ids.add(item)
            if key == "group_ids" and isinstance(item, list):
                ids.update(item)
            if isinstance(item, (dict, list)):
                extract_public(item, texts, ids)
    elif isinstance(value, list):
        for item in value:
            extract_public(item, texts, ids)


def exclusions():
    normalized, receipt = old.exclusion_inventory()
    ids = receipt.pop("root_ids")
    # Read only frozen input inventories, never result/trace/model-output files.
    listed = subprocess.run(
        ["rg", "--files", str(SIDE)], check=True, capture_output=True, text=True
    ).stdout.splitlines()
    paths = {
        Path(path)
        for path in listed
        if Path(path).name
        in (
            "PUBLIC.json",
            "GROUPS.json",
            "TRAIN_PUBLIC.json",
            "HELDOUT_PUBLIC.json",
            "EVAL_PUBLIC.json",
        )
        and "/outputs/" not in path
        and not path.startswith(str(ROOT) + "/")
    }
    paths.update(
        (
            old.OLD_PANEL,
            old.FRESH_PANEL,
            old.CURRENT32,
            old.ROOT320,
            FROZEN / "TRAIN_PUBLIC.json",
            FROZEN / "HELDOUT_PUBLIC.json",
        )
    )
    inventory = []
    for path in sorted(paths):
        texts, source_ids = set(), set()
        extract_public(old.read(path), texts, source_ids)
        normalized.update(old.whitespace_norm(text) for text in texts)
        normalized.update(old.word_norm(text) for text in texts)
        ids.update(source_ids)
        inventory.append(
            {
                "path": str(path),
                "sha256": old.sha(path),
                "text_count": len(texts),
                "id_count": len(source_ids),
            }
        )
    receipt.update(
        broader_inventory=inventory,
        normalized_union_count=len(normalized),
        excluded_id_count=len(ids),
        excluded_id_sha256=old.digest(sorted(ids)),
        normalized_union_sha256=old.digest(sorted(normalized)),
        id_rule="conservative union of IDs across available datasets; no local exposure inferred from a collision",
        scan_rule="all frozen sidecar public/GROUPS input JSON, excluding outputs and this new sidecar",
        extraction_fields=[
            "text",
            "question",
            "article",
            "id",
            "source_id",
            "group_id",
            "group_ids",
        ],
        base_pretraining_excluded=False,
    )
    return normalized, ids, receipt, paths


def requests_for(records, role, step, tokenizer, builder, historical, prefix, suffix):
    groups = []
    for index in range(0, len(records), 4):
        members = records[index : index + 4]
        ids = [row["id"] for row in members]
        text, labels = builder.prompt("ag_news", members)
        schema = {
            "type": "object",
            "properties": {key: {"type": "string", "enum": labels} for key in ids},
            "required": ids,
            "additionalProperties": False,
        }
        schema_text = json.dumps(schema, separators=(",", ":"), ensure_ascii=False)
        params = {
            **historical["body"]["sampling_params"],
            "temperature": 0.5 if role == "training" else 0.0,
            "top_p": 1.0,
            "top_k": -1,
            "min_p": 0.0,
            "presence_penalty": 0.0,
            "frequency_penalty": 0.0,
            "repetition_penalty": 1.0,
            "logprobs": 1,
            "max_tokens": 1024,
            "stop_token_ids": [151645, 151643],
            "structured_outputs": {"json": schema},
        }
        groups.append(
            {
                "context_id": f"agbroader-{role}-{step:03d}-{index // 4:03d}",
                "requested_ids": ids,
                "request_text": text,
                "schema_ordered_json": schema_text,
                "schema_ordered_sha256": old.text_sha(schema_text),
                "body": {
                    "model": prompt_source.CHILD_ALIAS,
                    "token_ids": prefix + tokenizer.encode(text, add_special_tokens=False) + suffix,
                    "sampling_params": params,
                    "cache_salt": "0",
                },
            }
        )
    bounds = context_bound([len(row["body"]["token_ids"]) for row in groups])
    requests = []
    for repeat in range(4 if role == "training" else 1):
        for index, group in enumerate(groups):
            row = copy.deepcopy(group)
            seed = (
                202609123000 + 128 * (step - 1) + 4 * index + repeat
                if role == "training"
                else 202609126000 + index
            )
            row.update(
                repeat=repeat,
                seed=seed,
                step=step,
                coordinate_id=old.digest(
                    {
                        "namespace": NAMESPACE,
                        "role": role,
                        "step": step,
                        "group": index,
                        "repeat": repeat,
                    }
                ),
            )
            row["body"]["sampling_params"]["seed"] = seed
            requests.append(row)
    return requests, {
        **bounds,
        "groups": len(groups),
        "requests": len(requests),
        "record_count": len(records),
        "gold_prompted": False,
    }


def main():
    from transformers import AutoTokenizer

    if os.environ.get("CUDA_VISIBLE_DEVICES") != "" or (ROOT / "inputs").exists():
        raise ValueError("CUDA must be hidden and new immutable inputs absent")
    started = datetime.now(timezone.utc).isoformat()
    excluded, ids, exposure, exclusion_paths = exclusions()
    steps, heldout, inventory = freeze_selection(old.source_rows(), excluded, ids)
    if any(
        len(step) != 128
        or Counter(row["label_id"] for row in step) != Counter({0: 32, 1: 32, 2: 32, 3: 32})
        for step in steps
    ):
        raise ValueError("step counts/balance differ")
    if len(heldout) != 512 or Counter(row["label_id"] for row in heldout) != Counter(
        {0: 128, 1: 128, 2: 128, 3: 128}
    ):
        raise ValueError("heldout counts/balance differ")
    builder = prompt_source.load_builder()
    actual, consumed = builder.actual_training()
    exposure["actual_c32_optimizer_exposure"] = {
        "unique_training_records": len(actual),
        "epochs_per_record": sorted(set(consumed.values())),
        "prepared_train_key": "train",
        "state_step_metrics_consumption_verified": True,
        "prepared_file": str(old.C32_TRAIN),
        "prepared_sha256": old.sha(old.C32_TRAIN),
        "training_state": str(builder.C32_STATE),
        "training_state_sha256": old.sha(builder.C32_STATE),
    }
    tokenizer = AutoTokenizer.from_pretrained(prompt_source.MODEL, local_files_only=True)
    historical = old.read(prompt_source.BATCH_SOURCES)["contexts"][
        "question-sensitive-sft-train-05"
    ]["partitions"]["4"]["0"]
    old_ids = tokenizer.encode(historical["request_text"], add_special_tokens=False)
    tokens = historical["body"]["token_ids"]
    hits = [
        i for i in range(len(tokens) - len(old_ids) + 1) if tokens[i : i + len(old_ids)] == old_ids
    ]
    if len(hits) != 1:
        raise ValueError("exact original helper wrapper not unique")
    prefix, suffix = tokens[: hits[0]], tokens[hits[0] + len(old_ids) :]
    train = [row for step in steps for row in step]
    artifacts = {
        "TRAIN_PUBLIC.json": old.public_bundle(train, "training"),
        "TRAIN_GOLD.json": old.gold_bundle(train, "training"),
        "HELDOUT_PUBLIC.json": old.public_bundle(heldout, "heldout_evaluation"),
        "HELDOUT_GOLD.json": old.gold_bundle(heldout, "heldout_evaluation"),
        "SELECTED_PROVENANCE.json": {
            "namespace": NAMESPACE,
            "training_steps": steps,
            "heldout": heldout,
        },
        "EXCLUSIONS.json": exposure,
    }
    audits = {}
    for step, rows in enumerate(steps, 1):
        public = old.public_bundle(rows, "training")
        requests, audit = requests_for(
            public["records"], "training", step, tokenizer, builder, historical, prefix, suffix
        )
        artifacts[f"step-{step:03d}/PUBLIC.json"] = public
        artifacts[f"step-{step:03d}/HOST_GOLD.json"] = old.gold_bundle(rows, "training")
        artifacts[f"step-{step:03d}/REQUESTS.json"] = requests
        audits[f"step-{step:03d}"] = audit
    requests, audit = requests_for(
        artifacts["HELDOUT_PUBLIC.json"]["records"],
        "heldout",
        0,
        tokenizer,
        builder,
        historical,
        prefix,
        suffix,
    )
    artifacts["HELDOUT_REQUESTS.json"] = requests
    audits["heldout"] = audit
    artifacts["TOKEN_BOUNDS.json"] = audits
    for name, value in artifacts.items():
        old.write_x(ROOT / "inputs" / name, value)
    sources = exclusion_paths | {
        OLD_PREPARE,
        EVAL_PREPARE,
        prompt_source.BUILDER,
        prompt_source.BATCH_SOURCES,
        old.PARQUET,
        old.C32_TRAIN,
        builder.C32_STATE,
        builder.EXPOSURE,
        Path(__file__),
        ROOT / "test_freeze.py",
        ROOT / "DESIGN.md",
        FROZEN / "MANIFEST.json",
        old.CACHE / "README.md",
        old.CACHE / "ACQUISITION.json",
        old.CACHE / "ACQUISITION_TRAIN_2026-09-12.json",
    }
    sources.update(
        prompt_source.MODEL / name
        for name in ("tokenizer.json", "tokenizer_config.json", "config.json")
    )
    manifest = {
        "schema": "helper-agnews-broader-data-manifest-v1",
        "status": "FROZEN_DATA_ONLY_NO_TRAINER_OR_GPU_ADMISSION",
        "created_utc": started,
        "namespace": NAMESPACE,
        "selection_before_model_scoring": True,
        "model_inference_calls": 0,
        "heldout_model_access": "prohibited until predeclared final endpoint",
        "counts": {
            "training": 1024,
            "training_steps": 8,
            "training_per_step": 128,
            "training_per_class": 256,
            "heldout": 512,
            "heldout_per_class": 128,
            "training_native_coordinates": 1024,
            "heldout_native_coordinates": 128,
        },
        "seeds": {
            "native_first": 202609123000,
            "native_last": 202609124023,
            "initial_training_rng": 202609125000,
            "numpy_legacy": 202609125000 % (2**32),
            "heldout_first": 202609126000,
            "heldout_last": 202609126127,
        },
        "selection_and_grouping": old.sha(ROOT / "DESIGN.md"),
        "inventory": inventory,
        "exclusion_artifact": "EXCLUSIONS.json",
        "base_pretraining_excluded": False,
        "dataset": {
            "name": "fancyzhx/ag_news",
            "revision": old.REVISION,
            "split": "train",
            "source_path": str(old.PARQUET),
            "source_sha256": old.SOURCE_SHA256,
            "source_row_index": "zero-based parquet row; source_id train:index",
            "license": "unknown/unspecified in pinned dataset card",
            "license_caution": "Local research only; no redistribution grant inferred",
            "acquired_new_data": False,
        },
        "environment": {
            "python": sys.version,
            "executable": sys.executable,
            "cuda_visible_devices": os.environ["CUDA_VISIBLE_DEVICES"],
            "packages": {
                name: importlib.metadata.version(name)
                for name in ("transformers", "tokenizers", "pyarrow", "numpy")
            },
        },
        "token_bounds": audits,
        "artifacts_sha256": {
            str(ROOT / "inputs" / name): old.sha(ROOT / "inputs" / name) for name in artifacts
        },
        "source_closure_sha256": {str(path): old.sha(path) for path in sorted(sources)},
    }
    manifest["identity"] = old.digest(manifest)
    old.write_x(ROOT / "inputs/MANIFEST.json", manifest)
    print(
        json.dumps(
            {
                "identity": manifest["identity"],
                "counts": manifest["counts"],
                "inventory": inventory,
                "token_bounds": audits,
            },
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
