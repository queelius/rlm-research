"""Public study module with an explicit parent-source binding."""
import importlib.util
import sys

import terminal_study as _study

for _name in dir(_study):
    if not _name.startswith("__"):
        globals()[_name] = getattr(_study, _name)

_spec = importlib.util.spec_from_file_location("lr_parent_terminal_study",
                                               SOURCE / "terminal_study.py")
source_study = importlib.util.module_from_spec(_spec)
_path = list(sys.path)
try:
    _spec.loader.exec_module(source_study)
finally:
    sys.path[:] = _path
