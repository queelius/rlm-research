"""5400s owner: missing7 capture, unchanged six updates, recovered fixed6 readout."""
import argparse
import functools
import os
from pathlib import Path
import signal
import time
import traceback
import recovery_study as s
import recovery_binding as b


class MainTermination(BaseException): pass


@functools.lru_cache(maxsize=1)
def dependencies():
    import qs_owner
    return qs_owner.dependencies()


def remaining(deadline):
    value = deadline - time.time()
    if value <= 0: raise TimeoutError("recovery shared/stage cap")
    return value


def alarm(deadline): signal.setitimer(signal.ITIMER_REAL, max(.001, deadline - time.time()))


def error(caught):
    return {"type": type(caught).__name__, "message": str(caught), "traceback": traceback.format_exc()}


def inventory(output):
    plan = s.read(s.ORIGINAL / "inputs/EVALUATION_PLAN.json")["full"]
    return [{**row, "path": str(output / "sft6" / ("dev" if row["panel"] == "dev" else "free") /
                                      row["coordinate"]["id"] / "RESULT.json"),
             "recorded": False, "available": False, "reward": None,
             "cause": "not_started_no_artifacts"}
            for row in plan if row["policy"] == "sft6"]


def harvest(output, rows):
    for row in rows:
        path = Path(row["path"]); directory = path.parent
        if path.exists():
            value = s.read(path); row.update(recorded=True, available=value["available"],
                reward=value["reward"], result_sha256=s.sha(path),
                cause="native_final" if value["available"] else "attempted_native_no_final")
        elif (directory / "FAILURE.json").exists() or list((directory / "physical").glob("*.json")):
            row["cause"] = "attempted_unavailable_no_result"
        elif directory.exists(): row["cause"] = "started_no_physical_receipt"
    return rows


def cost_ledger(output):
    groups = {
        "original_partial_capture": sorted((s.ORIGINAL_ATTEMPT / "capture").glob("*/physical/*.json")),
        "original_unchanged_baseline": sorted((s.ORIGINAL_ATTEMPT / "unchanged").glob("*/*/physical/*.json")),
        "recovery_missing_capture": sorted((output / "capture").glob("*/physical/*.json")),
        "recovery_sft6_readout": sorted((output / "sft6").glob("*/*/physical/*.json")),
    }
    def tally(paths):
        rows = [s.read(p) for p in paths]; actual = [r for r in rows if r.get("physical_request_attempt")]
        responses = [r for r in actual if isinstance(r.get("response"), dict)]
        choices = [r for r in responses if r["response"].get("choices")]
        usage = {"prompt_tokens": 0, "completion_tokens": 0, "unknown_records": 0}
        for row in actual:
            value = row.get("response", {}).get("usage") if isinstance(row.get("response"), dict) else None
            if not isinstance(value, dict): usage["unknown_records"] += 1
            else:
                usage["prompt_tokens"] += int(value.get("prompt_tokens", 0))
                usage["completion_tokens"] += int(value.get("completion_tokens", 0))
        return {"all_transport_records": len(rows), "physical_requests_attempted": len(actual),
                "http_responses_returned": sum(isinstance(r.get("response"), dict) or isinstance(r.get("status"), int) for r in actual),
                "choice_bearing_completions": len(choices), "usage": usage,
                "files_sha256": {str(p): s.sha(p) for p in paths}}
    return {"by_stage": {name: tally(paths) for name, paths in groups.items()},
            "original_partial_failure_charged": True, "baseline_not_rerun": True,
            "authored_transport_is_not_model_generation": True, "billing": "unknown/not measured"}


def _command_argv(entry, output, deadline, extra):
    return [str(s.NATIVE), str(s.SOURCE_ROOT / entry), *extra, "--output", str(output),
            "--deadline", str(float(deadline))]


def capture_binding():
    import qs_binding
    return qs_binding.binding("unchanged")


def execute(output):
    started = time.time(); work = started + 5220; owned = started + 5370
    if output.resolve() != s.ATTEMPT.resolve() or output.exists():
        raise ValueError("exact unused recovery attempt")
    s.runtime(); ready = s.verify(); baseline = s.baseline_reference()
    gpu = os.environ.get("CUDA_VISIBLE_DEVICES", "")
    if not gpu or "," in gpu or not os.environ.get("STRICT_RLM_CALIBRATION_API_KEY"):
        raise ValueError("one MAIN GPU/private credential preflight")
    output.mkdir(parents=True); s.write(output / "BASELINE_REFERENCE.json", baseline)
    boundary = s.capture_boundary(); s.write(output / "CAPTURE_BOUNDARY.json", boundary)
    planned = inventory(output); s.write(output / "PLANNED_EVALUATION.json", planned)
    s.write(output / "OWNER_RUN.json", {"identity": ready["identity"], "started_epoch": started,
        "outer_seconds": 5400, "owned_seconds": 5370, "work_seconds": 5220,
        "caps": {"capture": 600, "training": 2100, "sft6": 2100, "finalize": 420},
        "original_attempt_charged_separately": True, "original_baseline_reused_not_rerun": True,
        "capture_serial_missing_only": 7, "fresh_optimizer": True, "updates": 6})
    suite = dependencies(); active = None; errors = []; stages = []
    handlers = {}
    def expired(sig, frame):
        if sig in (signal.SIGINT, signal.SIGTERM): raise MainTermination("MAIN termination")
        raise TimeoutError("recovery active/shared cap")
    for sig in (signal.SIGINT, signal.SIGTERM, signal.SIGALRM):
        handlers[sig] = signal.signal(sig, expired)
    def service(name, binding, end, body):
        nonlocal active
        stage = output / name; stage.mkdir(); active = stage
        status = {"stage": name, "started_epoch": time.time(), "deadline_epoch": end}
        try:
            startup = min(time.time() + 180, end - 90); alarm(startup)
            suite.start_service(stage, binding, startup); body(stage, end - 90); status["work_complete"] = True
        except BaseException as caught:
            status["error"] = error(caught); errors.append({"stage": name, **status["error"]})
        finally:
            alarm(min(owned, end, time.time() + 90))
            try: suite.release_service(stage); active = None
            except BaseException as caught:
                status["release_error"] = error(caught); errors.append({"stage": name, **status["release_error"]})
            status["ended_epoch"] = time.time(); s.write(stage / "PHASE_TERMINAL.json", status); stages.append(status)
            alarm(owned)
        return status.get("work_complete", False) and active is None
    try:
        capture_end = min(time.time() + 600, work - 4620)
        def capture(stage, end):
            argv = _command_argv("recovery_collect.py", output / "capture", end, [
                "--binding", str(stage / "BINDING.json"), "--endpoint", str(stage / "service/endpoint-original.json")])
            alarm(end); suite.command(stage, "capture-missing7", argv, remaining(end), end)
            s.build_corpus_ready()
        if service("teacher-service", capture_binding(), capture_end, capture):
            train_end = min(time.time() + 2100, work - 2520)
            stage = output / "train-stage"; stage.mkdir(); status = {"stage": "training", "started_epoch": time.time(), "deadline_epoch": train_end}
            try:
                argv = [str(s.TRAIN), str(s.SOURCE_ROOT / "recovery_train.py"), "--mode", "train",
                        "--output", str(output / "training"), "--deadline", str(float(train_end))]
                alarm(train_end); suite.command(stage, "six-updates", argv, remaining(train_end), train_end)
                b.selected("sft6"); status["work_complete"] = True
            except BaseException as caught:
                status["error"] = error(caught); errors.append({"stage": "training", **status["error"]})
            finally:
                status["ended_epoch"] = time.time(); s.write(stage / "PHASE_TERMINAL.json", status); stages.append(status); alarm(owned)
            if status.get("work_complete"):
                read_end = min(time.time() + 2100, work - 420)
                def readout(stage, end):
                    dev_end = min(time.time() + 150, end)
                    common = ["--binding", str(stage / "BINDING.json"), "--endpoint", str(stage / "service/endpoint-original.json")]
                    argv = _command_argv("recovery_readout.py", output / "sft6/dev", dev_end,
                        ["--plan", "DEV_PLAN.json", "--stop", "8", *common])
                    alarm(dev_end); suite.command(stage, "dev8", argv, remaining(dev_end), dev_end)
                    protected_end = min(end, time.time() + 1860)
                    argv = _command_argv("recovery_readout.py", output / "sft6/free", protected_end,
                        ["--plan", "FREE_PLAN.json", "--stop", "72", *common])
                    alarm(protected_end); suite.command(stage, "protected72", argv, remaining(protected_end), protected_end)
                service("service-sft6", b.binding("sft6"), read_end, readout)
    finally:
        alarm(min(owned, time.time() + 420)); rows = harvest(output, planned)
        costs = cost_ledger(output); s.write(output / "COST_LEDGER.json", costs)
        result = {"identity": ready["identity"], "complete": not errors and all(r["recorded"] for r in rows),
            "error": errors or None, "capture_boundary": boundary, "baseline_reference": baseline,
            "readout_inventory": rows, "planned_readout": 80, "stages": stages,
            "released": active is None, "active_unreleased_service": str(active) if active else None,
            "elapsed_seconds": time.time() - started, "no_baseline_rerun": True}
        s.write(output / "OWNER_TERMINAL.json", result); signal.setitimer(signal.ITIMER_REAL, 0)
        for sig, handler in handlers.items(): signal.signal(sig, handler)
    return result


def parse_args():
    ap = argparse.ArgumentParser(); ap.add_argument("command", choices=("run", "verify"));
    ap.add_argument("--output", type=Path, default=s.ATTEMPT); return ap.parse_args()


if __name__ == "__main__":
    args = parse_args()
    if args.command == "verify": print(s.verify()["identity"])
    else:
        result = execute(args.output); print({"complete": result["complete"], "error": result["error"]})
        raise SystemExit(0 if result["complete"] else 1)
