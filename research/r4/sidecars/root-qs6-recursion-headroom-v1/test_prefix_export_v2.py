from pathlib import Path


def test_collection_and_export_resolve_mode_specific_task_hash_and_prefix():
    import collect_v2
    import study

    source_path = study.SOURCE_INPUTS / "TASKS.json"
    public = {row["id"]: row for row in study.read(study.SOURCE_INPUTS / "PUBLIC.json")}
    gold = study.read(study.SOURCE_INPUTS / "HOST_GOLD.json")
    for block_index, mode in ((0, "no_child"), (1, "enabled")):
        collect_v2.activate(block_index, mode)
        tasks = collect_v2.terminal_study.read(source_path)
        row = study.make_blocks()[block_index][0]
        task = collect_v2.make_task(
            public[row["context_id"]], tasks[row["task_name"]]["question"],
            gold[row["context_id"]]["answers"][row["family"]], row["task_name"])
        expected = tasks[row["task_name"]]
        assert task.hash == expected["task_hash"]
        assert collect_v2.first_prefix(task) == expected["first_prompt_token_ids"]
        assert expected["mode"] == mode
        assert Path(expected["source_tasks_v2_path"]) == study.ROOT / "TASKS_V2.json"
