"""V4 binding to the provenance-complete checkpoint qualifier."""

import importlib.util
import sys

import study_v4 as study


def _load():
    previous = sys.modules.get("study_v3")
    sys.modules["study_v3"] = study
    try:
        path = study.ROOT / "checkpoint_v3.py"
        spec = importlib.util.spec_from_file_location("token_tis_held_v4_checkpoint_source", path)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        return module
    finally:
        if previous is None:
            sys.modules.pop("study_v3", None)
        else:
            sys.modules["study_v3"] = previous


base = _load()
for _name in ("ARTIFACTS", "ZERO", "RECEIPT", "qualify_training", "seal_checkpoint",
              "verify_checkpoint", "ensure_checkpoint", "binding"):
    globals()[_name] = getattr(base, _name)

