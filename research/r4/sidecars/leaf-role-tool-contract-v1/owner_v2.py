"""Additive owner binding the preserved attempt to the V2 native-admission collector."""

from pathlib import Path
from types import ModuleType

import study as s

SOURCE = s.ROOT / "owner.py"
SOURCE_SHA256 = "196036051c7e1bdc18176d84a243cdd56999439319b9b6040e23a026361e83e4"


def source_text():
    if s.sha(SOURCE) != SOURCE_SHA256:
        raise ValueError("frozen V1 owner changed")
    source = SOURCE.read_text()
    changes = {
        "import driver\n": ("import driver_v2 as driver\n", 1),
        's.ROOT / "READY.json"': ('s.ROOT / "READY_V2.json"', 1),
        's.ROOT / "driver.py"': ('s.ROOT / "driver_v2.py"', 1),
    }
    for before, (after, count) in changes.items():
        if source.count(before) != count:
            raise ValueError("V2 owner seam changed: " + before)
        source = source.replace(before, after)
    return source


module = ModuleType("leaf_role_tool_owner_v2")
module.__file__ = str(Path(__file__).resolve())
exec(compile(source_text(), str(SOURCE) + ":native-admission-v2", "exec"), module.__dict__)


if __name__ == "__main__":
    module.main()
