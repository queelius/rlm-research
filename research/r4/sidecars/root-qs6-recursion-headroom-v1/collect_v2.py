"""Additive mode-specific TASKS seam for collector and terminal exporter."""

import functools
from pathlib import Path

import collect as v1
import study


qualified = v1.qualified
terminal_study = v1.terminal_study
_source_tasks_path = study.SOURCE_INPUTS / "TASKS.json"
_real_terminal_read = terminal_study.read
make_task = v1.make_task


def activate(block_index, mode):
    expected_mode, expected_block = v1.mode_from_phase(v1.phase(block_index, mode))
    if expected_mode != mode or expected_block != block_index:
        raise ValueError("mode/block mismatch")
    v1._activate(mode)


@functools.lru_cache(maxsize=1)
def task_tables():
    frozen = study.ROOT / "TASKS_V2.json"
    if frozen.exists():
        value = study.read(frozen)
    else:
        public = {row["id"]: row for row in study.read(study.SOURCE_INPUTS / "PUBLIC.json")}
        gold = study.read(study.SOURCE_INPUTS / "HOST_GOLD.json")
        prefixes = {(row["mode"], row["task_name"]): row["token_ids"]
                    for row in study.build_prefix_manifest()["coordinates"]}
        value = {"schema": "root-qs6-recursion-headroom-tasks-v2", "modes": {}}
        for mode, block_index in (("no_child", 0), ("enabled", 1)):
            activate(block_index, mode)
            entries = {}
            for row in study.make_blocks()[block_index]:
                task = make_task(public[row["context_id"]], row["question"],
                                 gold[row["context_id"]]["answers"][row["family"]],
                                 row["task_name"])
                entries[row["task_name"]] = {
                    "question": row["question"], "prompt": task.data.prompt,
                    "task_hash": task.hash,
                    "first_prompt_token_ids": prefixes[(mode, row["task_name"])],
                    "mode": mode, "source_tasks_v2_path": str(frozen),
                }
            value["modes"][mode] = entries
    if set(value["modes"]) != set(study.MODES):
        raise ValueError("frozen mode-specific TASKS inventory differs")
    if any(len(value["modes"][mode]) != 24 for mode in study.MODES):
        raise ValueError("frozen mode-specific TASKS count differs")
    return value


def first_prefix(task):
    mode = getattr(task, "recursion_mode", v1._mode)
    if mode is None:
        raise RuntimeError("mode unavailable for V2 prefix lookup")
    return task_tables()["modes"][mode][task.data.name]["first_prompt_token_ids"]


def _read(path):
    if Path(path).resolve() == _source_tasks_path.resolve():
        if v1._mode is None:
            raise RuntimeError("mode not activated before TASKS lookup")
        mode = v1._mode
        tables = task_tables()
        v1._activate(mode)
        return tables["modes"][mode]
    return _real_terminal_read(path)


terminal_study.read = _read


def planned(value):
    mode, block_index = v1.mode_from_phase(value)
    activate(block_index, mode)
    return study.make_blocks()[block_index]


def prepare_spec(value, binding_path, endpoint_path, destination, cap, generation=None):
    mode, block_index = v1.mode_from_phase(value)
    activate(block_index, mode)
    return v1.prepare_spec(value, binding_path, endpoint_path, destination, cap, generation)


def verify_spec(path):
    spec = study.read(path)
    mode, block_index = v1.mode_from_phase(spec["phase"])
    activate(block_index, mode)
    return v1.verify_spec(path)


qualified.verify_spec = verify_spec
qualified.qualified.verify_spec = verify_spec
qualified.qualified.impl.verify_spec = verify_spec
collect = qualified.collect
binding = v1.binding
binding_for = v1.binding_for
phase = v1.phase


def export_attempt(attempt, output):
    # terminal_export and its dynamically compiled qsr exporter both receive terminal_study;
    # the read seam therefore authenticates the same mode-specific task hash/prefix table.
    import terminal_export
    return terminal_export.export_attempt(attempt, output)


if __name__ == "__main__":
    import asyncio
    args = qualified.parse_args()
    raise SystemExit(asyncio.run(collect(args.spec, args.output, args.deadline)))
