"""Additive attempt-002 owner preserving the V2 science and score contract."""

from pathlib import Path
from types import ModuleType

import study as s

SOURCE = s.ROOT / "owner.py"
SOURCE_SHA256 = "bb684d3a2a17464526fb451e9e087fb72140d2addf678f7b1b2752ab7ebb2e45"


def source_text():
    if s.sha(SOURCE) != SOURCE_SHA256:
        raise ValueError("frozen owner V1 changed")
    source = SOURCE.read_text()
    changes = {
        "import lifecycle_adapter": ("import lifecycle_adapter_v3 as lifecycle_adapter", 1),
        's.ROOT / "outputs/attempt-001"': ('s.ROOT / "outputs/attempt-002"', 1),
        's.ROOT / "READY.json"': ('s.ROOT / "READY_RECOVERY.json"', 1),
        'str(s.ROOT / "driver.py")': ('str(s.ROOT / "driver_v2.py")', 1),
        '        suite.start_service(stage, binding(), min(work_deadline, time.time() + 300))': (
            '        suite.start_service(stage, binding(), min(work_deadline, time.time() + 300))\n'
            '        collection_deadline = min(work_deadline, time.time() + 1500)', 1),
        '"--deadline", str(work_deadline)': ('"--deadline", str(collection_deadline)', 1),
        '"only exact attempt-001 output is authorized"': (
            '"only exact attempt-002 output is authorized"', 1),
    }
    for before, (after, count) in changes.items():
        if source.count(before) != count:
            raise ValueError("attempt-002 owner seam changed: " + before)
        source = source.replace(before, after)
    return source


module = ModuleType("free_id_owner_attempt002")
module.__file__ = str(Path(__file__).resolve())
exec(compile(source_text(), str(SOURCE) + ":attempt002", "exec"), module.__dict__)


if __name__ == "__main__":
    module.main()
