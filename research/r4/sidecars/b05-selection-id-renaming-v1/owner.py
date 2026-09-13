"""Thin owner reuse with the frozen 36-call inventory."""

import argparse
import json
import types

import collect
import metrics
import study


SOURCE = study.SOURCE_EVAL / "owner.py"
SOURCE_SHA256 = "ec41e47abb3b0c97c2bc6813293dd5f715db7a18cf2038db9c644b494e5a309c"


def implementation():
    if study.sha(SOURCE) != SOURCE_SHA256:
        raise ValueError("accepted evaluator owner changed")
    text = SOURCE.read_text()
    if text.count("planned_calls=72") != 1:
        raise ValueError("owner planned-call seam changed")
    text = text.replace("planned_calls=72", "planned_calls=36")
    module = types.ModuleType("b05_id_rename_owner_reuse")
    module.__file__ = str(SOURCE) + ":renamed36"
    exec(compile(text, module.__file__, "exec"), module.__dict__)
    module.s, module.collect, module.metrics = study, collect, metrics
    return module


source = implementation()


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("command", choices=("verify", "run"))
    parser.add_argument("--outer-seconds", type=int, default=study.OWNER_SECONDS)
    args = parser.parse_args()
    if args.command == "verify":
        print(study.verify()["identity"])
    else:
        terminal = source.execute(args.outer_seconds)
        print(json.dumps(terminal))
        raise SystemExit(0 if terminal["complete"] else 1)

