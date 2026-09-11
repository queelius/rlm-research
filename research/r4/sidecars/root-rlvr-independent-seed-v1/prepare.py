"""Freeze exact reused tasks and distinct seeds without reading evaluation outcomes."""
import copy
import json
import subprocess
import sys

import campaign_common as c


def make_plans(old):
    def convert(rows, phase, seed_phase):
        out = []
        for source in rows:
            row = {k: copy.deepcopy(v) for k, v in source.items() if k not in ["id", "pair_id", "dispatch_order"]}
            row.update(study=c.ROOT.name, campaign_phase=phase,
                seed=c.sample_seed(seed_phase, row["task_name"], row["repeat"]),
                group_id=c.digest([c.ROOT.name, phase, row["task_name"], .5]))
            row["id"] = c.digest(row)
            row["pair_id"] = c.digest([row, "unpaired"])
            out.append(row)
        out.sort(key=lambda r: c.digest([c.SEED, seed_phase, r["task_name"], r["repeat"], "dispatch"]))
        return [{**r, "dispatch_order": i} for i, r in enumerate(out)]
    return {"training": {k: convert(v, int(k), int(k)) for k, v in old["training"].items()},
        "validation": convert(old["validation"], "validation", "validation"),
        "transfer_original": convert(old["transfer_original"], "transfer-original", "transfer"),
        "transfer_selected": convert(old["transfer_selected"], "transfer-selected", "transfer")}


def make_recipe(old):
    recipe = copy.deepcopy(old)
    recipe.update(training_seed=c.SEED, declared_at_utc="2026-09-09T04:30:00Z",
        limitations=old["limitations"] + "; independent RNG/rollouts from original root, exposed developmental transfer, original-then-selected serial stages")
    recipe["caps"]["global"] = 5880
    return recipe


def main():
    if (c.ROOT / "CAMPAIGN.json").exists():
        raise ValueError("already frozen")
    c.authenticate(c.PINS)
    old = c.read(c.OLD / "CAMPAIGN.json")
    c.authenticate(old["source_sha256"])
    c.authenticate(old["input_sha256"])
    plans = make_plans(c.read(c.OLD / "inputs/PLANS.json"))
    recipe = make_recipe(c.read(c.OLD / "RECIPE.json"))
    for name in ["TRANSFER_PUBLIC.json", "TRANSFER_HOST_GOLD.json"]:
        c.write_once(c.ROOT / "inputs" / name, c.read(c.OLD / "inputs" / name))
    provenance = c.read(c.OLD / "inputs/PROVENANCE.json")
    provenance.update(seed=c.SEED, freshness="Original compositions reused verbatim; exposed developmental data",
        original_provenance_path=str(c.OLD / "inputs/PROVENANCE.json"), original_provenance_sha256=c.file_hash(c.OLD / "inputs/PROVENANCE.json"))
    c.write_once(c.ROOT / "inputs/PROVENANCE.json", provenance)
    c.write_once(c.ROOT / "inputs/PLANS.json", plans)
    c.write_once(c.ROOT / "RECIPE.json", recipe)
    import campaign_native as native
    identities = native.task_identity(native.make_tasks())
    prior_ids = c.read(c.OLD / "inputs/TASK_IDENTITIES.json")
    if identities.keys() != prior_ids.keys() or any(identities[k]["prompt_sha256"] != prior_ids[k]["prompt_sha256"] or identities[k]["context_sha256"] != prior_ids[k]["context_sha256"] for k in identities):
        raise ValueError("task context/prompt content changed")
    c.write_once(c.ROOT / "inputs/TASK_IDENTITIES.json", identities)
    c.write_once(c.ROOT / "INPUT_AUDIT.json", {"source_task_identities_sha256": c.file_hash(c.OLD / "inputs/TASK_IDENTITIES.json"),
        "same_prompt_context_content": True, "new_task_hash_note": "Namespace metadata can change task hashes; actual prompt/context content must agree",
        "training_episodes": 256, "validation_episodes": 40, "transfer_episodes": 48,
        "fresh_seed": c.SEED, "initial_policy": c.original_policy(), "inherited_updates": 0,
        "original_rollouts_reused": 0, "gpu_calls": 0})
    tests = subprocess.run([sys.executable, "-m", "pytest", "-q", "-p", "no:cacheprovider", str(c.ROOT / "test_replication.py")], capture_output=True, text=True, timeout=60)
    if tests.returncode:
        raise ValueError(tests.stdout)
    c.write_once(c.ROOT / "CPU_TESTS.json", {"returncode": tests.returncode, "stdout": tests.stdout, "stderr": tests.stderr,
        "test_first": "3 expected failures while preparation implementation absent", "gpu_calls": 0})
    sources = dict(old["source_sha256"])
    sources.update({str(p): sha for p, sha in c.PINS.items()})
    sources.update({str(p): c.file_hash(p) for p in c.ROOT.iterdir() if p.suffix in [".py", ".md"]})
    inputs = {str(p): c.file_hash(p) for p in [*sorted((c.ROOT / "inputs").glob("*.json")), c.ROOT / "RECIPE.json", c.ROOT / "INPUT_AUDIT.json", c.ROOT / "CPU_TESTS.json"]}
    manifest = {"schema": c.ROOT.name, "namespace": c.ROOT.name, "seed": c.SEED,
        "source_sha256": sources, "input_sha256": inputs, "initial_policy": c.original_policy(),
        "fixed_child_sha256": c.CHILD_SHA, "inherited_updates": 0,
        "validation_selection": old["validation_selection"], "gpu_calls_during_preparation": 0}
    manifest["campaign_id"] = c.digest(manifest)
    c.write_once(c.ROOT / "CAMPAIGN.json", manifest)
    amendment = {"schema": "independent-seed-original-start-exclusion-only-v1", "namespace": c.ROOT.name,
        "source_sha256": sources, "input_sha256": inputs, "inherited_optimizer_steps": 0,
        "new_global_cap_seconds": 6000, "admission_change": "none; same authenticated unsampled-child-overflow exclusion only"}
    amendment["amendment_id"] = c.digest(amendment)
    c.write_once(c.ROOT / "AMENDMENT.json", amendment)
    lifecycle = {"schema": "private-rebinding-unchanged-lifecycle-v2", "source_sha256": sources,
        "new_campaign_sha256": c.file_hash(c.ROOT / "CAMPAIGN.json")}
    lifecycle["amendment_id"] = c.digest(lifecycle)
    c.write_once(c.ROOT / "LIFECYCLE_V2.json", lifecycle)
    c.write_once(c.ROOT / "READY.json", {"status": "CPU_PREPARED_PENDING_ADAPTER_QUALIFICATION", "campaign_sha256": c.file_hash(c.ROOT / "CAMPAIGN.json"),
        "campaign_id": manifest["campaign_id"], "seed": c.SEED, "inherited_updates": 0,
        "gpu_calls": 0, "dynamic_dependency": "First real fresh generation supplies native action likelihood/masks; never fabricated"})
    print(json.dumps({"campaign_id": manifest["campaign_id"], "cpu_prepared": True, "gpu_calls": 0}))


if __name__ == "__main__":
    main()
