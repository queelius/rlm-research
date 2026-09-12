"""Condition-aware facade over the qualified QS6 terminal collector."""

import copy
from pathlib import Path

import study


terminal_study = study._terminal_study()
import terminal_collect as qualified  # noqa: E402


_mode = None
_native = qualified.native
_real_make_task = _native.make_task
_stack = _native.stack()
_real_environment = _stack.interface.e.environment_config


def phase(block_index, mode):
    return f"recursion-headroom-block-{block_index}-{mode}"


def mode_from_phase(value):
    for block_index, mode in enumerate(study.BLOCK_MODES):
        if value == phase(block_index, mode):
            return mode, block_index
    raise ValueError("phase is outside frozen recursion-headroom blocks")


def _activate(mode):
    global _mode
    if mode not in study.MODES:
        raise ValueError("unknown recursion mode")
    _mode = mode


def planned(value):
    mode, block_index = mode_from_phase(value)
    block = study.make_blocks()[block_index]
    if {row["mode"] for row in block} != {mode}:
        raise ValueError("phase/plan mode mismatch")
    return block


def environment_config():
    if _mode is None:
        raise RuntimeError("recursion mode must be activated before environment construction")
    value = copy.deepcopy(_real_environment())
    value["agent"]["harness"]["max_depth"] = 0 if _mode == "no_child" else 1
    return value


def make_task(context, query, gold, name):
    if _mode is None:
        raise RuntimeError("recursion mode must be activated before task construction")
    task = _real_make_task(context, query, gold, name)
    prompt = study.common_prompt(context, query)
    task.data = task.data.model_copy(update={"prompt": prompt,
        "source_split": "protected-research-exposed-recursion-headroom-" + _mode})
    task.plain_query = query
    task.recursion_mode = _mode
    return task


def first_prefix(task):
    mode = getattr(task, "recursion_mode", _mode)
    if mode is None:
        raise RuntimeError("recursion mode unavailable for prefix authentication")
    rows = study.build_prefix_manifest()["coordinates"]
    matches = [row for row in rows if row["mode"] == mode and row["task_name"] == task.data.name]
    if len(matches) != 2:
        raise ValueError("frozen task/mode prefix inventory changed")
    if matches[0]["token_ids"] != matches[1]["token_ids"]:
        raise ValueError("repeat unexpectedly changes first prefix")
    return matches[0]["token_ids"]


for module in (_native, qualified.qualified.n, qualified.qualified.impl.n):
    module.make_task = make_task
    module.first_prefix = first_prefix
_stack.interface.e.environment_config = environment_config
qualified.planned = planned
qualified.qualified.planned = planned
qualified.qualified.impl.planned = planned

_base_prepare = qualified.prepare_spec
_base_verify = qualified.verify_spec


def prepare_spec(value, binding_path, endpoint_path, destination, cap, generation=None):
    mode, _ = mode_from_phase(value)
    _activate(mode)
    return _base_prepare(value, binding_path, endpoint_path, destination, cap, generation)


def verify_spec(path):
    value = study.read(path)
    mode, _ = mode_from_phase(value["phase"])
    _activate(mode)
    return _base_verify(Path(path))


qualified.verify_spec = verify_spec
qualified.qualified.verify_spec = verify_spec
qualified.qualified.impl.verify_spec = verify_spec
collect = qualified.collect
binding_for = qualified.binding_for


def binding():
    return binding_for(terminal_study.fixed_start())


def export_attempt(attempt, output):
    import terminal_export
    return terminal_export.export_attempt(attempt, output)


if __name__ == "__main__":
    import asyncio
    args = qualified.parse_args()
    raise SystemExit(asyncio.run(collect(args.spec, args.output, args.deadline)))
