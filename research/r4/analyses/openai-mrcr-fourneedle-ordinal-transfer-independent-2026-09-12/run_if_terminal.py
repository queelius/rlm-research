"""Check once for both owner terminals; never poll or score partial outputs."""

from pathlib import Path
import subprocess
import sys


ROOT = Path(__file__).resolve().parent
OUTPUTS = ROOT.parents[1] / "sidecars/openai-mrcr-fourneedle-ordinal-transfer-eval-v1/outputs"
TERMINALS = [
    OUTPUTS / "base-001/OWNER_TERMINAL.json",
    OUTPUTS / "checkpoint32-001/OWNER_TERMINAL.json",
]
if not all(path.exists() for path in TERMINALS):
    print("PENDING_BOTH_OWNER_TERMINALS")
    raise SystemExit(2)
raise SystemExit(
    subprocess.call(
        [sys.executable, str(ROOT / "analyze.py"), "check", "--output-dir", str(ROOT / "outcome")]
    )
)
