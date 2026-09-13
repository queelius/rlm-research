"""Owner entrypoint bound to the additive clock/attempt repair."""

import argparse
import json
import sys

import collect_v2 as collect
import study_v2 as study

old_study, old_collect = sys.modules.get("study"), sys.modules.get("collect")
sys.modules["study"], sys.modules["collect"] = study, collect
try:
    source = study.load("b05_qwen8_owner_source_v2", study.ROOT / "owner.py")
finally:
    if old_study is None:
        sys.modules.pop("study", None)
    else:
        sys.modules["study"] = old_study
    if old_collect is None:
        sys.modules.pop("collect", None)
    else:
        sys.modules["collect"] = old_collect


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("command", choices=["verify", "run"])
    parser.add_argument("--outer-seconds", type=int, default=study.OWNER_SECONDS)
    args = parser.parse_args()
    if args.command == "verify":
        print(study.verify()["identity"])
    else:
        result = source.execute(args.outer_seconds)
        print(json.dumps(result))
        raise SystemExit(0 if result["complete"] else 1)

