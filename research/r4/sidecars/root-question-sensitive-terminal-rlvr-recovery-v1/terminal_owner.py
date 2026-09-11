"""MAIN-only bounded owner over the qualified lifecycle and trainer dispatcher."""
import os
from pathlib import Path
import sys
import types

import terminal_collect as collect
import terminal_common as common
import terminal_export as export
import terminal_native as native
import terminal_study as study


def budget(start):
    return {"started": start, "training_end": start + 4500, "work": start + 6900,
            "owned": start + 7170, "outer": start + 7200}


def trainer_output(stage):
    return Path(stage) / "training"


def planned_inventory(output):
    plans = study.read(study.ROOT / "inputs/PLANS.json")
    rows = []
    for window, coordinates in plans["training"].items():
        rows.extend({"phase": "training", "window": int(window), "coordinate": row,
                     "export": str(Path(output) / f"window-{int(window):02d}/collection/export/EPISODES.json"),
                     "reward": None, "available": False, "reason": "planned before service"}
                    for row in coordinates)
    for arm in ("start", "rl_last"):
        rows.extend({"phase": "readout", "arm": arm, "coordinate": row,
                     "export": str(Path(output) / f"readout-{arm}/export/EPISODES.json"),
                     "reward": None, "available": False, "reason": "planned before service"}
                    for row in plans["readout"])
    return rows


def cleanup_deadline(now, stage_end, owned):
    return min(now + 90, stage_end, owned)


def learning_window_allowed(cutoff, now=None):
    import time
    return cutoff - (time.time() if now is None else now) >= 600


def collector_argv(stage, deadline):
    return [str(study.NATIVE), str(study.ROOT / "terminal_collect.py"), "--spec",
            str(stage / "CAPTURE_SPEC.json"), "--output", str(stage / "rollout"),
            "--deadline", str(float(deadline))]


def trainer_argv(stage, deadline):
    return [str(study.TRAIN), str(study.ROOT / "terminal_train.py"), "--group",
            str(stage / "collection/export/GROUP.json"), "--generation",
            str(stage / "GENERATION.json"), "--output", str(trainer_output(stage)),
            "--deadline", str(float(deadline))]


def _interval(path, start_key="started_epoch", end_key="ended_epoch"):
    if not path.exists():
        return None
    value = study.read(path)
    start, end = value.get(start_key), value.get(end_key)
    if not isinstance(start, (int, float)) or not isinstance(end, (int, float)) or end < start:
        return None
    return end - start


def _timing_bucket(values):
    measured = [value for value in values if value is not None]
    return {"measured_stages": len(measured),
            "seconds": sum(measured) if measured else None}


def timing_summary(output):
    """Separate observed rollout capture time from optimizer subprocess time."""
    output = Path(output)
    captures = [_interval(output / f"window-{window:02d}/collection/rollout/STATUS.json")
                for window in range(1, 9)]
    optimizers = []
    for window in range(1, 9):
        stage = output / f"window-{window:02d}"
        command, exited = stage / "TRAIN_COMMAND.json", stage / "TRAIN_EXIT.json"
        if command.exists() and exited.exists():
            start = study.read(command).get("started_epoch")
            end = study.read(exited).get("ended_epoch")
            optimizers.append(end - start if isinstance(start, (int, float))
                              and isinstance(end, (int, float)) and end >= start else None)
    readouts = [_interval(output / f"readout-{arm}/rollout/STATUS.json")
                for arm in ("start", "rl_last")]
    return {"training_capture": _timing_bucket(captures),
            "optimizer": _timing_bucket(optimizers),
            "protected_readout_capture": _timing_bucket(readouts),
            "source": "native STATUS and TRAIN_COMMAND/TRAIN_EXIT epochs"}


SOURCE = study.WARM / "warm_owner.py"
PIN = "97875483cdfe1623259875cf47c944b9aadc72fe79281da3055efcfeb3f22e2c"
study.check(SOURCE, PIN)
text = SOURCE.read_text()
changes = {
    '"planned_final": 96': '"planned_final": 144',
    "generation, 600)": "generation, 360)",
    "time.time() + 2550": "time.time() + 1200",
    "remaining(block_end - 30, 2340)": "remaining(block_end - 30, 1050)",
    'policies = {"unchanged": initial, "trained": state["policy"]}':
        'policies = {"start": initial, "rl_last": state["policy"]}',
    'for arm in ("unchanged", "trained")': 'for arm in ("start", "rl_last")',
    'set(readouts) == {"unchanged", "trained"}': 'set(readouts) == {"start", "rl_last"}',
    '"elapsed_seconds": time.time() - started, "released": active is None,':
        '"elapsed_seconds": time.time() - started, "timing": timing_summary(output), '
        '"released": active is None,',
}
for before, after in changes.items():
    expected = 2 if before in ('"planned_final": 96',
                               'for arm in ("unchanged", "trained")') else 1
    if text.count(before) != expected:
        raise ValueError("qualified owner seam changed: " + before)
    text = text.replace(before, after)
qualified = types.ModuleType("terminal_qualified_warm_owner")
qualified.__file__ = str(SOURCE)
qualified.timing_summary = timing_summary
sys.modules[qualified.__name__] = qualified
with study.aliases({"warm_study": study, "warm_common": common, "warm_collect": collect,
                    "warm_export": export, "warm_native": native}):
    exec(compile(text, str(SOURCE) + ":terminal-budgets", "exec"), qualified.__dict__)


def check_output(output):
    output = Path(output)
    if output.resolve() != study.ATTEMPT.resolve():
        raise ValueError("exact additive attempt-002 namespace only")
    if output.exists():
        raise FileExistsError("attempt-002 retained; no implicit retry or overwrite")


qualified.budget = budget
qualified.cleanup_deadline = cleanup_deadline
qualified.learning_window_allowed = learning_window_allowed
qualified.collector_argv = collector_argv
qualified.trainer_argv = trainer_argv
qualified.planned_inventory = planned_inventory
qualified.check_output = check_output

dependencies = qualified.dependencies
remaining = qualified.remaining
alarm = qualified.alarm
collection_stage = qualified.collection_stage
train_window = qualified.train_window
recover_commit_on_stop = qualified.recover_commit_on_stop
cost_ledger = qualified.cost_ledger
execute = qualified.execute
parse_args = qualified.parse_args


if __name__ == "__main__":
    args = parse_args()
    if args.command == "verify":
        print(study.verify_prepared()["campaign_id"])
    else:
        result = execute(args.output)
        print({"complete": result["complete"], "step": result["selection"]["actual_optimizer_step"],
               "elapsed_seconds": result["elapsed_seconds"]})
        raise SystemExit(0 if result["complete"] else 1)
