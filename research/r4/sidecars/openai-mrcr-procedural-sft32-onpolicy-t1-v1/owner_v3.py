"""Additive owner facade: V2 lifecycle with attempt-003/collector-v3."""

from __future__ import annotations

import argparse
import importlib.util
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parent
path = ROOT / "owner_v2.py"
text = path.read_text()
replacements = {
    "import study_v2 as study": "import study_v3 as study",
    'OUTPUT = study.ROOT / "outputs/attempt-002"': 'OUTPUT = study.ROOT / "outputs/attempt-003"',
    'str(study.ROOT / "collect_v2.py")': 'str(study.ROOT / "collect_v3.py")',
    '"mrcr-sft32-onpolicy-t1-repair-v2"': '"mrcr-sft32-onpolicy-t1-repair-v3"',
    '"exact unused attempt-002 output required"': '"exact unused attempt-003 output required"',
    '"proven-native-model-context-plus-temperature-only"': '"T1-role-audit-temperature-expectation"',
    'str(study.ROOT / "outputs/attempt-001")': 'str(study.ROOT / "outputs/attempt-002")',
}
for needle, replacement in replacements.items():
    if text.count(needle) != 1:
        raise ValueError("owner V2 transform source changed: " + needle)
    text = text.replace(needle, replacement)
spec = importlib.util.spec_from_loader("mrcr_t1_owner_v3_transformed", loader=None)
source = importlib.util.module_from_spec(spec)
source.__file__ = str(path)
exec(compile(text, str(path), "exec"), source.__dict__)
OUTPUT = source.OUTPUT
verify = source.verify
execute = source.execute


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("command", choices=("verify", "run"))
    parser.add_argument("--output", type=Path, default=OUTPUT)
    parser.add_argument("--outer-seconds", type=int, default=source.study.OWNER_SECONDS)
    args = parser.parse_args()
    if args.command == "verify":
        print(verify()["identity"])
    else:
        value = execute(args.output, args.outer_seconds)
        print(json.dumps(value, sort_keys=True))
        raise SystemExit(0 if value["complete"] else 1)

