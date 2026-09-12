"""Mode-specific facade over the qualified QS6 terminal collector."""

import copy
import functools
from pathlib import Path

import study


terminal_study = study._terminal_study()
import terminal_collect as qualified  # noqa: E402


_mode = None
_native = qualified.native
_real_make_task = _native.make_task
_stack = _native.stack()
_real_environment = _stack.interface.e.environment_config
_source_tasks_path = study.SOURCE_INPUTS / "TASKS.json"
_real_terminal_read = terminal_study.read


def phase(block_index, mode):
    return f"recursion-interface-qualifier-block-{block_index}-{mode}"


def mode_from_phase(value):
    for block_index, mode in enumerate(study.BLOCK_MODES):
        if value == phase(block_index, mode):
            return mode, block_index
    raise ValueError("phase outside frozen interface qualifier")


def activate(mode):
    global _mode
    if mode not in study.MODES:
        raise ValueError("unknown recursion mode")
    _mode = mode


def planned(value):
    mode, block_index = mode_from_phase(value)
    activate(mode)
    return study.make_blocks()[block_index]


def environment_config():
    if _mode is None:
        raise RuntimeError("recursion mode must be activated")
    value = copy.deepcopy(_real_environment())
    value["agent"]["harness"]["max_depth"] = 0 if _mode == "no_child" else 1
    return value


def make_task(context, query, gold, name):
    if _mode is None:
        raise RuntimeError("recursion mode must be activated before task construction")
    task = _real_make_task(context, query, gold, name)
    task.data = task.data.model_copy(
        update={
            "prompt": study.common_prompt(context, query),
            "source_split": "protected-research-exposed-recursion-interface-" + _mode,
        }
    )
    task.plain_query = query
    task.recursion_mode = _mode
    return task


@functools.lru_cache(maxsize=1)
def task_tables():
    path = study.ROOT / "TASKS.json"
    if not path.exists():
        raise FileNotFoundError("frozen TASKS.json is required; inputs are never reconstructed")
    value = study.read(path)
    if set(value.get("modes", {})) != set(study.MODES):
        raise ValueError("frozen mode inventory differs")
    if any(len(value["modes"][mode]) != 6 for mode in study.MODES):
        raise ValueError("frozen task count differs")
    return value


def first_prefix(task):
    mode = getattr(task, "recursion_mode", _mode)
    if mode is None:
        raise RuntimeError("mode unavailable for prefix lookup")
    return task_tables()["modes"][mode][task.data.name]["first_prompt_token_ids"]


def _read(path):
    if Path(path).resolve() == _source_tasks_path.resolve():
        if _mode is None:
            raise RuntimeError("mode not activated before TASKS lookup")
        return task_tables()["modes"][_mode]
    return _real_terminal_read(path)


terminal_study.read = _read
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
    activate(mode)
    return _base_prepare(value, binding_path, endpoint_path, destination, cap, generation)


def verify_spec(path):
    value = study.read(path)
    mode, _ = mode_from_phase(value["phase"])
    activate(mode)
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
