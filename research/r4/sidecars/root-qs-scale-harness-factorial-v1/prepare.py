"""Freeze the approved root-policy x scale x harness diagnostic; CPU only."""

from __future__ import annotations

import hashlib
import importlib.util
import json
import os
import re
import unicodedata
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path(__file__).resolve().parent
SIDE = ROOT.parent
NAMESPACE = "root-qs-scale-harness-factorial-20260910-v1"
SIZES = (16, 64, 128, 256)
POLICIES = ("unchanged", "sft6")
HARNESSES = {
    "raw_batch_20000b": ("B", 20000),
    "cumulative_4096b": ("C", 4096),
}
LABELS = [
    "abbreviation",
    "description and abstract concept",
    "entity",
    "human being",
    "location",
    "numeric value",
]
SOURCE = SIDE / "trec-leaf-sft-v1/source/data.py"
QS = SIDE / "root-question-sensitive-sft-v1"


def digest(value):
    return hashlib.sha256(
        json.dumps(value, sort_keys=True, separators=(",", ":")).encode()
    ).hexdigest()


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def read(path):
    return json.loads(Path(path).read_text())


def write_once(path, value):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(path.name + ".pending-" + os.urandom(8).hex())
    try:
        with temporary.open("x") as stream:
            json.dump(value, stream, indent=2, sort_keys=True, allow_nan=False)
            stream.write("\n")
            stream.flush()
            os.fsync(stream.fileno())
        os.link(temporary, path)
    finally:
        temporary.unlink(missing_ok=True)


def normalize(text):
    return " ".join(re.findall(r"\w+", unicodedata.normalize("NFKC", text).casefold()))


def load_module(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def select_clusters(rows, excluded):
    if len(rows) != len({row["group_id"] for row in rows}):
        raise ValueError("source pool group IDs must be unique")
    eligible = [row for row in rows if row["group_id"] not in excluded]
    proof = {
        "base_pool": len(rows),
        "excluded": len(set(excluded) & {row["group_id"] for row in rows}),
        "eligible": len(eligible),
        "required": 1024,
        "selection_namespace": NAMESPACE,
        "selection_rule": "first 1024 by sha256([namespace,'select',group_id]), group_id tie-break",
        "selection_uses_gold_or_length": False,
        "no_replacement_or_reranking": True,
    }
    if len(eligible) < 1024:
        raise ValueError("fewer than 1024 eligible groups; exclusion may not be weakened")
    ordered = sorted(
        eligible,
        key=lambda row: (digest([NAMESPACE, "select", row["group_id"]]), row["group_id"]),
    )[:1024]
    return [ordered[i * 256 : (i + 1) * 256] for i in range(4)], proof


def seed_for(cluster, size):
    # Fresh fixed seeds, shared by the four policy/harness cells at a coordinate.
    return 990412001 + cluster * len(SIZES) + SIZES.index(size)


def j1_spec(cluster):
    # Exact protected J1 family from qs_problem.specs('protected', cluster).
    r = cluster % 6
    return {
        "slot": "J1",
        "family": "J1",
        "operator": "conditional_weight",
        "target": LABELS[(r + 3) % 6],
        "target_b": LABELS[(r + 2) % 6],
        "scope": "ALL",
        "users": ["u0", "u1", "u2", "u3"],
        "threshold": None,
    }


def question(spec):
    return (
        "Across all records, regardless of which of u0, u1, u2, or u3 owns the record. "
        f"What is the total weight of category {spec['target_b']!r} records owned by scoped "
        f"users who also have at least one category {spec['target']!r} record? Count each "
        f"category {spec['target_b']!r} record once. Return only Answer: N, replacing N with "
        "the exact nonnegative integer."
    )


def answer(records, labels, spec):
    owners = {
        row["user"]
        for row in records
        if row["user"] in spec["users"] and labels[row["id"]] == spec["target"]
    }
    return sum(
        row["weight"]
        for row in records
        if row["user"] in owners and labels[row["id"]] == spec["target_b"]
    )


def build_factorial(clusters, used_seeds):
    if len(clusters) != 4 or any(len(cluster) != 256 for cluster in clusters):
        raise ValueError("exact four by 256 cluster allocation required")
    proposed = {seed_for(cluster, size) for cluster in range(4) for size in SIZES}
    if proposed & set(used_seeds):
        raise ValueError("seed collision; no reroll")
    contexts = []
    groups = []
    host = {}
    rows = []
    for cluster, members in enumerate(clusters):
        spec = j1_spec(cluster)
        query = question(spec)
        full_records = []
        full_labels = {}
        for index, source in enumerate(members):
            identifier = "r" + digest([NAMESPACE, "record", source["group_id"]])[:15]
            record = {
                "id": identifier,
                "user": f"u{index % 4}",
                "text": source["question"],
                "weight": 1 + int(digest([NAMESPACE, "weight", source["group_id"]])[:8], 16) % 7,
                "source_group_id": source["group_id"],
            }
            full_records.append(record)
            full_labels[identifier] = source["gold"]
        for size in SIZES:
            context_id = f"qs-scale-harness-c{cluster}-n{size}"
            records = full_records[:size]
            labels = {row["id"]: full_labels[row["id"]] for row in records}
            context = {
                "id": context_id,
                "cluster": cluster,
                "size": size,
                "split": "protected",
                "stratum": "root-training-manifest-new_child-training-exposed",
                "native_context_id": 991412000 + cluster * 1000 + size,
                "records": records,
                "text": "".join(json.dumps(row, sort_keys=True) + "\n" for row in records),
            }
            contexts.append(context)
            groups.append(
                {
                    "id": context_id,
                    "cluster": cluster,
                    "size": size,
                    "group_ids": [row["source_group_id"] for row in records],
                    "source_partition": "train",
                    "child_c32_optimizer_exposed": True,
                    "root_training_manifest_new": True,
                    "prior_research_exposure_not_excluded": True,
                }
            )
            truth = answer(records, labels, spec)
            host[context_id] = {"labels": labels, "answers": {"J1": truth}}
            coordinate = {"cluster": cluster, "size": size}
            cells = [(policy, harness) for policy in POLICIES for harness in HARNESSES]
            cells.sort(key=lambda cell: digest([NAMESPACE, "cell-order", cluster, size, *cell]))
            for order, (policy, harness) in enumerate(cells):
                return_arm, view_bytes = HARNESSES[harness]
                row = {
                    **coordinate,
                    **spec,
                    "context_id": context_id,
                    "parent_id": f"qs-scale-harness-c{cluster}",
                    "context_window_id": context["native_context_id"],
                    "task_name": f"{context_id}:J1:{policy}:{harness}",
                    "namespace": NAMESPACE,
                    "seed": seed_for(cluster, size),
                    "policy": policy,
                    "harness_arm": harness,
                    "return_arm": return_arm,
                    "view_bytes": view_bytes,
                    "dispatch_order_within_coordinate": order,
                    "question": query,
                    "role": "native",
                    "evidence": "raw",
                    "repeat": 0,
                    "arm": "typed",
                    "temperature": 0.5,
                    "client_path": "free",
                    "width": size,
                    "metadata_error": False,
                }
                row["id"] = digest(row)
                rows.append(row)
    rows.sort(key=lambda row: digest([NAMESPACE, "dispatch", row["cluster"], row["size"], row["dispatch_order_within_coordinate"]]))
    return {
        "PUBLIC.json": contexts,
        "GROUPS.json": groups,
        "HOST_GOLD.json": host,
        "FREE_PLAN.json": rows,
        "FREE_PLAN_UNCHANGED.json": [row for row in rows if row["policy"] == "unchanged"],
        "FREE_PLAN_SFT6.json": [row for row in rows if row["policy"] == "sft6"],
    }


def collect_named_exclusions(pool):
    pool_ids = {row["group_id"] for row in pool}
    normalized = {normalize(row["question"]): row["group_id"] for row in pool}
    excluded = set()
    manifest_rows = []
    paths = set(SIDE.glob("root-*/inputs/GROUPS.json"))
    paths.update(SIDE.glob("root-*/inputs/PUBLIC.json"))
    for path in sorted(paths):
        if path.is_relative_to(ROOT):
            continue
        value = read(path)
        found = set()

        def walk(node):
            if isinstance(node, dict):
                for key, item in node.items():
                    if key in {"group_id", "source_group_id"} and isinstance(item, str):
                        if item in pool_ids:
                            found.add(item)
                    elif key == "group_ids" and isinstance(item, list):
                        found.update(x for x in item if isinstance(x, str) and x in pool_ids)
                    elif key in {"text", "question"} and isinstance(item, str):
                        group_id = normalized.get(normalize(item))
                        if group_id:
                            found.add(group_id)
                    walk(item)
            elif isinstance(node, list):
                for item in node:
                    walk(item)

        walk(value)
        if found:
            excluded.update(found)
            manifest_rows.append({"path": str(path), "sha256": sha(path), "group_count": len(found)})
    return excluded, manifest_rows


def collect_used_seeds():
    seeds = set()
    rows = []
    for path in sorted(SIDE.glob("root-*/inputs/*PLAN*.json")):
        if path.is_relative_to(ROOT):
            continue
        value = read(path)

        def walk(node):
            if isinstance(node, dict):
                if isinstance(node.get("seed"), int):
                    seeds.add(node["seed"])
                for item in node.values():
                    walk(item)
            elif isinstance(node, list):
                for item in node:
                    walk(item)

        before = len(seeds)
        walk(value)
        if len(seeds) > before:
            rows.append({"path": str(path), "sha256": sha(path)})
    return seeds, rows


def main():
    if (ROOT / "inputs").exists():
        raise FileExistsError("immutable one-time allocation; no reroll")
    source = load_module("qs_scale_actual_trec_source", SOURCE)
    pool = source.load_partitions()["train"]
    if len(pool) != 5065:
        raise ValueError("exact pinned c32 optimizer source pool required")
    excluded, exclusion_rows = collect_named_exclusions(pool)
    used_seeds, seed_rows = collect_used_seeds()
    clusters, selection = select_clusters(pool, excluded)
    values = build_factorial(clusters, used_seeds)
    selected = [row["group_id"] for cluster in clusters for row in cluster]
    selection.update(
        {
            "created_utc": datetime.now(timezone.utc).isoformat(),
            "selected_group_ids": selected,
            "excluded_group_ids": sorted(excluded),
            "named_manifest_rows": exclusion_rows,
            "seed_inventory_rows": seed_rows,
            "source_path": str(SOURCE),
            "source_sha256": sha(SOURCE),
            "source_partition": "train",
            "dataset_revision": read(SIDE / "trec-leaf-split-provenance-v1/PROPOSED_SPLIT.json"),
            "source_exposure": (
                "All selected records are from the actual c32 optimizer source pool and are child-"
                "training exposed; prior research exposure is possible. They are disjoint from named "
                "root-training/QS train+dev+protected manifests under the frozen inventory only."
            ),
        }
    )
    values["PROVENANCE.json"] = selection
    values["EVALUATION_PLAN.json"] = {
        "schema": "root-qs-scale-harness-factorial-evaluation-v1",
        "planned": 64,
        "context_clusters": 4,
        "nested_sizes": list(SIZES),
        "policies": list(POLICIES),
        "harnesses": {
            name: {"return_arm": arm, "visible_view_max_bytes": view}
            for name, (arm, view) in HARNESSES.items()
        },
        "primary_outcome": "faithful_and_strict",
        "secondary_outcomes": [
            "strict",
            "availability",
            "acquisition",
            "retention",
            "full_aggregation",
            "child_label_diagnostic",
            "prompt_tokens",
            "completion_tokens",
            "elapsed_seconds",
            "tool_calls",
        ],
        "estimands": [
            "paired sft6-minus-unchanged by size and harness",
            "root-effect survival DID: size256 minus size16, separately by harness",
            "cumulative_4096b-minus-raw_batch_20000b for sft6, focus sizes128/256",
            "exploratory scale-by-root-by-harness contrast",
        ],
        "unit": "four preselected context clusters; n=4 exploratory, no inferential claim",
        "availability_rule": "authenticated observed empty final is observed incorrect; NULL only when native result is unavailable or unauthenticated",
        "zero_gold_retained": True,
        "no_retry": True,
        "no_reroll": True,
        "outer_seconds": 3600,
        "owned_seconds": 3570,
        "work_seconds": 3420,
        "release_seconds": 120,
        "harvest_seconds": 30,
        "episode_seconds": 180,
        "workers": 4,
        "service_schedule": "serial root services; harness cells interleaved within each policy plan",
    }
    values["NATIVE_TEMPLATE.json"] = read(QS / "inputs/NATIVE_TEMPLATE.json")
    for name, value in values.items():
        write_once(ROOT / "inputs" / name, value)
    print(json.dumps({"eligible": selection["eligible"], "excluded": selection["excluded"], "selected": 1024, "contexts": 16, "planned": 64}, sort_keys=True))


if __name__ == "__main__":
    main()
