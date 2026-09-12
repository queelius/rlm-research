"""Additive attempt002 and source seal; every scientific input remains V1."""
import importlib.util
from pathlib import Path

ROOT = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location('report_followup_study_v1_reuse', ROOT / 'study.py')
base = importlib.util.module_from_spec(spec); spec.loader.exec_module(base)
for key in dir(base):
    if not key.startswith('_'): globals()[key] = getattr(base, key)
ATTEMPT = ROOT / 'outputs/attempt-002'
READY = ROOT / 'READY_V2.json'


def verify():
    base.verify()
    value = read(READY)
    assert value['identity'] == digest({k: v for k, v in value.items() if k != 'identity'})
    assert value['schedule_sha256'] == digest(schedule()) and len(schedule()) == 132
    for path, expected in value['closure_sha256'].items(): assert sha(path) == expected, path
    return value
