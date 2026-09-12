"""Additive fresh-process path binding for the sealed V1 collector."""

import os
from pathlib import Path
import runpy
import sys


ROOT = Path(__file__).resolve().parent


def install_path():
    existing = [value for value in os.environ.get("PYTHONPATH", "").split(os.pathsep) if value]
    os.environ["PYTHONPATH"] = os.pathsep.join([str(ROOT), *[value for value in existing if value != str(ROOT)]])
    if str(ROOT) not in sys.path:
        sys.path.insert(0, str(ROOT))


if __name__ == "__main__":
    install_path()
    runpy.run_path(str(ROOT / "collect.py"), run_name="__main__")
