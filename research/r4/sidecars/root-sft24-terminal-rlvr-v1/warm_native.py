"""Pinned current native task/render interface in the warm-start namespace."""
import functools

import warm_study as study

SOURCE = study.QSR / "qsr_native.py"
PIN = "02aea033ef02a215577af03e18769adda0d9994e947900b310b1a7ee8356441c"
with study.aliases({"qsr_study": study}):
    qualified = study.load("warm_qualified_qsr_native", SOURCE, PIN)

stack = qualified.stack
prompt = qualified.prompt
make_task = qualified.make_task
first_prefix = qualified.first_prefix
interface = qualified.interface
exact_turns = qualified.exact_turns
validate_typed_audit = qualified.validate_typed_audit
