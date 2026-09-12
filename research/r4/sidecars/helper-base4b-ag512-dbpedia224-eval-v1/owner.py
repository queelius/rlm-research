"""Own one true-base service and evaluate the two frozen transfer panels."""

import argparse
import json
import os
import signal
import time
import traceback

import collect
import metrics
import study


def attest_start(service):
    directory = service / "service"
    start = study.read(directory / "SERVER_START.json")
    receipt_path = directory / "ENGINE_ENV_ATTESTATION.json"
    receipt = study.read(receipt_path)
    expected = {
        "schema": "batch-invariant-engine-preexec-attestation-v1",
        "pid": start["pid"],
        "VLLM_BATCH_INVARIANT": "1",
        "command_sha256": study.digest(start["command"]),
        "wrapper_sha256": study.sha(study.SERVICE_WRAPPER),
        "credentials_persisted": False,
    }
    if receipt != expected or start.get("launcher_sha256") != study.sha(study.SERVICE_WRAPPER):
        raise ValueError("actual engine start is not the sealed batch-invariant service")
    return {
        "server_pid": start["pid"],
        "preexec_receipt": str(receipt_path),
        "preexec_receipt_sha256": study.sha(receipt_path),
        "VLLM_BATCH_INVARIANT": "1",
        "credentials_persisted": False,
    }


def finalize_attestation(service, attestation, released):
    if not released:
        raise RuntimeError("kernel evidence requires clean service release")
    log = service / "service/inference.log"
    text = log.read_text(errors="replace")
    if "batch_invariant.py" not in text or "matmul_persistent" not in text:
        raise ValueError("actual batch-invariant kernel marker absent")
    value = dict(attestation)
    value.update(
        actual_kernel_marker="batch_invariant.py / matmul_persistent",
        inference_log=str(log),
        inference_log_sha256=study.sha(log),
        scope="true-base serial helper B4 over two frozen panels",
    )
    return value


def execute(outer_seconds):
    ready = study.verify()
    if outer_seconds != study.CAP or study.ATTEMPT.exists():
        raise ValueError("exact 900-second cap and unused attempt-001 required")
    gpu = os.environ.get("CUDA_VISIBLE_DEVICES", "")
    if not gpu or "," in gpu or not os.environ.get("STRICT_RLM_CALIBRATION_API_KEY"):
        raise ValueError("MAIN must supply one GPU and the inherited private credential")
    started = time.time()
    deadline = started + study.CAP - 90
    study.ATTEMPT.mkdir(parents=True)
    service = study.ATTEMPT / "service"
    service.mkdir()
    rows_by_panel = study.schedules()
    gold_by_panel = study.gold()
    binding = study.binding()
    study.write_x(study.ATTEMPT / "BINDING.json", binding)
    study.write_x(
        study.ATTEMPT / "OWNER_RUN.json",
        {
            "ready_identity": ready["identity"],
            "ready_sha256": study.sha(study.ROOT / "READY.json"),
            "started_epoch": started,
            "cap_seconds": study.CAP,
            "planned_calls": 184,
            "planned_records": 736,
            "optimizer_steps": 0,
            "authorization_source": "process environment only",
        },
    )
    suite, released, start_attestation = None, False, None
    errors, calls_by_panel, request_ids = [], {panel: [] for panel in study.PANELS}, set()

    def stop(sig, _frame):
        raise TimeoutError("true-base control interrupted by signal " + str(sig))

    previous = {
        sig: signal.signal(sig, stop)
        for sig in (signal.SIGALRM, signal.SIGTERM, signal.SIGINT)
    }
    signal.setitimer(signal.ITIMER_REAL, max(1, study.CAP - 30))
    try:
        from transformers import AutoTokenizer

        tokenizer = AutoTokenizer.from_pretrained(study.MODEL, local_files_only=True)
        suite = study.dependencies()
        suite.start_service(service, binding, min(started + 285, deadline))
        if (
            study.read(service / "BINDING.json") != binding
            or study.read(service / "service/BINDING.json") != binding
        ):
            raise ValueError("actual service binding differs from frozen true-base binding")
        config = study.read(service / "service/inference.json")
        if (
            config["vllm"].get("enable_lora") is not False
            or config["vllm"].get("enable_prefix_caching") is not False
            or config["vllm"].get("max_model_len") != 8192
        ):
            raise ValueError("actual true-base LoRA/cache/context configuration differs")
        runtime = study.sanitized_runtime(config)
        study.write_x(
            study.ATTEMPT / "RUNTIME.json",
            {
                "configuration": runtime,
                "configuration_sha256": study.digest(runtime),
                "service_wrapper": str(study.SERVICE_WRAPPER),
                "service_wrapper_sha256": study.sha(study.SERVICE_WRAPPER),
                "runtime_differences_from_trained_arms": {
                    "enable_lora": False,
                    "enable_prefix_caching": False,
                },
                "no_matched_cost_or_bitwise_claim": True,
            },
        )
        descriptor = study.read(service / "service/endpoint-original.json")
        start_attestation = attest_start(service)
        endpoint = f"http://{descriptor['host']}:{descriptor['port']}/inference/v1/generate"
        for panel, rows in zip(study.PANELS, rows_by_panel, strict=True):
            for row in rows:
                if time.time() >= deadline:
                    raise TimeoutError("owner deadline; remaining tail is explicitly unattempted")
                call = collect.send(endpoint, row, tokenizer, study.ATTEMPT / panel, deadline)
                request_id = call.get("request_id")
                if request_id and request_id in request_ids:
                    call.update(
                        status="invalid_response",
                        prediction={},
                        validation_error="duplicate provider request ID across both panels",
                    )
                if request_id:
                    request_ids.add(request_id)
                calls_by_panel[panel].append(call)
                study.write_x(
                    study.ATTEMPT / panel / "calls" / (row["call_id"] + ".json"), call
                )
                print(
                    json.dumps(
                        {
                            "panel": panel,
                            "attempted_panel": len(calls_by_panel[panel]),
                            "attempted_total": sum(map(len, calls_by_panel.values())),
                            "planned_total": 184,
                            "status": call["status"],
                            "elapsed": time.time() - started,
                        }
                    ),
                    flush=True,
                )
    except BaseException as error:
        errors.append(
            {
                "stage": "collection",
                "type": type(error).__name__,
                "message": str(error),
                "traceback": traceback.format_exc(),
            }
        )
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
                    raise RuntimeError("clean service release evidence absent")
            except BaseException as error:
                errors.append(
                    {"stage": "release", "type": type(error).__name__, "message": str(error)}
                )
        else:
            released = True
        kernel = None
        if start_attestation is not None and released:
            try:
                kernel = finalize_attestation(service, start_attestation, released)
                study.write_x(study.ATTEMPT / "ENGINE_ATTESTATION.json", kernel)
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

    panels = {
        panel: metrics.summarize_panel(panel, calls_by_panel[panel], gold_by_panel[panel], rows)
        for panel, rows in zip(study.PANELS, rows_by_panel, strict=True)
    }
    runtime_qualified = kernel is not None
    if not runtime_qualified:
        for panel in panels.values():
            panel["metrics"]["primary_accuracy"] = None
    result = {
        "schema": "helper-base4b-ag512-dbpedia224-eval-result-v1",
        "policy": "unadapted Qwen3-4B-Instruct-2507",
        "adapter": None,
        "runtime_qualified": runtime_qualified,
        "panels": panels,
        "historical_control": {
            "result": str(study.BASE_SOURCE / "outputs/attempt-002/RESULT.json"),
            "result_sha256": study.sha(study.BASE_SOURCE / "outputs/attempt-002/RESULT.json"),
            "old_fixed_256": {
                "ag_news": {"c32": 112, "base": 113, "c32_to_base_wins": 4, "losses": 3},
                "trec": {"c32": 119, "base": 92, "c32_to_base_wins": 1, "losses": 28},
            },
        },
        "comparison_boundary": (
            "The base endpoint supplements the four fixed trained arms. Different LoRA/prefix-cache "
            "runtime settings preclude matched-cost or bitwise claims."
        ),
    }
    study.write_x(study.ATTEMPT / "RESULT.json", result)
    terminal = {
        "complete": all(panel["complete"] for panel in panels.values())
        and runtime_qualified
        and released
        and not errors,
        "released": released,
        "runtime_qualified": runtime_qualified,
        "errors": errors,
        "attempted_calls": sum(map(len, calls_by_panel.values())),
        "planned_calls": 184,
        "elapsed_seconds": time.time() - started,
        "result_sha256": study.sha(study.ATTEMPT / "RESULT.json"),
    }
    study.write_x(study.ATTEMPT / "OWNER_TERMINAL.json", terminal)
    return terminal


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("command", choices=("verify", "run"))
    parser.add_argument("--outer-seconds", type=int, default=study.CAP)
    args = parser.parse_args()
    if args.command == "verify":
        print(study.verify()["identity"])
    else:
        terminal = execute(args.outer_seconds)
        print(json.dumps(terminal, sort_keys=True))
        raise SystemExit(0 if terminal["complete"] else 1)
