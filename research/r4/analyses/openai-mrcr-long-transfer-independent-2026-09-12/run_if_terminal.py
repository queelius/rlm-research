"""One-shot gate; never polls and never scores partial outputs."""
import subprocess
from pathlib import Path
import sys

ROOT=Path(__file__).resolve().parent
SIDE=ROOT.parents[1]/'sidecars/openai-mrcr-long-transfer-eval-v1/outputs'
terms=[SIDE/'base-002/OWNER_TERMINAL.json',SIDE/'checkpoint32-002/OWNER_TERMINAL.json']
if not all(path.exists() for path in terms):
    print('PENDING_BOTH_OWNER_TERMINALS');raise SystemExit(2)
raise SystemExit(subprocess.call([sys.executable,str(ROOT/'analyze.py'),'check','--output-dir',str(ROOT/'outcome')]))
