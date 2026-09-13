"""Pinned reviewed vector-credit objective."""
import hashlib, importlib.util
from pathlib import Path
SOURCE=Path(__file__).resolve().parents[1]/"b05-vector-credit-shared-v2/credit.py"
assert hashlib.sha256(SOURCE.read_bytes()).hexdigest()=="7b92efc408def3bedf9d6f43807b088228b31e548624989c07ca1fe97195a825"
spec=importlib.util.spec_from_file_location("vector_credit_math_v3",SOURCE);module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
credit_loss=module.credit_loss;advantages=module.advantages;token_credit=module.token_credit
