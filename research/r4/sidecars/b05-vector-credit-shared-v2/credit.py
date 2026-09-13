"""Immutable V2 binding to the reviewed vector-credit objective."""

import importlib.util
from pathlib import Path


SOURCE = Path(__file__).resolve().parents[1] / "b05-vector-credit-shared-v1/credit.py"
EXPECTED = "17f906a57f4d134b617ff5ea1f3995ed121a8a3f1335a40675caf46cacdeb937"
import hashlib
assert hashlib.sha256(SOURCE.read_bytes()).hexdigest() == EXPECTED
spec = importlib.util.spec_from_file_location("vector_credit_reviewed_math_v1", SOURCE)
module = importlib.util.module_from_spec(spec); spec.loader.exec_module(module)
credit_loss = module.credit_loss
advantages = module.advantages
token_credit = module.token_credit
