"""Qualified all-planned exporter with group-relative terminal rewards."""
import sys
import types

import terminal_collect as collect
import terminal_metrics as metrics
import terminal_native as native
import terminal_study as study

SOURCE = study.QSR / "qsr_export.py"
PIN = "3b0e58ef886720cf2efd578ace0629d04b54463532c0531a443dd7fac3447796"
study.check(SOURCE, PIN)
text = SOURCE.read_text()
before = "from qsr_collect import verify_spec"
after = "from terminal_collect import verify_spec"
if text.count(before) != 1:
    raise ValueError("qualified exporter lazy-import seam changed")
qualified = types.ModuleType("terminal_qualified_qsr_export")
qualified.__file__ = str(SOURCE)
sys.modules[qualified.__name__] = qualified
with study.aliases({"qsr_study": study, "qsr_native": native,
                    "qsr_metrics": metrics, "qsr_collect": collect}):
    exec(compile(text.replace(before, after), str(SOURCE) + ":terminal-collect", "exec"),
         qualified.__dict__)

rebuild = qualified.rebuild
export_attempt = qualified.export_attempt
authenticate_export = qualified.authenticate_export
