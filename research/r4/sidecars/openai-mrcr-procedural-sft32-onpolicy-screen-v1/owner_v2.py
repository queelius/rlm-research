"""Additive attempt-002 owner using the V2 collector and READY."""

from __future__ import annotations

import argparse
import importlib.util
import json
from pathlib import Path
import sys

import checkpoint_v2 as checkpoint
import study_v2 as study


ROOT = Path(__file__).resolve().parent
text = (ROOT / "owner.py").read_text()
if text.count('OUTPUT = study.ROOT / "outputs/attempt-001"') != 1:
    raise ValueError("V1 owner output boundary changed")
text = text.replace(
    'OUTPUT = study.ROOT / "outputs/attempt-001"',
    'OUTPUT = study.ROOT / "outputs/attempt-002"\nCOLLECTOR = study.ROOT / "collect_v2.py"',
)
if text.count('str(study.ROOT / "collect.py")') != 1:
    raise ValueError("V1 collector argv boundary changed")
text = text.replace('str(study.ROOT / "collect.py")', 'str(COLLECTOR)')
previous = {name: sys.modules.get(name) for name in ("study", "checkpoint")}
sys.modules.update(study=study, checkpoint=checkpoint)
try:
    spec = importlib.util.spec_from_loader("sft32_onpolicy_v1_owner_for_v2", loader=None)
    source = importlib.util.module_from_spec(spec)
    source.__file__ = str(ROOT / "owner.py") + ":v2"
    exec(compile(text, source.__file__, "exec"), source.__dict__)
finally:
    for name, value in previous.items():
        if value is None:
            sys.modules.pop(name, None)
        else:
            sys.modules[name] = value

OUTPUT = source.OUTPUT
COLLECTOR = source.COLLECTOR
verify = source.verify
execute = source.execute


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("command", choices=("verify", "run"))
    parser.add_argument("--output", type=Path, default=OUTPUT)
    parser.add_argument("--outer-seconds", type=int, default=study.OWNER_SECONDS)
    args = parser.parse_args()
    if args.command == "verify":
        print(verify()["identity"])
    else:
        value = execute(args.output, args.outer_seconds)
        print(json.dumps(value, sort_keys=True))
        raise SystemExit(0 if value["complete"] else 1)

