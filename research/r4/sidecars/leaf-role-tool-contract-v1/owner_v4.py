"""Attempt-003 owner with explicitly qualified service module binding."""

from pathlib import Path
from types import ModuleType

import study as s

SOURCE = s.ROOT / "owner.py"
SOURCE_SHA256 = "196036051c7e1bdc18176d84a243cdd56999439319b9b6040e23a026361e83e4"


def source_text():
    if s.sha(SOURCE) != SOURCE_SHA256:
        raise ValueError("frozen V1 owner changed")
    source = SOURCE.read_text()
    replacements = {
        "import driver\n": ("import driver_v4 as driver\n", 1),
        "import lifecycle\n": ("import lifecycle_v3 as lifecycle\n", 1),
        's.ROOT / "outputs/attempt-001"': ('s.ROOT / "outputs/attempt-003"', 1),
        's.ROOT / "READY.json"': ('s.ROOT / "READY_RECOVERY2.json"', 1),
        's.ROOT / "driver.py"': ('s.ROOT / "driver_v4.py"', 1),
        "only exact attempt-001 output is authorized":
            ("only exact attempt-003 output is authorized", 1),
    }
    for before, (after, count) in replacements.items():
        if source.count(before) != count:
            raise ValueError("attempt-003 owner seam changed: " + before)
        source = source.replace(before, after)
    return source


module = ModuleType("leaf_role_tool_owner_v4")
module.__file__ = str(Path(__file__).resolve())
exec(compile(source_text(), str(SOURCE) + ":attempt003", "exec"), module.__dict__)


if __name__ == "__main__":
    module.main()
