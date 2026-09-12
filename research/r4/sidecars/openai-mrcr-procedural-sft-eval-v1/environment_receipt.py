"""Record the immutable training environment without mutating the training READY."""

import importlib.metadata
import json
import os
from pathlib import Path
import platform
import subprocess
import sys
import time

import study


def main():
    if os.environ.get("CUDA_VISIBLE_DEVICES") != "":
        raise ValueError("environment inventory is CPU-only")
    import torch

    env_root = study.TRAIN_PYTHON.parents[2]
    pyproject = env_root / "pyproject.toml"
    lock = env_root / "uv.lock"
    pyvenv = study.TRAIN_PYTHON.parents[1] / "pyvenv.cfg"
    pyvenv_lines = dict(
        line.split(" = ", 1) for line in pyvenv.read_text().splitlines() if " = " in line
    )
    driver = subprocess.run(
        ["nvidia-smi", "--query-gpu=driver_version,name,memory.total", "--format=csv,noheader"],
        capture_output=True,
        text=True,
        timeout=10,
        check=False,
    )
    value = {
        "schema": "openai-mrcr-procedural-sft-training-environment-v2",
        "created_epoch": time.time(),
        "python_executable": sys.executable,
        "python_version": sys.version,
        "platform": platform.platform(),
        "packages": {
            name: importlib.metadata.version(name)
            for name in ("torch", "transformers", "peft", "safetensors", "numpy", "accelerate")
        },
        "torch_cuda_build": torch.version.cuda,
        "cudnn_build": torch.backends.cudnn.version(),
        "driver_inventory": {"returncode": driver.returncode, "stdout": driver.stdout.strip()},
        "uv_version": pyvenv_lines["uv"],
        "uv_executable_currently_available": False,
        "pyvenv_cfg": str(pyvenv),
        "pyvenv_cfg_sha256": study.sha(pyvenv),
        "pyproject": str(pyproject),
        "pyproject_sha256": study.sha(pyproject),
        "uv_lock": str(lock),
        "uv_lock_sha256": study.sha(lock),
        "uv_lock_format": {"version": 1, "revision": 3, "requires_python": "==3.12.*"},
        "cuda_visible_devices": "",
        "gpu_model_calls": 0,
    }
    value["identity"] = study.digest(value)
    study.write_x(study.ROOT / "TRAINING_ENVIRONMENT_V2.json", value)
    print(json.dumps(value, sort_keys=True))


if __name__ == "__main__":
    main()
