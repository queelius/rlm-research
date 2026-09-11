"""Create only the additive source/task provenance receipt; scientific inputs already frozen."""
import terminal_study as study


def build():
    source_inputs = study.SOURCE / "inputs"
    names = ("PLANS.json", "GROUPS.json", "PUBLIC.json", "HOST_GOLD.json",
             "NATIVE_TEMPLATE.json", "PROMPTS_ACCURATE.json", "PROVENANCE.json")
    byte_equal = all(study.sha(study.ROOT / "inputs" / name) == study.sha(source_inputs / name)
                     for name in names)
    tasks = study.read(study.ROOT / "inputs/TASKS.json")
    source_tasks = study.read(source_inputs / "TASKS.json")
    for name in tasks:
        if {key: value for key, value in tasks[name].items() if key != "task_hash"} != {
                key: value for key, value in source_tasks[name].items() if key != "task_hash"}:
            raise ValueError("native task scientific fields differ from parent")
    mapping = {name: {"source": row["task_hash"], "lr1e5": tasks[name]["task_hash"]}
               for name, row in source_tasks.items()}
    plans = study.read(study.ROOT / "inputs/PLANS.json")
    return {
        "schema": "lr1e5-source-map-v1",
        "parent_campaign_id": study.read(study.SOURCE / "CAMPAIGN.json")["campaign_id"],
        "new_campaign_id": study.CAMPAIGN_ID,
        "scientific_inputs_byte_equal": byte_equal,
        "task_hashes_preserved": False,
        "namespace_only_task_hash_changes": True,
        "namespace_only_generation_changes": True,
        "training_rows": sum(len(rows) for rows in plans["training"].values()),
        "readout_rows": len(plans["readout"]),
        "task_hash_map": mapping,
        "parent_input_sha256": {name: study.sha(source_inputs / name)
                                for name in (*names, "TASKS.json")},
    }


if __name__ == "__main__":
    path = study.ROOT / "inputs/SOURCE_MAP.json"
    if path.exists():
        if study.read(path) != build():
            raise ValueError("existing source map differs")
    else:
        study.write(path, build())
    print(study.sha(path))
