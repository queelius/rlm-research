"""Additive owner source adapter for scoring V2 and a true 1,500-second collection cap."""

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
        's.ROOT / "READY.json"': ('s.ROOT / "READY_V2.json"', 1),
        'str(s.ROOT / "driver.py")': ('str(s.ROOT / "driver_v2.py")', 1),
        '        suite.start_service(stage, binding(), min(work_deadline, time.time() + 300))': (
            '        suite.start_service(stage, binding(), min(work_deadline, time.time() + 300))\n'
            '        collection_deadline = min(work_deadline, time.time() + 1500)', 1),
        '"--deadline", str(work_deadline)': ('"--deadline", str(collection_deadline)', 1),
    }
    for before, (after, count) in changes.items():
        if source.count(before) != count:
            raise ValueError("owner V2 seam changed: " + before)
        source = source.replace(before, after)
    return source


module = ModuleType("free_id_owner_v2_adapted")
module.__file__ = str(Path(__file__).resolve())
exec(compile(source_text(), str(SOURCE) + ":scoring-and-deadline-v2", "exec"), module.__dict__)


if __name__ == "__main__":
    module.main()

