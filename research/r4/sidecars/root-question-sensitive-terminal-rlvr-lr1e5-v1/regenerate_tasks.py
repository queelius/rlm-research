"""Regenerate only namespace-sensitive native task hashes; preserve scientific fields."""
import terminal_prepare
import terminal_study as study


def run():
    built = terminal_prepare.build_inputs()
    for name, value in built.items():
        if name == "TASKS.json":
            continue
        if study.read(study.ROOT / "inputs" / name) != value:
            raise ValueError("non-task scientific input would change: " + name)
    old_path = study.ROOT / "inputs/TASKS.json"
    old = study.read(old_path)
    new = built["TASKS.json"]
    for name in old:
        if {key: value for key, value in old[name].items() if key != "task_hash"} != {
                key: value for key, value in new[name].items() if key != "task_hash"}:
            raise ValueError("task scientific fields changed: " + name)
    study.write(study.ROOT / "inputs/TASKS_LR1E5.json", new)
    return old, new


if __name__ == "__main__":
    before, after = run()
    print({"tasks": len(after), "changed_hashes": sum(before[k]["task_hash"] != after[k]["task_hash"]
                                                       for k in before)})
