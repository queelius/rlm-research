"""Condition-aware collector with frozen modified task identities."""

import copy
import importlib.util
from pathlib import Path

import study


SOURCE = study.SOURCE / "collect.py"
SOURCE_SHA256 = "32943291fd51618f71cd86003d2732591c8b2b317e69a806e58ddfaa793089b5"
if study.sha(SOURCE) != SOURCE_SHA256:
    raise ValueError("source collector changed")
spec = importlib.util.spec_from_file_location("syntax_screen_source_collect", SOURCE)
base = importlib.util.module_from_spec(spec)
spec.loader.exec_module(base)


TASKS = study.TASK_INPUT
terminal_study = base.terminal_study
_source_tasks_path = terminal_study.ROOT / "inputs/TASKS.json"
_real_terminal_read = terminal_study.read


def task_tables():
    value = study.read(TASKS)
    if set(value) != set(study.ARMS):
        raise ValueError("syntax task-table arm inventory differs")
    expected = {row["task_name"] for row in study.make_plan(study.ARMS[0])}
    for condition in study.ARMS:
        if set(value[condition]) != expected:
            raise ValueError("syntax task-table task inventory differs")
    return value


def _read(path):
    if Path(path).resolve() == _source_tasks_path.resolve():
        if base._active_arm is None:
            raise RuntimeError("syntax condition not active before TASKS lookup")
        return task_tables()[base._active_arm]
    return _real_terminal_read(path)


terminal_study.read = _read
activate = base.activate
public = base.public
environment_config = base.environment_config
make_task_from_row = base.make_task_from_row
first_prefix = base.first_prefix
binding = base.binding
binding_for = base.binding_for
prepare_spec = base.prepare_spec
verify_spec = base.verify_spec
export_attempt = base.export_attempt
collect = base.collect
qualified = base.qualified
_native = base._native


def build_task_tables():
    original = _real_terminal_read(_source_tasks_path)
    result = {}
    for condition in study.ARMS:
        activate(condition)
        by_name = {}
        for row in study.make_plan(condition):
            task = make_task_from_row(row)
            prior = by_name.setdefault(row["task_name"], task.hash)
            if prior != task.hash:
                raise ValueError("helper repeat changed modified task identity")
        if not set(by_name).issubset(original):
            raise ValueError("modified/source task inventories differ")
        result[condition] = {}
        for name, task_hash in by_name.items():
            result[condition][name] = copy.deepcopy(original[name])
            result[condition][name]["task_hash"] = task_hash
    return result


if __name__ == "__main__":
    import asyncio

    args = qualified.parse_args()
    raise SystemExit(asyncio.run(collect(args.spec, args.output, args.deadline)))
