"""One bounded service owner for four ABBA recursion-headroom blocks."""

import argparse
import functools
import importlib
import os
from pathlib import Path
import signal
import sys
import time
import traceback

import collect
import score
import study


@functools.lru_cache(maxsize=1)
def dependencies():
    sys.path.insert(0, str(study.RECOVERY))
    local_study = sys.modules.pop("study")
    try:
        recovery_owner = importlib.import_module("owner_v7")
    finally:
        sys.modules["study"] = local_study
    recovery_owner.s.bind_runtime(recovery_owner.qualified)
    return recovery_owner.qualified.dependencies()


def request_count(output):
    return sum(1 for path in output.glob("blocks/*/collection/rollout/typed-audit/*-request.json"))


def execute(output, outer_seconds):
    started = time.time()
    output = Path(output)
    if outer_seconds != study.OUTER_SECONDS:
        raise ValueError("exact 1900-second external cap required")
    if output.resolve() != study.ATTEMPT.resolve() or output.exists():
        raise ValueError("exact unused attempt-001 required")
    gpu = os.environ.get("CUDA_VISIBLE_DEVICES", "")
    if not gpu or "," in gpu or not os.environ.get("STRICT_RLM_CALIBRATION_API_KEY"):
        raise ValueError("one exclusive GPU and private provider credential required")
    ready = study.verify()
    owned = started + study.OWNED_SECONDS
    work = owned - 120
    output.mkdir(parents=True)
    study.write(output / "OWNER_RUN.json", {
        "ready_identity": ready["identity"], "started_epoch": started,
        "outer_seconds": outer_seconds, "owned_seconds": study.OWNED_SECONDS,
        "planned_episodes": 96, "blocks": list(study.BLOCK_MODES), "gpu": gpu,
        "physical_request_admission_stop_trigger": study.ADMISSION_TRIGGER,
        "trigger_is_not_hard_request_cap": True, "updates": 0,
    })
    service = output / "service"; service.mkdir()
    suite = None; active = True; errors = []; terminals = []; exported_rows = []

    def stop(_sig, _frame):
        raise TimeoutError("recursion-headroom ownership deadline")

    prior = {sig: signal.signal(sig, stop) for sig in (signal.SIGALRM, signal.SIGTERM, signal.SIGINT)}
    try:
        signal.setitimer(signal.ITIMER_REAL, max(0.001, owned - time.time()))
        suite = dependencies()
        suite.start_service(service, collect.binding(), min(started + 240, work - 120))
        for block_index, mode in enumerate(study.BLOCK_MODES):
            before = request_count(output)
            if before >= study.ADMISSION_TRIGGER:
                errors.append({"stage": "admission-stop", "block_index": block_index,
                               "physical_requests_before_block": before})
                break
            block_started = time.time()
            block = output / "blocks" / f"{block_index:02}-{mode}"
            block.mkdir(parents=True)
            plan = study.make_blocks()[block_index]
            study.write(block / "PLANNED_NULL_ENDPOINTS.json", [
                {"coordinate": row, "reward": None, "available": False,
                 "reason": "planned before service"} for row in plan])
            capture = block / "collection"; capture.mkdir()
            end = min(work, time.time() + 480)
            collect.prepare_spec(collect.phase(block_index, mode), service / "BINDING.json",
                service / "service/endpoint-original.json", capture / "CAPTURE_SPEC.json",
                max(0.001, end - time.time()), None)
            argv = [str(study.NATIVE), str(study.ROOT / "collect.py"), "--spec",
                    str(capture / "CAPTURE_SPEC.json"), "--output", str(capture / "rollout"),
                    "--deadline", str(float(end))]
            command_error = None
            try:
                suite.command(service, f"recursion-headroom-{block_index}-{mode}", argv,
                              max(0.001, end - time.time()), end)
            except Exception as error:
                command_error = {"type": type(error).__name__, "message": str(error)}
            manifest = None
            if (capture / "rollout/SPEC.json").exists():
                manifest = collect.export_attempt(capture / "rollout", capture / "export")
                rows = study.read(capture / "export/EPISODES.json")
                exported_rows.extend(rows)
            after = request_count(output)
            terminal = {"block_index": block_index, "mode": mode,
                "complete": command_error is None and manifest is not None and manifest["complete"]
                            and not manifest["integrity_failures"] and len(rows) == 24,
                "command_error": command_error, "physical_requests_before": before,
                "physical_requests_after": after, "physical_requests_in_block": after - before,
                "elapsed_seconds": time.time() - block_started,
                "export_complete": manifest["complete"] if manifest else False,
                "integrity_failures": manifest["integrity_failures"] if manifest else None}
            study.write(block / "BLOCK_TERMINAL.json", terminal); terminals.append(terminal)
            if not terminal["complete"]:
                errors.append({"stage": "block", "terminal": terminal}); break
        result = score.compute(exported_rows)
        result["physical_requests"] = request_count(output)
        result["admission_stop_trigger"] = study.ADMISSION_TRIGGER
        result["measured_trigger_overshoot"] = max(0, result["physical_requests"] - study.ADMISSION_TRIGGER)
        study.write(output / "RESULT.json", result)
    except BaseException as error:
        errors.append({"stage": "owner", "type": type(error).__name__, "message": str(error),
                       "traceback": traceback.format_exc()})
    finally:
        signal.setitimer(signal.ITIMER_REAL, max(0.001, min(owned, time.time() + 90) - time.time()))
        if suite is not None:
            try: suite.release_service(service); active = False
            except BaseException as error:
                errors.append({"stage": "release", "type": type(error).__name__, "message": str(error)})
        else: active = False
        complete = not errors and len(terminals) == 4 and all(item["complete"] for item in terminals)
        terminal = {"complete": complete, "released": not active, "errors": errors or None,
                    "block_terminals": terminals, "physical_requests": request_count(output),
                    "admission_stop_trigger": study.ADMISSION_TRIGGER,
                    "measured_trigger_overshoot": max(0, request_count(output) - study.ADMISSION_TRIGGER),
                    "elapsed_seconds": time.time() - started, "updates": 0}
        study.write(output / "OWNER_TERMINAL.json", terminal)
        signal.setitimer(signal.ITIMER_REAL, 0)
        for sig, handler in prior.items(): signal.signal(sig, handler)
    return terminal


if __name__ == "__main__":
    parser = argparse.ArgumentParser(); parser.add_argument("command", choices=("verify", "run"))
    parser.add_argument("--output", type=Path, default=study.ATTEMPT)
    parser.add_argument("--outer-seconds", type=int, default=study.OUTER_SECONDS)
    args = parser.parse_args()
    if args.command == "verify": print(study.verify()["identity"])
    else:
        result = execute(args.output, args.outer_seconds)
        print(result); raise SystemExit(0 if result["complete"] else 1)
