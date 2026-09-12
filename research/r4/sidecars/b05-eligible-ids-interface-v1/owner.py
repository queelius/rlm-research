"""Reuses V3's actual registry/lifecycle owner, without the full-report contract hook."""
import argparse
import json
import types
import collect
import metrics
import study


def implementation():
    with study.aliases({"runner_study": study.source}, study.SOURCE):
        v3 = study.load("ids_only_source_owner_v3", study.SOURCE / "runner_owner_v3.py")
    _original, repaired = v3.owner_sources()
    assert repaired.count('"planned_coordinates": 64') == 1
    assert repaired.count('"planned_physical_cap": 64') == 1
    repaired = repaired.replace('"planned_coordinates": 64', '"planned_coordinates": 24')
    repaired = repaired.replace('"planned_physical_cap": 64', '"planned_physical_cap": 24')
    module = types.ModuleType("ids_only_v3_native_owner")
    module.__file__ = __file__
    module.lifecycle = v3.lifecycle_module()
    with study.aliases({"runner_study": study, "runner_collect": collect, "runner_metrics": metrics}, study.ROOT):
        exec(compile(repaired, str(v3.SOURCE_PATH), "exec"), module.__dict__)
    assert module.study is study and module.collect is collect and module.metrics is metrics
    assert not getattr(collect.Collector, "b05_contract_clarification_v3", False)
    return module


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("command", choices=("verify", "run"))
    parser.add_argument("--outer-seconds", type=int, default=study.OWNER_SECONDS)
    args = parser.parse_args()
    module = implementation()
    if args.command == "verify":
        print(study.verify()["identity"])
    else:
        terminal = module.execute(args.outer_seconds)
        print(json.dumps(terminal))
        raise SystemExit(0 if terminal["complete"] else 1)
