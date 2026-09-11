"""Freeze a named-inventory-new 128-group training corpus and metadata72 readout."""
import asyncio
from collections import Counter
from datetime import datetime, timezone
import hashlib
import json
import rep_study as s


def inventory():
    started = datetime.now(timezone.utc).isoformat()
    proof = s.read(s.base.ss.ROOT / "inputs/PROVENANCE.json")
    base_ids = set(proof["pool_ids"])
    allocator = s.load("rep_group_inventory", s.CT / "prepare.py",
                       s.base.ss.ct_ready["source_sha256"][str(s.CT / "prepare.py")],
                       {"ct_study": s.base.ss.ct, "ct_protocol": s.base.ss.protocol()})
    qualifier = s.load("rep_collision_inventory", s.CT / "qualify_inventory.py",
                       s.base.ss.ct_ready["source_sha256"][str(s.CT / "qualify_inventory.py")],
                       {"ct_study": s.base.ss.ct})
    current, used_seeds, public_ids, native_ids, rows = set(), set(), set(), set(), []
    paths = set()
    for pattern in ("root-*/inputs/PUBLIC.json", "root-*/inputs/GROUPS.json",
                    "root-*/inputs/TASKS.json", "*/inputs/*PLAN*.json"):
        paths.update(s.SIDE.glob(pattern))
    pins = {str(s.base.ss.ROOT / "inputs/PROVENANCE.json"): s.sha(s.base.ss.ROOT / "inputs/PROVENANCE.json")}
    for path in sorted(paths):
        if path.parent.parent == s.ROOT or path.parent.parent.name == "root-broad-curriculum-v1":
            continue
        value = s.read(path); pins[str(path)] = s.sha(path)
        if path.name in ("PUBLIC.json", "GROUPS.json", "TASKS.json"):
            groups = allocator.positive_groups(value); current.update(groups)
            rows.append({"path": str(path), "sha256": s.sha(path), "positive_group_count": len(groups)})
        used_seeds.update(allocator.seeds(value)); public_ids.update(qualifier.collect(value, "id"))
        native_ids.update(qualifier.collect(value, "native_context_id"))
        native_ids.update(qualifier.collect(value, "context_window_id"))
    eligible = base_ids - current
    source_path = s.SIDE / "trec-leaf-sft-v1/source/data.py"
    pin = s.base.cf_ready["source_sha256"].get(str(source_path)) or s.base.cf_ready["input_sha256"][str(source_path)]
    source = s.load("rep_actual_trec_source", source_path, pin)
    pool = [r for r in source.load_partitions()["train"] if r["group_id"] in eligible]
    if len(pool) != len(eligible) or len({r["group_id"] for r in pool}) != len(pool) or len(pool) < 128:
        raise ValueError("actual eligible train mapping")
    return pool, {
        "scan_started_utc": started, "scan_ended_utc": datetime.now(timezone.utc).isoformat(),
        "base_pool": len(base_ids), "eligible": len(pool), "named_manifest_count": len(rows),
        "current_excluded_group_ids": sorted(current), "eligible_group_ids": sorted(eligible),
        "named_manifest_rows": rows, "source_sha256": {**pins, str(source_path): pin},
        "selection_uses_gold_or_length": False,
        "source_exposure": "TREC train; c32 optimizer/catalog exposed; root-new only under this named scan cutoff",
        "not_pristine_or_globally_unseen": True,
    }, used_seeds, public_ids, native_ids


def build(pool):
    ordered = sorted(pool, key=lambda x: (s.digest([s.NAMESPACE, "source", x["group_id"]]), x["group_id"]))[:128]
    contexts, groups, host, train = [], [], {}, []
    layouts = s.load("rep_layouts", s.OLD / "od_protocol.py",
                     s.base.cf_ready["source_sha256"][str(s.OLD / "od_protocol.py")], {"od_study": s})
    for ci in range(8):
        cid = f"question-sensitive-new-corpus-train-{ci:02}"
        members = sorted(ordered[ci * 16:(ci + 1) * 16],
                         key=lambda x: (s.digest([s.NAMESPACE, "order", ci, x["group_id"]]), x["group_id"]))
        records, labels = [], {}
        for i, row in enumerate(members):
            rid = "n" + s.digest([s.NAMESPACE, "record", row["group_id"]])[:12]
            records.append({"id": rid, "user": f"u{i % 4}", "text": row["question"],
                            "weight": 1 + int(s.digest([s.NAMESPACE, "weight", row["group_id"]])[:8], 16) % 7})
            labels[rid] = row["gold"]
        native_id = 992173100 + ci
        context = {"id": cid, "index": ci, "split": "train", "stratum": "new_corpus_replication",
                   "size": 16, "records": records,
                   "text": "".join(json.dumps(r, sort_keys=True) + "\n" for r in records),
                   "native_context_id": native_id}
        contexts.append(context)
        groups.append({"id": cid, "split": "train", "group_ids": [r["group_id"] for r in members],
                       "source_partition": "train", "child_training_exposed": True,
                       "prepared_catalog_exposed": True,
                       "source_rows": [{k: r[k] for k in ("group_id", "source_path", "source_line_1based")} for r in members]})
        host[cid] = {"labels": labels, "answers": {}}
        for spec in s.problem.specs("train", ci):
            layout = int(s.digest([s.NAMESPACE, "style", ci, spec["slot"]])[:8], 16) % 4
            seed = int(s.digest([s.NAMESPACE, "capture", ci, spec["slot"]])[:8], 16) % (2**31)
            row = {"context_id": cid, "parent_id": cid, "context_window_id": native_id,
                   "task_name": cid + ":" + spec["slot"], "family": spec["slot"], "split": "train",
                   "namespace": s.NAMESPACE, "seed": seed, "width": 16, "metadata_error": False,
                   "names": layouts.LAYOUTS[layout], "layout": layout, "template": 0, "role": "native",
                   "evidence": "raw", "repeat": 0, "arm": "typed", "temperature": .5,
                   "client_path": "train", **spec}
            row["question"] = s.problem.question(row); row["id"] = s.digest(row)
            expected = s.answer(records, labels, row)
            if expected != s.problem.enumerated_answer(records, labels, row):
                raise ValueError("independent truth mismatch")
            host[cid]["answers"][row["family"]] = expected; train.append(row)
    train = sorted(train, key=lambda r: s.digest([s.NAMESPACE, "dispatch", r["context_id"], r["slot"]]))
    baseline = {}
    for panel in ("all", "primitive", "composition"):
        selected = [r for r in train if panel == "all" or r["slot"].startswith("P") == (panel == "primitive")]
        counts = Counter(host[r["context_id"]]["answers"][r["family"]] for r in selected)
        baseline["train:" + panel] = {"planned": len(selected), "histogram": {str(k): v for k, v in sorted(counts.items())},
                                      "zero": counts[0], "best_constant": max(counts.values())}
    return {"selected": [r["group_id"] for r in ordered], "values": {
        "PUBLIC.json": contexts, "GROUPS.json": groups, "HOST_GOLD.json": host,
        "TRAIN_PLAN.json": train, "BASELINES.json": baseline,
        "START_BINDING.json": {"decision": "APPROVED_FIXED24_START", "selected": s.starting_policy(),
                               "starting_policy_is_fixed24": True, "optimizer": "fresh Adam0"},
        "READOUT_REFERENCE.json": {"plan": str(s.METADATA / "inputs/FREE_PLAN.json"),
                                   "plan_sha256": s.sha(s.METADATA / "inputs/FREE_PLAN.json"),
                                   "planned": 72, "policy": "new_corpus_sft6",
                                   "comparators_reused_not_rerun": ["unchanged", "original_qs_sft6"]},
    }}


async def _files(task):
    class Memory:
        def __init__(self): self.files = {}
        async def write(self, name, data): self.files[name] = data
    memory = Memory(); await task.setup(None, memory); return memory.files


def main():
    if (s.ROOT / "inputs").exists():
        raise FileExistsError("immutable one-time allocation")
    pool, proof, used, existing_ids, existing_native = inventory(); built = build(pool)
    values = built["values"]; rows = values["TRAIN_PLAN.json"]
    proposed = {s.SEED, *[r["seed"] for r in rows]}
    ids = {r["id"] for c in values["PUBLIC.json"] for r in c["records"]}
    native = {c["native_context_id"] for c in values["PUBLIC.json"]}
    if proposed & used or ids & existing_ids or native & existing_native:
        raise ValueError("seed/public/native collision; no replacement")
    contexts = {c["id"]: c for c in values["PUBLIC.json"]}; prompts = {}; checks = []
    for row in rows:
        task = s.make_task(contexts[row["context_id"]], row, 0)
        other = s.make_task(contexts[row["context_id"]], row, 999999)
        prefix = s.qnative().first_prefix(task); files = asyncio.run(_files(task))
        if prefix != s.qnative().first_prefix(other) or len(prefix) + 2048 > 8192:
            raise ValueError("gold-independent native budget")
        prompts[row["id"]] = {"prompt": task.data.prompt, "plain_query": row["question"], "token_ids": prefix}
        checks.append({"id": row["id"], "prefix_tokens": len(prefix), "files_sha256": {k: hashlib.sha256(v).hexdigest() for k, v in files.items()}})
    proof.update({"selected_group_sequence": built["selected"], "selected_count": 128,
                  "proposed_seed_values": sorted(proposed), "seed_collisions": [],
                  "public_id_collisions": [], "native_id_collisions": []})
    values.update({"PROVENANCE.json": proof, "PROMPTS_ACCURATE.json": prompts,
                   "NATIVE_TEMPLATE.json": s.read(s.ORIGINAL / "inputs/NATIVE_TEMPLATE.json")})
    for name, value in values.items(): s.write(s.ROOT / "inputs" / name, value)
    s.write(s.ROOT / "CPU_INPUT_NATIVE.json", {"rows": checks, "contexts": 8, "groups": 128,
                                                "training": 72, "readout": 72,
                                                "max_prefix": max(r["prefix_tokens"] for r in checks),
                                                "scientific_calls": 0})


if __name__ == "__main__": main()
