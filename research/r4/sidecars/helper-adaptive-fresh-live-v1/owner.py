"""One native service; live disagreement commit; terminal-only host scoring."""

import argparse
import json
import os
import signal
import time

import adaptive_metrics as metrics
import adaptive_study as study


def execute(cap):
    ready = study.verify()
    if cap != study.CAP or study.ATTEMPT.exists():
        raise ValueError("unused attempt001 and exact1100-second owner cap required")
    gpu = os.environ.get("CUDA_VISIBLE_DEVICES", "")
    if not gpu or "," in gpu or not os.environ.get("STRICT_RLM_CALIBRATION_API_KEY"):
        raise ValueError("MAIN must assign one GPU and inherited private credential")
    started, calls, errors, suite, released = time.time(), [], [], None, False
    deadline = started + cap - 90
    rows = study.schedule()
    public = study.read(study.PANEL / "PUBLIC.json")["records"]
    study.ATTEMPT.mkdir(parents=True)
    service = study.ATTEMPT / "service"
    service.mkdir()
    study.write(
        study.ATTEMPT / "OWNER_RUN.json",
        {
            "ready_identity": ready["identity"],
            "ready_sha256": study.sha(study.ROOT / "READY.json"),
            "started_epoch": started,
            "planned_calls": 152,
            "physical_prediction_slots": 512,
            "unique_records": 128,
            "cap_seconds": cap,
            "collection_deadline_epoch": deadline,
            "root_calls": 0,
            "training_updates": 0,
            "runtime_flag": "VLLM_BATCH_INVARIANT=1",
            "policy_call_counts": {
                "original16": 8,
                "three_vote": 24,
                "selective_singleton": "16+D",
                "always_singleton": 128,
            },
        },
    )

    def stop(sig, _frame):
        raise TimeoutError("adaptive owner interrupted by signal " + str(sig))

    previous = {
        sig: signal.signal(sig, stop) for sig in (signal.SIGALRM, signal.SIGTERM, signal.SIGINT)
    }
    signal.setitimer(signal.ITIMER_REAL, cap - 30)
    startup_seconds, attestation, committed = None, None, None
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

        def call_one(row):
            if time.time() >= deadline:
                raise TimeoutError("request deadline; remaining components stay unattempted")
            destination = study.ATTEMPT / "calls" / row["call_id"]
            if destination.exists():
                raise ValueError("physical call cannot be repeated")
            result = send(
                endpoint, row, tokenizer, destination, max(0.001, min(180, deadline - time.time()))
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
                    "routing_commit_sha256": study.sha(study.ATTEMPT / "ESCALATION.json")
                    if committed
                    else None,
                    "elapsed_seconds": time.time() - started,
                },
            )
            return result

        def commit(routing, source_calls):
            nonlocal committed
            path = study.ATTEMPT / "ESCALATION.json"
            if (
                path.exists()
                or len(source_calls) != 16
                or any(c["arm"] not in ("original", "neighbor_A") for c in source_calls)
            ):
                raise ValueError("routing commit requires exactly16 O/A calls and no future calls")
            receipt = {
                "routing": routing,
                "committed_epoch": time.time(),
                "ready_identity": ready["identity"],
                "public_sha256": study.sha(study.PANEL / "PUBLIC.json"),
                "source_call_sha256": {
                    c["call_id"]: study.sha(study.ATTEMPT / "calls" / c["call_id"] / "CALL.json")
                    for c in source_calls
                },
                "prior_physical_call_ids": [c["call_id"] for c in source_calls],
                "gold_loaded": False,
                "future_outputs_loaded": False,
            }
            receipt["identity"] = study.digest(receipt)
            study.write(path, receipt)
            committed = receipt

        collected, routing = metrics.collect(rows, public, call_one, commit)
        if len(collected) != len(calls) or len(calls) != 152 or routing != committed["routing"]:
            raise ValueError("staged collection accounting differs")
    except BaseException as error:
        errors.append({"type": type(error).__name__, "message": str(error)})
    finally:
        signal.setitimer(signal.ITIMER_REAL, min(60, max(1, started + cap - time.time())))
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
        # First semantic gold read: generation and service release are now terminal.
        gold = study.read(study.PANEL / "HOST_GOLD.json")["labels"]
        summary = metrics.summarize(
            calls, rows, public, gold, committed["routing"] if committed else None
        )
        eligible = qualified and released and summary["complete_available"] and not errors
        summary.update(
            runtime_qualified=qualified,
            released=released,
            startup_seconds=startup_seconds,
            owner_elapsed_seconds=time.time() - started,
            full_panel_interpretation_eligible=eligible,
            routing_commit_sha256=study.sha(study.ATTEMPT / "ESCALATION.json")
            if committed
            else None,
        )
        for dataset in summary["datasets"].values():
            dataset["screen"]["passes"] = eligible and dataset["screen"]["metric_passes"]
        study.write(study.ATTEMPT / "RESULT.json", summary)
        terminal = {
            "complete": eligible and len(calls) == study.CALLS,
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
