"""Exact reviewed collector rebound to renamed train tasks."""

import study

with study.aliases({"study": study}, study.SOURCE_EVAL):
    inherited = study.load("b05_id_rename_native_collector", study.SOURCE_EVAL / "collect.py")

execute = inherited.execute

