"""Thin native owner for the source-authenticated repaired paired branches."""

import argparse
import importlib.util
import json
import sys

import paired_eval_study as study

_spec = importlib.util.spec_from_file_location("paired_repair_eval_owner_v1", study.V1 / "owner.py")
_module = importlib.util.module_from_spec(_spec)
_previous = sys.modules.get("paired_eval_study")
sys.modules["paired_eval_study"] = study
try:
    _spec.loader.exec_module(_module)
finally:
    if _previous is None:
        sys.modules.pop("paired_eval_study", None)
    else:
        sys.modules["paired_eval_study"] = _previous
build = _module.build


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command", choices=("verify", "qualify", "run"))
    parser.add_argument("--branch", choices=tuple(study.ARMS), required=True)
    parser.add_argument("--outer-seconds", type=int, default=study.CAP)
    args = parser.parse_args()
    if args.command == "verify":
        print(study.verify(args.branch)["identity"])
    elif args.command == "qualify":
        print(json.dumps(study.qualify_pair(args.branch), sort_keys=True))
    else:
        if args.outer_seconds != study.CAP:
            raise ValueError("sealed owner cap differs")
        study.verify(args.branch)
        terminal = build(args.branch).execute(args.outer_seconds)
        print(json.dumps(terminal, sort_keys=True))
        raise SystemExit(0 if terminal["complete"] else 1)
