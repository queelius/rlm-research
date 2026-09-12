"""Additive attempt003, unchanged scientific inputs and two earlier seals."""
import importlib.util
from pathlib import Path

ROOT = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location('report_followup_study_v2_reuse_v3', ROOT / 'study_v2.py')
previous = importlib.util.module_from_spec(spec); spec.loader.exec_module(previous)
for key in dir(previous):
    if not key.startswith('_'): globals()[key] = getattr(previous, key)
ATTEMPT = ROOT / 'outputs/attempt-003'
READY = ROOT / 'READY_V3.json'


def verify():
    previous.verify()
    value = read(READY)
    assert value['identity'] == digest({k: v for k, v in value.items() if k != 'identity'})
    assert value['schedule_sha256'] == digest(schedule()) and len(schedule()) == 132
    for path, expected in value['closure_sha256'].items(): assert sha(path) == expected, path
    return value

