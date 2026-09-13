"""Pinned reviewed finite subprocess owner."""
import hashlib, importlib.util
from pathlib import Path
SOURCE=Path(__file__).resolve().parents[1]/"b05-vector-credit-shared-v2/owner_core.py"
assert hashlib.sha256(SOURCE.read_bytes()).hexdigest()=="4535139f906b95a89ff270cd8b88d095ba8dffb43a93c65914ec81125e4ca446"
spec=importlib.util.spec_from_file_location("vector_credit_owner_v3",SOURCE);module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
run=module.run
