"""Immutable V2 binding to the finite subprocess owner."""

import hashlib
import importlib.util
from pathlib import Path


SOURCE = Path(__file__).resolve().parents[1] / "b05-vector-credit-shared-v1/owner_core.py"
EXPECTED = "7e28b32fe15392ec47feebb359869554c0d6a040753abd93d53008b91e0a44dc"
assert hashlib.sha256(SOURCE.read_bytes()).hexdigest() == EXPECTED
spec = importlib.util.spec_from_file_location("vector_credit_reviewed_owner_v1", SOURCE)
module = importlib.util.module_from_spec(spec); spec.loader.exec_module(module)
run = module.run
