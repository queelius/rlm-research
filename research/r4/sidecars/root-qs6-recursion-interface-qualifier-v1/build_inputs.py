"""One-time CPU construction of authenticated prompt and task tables."""

import json
import os

import collect
import study


def main():
    if os.environ.get("CUDA_VISIBLE_DEVICES") != "":
        raise ValueError("CPU-only input construction")
    prefixes = study.build_prefix_manifest()
    prefix_by_id = {row["id"]: row for row in prefixes["coordinates"]}
    modes = {}
    gold = study.read(study.SOURCE_INPUTS / "HOST_GOLD.json")
    for block_index, mode in enumerate(study.BLOCK_MODES):
        collect.activate(mode)
        entries = {}
        for row in study.make_blocks()[block_index]:
            task = collect.make_task(
                study.public()[row["context_id"]],
                row["question"],
                gold[row["context_id"]]["answers"][row["family"]],
                row["task_name"],
            )
            entries[row["task_name"]] = {
                "question": row["question"],
                "prompt": task.data.prompt,
                "task_hash": task.hash,
                "first_prompt_token_ids": prefix_by_id[row["id"]]["token_ids"],
                "mode": mode,
                "source_tasks_path": str(study.ROOT / "TASKS.json"),
            }
        modes[mode] = entries
    tasks = {
        "schema": "root-qs6-recursion-interface-qualifier-tasks-v1",
        "modes": modes,
    }
    study.write(study.ROOT / "PREFIXES.json", prefixes)
    study.write(study.ROOT / "TASKS.json", tasks)
    print(
        json.dumps(
            {
                "prefixes_sha256": study.sha(study.ROOT / "PREFIXES.json"),
                "tasks_sha256": study.sha(study.ROOT / "TASKS.json"),
                "coordinates": len(prefixes["coordinates"]),
                "max_prefix_tokens": max(row["token_count"] for row in prefixes["coordinates"]),
            },
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
