"""Freeze inventory-new TREC groups before gold, then exact changed-metadata tasks."""
import asyncio
from collections import Counter
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path

import study as s


def inventory():
    proof = s.read(s.base.ss.ROOT / "inputs/PROVENANCE.json")
    base_ids = set(proof["pool_ids"])
    allocator = s.load("fresh_qualified_group_inventory", s.base.CT / "prepare.py",
                       s.base.ss.ct_ready["source_sha256"][str(s.base.CT / "prepare.py")],
                       {"ct_study": s.base.ss.ct, "ct_protocol": s.base.ss.protocol()})
    qualifier = s.load("fresh_qualified_collision_inventory", s.base.CT / "qualify_inventory.py",
                       s.base.ss.ct_ready["source_sha256"][str(s.base.CT / "qualify_inventory.py")],
                       {"ct_study": s.base.ss.ct})
    paths = set()
    for pattern in ("root-*/inputs/PUBLIC.json", "root-*/inputs/GROUPS.json",
                    "root-*/inputs/TASKS.json", "*/inputs/*PLAN*.json"):
        paths.update(s.SIDE.glob(pattern))
    excluded, seeds, public_ids, native_ids, rows, pins = set(), set(), set(), set(), [], {}
    for path in sorted(paths):
        if path.parent.parent == s.ROOT or path.parent.parent.name == "root-broad-curriculum-v1":
            continue
        value = s.read(path); pin = s.sha(path); pins[str(path)] = pin
        groups = allocator.positive_groups(value)
        excluded.update(groups)
        rows.append({"path": str(path), "sha256": pin, "positive_group_count": len(groups)})
        seeds.update(allocator.seeds(value))
        public_ids.update(qualifier.collect(value, "id"))
        native_ids.update(qualifier.collect(value, "native_context_id"))
        native_ids.update(qualifier.collect(value, "context_window_id"))
    eligible_ids = base_ids - excluded
    if len(base_ids) != 2000 or len(base_ids & excluded) != 1819 or len(eligible_ids) != 181:
        raise ValueError("inventory changed before immutable freeze")
    source_path = s.SIDE / "trec-leaf-sft-v1/source/data.py"
    pin = s.base.cf_ready["source_sha256"].get(str(source_path)) or s.base.cf_ready["input_sha256"][str(source_path)]
    source = s.load("fresh_actual_trec_source", source_path, pin); pins[str(source_path)] = pin
    pool = [row for row in source.load_partitions()["train"] if row["group_id"] in eligible_ids]
    if len(pool) != 181 or len({row["group_id"] for row in pool}) != 181:
        raise ValueError("eligible source mapping")
    snapshot = {
        "created_utc": datetime.now(timezone.utc).isoformat(), "base_pool": 2000,
        "excluded": 1819, "eligible": 181, "eligible_group_ids": sorted(eligible_ids),
        "manifest_rows": rows, "source_sha256": pins,
        "broad_catalog_not_execution": True,
        "newness": "new to recorded root evaluation/training inventory, not globally unseen",
        "child_source_exposure": "TREC-train source/catalog and likely examples exposed to fixed c32 child training",
        "selection_before_gold": True,
    }
    return pool, snapshot, seeds, public_ids, native_ids


def transformed_specs(index):
    result = []
    for old in s.base.problem.specs("protected", index):
        row = dict(old)
        row["users"] = ["u" + str(int(user[1:]) + 4) for user in row["users"]]
        if row["threshold"] is not None:
            row["threshold"] = {4: 13, 8: 25}[row["threshold"]]
        row["question"] = s.base.problem.question(row).replace(
            "u0, u1, u2, or u3", "u4, u5, u6, or u7")
        result.append(row)
    return result


def build(pool, snapshot):
    ordered = sorted(pool, key=lambda row: (s.digest([s.NAMESPACE, "source", row["group_id"]]),
                                            row["group_id"]))[:128]
    snapshot["selected_group_sequence"] = [row["group_id"] for row in ordered]
    contexts, groups, host, plan = [], [], {}, []
    layouts = s.load("fresh_qualified_layouts", s.base.OLD / "od_protocol.py",
                     s.base.cf_ready["source_sha256"][str(s.base.OLD / "od_protocol.py")],
                     {"od_study": s}).LAYOUTS
    for index in range(8):
        context_id = f"question-sensitive-fresh-input-{index:02d}"
        members = sorted(ordered[index * 16:index * 16 + 16],
                         key=lambda row: (s.digest([s.NAMESPACE, "order", index, row["group_id"]]),
                                          row["group_id"]))
        records, labels = [], {}
        for position, source in enumerate(members):
            gid = source["group_id"]
            record_id = "q" + s.digest([s.NAMESPACE, "record", gid])[:12]
            records.append({"id": record_id, "user": f"u{4 + position % 4}",
                            "text": source["question"],
                            "weight": 8 + int(s.digest([s.NAMESPACE, "weight", record_id])[:16], 16) % 8})
            labels[record_id] = source["gold"]
        context = {"id": context_id, "index": index, "split": "protected",
                   "stratum": "inventory_new_changed_metadata", "size": 16, "records": records,
                   "text": "".join(json.dumps(row, sort_keys=True) + "\n" for row in records),
                   "native_context_id": 991731000 + index}
        contexts.append(context)
        groups.append({"id": context_id, "split": "protected",
                       "group_ids": [row["group_id"] for row in members],
                       "source_partition": "train", "child_training_exposed": True,
                       "root_recorded_inventory_new": True,
                       "source_rows": [{key: row[key] for key in ("group_id", "source_path", "source_line_1based")}
                                       for row in members]})
        host[context_id] = {"labels": labels, "answers": {}}
        for spec in transformed_specs(index):
            layout = int(s.digest([s.NAMESPACE, "style", context_id, spec["slot"]])[:8], 16) % 4
            seed = int(s.digest([s.NAMESPACE, "readout", context_id, spec["slot"]])[:8], 16) % (2**31)
            row = {"context_id": context_id, "parent_id": context_id,
                   "context_window_id": context["native_context_id"],
                   "task_name": context_id + ":" + spec["slot"], "family": spec["slot"],
                   "split": "protected", "namespace": s.NAMESPACE, "seed": seed, "width": 16,
                   "metadata_error": False, "names": layouts[layout], "layout": layout,
                   "template": 0, "role": "native", "evidence": "raw", "repeat": 0,
                   "arm": "typed", "temperature": 0.5, "client_path": "train", **spec}
            row["id"] = s.digest(row); plan.append(row)
            first = s.base.answer(records, labels, row)
            second = s.base.problem.enumerated_answer(records, labels, row)
            if first != second:
                raise ValueError("independent gold disagreement")
            host[context_id]["answers"][row["family"]] = first
    plan.sort(key=lambda row: s.digest([s.NAMESPACE, "dispatch", row["context_id"], row["family"]]))
    histogram = Counter(host[row["context_id"]]["answers"][row["family"]] for row in plan)
    snapshot["gold_computed_after_selection"] = True
    snapshot["gold_histogram"] = {str(key): value for key, value in sorted(histogram.items())}
    snapshot["zero"] = histogram[0]
    return contexts, groups, host, plan


def main():
    if (s.ROOT / "inputs").exists():
        raise FileExistsError("immutable inventory/selection already frozen")
    pool, snapshot, used_seeds, used_ids, used_native = inventory()
    contexts, groups, host, plan = build(pool, snapshot)
    proposed_seeds = {row["seed"] for row in plan}
    record_ids = {record["id"] for context in contexts for record in context["records"]}
    native_ids = {context["native_context_id"] for context in contexts}
    if proposed_seeds & used_seeds or record_ids & used_ids or native_ids & used_native:
        raise ValueError("fresh public/native identity collision; no replacement")
    class Memory:
        def __init__(self): self.files = {}
        async def write(self, name, data): self.files[name] = data
    async def files(task):
        memory = Memory(); await task.setup(None, memory); return memory.files
    prompts, checks = {}, []
    by_context = {context["id"]: context for context in contexts}
    for row in plan:
        task = s.make_task(by_context[row["context_id"]], row, 0)
        other = s.make_task(by_context[row["context_id"]], row, 999999)
        prefix = s.base.qnative().first_prefix(task)
        public_files, other_files = asyncio.run(files(task)), asyncio.run(files(other))
        if public_files != other_files or prefix != s.base.qnative().first_prefix(other) or len(prefix) + 2048 > 8192:
            raise ValueError("gold-independent native admission; no rerank")
        if set(public_files) != {"records.json", "context.txt", "query.txt", "batch_contract.py"}:
            raise ValueError("exact four-file interface")
        prompts[row["id"]] = {"prompt": task.data.prompt, "plain_query": row["question"],
                              "token_ids": prefix}
        checks.append({"id": row["id"], "prefix_tokens": len(prefix), "gold_independent": True,
                       "files_sha256": {name: hashlib.sha256(value).hexdigest()
                                        for name, value in public_files.items()}})
    snapshot.update({"unique_public_ids": len(record_ids), "unique_native_ids": len(native_ids),
                     "unique_seeds": len(proposed_seeds), "seed_collisions": [],
                     "public_id_collisions": [], "native_id_collisions": []})
    values = {"PUBLIC.json": contexts, "GROUPS.json": groups, "HOST_GOLD.json": host,
              "FREE_PLAN.json": plan, "PROMPTS_ACCURATE.json": prompts,
              "PROVENANCE.json": snapshot,
              "NATIVE_TEMPLATE.json": s.read(s.ORIGINAL / "inputs/NATIVE_TEMPLATE.json"),
              "EVALUATION_PLAN.json": {"planned": 216,
                  "policy_order": ["new_corpus_sft6", "original_sft6", "fixed24"],
                  "episodes_per_policy": 72, "contexts": 8, "tasks_per_context": 9,
                  "outer_seconds": 5400, "owned_seconds": 5370, "no_retry": True}}
    for name, value in values.items():
        s.write(s.ROOT / "inputs" / name, value)
    s.write(s.ROOT / "CPU_NATIVE.json", {"rows": checks, "contexts": 8, "tasks": 72,
            "max_prefix": max(row["prefix_tokens"] for row in checks), "scientific_calls": 0})
    print(json.dumps({"eligible": 181, "selected": 128, "tasks": 72,
                      "zero": snapshot["zero"], "max_prefix": max(row["prefix_tokens"] for row in checks)}))


if __name__ == "__main__":
    main()
