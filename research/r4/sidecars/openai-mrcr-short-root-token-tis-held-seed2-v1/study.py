"""Fresh paired seed-block facade over the qualified token-TIS held evaluator."""

from __future__ import annotations

import functools
import importlib.util
from pathlib import Path


ROOT = Path(__file__).resolve().parent
SIDE = ROOT.parent
QUALIFIED = SIDE / "openai-mrcr-short-root-token-tis-held-eval-v1"
SOURCE_EVAL = SIDE / "openai-mrcr-short-root-shaped-eval-v1"
READY = ROOT / "CPU_READY.json"
INPUTS = ROOT / "inputs"
OWNER_SECONDS = 650
SCIENCE_SECONDS = 500


def _load_base():
    path = SOURCE_EVAL / "study.py"
    spec = importlib.util.spec_from_file_location("token_tis_seed2_shaped_study", path)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


base = _load_base()
original_schedule = base.schedule
original_input_dir = base.input_dir
for _name in dir(base):
    if not _name.startswith("_"):
        globals()[_name] = getattr(base, _name)

# The inherited functions retain the base module as their global namespace, so
# bind every experiment-local path and callable there as well as in this facade.
ROOT = Path(__file__).resolve().parent
READY = ROOT / "CPU_READY.json"
INPUTS = ROOT / "inputs"
QUALIFIED = SIDE / "openai-mrcr-short-root-token-tis-held-eval-v1"
SOURCE_EVAL = SIDE / "openai-mrcr-short-root-shaped-eval-v1"
OWNER_SECONDS = 650
SCIENCE_SECONDS = 500


@functools.lru_cache(maxsize=1)
def schedule(phase: str):
    values = []
    for index, row in enumerate(records(phase)):
        coordinate = {
            "study": ROOT.name,
            "phase": phase,
            "record_id": row["id"],
            "source_row_sha256": row["source_row_sha256"],
            "ordered_core_sha256": row["ordered_core_sha256"],
            "context_sha256": row["prompt_json_sha256"],
            "row_index": index,
            "repeat": 0,
            "seed": 2026091900 + index,
            "temperature": 0.5,
        }
        values.append({**coordinate, "id": digest(coordinate)})
    return values


def input_dir(phase: str) -> Path:
    if phase != "held":
        raise ValueError("only held inputs exist")
    return INPUTS / phase


base.ROOT = ROOT
base.READY = READY
base.INPUTS = INPUTS
base.schedule = schedule
base.input_dir = input_dir

prepare_inputs = base.prepare_inputs
environment_config = base.environment_config
environment = base.environment
official_grade = base.official_grade
dependencies = base.dependencies
load = base.load
source = base.source


def verify_frozen_inputs():
    qualified_ready_path = QUALIFIED / "CPU_READY_V4.json"
    qualified_ready = read(qualified_ready_path)
    for raw, expected in qualified_ready["closure_sha256"].items():
        if sha(Path(raw)) != expected:
            raise ValueError("qualified V4 closure changed: " + raw)
    old = _load_base()
    new_schedule = schedule("held")
    old_schedule = old.schedule("held")
    if len(new_schedule) != 16 or len(old_schedule) != 16:
        raise ValueError("held16 inventory changed")
    if [row["seed"] for row in new_schedule] != list(range(2026091900, 2026091916)):
        raise ValueError("seed2 block changed")
    if [row["record_id"] for row in new_schedule] != [row["record_id"] for row in old_schedule]:
        raise ValueError("held record order changed")
    return qualified_ready
