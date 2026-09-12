"""Thin exact 24-episode facade over the admitted MRCR root HF trainer."""

import functools
import hashlib
from pathlib import Path
from types import ModuleType


ROOT = Path(__file__).resolve().parent
SOURCE = ROOT.parent / "mrcr-root-hf-one-update-preflight-v1/train.py"
SOURCE_SHA = "42d32e58ec36a147234c7b03b207730b14e5ee38576ee26e85d43c01e6d64c20"


def replace_once(text, before, after):
    if text.count(before) != 1:
        raise ValueError("admitted trainer transform boundary changed: " + before)
    return text.replace(before, after)


def source_text():
    raw = SOURCE.read_bytes()
    if hashlib.sha256(raw).hexdigest() != SOURCE_SHA:
        raise ValueError("admitted MRCR root trainer changed")
    text = raw.decode()
    changes = (
        ('data.get("schema") != "mrcr-v6-root-hf-training-inputs-v1" or len(episodes) != 32',
         'data.get("schema") != "mrcr-short-shaped-root-hf-training-inputs-v1" or len(episodes) != 24'),
        ('raise ValueError("exact V6 32-episode input inventory required")',
         'raise ValueError("exact shaped 24-episode input inventory required")'),
        ('if len(set(groups)) != 8:', 'if len(set(groups)) != 6:'),
        ('raise ValueError("exact eight MRCR questions required")',
         'raise ValueError("exact six complete MRCR groups required")'),
        (' / 32', ' / 24'),
        ('"all32_passed":', '"all24_passed":'),
        ('len(replay_rows) == 32', 'len(replay_rows) == 24'),
        ('replay["all32_passed"]', 'replay["all24_passed"]'),
        ('"episodes": 32, "groups": 8', '"episodes": 24, "groups": 6'),
        ('sequence-SUM/32', 'sequence-SUM/24'),
        ('data["source"]["ready_v6_sha256"]',
         'data["source"]["short32_ready_v2_sha256"]'),
        ('SEED = 202609121701', 'SEED = 202609131900'),
        ('RUN_READY_V6_GATE_PASSED', 'RUN_READY_SHAPED24_GATE_PASSED'),
        ('mrcr-root-hf-one-update-checkpoint-v1',
         'mrcr-short-shaped-root-hf-one-update-checkpoint-v1'),
        ('mrcr-root-hf-step-commit-v1', 'mrcr-short-shaped-root-hf-step-commit-v1'),
        ('"source_v6_ready_sha256":', '"source_short32_ready_v2_sha256":'),
    )
    for before, after in changes:
        text = replace_once(text, before, after)
    return text


@functools.lru_cache(maxsize=1)
def module():
    value = ModuleType("mrcr_short_shaped_root_trainer")
    value.__file__ = str(ROOT / "train.py")
    exec(compile(source_text(), str(SOURCE) + ":shaped24", "exec"), value.__dict__)
    return value


def streamed_objective(root_turn_logprobs, advantages, ratios):
    """Same streamed episode/turn SUM divided once by the fixed 24 episodes."""
    terms = []
    for index, turns in enumerate(root_turn_logprobs):
        for values in turns:
            terms.append(-(ratios[index].detach() * advantages[index] * values.sum()) / 24)
    return sum(terms)
