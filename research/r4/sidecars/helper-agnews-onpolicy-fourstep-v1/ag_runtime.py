"""AG-specific inventory and reward seam over the proven true-HF implementation."""

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parent
AG_VALUES = ("World", "Sports", "Business", "Sci/Tech")
GROUPS = 32


def local_reward(content: str, record_id: str, gold: str, terminated: bool) -> float:
    if not terminated:
        return 0.0
    try:
        value = json.loads(content)
    except (TypeError, json.JSONDecodeError):
        return 0.0
    if (
        not isinstance(value, dict)
        or list(value) != [record_id]
        or value[record_id] not in AG_VALUES
    ):
        return 0.0
    return float(value[record_id] == gold)


def load_training_inputs():
    steps = json.loads((ROOT / "inputs/STEP_GROUPS.json").read_text())
    if len(steps) != 4 or any(len(step) != GROUPS for step in steps):
        raise ValueError("four exact balanced32 steps required")
    ids = [row["group_id"] for step in steps for row in step]
    if len(ids) != 128 or len(set(ids)) != 128:
        raise ValueError("training group IDs are not unique")
    return steps
