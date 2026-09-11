"""Own the four fixed checkpoint readout stages."""
import argparse
import functools
import json
import os
from pathlib import Path
import signal
import time
import traceback

import id_study as s


class MainTermination(BaseException):
    pass


@functools.lru_cache(maxsize=1)
def dependencies():
    return s.base.dose.dependencies()


def budget(started):
    return {"started": started, "work": started + 3150, "owned": started + 3270,
            "outer": started + 3300, "phase_ends": [started + 750 * index for index in range(1, 5)],
            "harvest_seconds": 150}


def stage_caps():
    return {"startup": 180, "probe": 60, "free": 480, "cleanup_reserve": 30}


def classify_slot(path):
    path = Path(path); result = path / "RESULT.json"
    if result.exists(): return "native_final" if json.loads(result.read_text())["available"] else "attempted_no_native_final"
    if list((path / "physical").glob("*.json")) or (path / "FAILURE.json").exists(): return "attempted_failure_no_result"
    return "unstarted"


def collector_argv(policy, stage, destination, deadline):
    return [str(s.NATIVE), str(s.ROOT / "id_collect.py"), "--plan", f"FREE_PLAN_{policy}.json",
            "--start", "0", "--stop", "16", "--binding", str(stage / "BINDING.json"),
            "--endpoint", str(stage / "service/endpoint-original.json"), "--output", str(destination),
            "--deadline", str(float(deadline))]


def probe_argv(stage, destination, deadline):
    return [str(s.NATIVE), str(s.ROOT / "id_probe.py"), "--binding", str(stage / "BINDING.json"),
            "--endpoint", str(stage / "service/endpoint-original.json"), "--output", str(destination),
            "--deadline", str(float(deadline))]


def training_receipt():
    terminal = s.base.dose.ATTEMPT / "OWNER_TERMINAL.json"
    owner = s.read(terminal)
    if not owner["complete"] or not owner["released"]:
        raise ValueError("fixed24 training lineage must be complete and released")
    return {
        "training_owner_terminal": str(terminal),
        "training_owner_terminal_sha256": s.sha(terminal),
        "checkpoints": {policy: s.selected(policy) for policy in ("sft6", "sft12", "sft18", "sft24")},
        "no_performance_selection": True,
    }


def ledger(output):
    output = Path(output)
    episode_paths = sorted({path.parent for path in output.glob("*/free/*/RESULT.json")})
    episode_paths += sorted({path.parent for path in output.glob("*/free/*/FAILURE.json")
                             if path.parent not in episode_paths})
    counts = {name: 0 for name in ("native_final", "attempted_no_native_final",
                                   "attempted_failure_no_result", "unstarted")}
    for path in episode_paths:
        counts[classify_slot(path)] += 1
    physical = sorted(output.glob("*/free/*/physical/*.json"))
    return {
        "slot_taxonomy": counts,
        "physical_requests": sum(bool(s.read(path).get("physical_request_attempt")) for path in physical),
        "physical_record_sha256": {str(path): s.sha(path) for path in physical},
        "billing": "not measured; local physical requests only",
    }


def check_output(output):
    if Path(output).resolve() != s.ATTEMPT.resolve():
        raise ValueError("exact immutable attempt-001 namespace only")
    if Path(output).exists():
        raise FileExistsError("no retry or overwrite")


def remaining(deadline, cap):
    value = min(cap, deadline - time.time())
    if value <= 0:
        raise TimeoutError("fixed stage deadline")
    return value


def _inventory(output, rows, kind):
    items = []
    for item in rows:
        row = item["coordinate"]
        directory = Path(output) / item["policy"] / kind / row["id"]
        taxonomy = classify_slot(directory)
        value = {**item, "taxonomy": taxonomy, "available": False}
        result = directory / "RESULT.json"
        if result.exists():
            record = s.read(result)
            value.update(available=bool(record.get("available")), result_path=str(result),
                         result_sha256=s.sha(result))
            if "reward" in record:
                value["reward"] = record["reward"]
        items.append(value)
    return items


def execute(output):
    started = time.time()
    limits = budget(started)
    check_output(output)
    ready = s.verify()
    s.runtime()
    receipt = training_receipt()
    gpu = os.environ.get("CUDA_VISIBLE_DEVICES", "")
    if not gpu or "," in gpu:
        raise ValueError("MAIN must assign exactly one GPU")
    suite = dependencies()
    output = Path(output)
    output.mkdir(parents=True, exist_ok=False)
    plan = s.read(s.ROOT / "inputs/EVALUATION_PLAN.json")
    s.write(output / "PLANNED_EVALUATION.json", plan)
    s.write(output / "TRAINING_ARTIFACT_RECEIPT.json", receipt)
    s.write(output / "OWNER_RUN.json", {
        "identity": ready["identity"], "started_epoch": started, **limits,
        "policy_order": plan["policy_order"], "gpu": gpu, "no_training": True,
        "stage_caps_seconds": stage_caps(),
    })

    def expire(sig, _frame):
        if sig in (signal.SIGINT, signal.SIGTERM):
            raise MainTermination("MAIN termination")
        raise TimeoutError("owned deadline")

    handlers = {sig: signal.signal(sig, expire)
                for sig in (signal.SIGINT, signal.SIGTERM, signal.SIGALRM)}
    signal.setitimer(signal.ITIMER_REAL, max(.001, limits["owned"] - time.time()))
    errors, stages, active = [], [], None
    halt = False
    try:
        for index, policy in enumerate(plan["policy_order"]):
            if halt:
                break
            stage_end = limits["phase_ends"][index]
            stage = output / f"service-{policy}"
            stage.mkdir()
            active = stage
            status = {"policy": policy, "started_epoch": time.time(), "deadline_epoch": stage_end}
            try:
                startup_end = min(stage_end - 570, time.time() + 180)
                signal.setitimer(signal.ITIMER_REAL, remaining(startup_end, 180))
                suite.start_service(stage, s.binding(policy), startup_end)
                probe_end = min(stage_end - 510, time.time() + 60)
                signal.setitimer(signal.ITIMER_REAL, remaining(probe_end, 60))
                try:
                    suite.command(stage, "first-action12",
                                  probe_argv(stage, output / policy / "probes", probe_end),
                                  remaining(probe_end, 60), probe_end)
                except Exception as error:
                    status["probe_error"] = {"type": type(error).__name__, "message": str(error)}
                    errors.append({"policy": policy, "stage": "probe", **status["probe_error"]})
                free_end = min(stage_end - 30, time.time() + 480)
                signal.setitimer(signal.ITIMER_REAL, remaining(free_end, 480))
                suite.command(stage, "free16", collector_argv(policy, stage,
                              output / policy / "free", free_end),
                              remaining(free_end, 480), free_end)
                status["work_complete"] = True
            except BaseException as error:
                status["error"] = {"type": type(error).__name__, "message": str(error),
                                   "traceback": traceback.format_exc()}
                errors.append({"policy": policy, **status["error"]})
                if not isinstance(error, Exception):
                    halt = True
            finally:
                cleanup_end = min(limits["owned"], stage_end)
                signal.setitimer(signal.ITIMER_REAL, max(.001, cleanup_end - time.time()))
                try:
                    suite.release_service(stage)
                    active = None
                except BaseException as error:
                    status["release_error"] = {"type": type(error).__name__, "message": str(error)}
                    errors.append({"policy": policy, "stage": "release", **status["release_error"]})
                    halt = True
                status["ended_epoch"] = time.time()
                stages.append(status)
                s.write(stage / "PHASE_TERMINAL.json", status)
                signal.setitimer(signal.ITIMER_REAL, max(.001, limits["owned"] - time.time()))
    finally:
        full = _inventory(output, plan["full"], "free")
        probes = _inventory(output, plan["first_action"], "probes")
        result = {
            "identity": ready["identity"], "complete": not errors and len(stages) == 4,
            "error": errors or None, "stages": stages, "readout_inventory": full,
            "first_action_inventory": probes, "planned_full": 64, "planned_first_action": 48,
            "released": active is None, "active_unreleased_service": str(active) if active else None,
            "elapsed_seconds": time.time() - started, "all_ordinary_failed_stages_still_attempted": True,
            "native_availability_not_implied_by_owner_completion": True,
        }
        s.write(output / "COST_LEDGER.json", ledger(output))
        s.write(output / "OWNER_TERMINAL.json", result)
        signal.setitimer(signal.ITIMER_REAL, 0)
        for sig, handler in handlers.items():
            signal.signal(sig, handler)
    return result


def parse_args(argv=None):
    parser = argparse.ArgumentParser()
    parser.add_argument("command", choices=("verify", "run"))
    parser.add_argument("--output", type=Path, default=s.ATTEMPT)
    return parser.parse_args(argv)


if __name__ == "__main__":
    args = parse_args()
    if args.command == "verify":
        print(s.verify()["identity"])
    else:
        outcome = execute(args.output)
        print({"complete": outcome["complete"], "errors": outcome["error"],
               "elapsed_seconds": outcome["elapsed_seconds"]})
        raise SystemExit(0 if outcome["complete"] else 1)
