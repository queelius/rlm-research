"""Attempt-003 namespace wrapper around the frozen V2 collector."""

from pathlib import Path
from types import ModuleType

import study as s

SOURCE = s.ROOT / "driver_v2.py"
SOURCE_SHA256 = "5193ea28616616268a924f2bb059d93dc96c7ffafd3df60439c5c5641b3969e7"


def source_text():
    if s.sha(SOURCE) != SOURCE_SHA256:
        raise ValueError("frozen V2 collector changed")
    source = SOURCE.read_text()
    replacements = {
        "outputs/attempt-001/rollout": ("outputs/attempt-003/rollout", 1),
        "attempt-001 rollout is authorized": ("attempt-003 rollout is authorized", 1),
    }
    for before, (after, count) in replacements.items():
        if source.count(before) != count:
            raise ValueError("collector output namespace seam changed")
        source = source.replace(before, after)
    return source


module = ModuleType("leaf_role_tool_driver_v4")
module.__file__ = str(Path(__file__).resolve())
exec(compile(source_text(), str(SOURCE) + ":attempt003", "exec"), module.__dict__)
AUTHORIZED_OUTPUT = module.AUTHORIZED_OUTPUT
verify = module.verify
validate_output = module.validate_output
run = module.run
main = module.main


if __name__ == "__main__":
    main()
