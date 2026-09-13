"""Immutable V2 binding to the reviewed fixed-step checkpoint audit."""

import hashlib
import importlib.util
from pathlib import Path


SOURCE = Path(__file__).resolve().parents[1] / "b05-vector-credit-shared-v1/qualify_checkpoint.py"
EXPECTED = "6a7b8cb7beb2779a94cf5f791f64f69b670e113cf22e87221983ae0e284844c9"
assert hashlib.sha256(SOURCE.read_bytes()).hexdigest() == EXPECTED
spec = importlib.util.spec_from_file_location("vector_credit_reviewed_checkpoint_v1", SOURCE)
module = importlib.util.module_from_spec(spec); spec.loader.exec_module(module)
endpoint = module.endpoint
