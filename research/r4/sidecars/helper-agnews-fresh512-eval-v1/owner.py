"""Bounded fresh512 native owner; MAIN alone supplies endpoint fixation and GPU."""

import argparse
import json
import os
import signal
import time

import collect
import eligibility
import metrics
import study


def execute(arm, cap):
    started = time.time()
    ready = study.verify(arm)
    if cap != study.CAP or study.attempt(arm).exists():
        raise ValueError("exact900 cap and unused arm attempt required")
    fixed = eligibility.fixed_endpoints(arm)
    gpu = os.environ.get("CUDA_VISIBLE_DEVICES", "")
    if not gpu or "," in gpu or not os.environ.get("STRICT_RLM_CALIBRATION_API_KEY"):
        raise ValueError("MAIN must provide one GPU and inherited private credential")
    output = study.attempt(arm)
    output.mkdir(parents=True)
    service = output / "service"
    service.mkdir()
    rows, gold = study.schedule(), study.gold()
    binding = fixed["arm_eligibility"]["binding"]
    study.write_x(output / "ELIGIBILITY.json", fixed)
    study.write_x(
        output / "OWNER_RUN.json",
        {
            "arm": arm,
            "ready_sha256": study.sha(study.ready_path(arm)),
            "ready_identity": ready["identity"],
            "started_epoch": started,
            "cap_seconds": cap,
            "planned_calls": 128,
            "planned_records": 512,
            "schedule_sha256": study.digest(rows),
            "root_calls": 0,
            "optimizer_steps": 0,
            "authorization_source": "MAIN endpoint receipt and process environment",
        },
    )
    deadline = started + cap - 90
    suite, lifecycle, attestation = None, None, None
    released, runtime_qualified = False, False
    calls, errors, request_ids = [], [], set()

    def stop(sig, _frame):
        raise TimeoutError("fresh512 owner interrupted by signal " + str(sig))

    previous = {
        sig: signal.signal(sig, stop) for sig in (signal.SIGALRM, signal.SIGTERM, signal.SIGINT)
    }
    signal.setitimer(signal.ITIMER_REAL, max(1, started + cap - 30 - time.time()))
    try:
        from transformers import AutoTokenizer

        tokenizer = AutoTokenizer.from_pretrained(study.MODEL, local_files_only=True)
        lifecycle, suite = study.lifecycle()
        suite.start_service(service, binding, min(time.time() + 240, deadline))
        if (
            study.read(service / "BINDING.json") != binding
            or study.read(service / "service/BINDING.json") != binding
        ):
            raise ValueError("running service binding differs from qualified endpoint")
        config = study.read(service / "service/inference.json")
        runtime = study.sanitized_runtime(config)
        context_cap = config["vllm"]["max_model_len"]
        maximum = max(len(row["body"]["token_ids"]) + 1024 for row in rows)
        if context_cap != 8192 or maximum > context_cap:
            raise ValueError("fixed request/output bound exceeds actual service context")
        study.write_x(
            output / "RUNTIME.json",
            {
                "configuration": runtime,
                "configuration_sha256": study.digest(runtime),
                "binding_sha256": study.sha(service / "BINDING.json"),
                "service_wrapper_sha256": study.sha(lifecycle.SERVICE_WRAPPER),
                "native_python": str(study.NATIVE),
                "max_prompt_plus_1024": maximum,
                "actual_max_model_len": context_cap,
                "concurrency": 1,
                "batch": 4,
            },
        )
        descriptor = study.read(service / "service/endpoint-original.json")
        server_pid = study.read(service / "service/SERVER_START.json")["pid"]
        attestation = lifecycle.attest_engine(service, server_pid)
        endpoint = f"http://{descriptor['host']}:{descriptor['port']}/inference/v1/generate"
        for row in rows:
            if time.time() >= deadline:
                raise TimeoutError("request deadline; remaining fixed tail is unattempted")
            call = collect.send(endpoint, row, tokenizer, output, deadline)
            request_id = call.get("request_id")
            if request_id and request_id in request_ids:
                call.update(
                    status="invalid_response",
                    prediction={},
                    validation_error="duplicate provider request ID",
                )
            if request_id:
                request_ids.add(request_id)
            calls.append(call)
            study.write_x(output / "calls" / (row["call_id"] + ".json"), call)
            print(
                json.dumps(
                    {
                        "arm": arm,
                        "attempted": len(calls),
                        "planned": 128,
                        "status": call["status"],
                        "elapsed": time.time() - started,
                    }
                ),
                flush=True,
            )
    except BaseException as error:
        errors.append({"stage": "collection", "type": type(error).__name__, "message": str(error)})
    finally:
        signal.setitimer(signal.ITIMER_REAL, 60)
        if suite is not None:
            try:
                suite.release_service(service)
                stopped = study.read(service / "SERVICE_STOPPED.json")
                released = bool(
                    stopped.get("all_owned_process_identities_exited") and stopped.get("ports_free")
                )
                if not released:
                    raise RuntimeError("native clean release evidence absent")
            except BaseException as error:
                errors.append(
                    {"stage": "release", "type": type(error).__name__, "message": str(error)}
                )
        else:
            released = True
        if attestation is not None and released:
            try:
                evidence = lifecycle.finalize_kernel_attestation(service, attestation, released)
                evidence["current_config_scope"] = (
                    "helper-only serial B4; exact fixed shared service flags"
                )
                study.write_x(output / "ENGINE_ATTESTATION.json", evidence)
                runtime_qualified = True
            except BaseException as error:
                errors.append(
                    {
                        "stage": "kernel_attestation",
                        "type": type(error).__name__,
                        "message": str(error),
                    }
                )
        signal.setitimer(signal.ITIMER_REAL, 0)
        for sig, handler in previous.items():
            signal.signal(sig, handler)
    result = metrics.summarize(calls, gold, rows)
    result.update(
        arm=arm,
        runtime_qualified=runtime_qualified,
        eligibility_sha256=study.sha(output / "ELIGIBILITY.json"),
        training_cost="separate source training result; excluded from endpoint usage",
        ready_sha256=study.sha(study.ready_path(arm)),
    )
    if not runtime_qualified:
        result["metrics"]["primary_accuracy"] = None
    study.write_x(output / "RESULT.json", result)
    terminal = {
        "complete": result["complete"] and runtime_qualified and released and not errors,
        "released": released,
        "runtime_qualified": runtime_qualified,
        "errors": errors,
        "attempted_calls": len(calls),
        "planned_calls": 128,
        "planned_records": 512,
        "elapsed_seconds": time.time() - started,
        "result_sha256": study.sha(output / "RESULT.json"),
    }
    study.write_x(output / "OWNER_TERMINAL.json", terminal)
    return terminal


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("command", choices=("verify", "qualify", "run"))
    parser.add_argument("--arm", choices=study.ARMS, required=True)
    parser.add_argument("--outer-seconds", type=int, default=study.CAP)
    args = parser.parse_args()
    if args.command == "verify":
        print(study.verify(args.arm)["identity"])
    elif args.command == "qualify":
        print(json.dumps(eligibility.qualify(args.arm), sort_keys=True))
    else:
        terminal = execute(args.arm, args.outer_seconds)
        print(json.dumps(terminal, sort_keys=True))
        raise SystemExit(0 if terminal["complete"] else 1)
