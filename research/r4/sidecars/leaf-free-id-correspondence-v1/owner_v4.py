"""Additive attempt-003 owner with verified owner-to-collector path composition."""

from pathlib import Path
from types import ModuleType

import driver_v3
import study as s

SOURCE = s.ROOT / "owner.py"
SOURCE_SHA256 = "bb684d3a2a17464526fb451e9e087fb72140d2addf678f7b1b2752ab7ebb2e45"


def collector_argv(stage, output, deadline):
    argv = [str(Path("/project/alex_phd/envs/prime-rl-5990b1b/bin/python")),
            str(s.ROOT / "driver_v3.py"), "run", "--endpoint",
            str(stage / "service/endpoint-original.json"), "--output",
            str(output / "rollout"), "--deadline", str(deadline)]
    driver_v3.validate_owner_argv(argv)
    return argv


def source_text():
    if s.sha(SOURCE) != SOURCE_SHA256:
        raise ValueError("frozen owner V1 changed")
    source = SOURCE.read_text()
    old_argv = '''        argv = [str(NATIVE), str(s.ROOT / "driver.py"), "run", "--endpoint",
                str(stage / "service/endpoint-original.json"), "--output",
                str(output / "rollout"), "--deadline", str(work_deadline)]'''
    changes = {
        "import driver": ("import driver_v3 as driver", 1),
        "import lifecycle_adapter": ("import lifecycle_adapter_v3 as lifecycle_adapter", 1),
        's.ROOT / "outputs/attempt-001"': ('s.ROOT / "outputs/attempt-003"', 1),
        's.ROOT / "READY.json"': ('s.ROOT / "READY_RECOVERY3.json"', 1),
        '        suite.start_service(stage, binding(), min(work_deadline, time.time() + 300))': (
            '        suite.start_service(stage, binding(), min(work_deadline, time.time() + 300))\n'
            '        collection_deadline = min(work_deadline, time.time() + 1500)', 1),
        old_argv: ("        argv = collector_argv(stage, output, collection_deadline)", 1),
        '"only exact attempt-001 output is authorized"': (
            '"only exact attempt-003 output is authorized"', 1),
    }
    for before, (after, count) in changes.items():
        if source.count(before) != count:
            raise ValueError("attempt-003 owner seam changed: " + before)
        source = source.replace(before, after)
    return source


module = ModuleType("free_id_owner_attempt003")
module.__file__ = str(Path(__file__).resolve())
module.__dict__["collector_argv"] = collector_argv
exec(compile(source_text(), str(SOURCE) + ":attempt003", "exec"), module.__dict__)


if __name__ == "__main__":
    module.main()
