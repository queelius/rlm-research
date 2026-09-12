"""Complete RNG snapshots and immutable commits; no automatic resume owner."""

import random
from pathlib import Path

import numpy as np
import torch
from core import read, sha, write


def save_rng(path, generator):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists():
        raise ValueError("preserve existing RNG snapshot")
    torch.save(
        {
            "python": random.getstate(),
            "numpy": np.random.get_state(),
            "torch": torch.get_rng_state(),
            "cuda": torch.cuda.get_rng_state_all(),
            "sampling_generator": generator.get_state(),
            "sampling_device": str(generator.device),
        },
        path,
    )
    return sha(path)


def restore_rng(path, generator):
    state = torch.load(path, map_location="cpu", weights_only=False)
    if state["sampling_device"] != str(generator.device):
        raise ValueError("sampler device changed")
    random.setstate(state["python"])
    np.random.set_state(state["numpy"])
    torch.set_rng_state(state["torch"])
    torch.cuda.set_rng_state_all(state["cuda"])
    generator.set_state(state["sampling_generator"])


def commit_files(path, files, metadata):
    path = Path(path)
    if path.exists():
        raise ValueError("preserve existing immutable commit")
    if "files_sha256" in metadata:
        raise ValueError("commit file inventory is derived, not caller supplied")
    result = {
        **metadata,
        "files_sha256": {str(Path(file).resolve()): sha(Path(file)) for file in files},
    }
    write(path, result)
    return result


def verify_commit(path, parent_identity):
    receipt = read(Path(path))
    if receipt["parent_identity"] != parent_identity:
        raise ValueError("commit frozen parent identity changed")
    for raw, expected in receipt["files_sha256"].items():
        if sha(Path(raw)) != expected:
            raise ValueError("committed file changed: " + raw)
    return receipt
