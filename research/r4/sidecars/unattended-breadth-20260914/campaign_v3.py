"""Unicode-safe owner with an explicit tokenizer return type and admission-error monitoring."""
import hashlib
import importlib.util
import json
from pathlib import Path

def read_cases(path):
    with Path(path).open() as stream: return [json.loads(line) for line in stream]

_path=Path(__file__).with_name('runner_v2.py')
_spec=importlib.util.spec_from_file_location('breadth_runner_v2',_path)
RUNNER_V2=importlib.util.module_from_spec(_spec); _spec.loader.exec_module(RUNNER_V2)
SOURCE=Path(__file__).with_name('campaign.py')
assert hashlib.sha256(SOURCE.read_bytes()).hexdigest()=='d9117b2ec84a95ea52b65bace5bb2570c7a8bf46ac91261f5376d2d67c051b31'
source=SOURCE.read_text()
for old,new in [
    ('import runner\n','runner=RUNNER_V2\n'),
    ("cases=[json.loads(line) for line in args.cases.read_text().splitlines()]", "cases=read_cases(args.cases)"),
    ("(ROOT/'runner.py',ROOT/'campaign.py')", "(ROOT/'runner.py',ROOT/'runner_v2.py',ROOT/'campaign.py',Path(__file__))"),
    ("if client.returned==0 and client.errors: client.stop.set()", "if client.returned==0 and (client.errors or any(r.get('error') for r in rows[-4:])): client.stop.set()"),
    ("(['calculate'] if dataset=='finqa' else [])", "(['calculate'] if dataset=='finqa' and case['answer_type']=='number' else [])"),
]:
    assert source.count(old)==1, old
    source=source.replace(old,new)
exec(compile(source,str(SOURCE),'exec'),globals())
