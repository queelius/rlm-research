"""Pinned bindings for the mixed-contract TREC child-interface continuation study."""

import hashlib
import importlib.util
import json
import os
from pathlib import Path

ROOT = Path(__file__).resolve().parent
SIDE = ROOT.parent
ATTEMPT = ROOT / "outputs/attempt-001"
PREPARED = ROOT / "prepared-v1"
SFT = SIDE / "trec-leaf-sft-v1"
QUERY = SIDE / "leaf-trec-query-conditioned-interface-v1"
TEST500 = SIDE / "leaf-trec-test-adapter-granularity-v1"
SPLIT = SIDE / "trec-leaf-split-provenance-v1"
SUITE = SIDE / "leaf-post-sft-suite-v1"
START = SFT / "outputs/attempt-001/checkpoint-0128"
BASE = Path(
    "/project/alex_phd/research-cache/models/Qwen--Qwen3-4B-Instruct-2507--cdbee75f17c01a7cc42f958dc650907174af0554"
)
TRAIN_PYTHON = Path(
    "/project/alex_phd/repos/rlm-bootstrap/.worktrees/a100-lora-roundtrip/gpu/training/.venv/bin/python"
)
NATIVE_PYTHON = Path("/project/alex_phd/envs/prime-rl-5990b1b/bin/python")
C32_SHA = "c32de1293c01bba5104eb1f123867649c71dd38e5194661ace4b17dcbbe66ba3"
TRAIN_DIGEST = "fab949da3e3cb3614783c7ac0d708ec125392d3daffab2f6647f989f221539d5"
PRIMARY_DIGEST = "b5e6ddec556706ae20cd0eabada097b394ae1d824e145e440545f9950c5d8f0a"
CATEGORIES = (
    "human being",
    "location",
    "abbreviation",
    "entity",
    "description and abstract concept",
    "numeric value",
)
TRAIN_PAIRS = tuple((CATEGORIES[i], CATEGORIES[(i + 1) % 6]) for i in range(6))
NEW_PAIRS = (
    (CATEGORIES[0], CATEGORIES[3]),
    (CATEGORIES[3], CATEGORIES[5]),
    (CATEGORIES[5], CATEGORIES[1]),
    (CATEGORIES[1], CATEGORIES[4]),
    (CATEGORIES[4], CATEGORIES[2]),
    (CATEGORIES[2], CATEGORIES[0]),
)
ALIASES = {"c32": "trec-c32", "mixed_sft24": "trec-mixed-sft24"}


def sha(path):
    with Path(path).open("rb") as stream:
        return hashlib.file_digest(stream, "sha256").hexdigest()


def digest(value):
    return hashlib.sha256(
        json.dumps(value, sort_keys=True, separators=(",", ":")).encode()
    ).hexdigest()


def read(path):
    return json.loads(Path(path).read_text())


def write(path, value):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(path.name + ".partial")
    temporary.write_text(json.dumps(value, indent=2, sort_keys=True, allow_nan=False) + "\n")
    os.replace(temporary, path)


def load(name, path, expected):
    if sha(path) != expected:
        raise ValueError("qualified source changed: " + str(path))
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def recipe():
    return read(ROOT / "RECIPE.json")


def verify():
    ready = read(ROOT / "READY.json")
    if digest({k: v for k, v in ready.items() if k != "identity"}) != ready["identity"]:
        raise ValueError("READY identity changed")
    for field in ("source_sha256", "input_sha256"):
        for path, expected in ready[field].items():
            if sha(path) != expected:
                raise ValueError("frozen closure changed: " + path)
    if sha(START / "adapter_model.safetensors") != C32_SHA:
        raise ValueError("c32 start changed")
    return ready
