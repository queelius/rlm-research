"""Additive V2 launcher repairing only NumPy's legacy uint32 seed seam."""

import argparse
import hashlib
import importlib.util
import json
from pathlib import Path
import random
import time


ROOT = Path(__file__).resolve().parent
SIDE = ROOT.parent
V1 = SIDE / "root-qs6-leaf-rloo-fresh-batch-invariant-one-update-v1"
V1_TRAIN_SHA = "17262d02861b66b51d0464f7eaadf44ceb24d018f4bc38d4e496cd3528a43a23"
MASTER_SEED = 202609121401
NUMPY_SEED = MASTER_SEED % (2**32)


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def write_x(path, value):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("x") as stream:
        stream.write(json.dumps(value, indent=2, sort_keys=True, allow_nan=False) + "\n")


def source_sha256():
    return sha(V1 / "train.py")


def load_v1():
    if source_sha256() != V1_TRAIN_SHA:
        raise ValueError("sealed V1 trainer changed")
    spec = importlib.util.spec_from_file_location("fresh48_one_update_v1_sealed", V1 / "train.py")
    if spec is None or spec.loader is None:
        raise RuntimeError("cannot load sealed V1 trainer")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    if module.SEED != MASTER_SEED:
        raise ValueError("V1 master seed changed")
    return module


def seed_map():
    return {
        "master": MASTER_SEED,
        "python": MASTER_SEED,
        "numpy_legacy": NUMPY_SEED,
        "torch": MASTER_SEED,
        "torch_cuda_all": MASTER_SEED,
    }


def initialize_rng(np_module, torch_module):
    """Exercise the exact repaired initialization independently on CPU."""
    random.seed(MASTER_SEED)
    np_module.random.seed(NUMPY_SEED)
    torch_module.manual_seed(MASTER_SEED)
    torch_module.cuda.manual_seed_all(MASTER_SEED)
    return seed_map()


def run(output, cap_seconds, source=None):
    """Run sealed V1 with a narrowly scoped adapter at np.random.seed."""
    import numpy as np

    output = Path(output)
    expected = (ROOT / "outputs/attempt-001").resolve()
    # Tests may exercise the wrapper in a temporary output with an injected source.
    if source is None and output.resolve() != expected:
        raise ValueError("exact sealed V2 output required")
    source = source or load_v1()
    source.ROOT = ROOT
    original_seed = np.random.seed
    observed = {"called": False}

    def repaired_numpy_seed(value=None):
        if value == MASTER_SEED:
            observed["called"] = True
            return original_seed(NUMPY_SEED)
        return original_seed(value)

    np.random.seed = repaired_numpy_seed
    try:
        result = source.run(output, cap_seconds)
        return result
    finally:
        np.random.seed = original_seed
        if output.exists() and observed["called"] and not (output / "RNG_SEEDS_ACTUAL.json").exists():
            write_x(
                output / "RNG_SEEDS_ACTUAL.json",
                {
                    "schema": "fresh48-one-update-rng-seeds-v2",
                    "master_seed_unchanged": True,
                    "master_seed": MASTER_SEED,
                    "python_seed": MASTER_SEED,
                    "numpy_legacy_seed": NUMPY_SEED,
                    "torch_seed": MASTER_SEED,
                    "torch_cuda_all_seed": MASTER_SEED,
                    "only_behavioral_change_from_v1": "np.random.seed(master) mapped modulo 2**32",
                    "v1_train_sha256": V1_TRAIN_SHA,
                    "v1_failure_preserved": True,
                    "recorded_epoch": time.time(),
                },
            )


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--cap-seconds", type=int, required=True)
    args = parser.parse_args()
    print(json.dumps(run(args.output, args.cap_seconds), sort_keys=True))
