"""Freeze AG News train/held-out inventories without model calls or code execution."""

from __future__ import annotations

from collections import Counter, defaultdict
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import re
import unicodedata

import pyarrow.parquet as pq


ROOT = Path(__file__).resolve().parent
SIDE = ROOT.parent
CACHE = Path(
    "/project/alex_phd/research-cache/datasets/"
    "fancyzhx--ag_news--eb185aade064a813bc0b7f42de02595523103ca4"
)
PARQUET = CACHE / "train.parquet"
OLD_PANEL = SIDE / "helper-unseen-generalization-panel-v1/PUBLIC.json"
FRESH_PANEL = SIDE / "helper-adaptive-fresh-panel-v1/PUBLIC.json"
CURRENT32 = SIDE / "helper-hf-onpolicy-v1/inputs/GROUPS.json"
C32_TRAIN = SIDE / "trec-leaf-sft-v1/prepared-v1/data.json"
ROOT320 = SIDE / "root-question-sensitive-sft-v1/inputs/GROUPS.json"
NAMESPACE = "agnews-helper-data-vs-mechanics-v1|20260912"
REVISION = "eb185aade064a813bc0b7f42de02595523103ca4"
SOURCE_SHA256 = "fc508d6d9868594e3da960a8cfeb63ab5a4746598b93428c224397080c1f52ee"
AG_LABELS = {0: "World", 1: "Sports", 2: "Business", 3: "Sci/Tech"}


def read(path: Path):
    return json.loads(path.read_text())


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def digest(value) -> str:
    return hashlib.sha256(
        json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode()
    ).hexdigest()


def text_sha(text: str) -> str:
    return hashlib.sha256(text.encode()).hexdigest()


def whitespace_norm(text: str) -> str:
    return " ".join(unicodedata.normalize("NFKC", text).casefold().split())


def word_norm(text: str) -> str:
    return " ".join(re.findall(r"\w+", unicodedata.normalize("NFKC", text).casefold()))


def write_x(path: Path, value) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("x") as stream:
        stream.write(json.dumps(value, indent=2, sort_keys=True, ensure_ascii=False) + "\n")


def source_rows() -> list[dict]:
    if sha(PARQUET) != SOURCE_SHA256:
        raise ValueError("AG News train parquet changed")
    table = pq.read_table(PARQUET, columns=["text", "label"])
    if table.num_rows != 120_000:
        raise ValueError("AG News train row count changed")
    rows = []
    for index, raw in enumerate(table.to_pylist()):
        label_id = int(raw["label"])
        text = raw["text"]
        normalized = whitespace_norm(text)
        rows.append(
            {
                "source_id": f"train:{index}",
                "source_row_0based": index,
                "text": text,
                "label_id": label_id,
                "label": AG_LABELS[label_id],
                "normalized_text_sha256": text_sha(normalized),
                "word_normalized_sha256": text_sha(word_norm(text)),
            }
        )
    if Counter(row["label_id"] for row in rows) != Counter({0: 30000, 1: 30000, 2: 30000, 3: 30000}):
        raise ValueError("AG News train label inventory changed")
    return rows


def exclusion_inventory() -> tuple[set[str], dict]:
    old_records = read(OLD_PANEL)["records"]
    fresh_records = read(FRESH_PANEL)["records"]
    current = [row["public_record"] for row in read(CURRENT32)]
    c32_records = {}
    for epoch in read(C32_TRAIN)["train"]:
        for batch in epoch:
            for row in batch["records"]:
                c32_records[row["group_id"]] = row["question"]
    root_ids = {group_id for row in read(ROOT320) for group_id in row["group_ids"]}
    sources = {
        "existing256": [row["text"] for row in old_records],
        "freshadaptive128": [row["text"] for row in fresh_records],
        "current32": [row["text"] for row in current],
        "actual_c32_train": list(c32_records.values()),
    }
    union = {whitespace_norm(text) for texts in sources.values() for text in texts}
    union.update(word_norm(text) for texts in sources.values() for text in texts)
    return union, {
        "source_counts": {name: len(texts) for name, texts in sources.items()},
        "normalized_union_count": len(union),
        "known_root_catalog_ids": len(root_ids),
        "known_root_catalog_id_sha256": digest(sorted(root_ids)),
        "known_root_id_check": "candidate source_id and normalized-text SHA256 are rejected if in this set",
        "root_ids": root_ids,
    }


def select_rows(
    rows: list[dict],
    excluded_normalized: set[str],
    *,
    train_per_label: int = 32,
    heldout_per_label: int = 64,
    excluded_ids: set[str] | None = None,
) -> tuple[list[dict], list[dict], dict]:
    excluded_ids = excluded_ids or set()
    grouped = defaultdict(list)
    for row in rows:
        normalized = whitespace_norm(row["text"])
        grouped[normalized].append(row)
    duplicate_same = sum(
        len({row["label_id"] for row in group}) == 1
        for group in grouped.values()
        if len(group) > 1
    )
    duplicate_conflict = sum(
        len({row["label_id"] for row in group}) > 1
        for group in grouped.values()
        if len(group) > 1
    )
    eligible, excluded_rows = [], 0
    for normalized, group in grouped.items():
        if len(group) > 1:
            continue
        row = group[0]
        word = word_norm(row["text"])
        norm_sha = text_sha(normalized)
        if normalized in excluded_normalized or word in excluded_normalized:
            excluded_rows += 1
            continue
        if row["source_id"] in excluded_ids or norm_sha in excluded_ids or text_sha(word) in excluded_ids:
            excluded_rows += 1
            continue
        enriched = dict(row)
        enriched["normalized_text_sha256"] = norm_sha
        eligible.append(enriched)
    by_label = defaultdict(list)
    for row in eligible:
        by_label[row["label_id"]].append(row)
    train, heldout = [], []
    need = train_per_label + heldout_per_label
    for label_id in AG_LABELS:
        ordered = sorted(
            by_label[label_id],
            key=lambda row: text_sha(NAMESPACE + "|candidate|" + row["source_id"]),
        )
        if len(ordered) < need:
            raise ValueError("insufficient eligible AG News rows")
        train.extend(ordered[:train_per_label])
        heldout.extend(ordered[train_per_label:need])
    train.sort(key=lambda row: text_sha(NAMESPACE + "|train|" + row["source_id"]))
    heldout.sort(key=lambda row: text_sha(NAMESPACE + "|heldout|" + row["source_id"]))
    return train, heldout, {
        "source_rows": len(rows),
        "eligible_unique_normalized": len(eligible),
        "excluded_union": excluded_rows,
        "duplicate_same_label_groups": duplicate_same,
        "duplicate_conflicting_label_groups": duplicate_conflict,
        "duplicate_rows_rejected": sum(len(group) for group in grouped.values() if len(group) > 1),
        "eligible_by_label": dict(Counter(row["label"] for row in eligible)),
    }


def record_id(row: dict) -> str:
    return "agtr" + text_sha("ag_news|" + row["source_id"])[:16]


def public_bundle(rows: list[dict], role: str) -> dict:
    return {
        "schema": "helper-agnews-prospective-public-v1",
        "role": role,
        "contains_gold": False,
        "records": [
            {
                "id": record_id(row),
                "dataset": "ag_news",
                "source_id": row["source_id"],
                "text": row["text"],
            }
            for row in rows
        ],
    }


def gold_bundle(rows: list[dict], role: str) -> dict:
    return {
        "schema": "helper-agnews-prospective-host-gold-v1",
        "role": role,
        "never_include_in_model_prompt": True,
        "labels": {record_id(row): row["label"] for row in rows},
    }


def main() -> None:
    if (ROOT / "inputs").exists():
        raise ValueError("immutable inputs already exist")
    rows = source_rows()
    excluded, exclusion = exclusion_inventory()
    train, heldout, inventory = select_rows(
        rows,
        excluded,
        excluded_ids=exclusion.pop("root_ids"),
    )
    if len(train) != 128 or len(heldout) != 256:
        raise ValueError("prospective selection size differs")
    if Counter(row["label"] for row in train) != Counter({label: 32 for label in AG_LABELS.values()}):
        raise ValueError("training split not balanced")
    if Counter(row["label"] for row in heldout) != Counter({label: 64 for label in AG_LABELS.values()}):
        raise ValueError("heldout split not balanced")
    train_norm = {row["normalized_text_sha256"] for row in train}
    heldout_norm = {row["normalized_text_sha256"] for row in heldout}
    if len(train_norm) != 128 or len(heldout_norm) != 256 or train_norm & heldout_norm:
        raise ValueError("train/heldout normalized-text separation failed")
    artifacts = {
        "TRAIN_PUBLIC.json": public_bundle(train, "training"),
        "TRAIN_GOLD.json": gold_bundle(train, "training"),
        "HELDOUT_PUBLIC.json": public_bundle(heldout, "heldout_evaluation"),
        "HELDOUT_GOLD.json": gold_bundle(heldout, "heldout_evaluation"),
        "SELECTED_PROVENANCE.json": {
            "schema": "helper-agnews-prospective-selection-v1",
            "namespace": NAMESPACE,
            "training": train,
            "heldout": heldout,
        },
    }
    for name, value in artifacts.items():
        write_x(ROOT / "inputs" / name, value)
    paths = [ROOT / "inputs" / name for name in artifacts]
    manifest = {
        "schema": "helper-agnews-data-vs-mechanics-input-manifest-v1",
        "status": "CPU_SELECTED_NOT_RUNNABLE_NO_TRAINER",
        "created_utc": datetime.now(timezone.utc).isoformat(),
        "namespace": NAMESPACE,
        "selection_before_model_scoring": True,
        "selection_rule": (
            "Within each gold stratum, sort unique eligible rows by "
            "SHA256(namespace|candidate|source_id); take first 32 for training and next 64 "
            "for heldout, then apply role-specific label-blind presentation ordering."
        ),
        "counts": {"training": 128, "heldout": 256, "per_training_label": 32, "per_heldout_label": 64},
        "inventory": inventory,
        "exclusion_audit": exclusion,
        "selected_overlap_with_exclusion_union": 0,
        "train_heldout_normalized_overlap": 0,
        "dataset": {
            "name": "fancyzhx/ag_news",
            "revision": REVISION,
            "split": "train",
            "source_path": str(PARQUET),
            "source_sha256": SOURCE_SHA256,
            "source_rows": 120000,
            "source_labels": AG_LABELS,
            "license": "unknown/unspecified in the pinned dataset card",
            "license_caution": "Research-only local use; no redistribution grant inferred.",
            "downloaded_code_executed": False,
            "reader": "pyarrow.parquet columns text,label only",
        },
        "artifacts_sha256": {str(path): sha(path) for path in paths},
        "source_closure_sha256": {
            str(path): sha(path)
            for path in (PARQUET, OLD_PANEL, FRESH_PANEL, CURRENT32, C32_TRAIN, ROOT320, Path(__file__))
        },
    }
    manifest["identity"] = digest(manifest)
    write_x(ROOT / "inputs" / "MANIFEST.json", manifest)
    print(json.dumps({"identity": manifest["identity"], "counts": manifest["counts"], "inventory": inventory}, sort_keys=True))


if __name__ == "__main__":
    main()
