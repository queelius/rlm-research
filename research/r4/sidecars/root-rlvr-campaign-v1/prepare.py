"""Freeze all campaign coordinates and source-train-supported transfer documents."""

import argparse
import hashlib

import campaign_common as c


def coordinates(tasks, phase, repeats, split, *, seed_phase=None):
    rows = []
    for task in tasks:
        for repeat in range(repeats):
            row = {"study": c.ROOT.name, "task_name": task["name"],
                   "source_id": task["source_id"], "context_window_id": task["context_window_id"],
                   "context_sha256": task["context_sha256"], "split": split,
                   "analysis_split": "root_transfer_leaf_train_supported" if split == "transfer" else "repeated_root_contexts_leaf_train_supported",
                   "repeat": repeat, "seed": c.sample_seed(phase if seed_phase is None else seed_phase, task["name"], repeat),
                   "temperature": 0.5, "client_path": "train", "arm": "sft_child",
                   "campaign_phase": phase, "group_id": c.digest([c.ROOT.name, phase, task["name"], 0.5])}
            rows.append({**row, "id": c.digest(row), "pair_id": c.digest([row, "unpaired"]), "pair_order": 0})
    rows.sort(key=lambda r: c.digest([c.SEED, "dispatch", r["id"]]))
    return [{**row, "dispatch_order": i} for i, row in enumerate(rows)]


def build_inputs():
    c.pilot_recipe()
    spec = c.read(c.PILOT / "SPEC.json")
    c.authenticate(spec["source_file_sha256"])
    data = c.load("campaign_frozen_pilot_data", c.PILOT / "credit_data.py")
    source = c.load("campaign_trec_source", data.SOURCE)
    partitions = source.load_partitions()
    pilot = c.read(c.PILOT / "inputs/PUBLIC.json")
    pilot_groups = {g for context in pilot["contexts"] for g in context["group_ids"]}
    composition_groups = {g for context in c.read(data.COMPOSITION)["contexts"] for g in context["group_ids"]}
    forbidden = pilot_groups | composition_groups
    eligible = [r for r in partitions["train"] if r["group_id"] not in forbidden]
    eligible.sort(key=lambda r: c.digest([c.ROOT.name, c.SEED, "transfer", r["group_id"]]))
    selected = eligible[:384]
    if len(selected) != 384 or len({r["group_id"] for r in selected}) != 384:
        raise ValueError("insufficient distinct unused source-training groups")
    public, gold = {"contexts": [], "tasks": []}, {}
    for index in range(6):
        records = selected[index * 64:(index + 1) * 64]
        if any("\n" in r["question"] or "\r" in r["question"] for r in records):
            raise ValueError("multiline question would alter record boundaries")
        text = "\n".join(f"Date: 2000-01-{i % 28 + 1:02d} || User: {i % 8} || Instance: {r['question']}" for i, r in enumerate(records)) + "\n"
        sha = hashlib.sha256(text.encode()).hexdigest()
        context_id = f"root-campaign-transfer-{index:02d}"
        public["contexts"].append({"id": context_id, "text": text, "sha256": sha,
                                   "split": "transfer", "group_ids": [r["group_id"] for r in records]})
        for query, label in enumerate(("human being", "numeric value")):
            template = next(t for t in pilot["tasks"] if t["label"] == label)
            task = {**template, "name": f"root-campaign-transfer:{index:02d}:{query}",
                    "context_id": context_id, "context_sha256": sha, "context_window_id": 1200 + index,
                    "source_id": 14200000 + index * 2 + query, "split": "transfer"}
            public["tasks"].append(task)
            gold[task["name"]] = {"answer": repr([sum(r["gold"] == label for r in records)]), "records": records}
    training = [t for t in pilot["tasks"] if t["split"] == "training"]
    validation = [t for t in pilot["tasks"] if t["split"] == "validation"]
    plans = {"training": {str(r): coordinates(training, r, 4, "training") for r in range(1, 9)},
             "validation": coordinates(validation, "validation", 2, "validation"),
             "transfer_original": coordinates(public["tasks"], "transfer-original", 2, "transfer", seed_phase="transfer"),
             "transfer_selected": coordinates(public["tasks"], "transfer-selected", 2, "transfer", seed_phase="transfer")}
    seeds = [r["seed"] for rows in plans["training"].values() for r in rows]
    seeds += [r["seed"] for r in plans["validation"] + plans["transfer_original"]]
    earlier = {r["seed"] for r in c.read(c.PILOT / "inputs/PLAN.json")}
    earlier.update(r["seed"] for r in c.read(c.ROOT.parent / "root-credit-validation-replay-v1/SPEC_ORIGINAL.json")["plan"])
    if len(set(seeds)) != len(seeds) or set(seeds) & earlier:
        raise ValueError("campaign seed collision with another coordinate or pilot")
    selected_groups = {r["group_id"] for r in selected}
    validation_groups = {r["group_id"] for r in partitions["validation"]}
    test_groups = {r["group_id"] for r in partitions["test"]}
    if selected_groups & (forbidden | validation_groups | test_groups):
        raise ValueError("transfer source grouping overlaps a forbidden partition")
    provenance = {"seed": c.SEED, "source_split_sha256": source.SPLIT_SHA,
        "source_train_question_groups": len(partitions["train"]), "pilot_groups_excluded": len(pilot_groups),
        "prior_composition_groups_excluded": len(composition_groups), "eligible_train_groups": len(eligible),
        "selected_transfer_groups": 384, "contexts": 6, "records_per_context": 64,
        "overlap_pilot_root_groups": 0, "overlap_prior_composition_groups": 0,
        "overlap_leaf_validation": 0, "overlap_leaf_test": 0,
        "training_trajectories": 256, "validation_unique_coordinates": 8,
        "validation_checkpoints": [0, 2, 4, 6, 8], "transfer_pairs": 24,
        "seed_collisions": 0, "transfer_same_seed_pairing_intentional": True,
        "child_training_supported": True, "base_pretraining_contamination_unknown": True,
        "gold_scope": "host-only task scoring; only context text/public question enter rootless runtime",
        "source_sha256": {**c.read(c.PILOT / "inputs/PROVENANCE.json")["source_sha256"],
                           str(c.PILOT / "inputs/PUBLIC.json"): c.file_hash(c.PILOT / "inputs/PUBLIC.json"),
                           str(c.PILOT / "inputs/HOST_GOLD.json"): c.file_hash(c.PILOT / "inputs/HOST_GOLD.json")}}
    for name, value in (("TRANSFER_PUBLIC.json", public), ("TRANSFER_HOST_GOLD.json", gold),
                        ("PLANS.json", plans), ("PROVENANCE.json", provenance)):
        c.write_once(c.ROOT / "inputs" / name, value)
    recipe = {**c.pilot_recipe(), "schema": "eight-generation-root-only-persistent-adam-v1",
        "training_seed": c.SEED, "optimizer_steps": 8, "max_concurrent_pairs": 8,
        "declared_at_utc": "2026-09-08T22:56:00Z",
        "concurrency_amendment": "Parent approved8 workers before READY after pilot runtime/long-tail evidence; vLLM max_num_seqs16 unchanged; no reward/termination change",
        "optimizer_state": "persistent AdamW moments; exactly one full-batch increment per fresh generation",
        "checkpoint_policy": "atomic checkpoint state is commit; recover saved generation without applying it twice",
        "limitations": "conditional capped token correction is not exact trajectory correction; eight repeated development coordinates, four training contexts; transfer is child-SFT-supported",
        "caps": {"global": 14400, "collection": 1800, "training": 600, "service_ready": 180,
                 "validation": 600, "transfer": 1800, "minimum_new_round_remaining": 900}}
    c.write_once(c.ROOT / "RECIPE.json", recipe)
    return provenance


def seal():
    external = dict(c.read(c.PILOT / "SPEC.json")["source_file_sha256"])
    external.update(c.pilot_recipe()["authenticated_dependencies"])
    extra = [c.PILOT / "SPEC.json", c.PILOT / "source/train_root.py", c.PILOT / "TRAINING_RECIPE.json",
             c.ROLE / "source/serve.py", c.ROLE / "source/routing.py", c.ROLE / "BOUND_WEIGHTS.json",
             c.ROOT.parent / "strict-rlm-temperature-adherence-v1/scripts/launch.py",
             c.ROOT.parent / "strict-rlm-temperature-adherence-v1/configs/inference-replica0.json",
             c.ROOT.parent.parent / "ROOT_CAMPAIGN_DRAFT.md"]
    external.update({str(p): c.file_hash(p) for p in extra})
    own = [p for p in c.ROOT.iterdir() if p.suffix in (".py", ".md")]
    external.update({str(p): c.file_hash(p) for p in own})
    inputs = [*sorted((c.ROOT / "inputs").glob("*.json")), c.ROOT / "RECIPE.json"]
    value = {"schema": c.ROOT.name, "namespace": c.ROOT.name, "seed": c.SEED,
             "source_sha256": external, "input_sha256": {str(p): c.file_hash(p) for p in inputs},
             "initial_policy": c.original_policy(), "fixed_child_sha256": c.CHILD_SHA,
             "validation_selection": "greatest strict successes among fixed8; earliest checkpoint tie; null infrastructure reported separately",
             "metadata_questions": [], "estimated_gpu_hours": [2, 4], "gpu_calls_during_preparation": 0}
    value["campaign_id"] = c.digest(value)
    c.write_once(c.ROOT / "CAMPAIGN.json", value)
    return {"campaign_id": value["campaign_id"], "campaign_sha256": c.file_hash(c.ROOT / "CAMPAIGN.json")}


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("command", choices=("inputs", "seal"))
    args = parser.parse_args()
    print(build_inputs() if args.command == "inputs" else seal())
