"""Fixed entrypoint for the token-TIS two-independent-dose trainer."""

from __future__ import annotations

import argparse
import importlib.util
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parent


def _load(name):
    path = ROOT / f"{name}.py"
    spec = importlib.util.spec_from_file_location(f"token_tis_owner_{name}", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def plan():
    study = _load("study")
    return {
        "schema": "mrcr-short-root-token-tis-two-lr-plan-v1",
        "output": str(study.OUTPUT),
        "cap_seconds": study.CAP_SECONDS,
        "external_cap_seconds": study.EXTERNAL_CAP_SECONDS,
        "branches": [name for name, _ in study.BRANCHES],
        "learning_rates": [rate for _, rate in study.BRANCHES],
        "optimizer_steps_per_branch": 1,
        "same_initial_lora": True,
        "same_saved_gradient": True,
        "token_tis_cap": study.TOKEN_TIS_CAP,
        "fixed_denominator": study.DENOMINATOR,
        "new_generation_calls": 0,
        "heldout_queries": 0,
        "child_loss_tokens": 0,
        "selection": "both fixed branches retained; no best-checkpoint choice",
        "command": [
            str(study.PYTHON),
            str(ROOT / "owner.py"),
            "run",
            "--output",
            str(study.OUTPUT),
            "--cap-seconds",
            str(study.CAP_SECONDS),
        ],
    }


def run(output: Path, cap_seconds: int):
    trainer = _load("trainer")
    return trainer.run(output, cap_seconds)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("action", choices=["plan", "run"])
    parser.add_argument("--output", type=Path)
    parser.add_argument("--cap-seconds", type=int)
    args = parser.parse_args()
    if args.action == "plan":
        value = plan()
    else:
        if args.output is None or args.cap_seconds is None:
            parser.error("run requires --output and --cap-seconds")
        value = run(args.output, args.cap_seconds)
    print(json.dumps(value, indent=2, sort_keys=True))
