"""Own one64-call native service; reuse sealed wire/token validation only."""

import argparse
import json
import os
import signal
import time

import companion_study as study
from companion_metrics import summarize


def execute(cap):
    ready = study.verify()
    if cap != study.CAP or study.ATTEMPT.exists():
        raise ValueError("unused attempt001 and exact900-second cap required")
    gpu = os.environ.get("CUDA_VISIBLE_DEVICES", "")
    if not gpu or "," in gpu or not os.environ.get("STRICT_RLM_CALIBRATION_API_KEY"):
        raise ValueError("MAIN must assign one GPU and inherited private credential")
    started, calls, errors, suite, released = time.time(), [], [], None, False
    deadline = started + cap - 90
    rows, gold = study.schedule(), study.source().panel()[3]
    study.ATTEMPT.mkdir(parents=True)
    service = study.ATTEMPT / "service"
    service.mkdir()
    study.write(
        study.ATTEMPT / "OWNER_RUN.json",
        {
            "ready_identity": ready["identity"],
            "ready_sha256": study.sha(study.ROOT / "READY.json"),
            "started_epoch": started,
            "planned_calls": 64,
            "physical_prediction_slots": 1024,
            "unique_records": 256,
            "cap_seconds": cap,
            "root_calls": 0,
            "training_updates": 0,
        },
    )

    def stop(sig, _frame):
        raise TimeoutError("companion comparison interrupted by signal " + str(sig))

    previous = {
        sig: signal.signal(sig, stop) for sig in (signal.SIGALRM, signal.SIGTERM, signal.SIGINT)
    }
    signal.setitimer(signal.ITIMER_REAL, cap - 30)
    startup_seconds, attestation = None, None
    try:
        from transformers import AutoTokenizer

        tokenizer = AutoTokenizer.from_pretrained(study.MODEL, local_files_only=True)
        send = study.wire_send()
        suite = study.dependencies()
        suite.start_service(service, study.source().binding(), min(started + 240, deadline))
        startup_seconds = time.time() - started
        attestation = study.attest(service / "service")
        study.write(study.ATTEMPT / "RUNTIME_ATTESTATION.json", attestation)
        descriptor = study.read(service / "service/endpoint-original.json")
        endpoint = f"http://{descriptor['host']}:{descriptor['port']}/inference/v1/generate"
        request_ids = set()
        for row in rows:
            if time.time() >= deadline:
                raise TimeoutError("request deadline; remaining slots stay unattempted")
            destination = study.ATTEMPT / "calls" / row["call_id"]
            result = send(
                endpoint, row, tokenizer, destination, max(1, min(180, deadline - time.time()))
            )
            request_id = result.get("request_id")
            if request_id and request_id in request_ids:
                result.update(
                    status="integrity_error", prediction={}, error="duplicate provider request ID"
                )
                study.write(destination / "CALL.json", result)
            if request_id:
                request_ids.add(request_id)
            calls.append(result)
            study.write(
                study.ATTEMPT / "PROGRESS.json",
                {
                    "attempted_calls": len(calls),
                    "last_call_id": row["call_id"],
                    "last_arm": row["arm"],
                    "last_call_sha256": study.sha(destination / "CALL.json"),
                    "elapsed_seconds": time.time() - started,
                },
            )
    except BaseException as error:
        errors.append({"type": type(error).__name__, "message": str(error)})
    finally:
        signal.setitimer(signal.ITIMER_REAL, 60)
        if suite is not None:
            try:
                suite.release_service(service)
                released = True
            except BaseException as error:
                errors.append(
                    {"stage": "release", "type": type(error).__name__, "message": str(error)}
                )
        else:
            released = True
        marker = study.engine_marker(service / "service")
        study.write(study.ATTEMPT / "ENGINECORE_BATCH_INVARIANT_FINAL.json", marker)
        qualified = bool(attestation and attestation["verified"] and marker["verified"])
        if not qualified:
            errors.append(
                {"stage": "runtime", "message": "pre-exec and actual EngineCore evidence required"}
            )
        summary = summarize(calls, rows, gold)
        summary.update(
            runtime_qualified=qualified,
            startup_seconds=startup_seconds,
            owner_elapsed_seconds=time.time() - started,
            full_panel_interpretation_eligible=qualified and summary["complete_available"],
        )
        study.write(study.ATTEMPT / "RESULT.json", summary)
        terminal = {
            "complete": not errors and released and len(calls) == study.CALLS,
            "released": released,
            "runtime_qualified": qualified,
            "errors": errors,
            "attempted_calls": len(calls),
            "elapsed_seconds": time.time() - started,
            "result_sha256": study.sha(study.ATTEMPT / "RESULT.json"),
        }
        study.write(study.ATTEMPT / "OWNER_TERMINAL.json", terminal)
        signal.setitimer(signal.ITIMER_REAL, 0)
        for sig, handler in previous.items():
            signal.signal(sig, handler)
    return terminal


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("command", choices=("verify", "run"))
    parser.add_argument("--outer-seconds", type=int, default=study.CAP)
    args = parser.parse_args()
    if args.command == "verify":
        print(study.verify()["identity"])
    else:
        result = execute(args.outer_seconds)
        print(json.dumps(result, sort_keys=True))
        raise SystemExit(0 if result["complete"] else 1)
