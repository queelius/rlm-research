"""Additive Unicode JSONL repair; retain the failed pre-GPU pilot unchanged."""
import hashlib
import json
from pathlib import Path

def read_cases(path):
    with Path(path).open() as stream:
        return [json.loads(line) for line in stream]

SOURCE=Path(__file__).with_name('campaign.py')
assert hashlib.sha256(SOURCE.read_bytes()).hexdigest()=='d9117b2ec84a95ea52b65bace5bb2570c7a8bf46ac91261f5376d2d67c051b31'
source=SOURCE.read_text()
for old,new in [
    ("cases=[json.loads(line) for line in args.cases.read_text().splitlines()]", "cases=read_cases(args.cases)"),
    ("(ROOT/'runner.py',ROOT/'campaign.py')", "(ROOT/'runner.py',ROOT/'campaign.py',Path(__file__))"),
]:
    assert source.count(old)==1
    source=source.replace(old,new)
exec(compile(source,str(SOURCE),'exec'),globals())
