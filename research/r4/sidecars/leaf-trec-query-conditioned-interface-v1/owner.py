"""MAIN-only bounded owner for the 192-call query-conditioned study."""

import argparse
import os
from pathlib import Path
import signal
import time

import collect
import study as s


class MainTermination(BaseException):
    pass


def collector_argv(stage, output, deadline):
    return [str(s.NATIVE), str(s.ROOT / "collect.py"), "--endpoint", str(stage / "service/endpoint-original.json"), "--output", str(output), "--deadline", str(float(deadline))]


def execute(output):
    output = Path(output)
    started = time.time()
    work, owned = started + 1650, started + 1770
    if output.resolve() != s.ATTEMPT.resolve() or output.exists():
        raise ValueError("exact unused attempt required")
    ready = s.verify()
    gpu = os.environ.get("CUDA_VISIBLE_DEVICES", "")
    if not gpu or "," in gpu or not os.environ.get("STRICT_RLM_CALIBRATION_API_KEY"):
        raise ValueError("one MAIN GPU and private credential required")
    suite, plan = s.dependencies(), s.read(s.ROOT / "inputs/PLAN.json")
    output.mkdir(parents=True)
    stage = output / "owned-service"
    stage.mkdir()
    s.write(output / "PLANNED.json", plan)
    s.write(output / "OWNER_RUN.json", {"identity": ready["identity"], "started_epoch": started, "work_deadline": work, "owned_deadline": owned, "outer_seconds": 1800, "startup_cap": 180, "collector_harvest_reserve": 30, "release_cap": 90, "finalize_reserve": 30, "outer_margin": 30, "scientific_role": "trec_query_conditioned_child_interface", "credential_present": True, "gpu": gpu})

    def expired(sig, frame):
        if sig in (signal.SIGINT, signal.SIGTERM):
            raise MainTermination("MAIN cancellation")
        raise TimeoutError("bounded query-conditioned stage cap")

    handlers = {sig: signal.signal(sig, expired) for sig in (signal.SIGINT, signal.SIGTERM, signal.SIGALRM)}
    errors, active = [], True
    try:
        startup = min(work - 30, time.time() + 180)
        signal.setitimer(signal.ITIMER_REAL, max(0.001, startup - time.time()))
        suite.start_service(stage, s.binding(), startup)
        signal.setitimer(signal.ITIMER_REAL, max(0.001, work - time.time()))
        suite.command(stage, "trec-query-conditioned192", collector_argv(stage, output / "rollout", work), max(0.001, work - time.time()), work)
    except BaseException as error:
        errors.append({"stage": "work", "type": type(error).__name__, "message": str(error)})
    finally:
        release_started = time.time()
        signal.setitimer(signal.ITIMER_REAL, max(0.001, min(owned - 30, time.time() + 90) - time.time()))
        try:
            suite.release_service(stage)
            active = False
        except BaseException as error:
            errors.append({"stage": "release", "type": type(error).__name__, "message": str(error)})
        signal.setitimer(signal.ITIMER_REAL, max(0.001, owned - time.time()))
        ledger = collect.harvest(output / "rollout", plan)
        s.write(output / "COST_LEDGER.json", {key: value for key, value in ledger.items() if key != "rows"})
        s.write(output / "SUMMARY.json", collect.summarize(ledger["rows"]))
        result = {"identity": ready["identity"], "complete": not errors, "released": not active, "active_unreleased_service": str(stage) if active else None, "error": errors or None, "inventory": ledger["rows"], "planned": 192, "physical": ledger["cost"], "elapsed_seconds": time.time() - started, "release_started_epoch": release_started, "ended_epoch": time.time(), "root_model_calls": 0, "no_training": True, "no_retry": True}
        s.write(output / "OWNER_TERMINAL.json", result)
        signal.setitimer(signal.ITIMER_REAL, 0)
        for sig, handler in handlers.items():
            signal.signal(sig, handler)
    return result


def main():
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


if __name__ == "__main__":
    main()
