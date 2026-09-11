"""Qualified four-worker stable collector rebound to Qwen3-8B."""
import argparse
import asyncio
from pathlib import Path
import owner
import protocol as p
import scoring
import study as s

path = s.SIDE / "leaf-mnli-positional-anchor-new-context-v1/collect.py"
source = path.read_text()
if s.sha(path) != "7cc6d945da253f3fab414c80b4fb1ec8b56ac79a80d7856ac94966775c9f6312":
    raise ValueError("qualified collector changed")
if source.count('"planned": 192') != 1 or source.count('len(rows) == 192') != 1:
    raise ValueError("collector inventory seam")
source = source.replace('"planned": 192', '"planned": 144').replace('len(rows) == 192', 'len(rows) == 144')
module = type(s)("qwen8b_stable_collect")
module.__dict__.update({"__file__": str(path), "__name__": "qwen8b_stable_collect"})
with s.aliases({"study": s, "protocol": p, "scoring": scoring, "owner": owner}):
    exec(compile(source, str(path) + "::qwen8b144", "exec"), module.__dict__)
run, summarize = module.run, module.summarize

if __name__ == "__main__":
    parser = argparse.ArgumentParser(); parser.add_argument("command", choices=("run",))
    parser.add_argument("--endpoint", required=True, type=Path); parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--deadline", required=True, type=float); args = parser.parse_args()
    owner.validate_argv([str(s.NATIVE), str(s.ROOT / "collect.py"), "run", "--endpoint", str(args.endpoint), "--output", str(args.output), "--deadline", str(args.deadline)])
    print(asyncio.run(run(args.endpoint, args.output, args.deadline)))
