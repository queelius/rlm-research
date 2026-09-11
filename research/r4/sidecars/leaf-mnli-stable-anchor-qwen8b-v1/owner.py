"""MAIN-only 144-call owner adapted from the qualified stable192 owner."""
import argparse
from pathlib import Path
import protocol as p
import study as s

path = s.SIDE / "leaf-mnli-positional-anchor-new-context-v1/owner.py"
source = path.read_text()
if s.sha(path) != "021eae6f5edfceaf95d190f8f1b556053fc83333debdeb7e4b846f9d813d74b6":
    raise ValueError("qualified owner changed")
replacements = {
    'CLOCK = {"outer": 1800, "work": 1650, "owned": 1770, "startup": 180, "release": 90, "harvest": 30, "finalize": 30, "margin": 30}': 'CLOCK = {"outer": 2400, "work": 2250, "owned": 2370, "startup": 300, "release": 90, "harvest": 30, "finalize": 30, "margin": 30}',
    's.sha(s.base.FREE / "WEIGHTS.json")': 's.sha(s.ROOT / "WEIGHTS.json")',
    'terminal["planned"] != 192 or terminal["recorded"] != 192': 'terminal["planned"] != 144 or terminal["recorded"] != 144',
    '"planned": 192': '"planned": 144',
    'mnli-position-anchor-new-context192-collect': 'mnli-stable-anchor-qwen8b144-collect',
}
for before, after in replacements.items():
    if source.count(before) != 1: raise ValueError("owner adaptation seam: " + before)
    source = source.replace(before, after)
exec(compile(source, str(path) + "::qwen8b144", "exec"), globals())

if __name__ == "__main__":
    parser = argparse.ArgumentParser(); parser.add_argument("command", choices=("verify", "run")); parser.add_argument("--output", type=Path, default=s.ATTEMPT); args = parser.parse_args()
    if args.command == "verify": print(s.verify()["identity"])
    else:
        result = execute(args.output); print(result); raise SystemExit(0 if result["complete"] else 1)
