"""MAIN-only exact train+metadata72 completion; never recaptures teachers."""
import argparse
import os
from pathlib import Path
import signal
import time
import traceback

import recovery as r


def alarm(deadline):
    signal.setitimer(signal.ITIMER_REAL, max(0.001, deadline - time.time()))


def problem(error):
    return {"type": type(error).__name__, "message": str(error),
            "traceback": traceback.format_exc()}


def inventory(output):
    return [{"coordinate": row, "path": str(output / "new_corpus_sft6/free" / row["id"] / "RESULT.json"),
             "recorded": False, "available": False, "reward": None,
             "cause": "not_started_no_artifacts"}
            for row in r.s.read(r.s.METADATA / "inputs/FREE_PLAN.json")]


def physical_ledger(output):
    paths = sorted((output / "new_corpus_sft6/free").glob("*/physical/*.json"))
    rows = [r.s.read(path) for path in paths]
    attempted = [row for row in rows if row.get("physical_request_attempt")]
    usage = {key: {"known": 0, "sum": 0} for key in ("prompt_tokens", "completion_tokens")}
    for row in attempted:
        value = row.get("response", {}).get("usage") if isinstance(row.get("response"), dict) else None
        for key in usage:
            if isinstance(value, dict) and isinstance(value.get(key), int):
                usage[key]["known"] += 1
                usage[key]["sum"] += value[key]
    for key in usage:
        usage[key]["unknown"] = len(attempted) - usage[key]["known"]
    return {"transport_records": len(rows), "physical_requests_attempted": len(attempted),
            "choice_bearing_responses": sum(bool(row.get("response", {}).get("choices"))
                for row in attempted if isinstance(row.get("response"), dict)),
            "usage": usage, "files_sha256": {str(path): r.s.sha(path) for path in paths},
            "source_capture_reused": r.source_corpus_receipt(), "capture_repeated": False,
            "baseline_repeated": False, "billing": "unknown/not measured"}


def execute(output, now=time.time):
    output = Path(output)
    started = now()
    work, owned = started + r.BUDGET["work"], started + r.BUDGET["owned"]
    if output.resolve() != r.ATTEMPT.resolve() and now is time.time:
        raise ValueError("exact owned recovery namespace")
    if output.exists():
        raise FileExistsError("recovery attempt exists; no overwrite")
    ready = r.verify()
    gpu = os.environ.get("CUDA_VISIBLE_DEVICES", "")
    if not gpu or "," in gpu or not os.environ.get("STRICT_RLM_CALIBRATION_API_KEY"):
        raise ValueError("one MAIN GPU and private credential required")
    suite = r.dependencies()
    output.mkdir(parents=True)
    rows = inventory(output)
    r.s.write(output / "PLANNED_NULL_ENDPOINTS.json", rows)
    r.s.write(output / "OWNER_RUN.json", {"identity": ready["identity"], "started_epoch": started,
        "budget": r.BUDGET, "source_failure": "CPU-only inherited command hid assigned CUDA",
        "source_attempt": str(r.SOURCE_ATTEMPT), "capture_rerun": False,
        "fresh_adam_zero": True, "planned_updates": 6, "planned_readout": 72,
        "baseline_reused_not_rerun": True, "original_qs6_reused_not_rerun": True})
    active = None
    errors = []
    stages = []
    training_complete = False

    class MainTermination(BaseException):
        pass
    def expired(sig, _frame):
        if sig in (signal.SIGINT, signal.SIGTERM):
            raise MainTermination("MAIN termination")
        raise TimeoutError("completion deadline")
    previous = {sig: signal.signal(sig, expired) for sig in (signal.SIGINT, signal.SIGTERM, signal.SIGALRM)}
    alarm(owned)
    try:
        deadline = min(now() + r.BUDGET["training"], work - r.BUDGET["readout"] - r.BUDGET["finalize"])
        status = {"stage": "training", "started_epoch": now(), "deadline_epoch": deadline}
        try:
            alarm(deadline)
            r.gpu_command(suite, output / "training-stage", r.training_argv(output, deadline), deadline)
            r.selected()
            training_complete = True
            status["work_complete"] = True
        except BaseException as error:
            status["error"] = problem(error)
            errors.append({"stage": "training", **status["error"]})
        finally:
            status["ended_epoch"] = now()
            stages.append(status)
            r.s.write(output / "TRAINING_TERMINAL.json", status)
            alarm(owned)

        if training_complete:
            end = min(now() + r.BUDGET["readout"], work - r.BUDGET["finalize"])
            stage = output / "readout-service"
            stage.mkdir()
            active = stage
            status = {"stage": "metadata72", "started_epoch": now(), "deadline_epoch": end}
            try:
                startup = min(now() + 180, end - r.BUDGET["cleanup"])
                alarm(startup)
                suite.start_service(stage, r.binding_module().binding("new_corpus_sft6"), startup)
                collection = end - r.BUDGET["cleanup"]
                alarm(collection)
                argv = r.collector_argv(stage, output / "new_corpus_sft6/free", collection)
                suite.command(stage, "metadata72", argv, collection - now(), collection)
                status["work_complete"] = True
            except BaseException as error:
                status["error"] = problem(error)
                errors.append({"stage": "metadata72", **status["error"]})
            finally:
                alarm(min(owned, end, now() + r.BUDGET["cleanup"]))
                try:
                    suite.release_service(stage)
                    active = None
                except BaseException as error:
                    status["release_error"] = problem(error)
                    errors.append({"stage": "release", **status["release_error"]})
                status["ended_epoch"] = now()
                stages.append(status)
                r.s.write(output / "READOUT_TERMINAL.json", status)
                alarm(owned)
    finally:
        alarm(min(owned, now() + r.BUDGET["finalize"]))
        for row in rows:
            path = Path(row["path"])
            if path.exists():
                value = r.s.read(path)
                row.update(recorded=True, available=value["available"], reward=value["reward"],
                           result_sha256=r.s.sha(path), cause="native_final" if value["available"] else "observed_invalid")
            elif list(path.parent.glob("physical/*.json")) or (path.parent / "FAILURE.json").exists():
                row["cause"] = "attempted_unavailable_no_result"
            elif path.parent.exists():
                row["cause"] = "started_no_physical_receipt"
        r.s.write(output / "COST_LEDGER.json", physical_ledger(output))
        result = {"identity": ready["identity"], "complete": not errors and training_complete and all(x["recorded"] for x in rows),
            "errors": errors or None, "training_complete": training_complete, "optimizer_steps_required": 6,
            "readout_inventory": rows, "stages": stages, "released": active is None,
            "active_unreleased_service": str(active) if active else None, "elapsed_seconds": now() - started,
            "capture_rerun": False, "source_attempt_preserved": True}
        r.s.write(output / "OWNER_TERMINAL.json", result)
        signal.setitimer(signal.ITIMER_REAL, 0)
        for sig, handler in previous.items():
            signal.signal(sig, handler)
    return result


def parse_args(argv=None):
    parser = argparse.ArgumentParser()
    parser.add_argument("command", choices=("verify", "run"))
    parser.add_argument("--output", type=Path, default=r.ATTEMPT)
    return parser.parse_args(argv)


if __name__ == "__main__":
    args = parse_args()
    if args.command == "verify":
        print(r.verify()["identity"])
    else:
        value = execute(args.output)
        print({"complete": value["complete"], "elapsed_seconds": value["elapsed_seconds"]})
        raise SystemExit(0 if value["complete"] else 1)
