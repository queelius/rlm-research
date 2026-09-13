"""Pinned reviewed checkpoint audit."""
import hashlib, importlib.util
from pathlib import Path
SOURCE=Path(__file__).resolve().parents[1]/"b05-vector-credit-shared-v2/qualify_checkpoint.py"
assert hashlib.sha256(SOURCE.read_bytes()).hexdigest()=="6e611e0b3f6423cf278b86e2dfa4676a16b5ab8451c2e79d6dac19e12d5d6066"
spec=importlib.util.spec_from_file_location("vector_credit_checkpoint_v3",SOURCE);module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
endpoint=module.endpoint
