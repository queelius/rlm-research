"""Qualified native owner for the frozen 72-call three-view screen."""

import argparse
import json
import types

import collect
import metrics
import study


def implementation():
    with study.aliases({"runner_study": study.source}, study.SOURCE):
        v3 = study.load("b05_state_repr_owner_v3", study.SOURCE / "runner_owner_v3.py")
    _, text = v3.owner_sources()
    for field in ("planned_coordinates", "planned_physical_cap"):
        before = f'"{field}": 64'
        assert text.count(before) == 1
        text = text.replace(before, f'"{field}": 72')
    module = types.ModuleType("b05_state_repr_native_owner")
    module.__file__ = __file__
    module.lifecycle = v3.lifecycle_module()
    with study.aliases({"runner_study": study, "runner_collect": collect,
                        "runner_metrics": metrics}, study.ROOT):
        exec(compile(text, str(v3.SOURCE_PATH), "exec"), module.__dict__)
    assert module.study is study and module.collect is collect and module.metrics is metrics
    assert collect.inherited.study is study
    return module


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("command", choices=("verify", "run"))
    parser.add_argument("--outer-seconds", type=int, default=study.OWNER_SECONDS)
    args = parser.parse_args(); module = implementation()
    if args.command == "verify":
        print(study.verify()["identity"])
    else:
        result = module.execute(args.outer_seconds); print(json.dumps(result))
        raise SystemExit(0 if result["complete"] else 1)

