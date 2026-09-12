"""Regression for the context-mount wrapper's fresh-process import boundary."""

import os
from pathlib import Path
import subprocess


ROOT = Path(__file__).resolve().parent
PYTHON = "/project/alex_phd/envs/prime-rl-5990b1b/bin/python"


def test_collector_entry_exposes_sidecar_to_fresh_docker_wrapper():
    script = ROOT / "collector_entry_v2.py"
    assert script.exists(), "additive V2 collector entry is missing"
    code = (
        "import importlib.util,os,runpy;"
        f"p={str(script)!r};"
        "s=importlib.util.spec_from_file_location('entry_v2',p);"
        "m=importlib.util.module_from_spec(s);s.loader.exec_module(m);m.install_path();"
        f"runpy.run_path({str(ROOT / 'boundary.py')!r});"
        "assert os.environ['PYTHONPATH'].split(os.pathsep)[0]==" + repr(str(ROOT))
    )
    result = subprocess.run([PYTHON, "-c", code], cwd="/tmp",
        env={**os.environ, "PYTHONPATH": "", "PYTHONDONTWRITEBYTECODE": "1"},
        capture_output=True, text=True)
    assert result.returncode == 0, result.stderr


def test_repaired_owner_dispatches_only_additive_entry():
    import owner_v2

    assert owner_v2.COLLECTOR == ROOT / "collector_entry_v2.py"
    assert owner_v2.OWNER_SECONDS == 900
    assert owner_v2.ATTEMPT == ROOT / "outputs/attempt-002"

