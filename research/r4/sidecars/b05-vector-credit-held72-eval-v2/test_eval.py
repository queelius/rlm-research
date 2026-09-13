"""Execute the pinned V1 focused tests through repaired imports."""
import hashlib
from pathlib import Path
SOURCE=Path(__file__).resolve().parents[1]/"b05-vector-credit-held72-eval-v1/test_eval.py"
assert hashlib.sha256(SOURCE.read_bytes()).hexdigest()=="5bd058c6e213245bd9e0145f8f1e7e51fa28a8d32a5a3e07a521d42daceea204"
exec(compile(SOURCE.read_text(),str(SOURCE),"exec"),globals())
