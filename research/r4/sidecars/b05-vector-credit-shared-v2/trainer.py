"""Immutable V2 binding to the reviewed trainer; interface fixes live in V2 studies."""

import hashlib
import importlib.util
from pathlib import Path


SOURCE = Path(__file__).resolve().parents[1] / "b05-vector-credit-shared-v1/trainer.py"
EXPECTED = "49facea410f0c3d7f96a931eff2631507d2c05de3fbcdf5f8a7c9e58590fdea3"
assert hashlib.sha256(SOURCE.read_bytes()).hexdigest() == EXPECTED
spec = importlib.util.spec_from_file_location("vector_credit_reviewed_trainer_v1", SOURCE)
module = importlib.util.module_from_spec(spec); spec.loader.exec_module(module)
dependencies = module.dependencies
preflight = module.preflight
run = module.run
