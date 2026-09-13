"""Freeze a public, outcome-blind bijection over every local training-stage ID."""

import hashlib
import importlib.util
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parent
SOURCE = ROOT.parent / "b05-flat-selection-rl-v1"
spec = importlib.util.spec_from_file_location("b05_id_rename_source", SOURCE / "study.py")
source = importlib.util.module_from_spec(spec)
spec.loader.exec_module(source)
NAMESPACE = "b05-selection-id-renaming-20260913-v1"


def renamed(old):
    return "impl_" + hashlib.sha256(f"{NAMESPACE}\0{old}".encode()).hexdigest()[:12]


def main():
    source_tasks = [row for row in source.read(SOURCE / "EVAL_TASKS.json")["tasks"]
                    if row["split"] == "train"]
    old_ids = sorted({item for row in source_tasks for item in row["known_ids"]})
    mapping = {old: renamed(old) for old in old_ids}
    assert len(mapping) == len(set(mapping.values())) and not (set(mapping) & set(mapping.values()))
    tasks, occurrence_ledger = [], []
    for row in source_tasks:
        prompt = row["prompt"]
        counts = {old: prompt.count(old) for old in row["known_ids"]}
        assert all(count > 0 for count in counts.values())
        for old in sorted(row["known_ids"], key=len, reverse=True):
            prompt = prompt.replace(old, mapping[old])
        assert not any(old in prompt for old in old_ids)
        known = [mapping[old] for old in row["known_ids"]]
        request = source.width.request_body(prompt, row["seed"], 384)
        tasks.append({**row, "prompt": prompt, "known_ids": known, "request": request,
            "source_prompt_sha256": source.digest(row["prompt"]),
            "renamed_prompt_sha256": source.digest(prompt)})
        occurrence_ledger.append({"root_id": row["root_id"], "repeat": row["repeat"],
                                  "source_occurrences": counts})
    gold_rows = []
    for row in source.read(SOURCE / "HOST_GOLD.json")["rows"]:
        if row["split"] == "train":
            gold_rows.append({**row, "gold_ids": [mapping[item] for item in row["gold_ids"]]})
    assert len(tasks) == 18 and len(gold_rows) == 9
    source.write_x(ROOT / "ID_MAPPING_PUBLIC.json", {"schema": "b05-public-id-bijection-v1",
        "namespace": NAMESPACE, "forward": mapping,
        "reverse": {value: key for key, value in mapping.items()},
        "selection_used_model_outcomes_or_gold": False, "occurrence_ledger": occurrence_ledger})
    source.write_x(ROOT / "RENAMED_TASKS.json", {"schema": "b05-renamed-selection-tasks-v1",
        "tasks": tasks, "planned_per_model": 18, "total36": 36})
    source.write_x(ROOT / "HOST_GOLD.json", {"schema": "b05-renamed-selection-host-gold-v1",
        "rows": gold_rows, "mapping_applied_after_public_mapping_freeze": True})
    source.write_x(ROOT / "DATA_READY.json", {"schema": "b05-id-renaming-data-ready-v1",
        "source_eval_tasks_sha256": source.sha(SOURCE / "EVAL_TASKS.json"),
        "source_host_gold_sha256": source.sha(SOURCE / "HOST_GOLD.json"),
        "mapping_sha256": source.sha(ROOT / "ID_MAPPING_PUBLIC.json"),
        "tasks_sha256": source.sha(ROOT / "RENAMED_TASKS.json"),
        "host_gold_sha256": source.sha(ROOT / "HOST_GOLD.json"),
        "tasks": 18, "stage_contexts": 9, "models": 2, "planned_calls": 36,
        "all_numeric_policy_history_and_check_facts_unchanged": True,
        "only_implementation_id_strings_changed": True, "GPU_calls": 0, "model_calls": 0})
    print(json.dumps(source.read(ROOT / "DATA_READY.json"), sort_keys=True))


if __name__ == "__main__":
    main()
