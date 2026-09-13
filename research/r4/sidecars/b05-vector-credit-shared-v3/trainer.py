"""V3 owner/trainer directory handshake repair over the immutable V1 trainer."""

import hashlib
import importlib.util
from pathlib import Path
import types


SOURCE = Path(__file__).resolve().parents[1] / "b05-vector-credit-shared-v1/trainer.py"
EXPECTED = "49facea410f0c3d7f96a931eff2631507d2c05de3fbcdf5f8a7c9e58590fdea3"
assert hashlib.sha256(SOURCE.read_bytes()).hexdigest() == EXPECTED
text = SOURCE.read_text()
old = "output.mkdir(parents=True)"
assert text.count(old) == 1
text = text.replace(old, "output.mkdir(parents=True, exist_ok=True)")
module = types.ModuleType("vector_credit_trainer_directory_repair_v3"); module.__file__ = str(SOURCE)
exec(compile(text, str(SOURCE), "exec"), module.__dict__)
dependencies = module.dependencies
preflight = module.preflight
run = module.run
