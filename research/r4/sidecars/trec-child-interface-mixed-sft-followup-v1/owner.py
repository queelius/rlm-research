"""MAIN-only bounded owner: one mixed training, then one dual-LoRA readout service."""

import argparse
import functools
import os
import signal
import subprocess
import time
from pathlib import Path

import collect
import study as s


@functools.lru_cache(maxsize=1)
def suite():
    """Return the query study's qualified wrapper/lifecycle dependency chain."""
    return collect.QSTUDY.dependencies()


class MainTermination(BaseException):
    pass


def model(alias, path):
    return {
        "path": str(path),
        "adapter_sha256": s.sha(path / "adapter_model.safetensors"),
        "config_sha256": s.sha(path / "adapter_config.json"),
    }


def run_training(output, deadline):
    command = [
        str(s.TRAIN_PYTHON),
        str(s.ROOT / "train.py"),
        "run",
        "--output",
        str(output),
        "--deadline",
        str(deadline),
    ]
    s.write(
        output.parent / "TRAIN_COMMAND.json",
        {"argv": command, "deadline": deadline, "gpu": os.environ["CUDA_VISIBLE_DEVICES"]},
    )
    with (output.parent / "training.log").open("x") as log:
        process = subprocess.Popen(
            command,
            stdout=log,
            stderr=subprocess.STDOUT,
            env={**os.environ, "PYTHONDONTWRITEBYTECODE": "1"},
            start_new_session=True,
        )
    lifecycle = suite()
    observation = lifecycle.life.observe(process.pid)
    if (
        observation is None
        or observation["pgid"] != process.pid
        or observation["uid"] != os.getuid()
    ):
        raise ValueError("cannot authenticate training process")
    try:
        while process.poll() is None:
            if time.time() >= deadline:
                raise TimeoutError("training stage cap")
            time.sleep(0.5)
        if process.returncode:
            raise RuntimeError(f"training exited {process.returncode}; retained log")
    finally:
        try:
            lifecycle.stop_child(process, lifecycle.life.safe_observation(observation))
        finally:
            s.write(
                output.parent / "TRAIN_EXIT.json",
                {"returncode": process.returncode, "ended_epoch": time.time()},
            )


def collect_command(stage, output, deadline, policies):
    argv = [
        str(s.NATIVE_PYTHON),
        str(s.ROOT / "collect.py"),
        "--endpoint",
        str(stage / "service/endpoint-original.json"),
        "--output",
        str(output),
        "--deadline",
        str(deadline),
        "--policies",
        ",".join(policies),
    ]
    suite().command(
        stage, "collect-" + "-".join(policies), argv, max(0.001, deadline - time.time()), deadline
    )


def binding(output, aliases):
    training = output / "training"
    paths = {
        "c32": s.START,
        "mixed_sft24": training / "mixed/checkpoint-0024",
    }
    models = {s.ALIASES[name]: model(s.ALIASES[name], paths[name]) for name in aliases}
    decision = output / ("BINDING_" + "_".join(aliases) + ".json")
    selections = {
        name: s.read(paths[name].parent / "SELECTION.json")
        if name != "c32"
        else {"rule": "unchanged authenticated c32", "step": 128}
        for name in aliases
    }
    s.write(
        decision,
        {
        "schema": "trec-child-interface-mixed-fixed-binding-v1",
            "models": models,
            "selections": selections,
            "outcomes_consulted": False,
        },
    )
    result = suite().final_binding(models, decision)
    result["selection_semantics"] = (
        "fixed true completed update24 for the mixed continuation adapter; "
        "unchanged c32 baseline; no validation or outcome selection"
    )
    return result


def execute(output):
    output = Path(output)
    started = time.time()
    owned = started + 3600
    work = owned - 300
    if output.resolve() != s.ATTEMPT.resolve() or output.exists():
        raise ValueError("exact unused attempt required")
    ready = s.verify()
    if not os.environ.get("CUDA_VISIBLE_DEVICES") or "," in os.environ["CUDA_VISIBLE_DEVICES"]:
        raise ValueError("one MAIN-assigned GPU required")
    if not os.environ.get("STRICT_RLM_CALIBRATION_API_KEY"):
        raise ValueError("private existing credential required")
    output.mkdir(parents=True)
    s.write(
        output / "OWNER_RUN.json",
        {
            "identity": ready["identity"],
            "started_epoch": started,
            "work_deadline": work,
            "owned_deadline": owned,
            "hard_cap_seconds": 3600,
            "training_setup_cap_seconds": 900,
            "readout_cap_seconds": 2400,
            "cleanup_recovery_seconds": 300,
            "gpu": os.environ["CUDA_VISIBLE_DEVICES"],
        },
    )
    handlers = {}
    active = []
    errors = []

    def expired(sig, _frame):
        if sig in (signal.SIGINT, signal.SIGTERM):
            raise MainTermination("MAIN cancellation")
        raise TimeoutError("study hard cap")

    for sig in (signal.SIGINT, signal.SIGTERM, signal.SIGALRM):
        handlers[sig] = signal.signal(sig, expired)
    signal.setitimer(signal.ITIMER_REAL, max(0.001, owned - time.time()))
    try:
        run_training(output / "training", min(work, time.time() + 900))
        stages = [("mixed-readout", ("c32", "mixed_sft24"), ("mixed_sft24",), 2400)]
        for name, aliases, policies, cap in stages:
            stage = output / name
            stage.mkdir()
            active.append(stage)
            stage_deadline = min(work, time.time() + cap)
            suite().start_service(
                stage, binding(output, aliases), min(stage_deadline, time.time() + 600)
            )
            collect_command(stage, output / "rollout" / name, stage_deadline, policies)
            suite().release_service(stage)
            active.remove(stage)
    except BaseException as error:
        errors.append({"type": type(error).__name__, "message": str(error)})
    finally:
        for stage in list(reversed(active)):
            try:
                suite().release_service(stage)
                active.remove(stage)
            except BaseException as error:
                errors.append(
                    {"stage": str(stage), "type": type(error).__name__, "message": str(error)}
                )
        plan = s.read(s.PREPARED / "EVAL_PLAN.json")
        combined = []
        for name, policies in (("mixed-readout", {"mixed_sft24"}),):
            subset = [row for row in plan if row["model_policy"] in policies]
            combined.extend(collect.harvest(output / "rollout" / name, subset)["rows"])
        summary = collect.summarize(combined)
        s.write(output / "SUMMARY.json", summary)
        terminal = {
            "identity": ready["identity"],
            "complete": not errors and len(combined) == 192,
            "released": not active,
            "active_unreleased_services": [str(path) for path in active],
            "error": errors or None,
            "planned": 192,
            "inventory": combined,
            "training_complete": (output / "training/RESULT.json").exists(),
            "fixed_last_required": 24,
            "elapsed_seconds": time.time() - started,
            "ended_epoch": time.time(),
            "no_retry": True,
        }
        s.write(output / "OWNER_TERMINAL.json", terminal)
        signal.setitimer(signal.ITIMER_REAL, 0)
        for sig, handler in handlers.items():
            signal.signal(sig, handler)
    return terminal


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("command", choices=("verify", "run"))
    parser.add_argument("--output", type=Path, default=s.ATTEMPT)
    args = parser.parse_args()
    if args.command == "verify":
        print(s.verify()["identity"])
    else:
        result = execute(args.output)
        print({"complete": result["complete"], "released": result["released"]})
        raise SystemExit(0 if result["complete"] else 1)
