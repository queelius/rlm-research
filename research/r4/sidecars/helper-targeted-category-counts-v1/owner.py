"""One native service,96fixed calls, per-call checkpointing, unconditional cleanup."""

import argparse
import json
import os
import signal
import time
from urllib.request import Request, urlopen

import target_study as study
from metrics import summarize


def send(endpoint, row, tokenizer, destination, timeout):
    began, raw = time.time(), None
    study.write(destination / "REQUEST.json", row)
    request_wire = json.dumps(row["body"], separators=(",", ":")).encode()
    (destination / "REQUEST_WIRE.bin").write_bytes(request_wire)
    try:
        request = Request(
            endpoint,
            data=request_wire,
            headers=study.prior.validator().headers(),
            method="POST",
        )
        with urlopen(request, timeout=timeout) as response:
            wire = response.read()
        (destination / "RESPONSE_WIRE.bin").write_bytes(wire)
        raw = json.loads(wire)
        study.write(destination / "RESPONSE.json", raw)
        result = study.response_record(row, raw, tokenizer)
    except Exception as error:
        result = {
            "status": "integrity_error"
            if (destination / "RESPONSE_WIRE.bin").exists()
            else "request_error",
            "prediction": {},
            "error": {"type": type(error).__name__, "message": str(error)},
        }
        if isinstance(raw, dict):
            result["request_id"] = raw.get("request_id")
            for name in ("prompt_tokens", "completion_tokens"):
                value = raw.get("usage", {}).get(name)
                if isinstance(value, int) and not isinstance(value, bool) and value >= 0:
                    result[name] = value
    result.update(
        {key: row[key] for key in ("call_id", "dataset", "block", "start", "ids", "arm", "target")}
    )
    result.update(
        started_epoch=began,
        ended_epoch=time.time(),
        wall_seconds=time.time() - began,
        requested_prompt_tokens=len(row["body"]["token_ids"]),
        request_body_sha256=study.digest(row["body"]),
        ordered_schema_sha256=study.digest(row["schema_ordered_json"]),
        request_file_sha256=study.sha(destination / "REQUEST.json"),
        request_wire_sha256=study.sha(destination / "REQUEST_WIRE.bin"),
        response_wire_sha256=study.sha(destination / "RESPONSE_WIRE.bin")
        if (destination / "RESPONSE_WIRE.bin").exists()
        else None,
        response_file_sha256=study.sha(destination / "RESPONSE.json") if raw is not None else None,
    )
    study.write(destination / "CALL.json", result)
    return result


def execute(cap):
    ready = study.verify()
    if cap != study.CAP or study.ATTEMPT.exists():
        raise ValueError("unused attempt001 and exact900-second owner cap required")
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
            "planned_calls": 96,
            "physical_prediction_slots": 1536,
            "target_tasks": 80,
            "binary_decisions_per_arm": 1280,
            "cap_seconds": cap,
            "root_calls": 0,
            "training_updates": 0,
            "runtime_flag": "VLLM_BATCH_INVARIANT=1",
        },
    )

    def stop(sig, _frame):
        raise TimeoutError("targeted comparison interrupted by signal " + str(sig))

    previous = {
        sig: signal.signal(sig, stop) for sig in (signal.SIGALRM, signal.SIGTERM, signal.SIGINT)
    }
    signal.setitimer(signal.ITIMER_REAL, cap - 30)
    startup_seconds = None
    attestation = None
    try:
        from transformers import AutoTokenizer

        tokenizer = AutoTokenizer.from_pretrained(study.MODEL, local_files_only=True)
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
                raise TimeoutError("request deadline; all remaining slots explicitly unattempted")
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
        runtime_qualified = bool(attestation and attestation["verified"] and marker["verified"])
        if not runtime_qualified:
            errors.append(
                {"stage": "runtime", "message": "final EngineCore and pre-exec evidence required"}
            )
        summary = summarize(calls, rows, gold)
        summary.update(
            runtime_qualified=runtime_qualified,
            startup_seconds=startup_seconds,
            owner_elapsed_seconds=time.time() - started,
        )
        for dataset in summary["datasets"].values():
            screen = dataset["prospective_screen"]
            screen["metric_screen_passes_before_runtime_gate"] = screen["passes"]
            screen["passes"] = screen["passes"] and runtime_qualified
        study.write(study.ATTEMPT / "RESULT.json", summary)
        terminal = {
            "complete": not errors and released and len(calls) == study.CALLS,
            "released": released,
            "runtime_qualified": runtime_qualified,
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
