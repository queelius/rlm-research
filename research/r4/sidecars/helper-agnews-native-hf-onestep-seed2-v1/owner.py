"""Bounded serial native -> CPU masks -> one-load HF lifecycle."""

import argparse
import json
import os
import signal
import subprocess
import time

import ag_study as study
import native_collect


def numeric_environment():
    return {
        key: value
        for key, value in os.environ.items()
        if not any(word in key.upper() for word in ("API_KEY", "AUTH_TOKEN", "ACCESS_TOKEN"))
    }


def context_receipt(inference, audit):
    context_cap = inference["vllm"]["max_model_len"]
    if context_cap != 8192 or audit["max_prompt_plus_completion"] > context_cap:
        raise ValueError("actual context cap differs or request bound exceeds it")
    return {"actual_max_model_len": context_cap, **audit}


def run_child(command, name, seconds, environment):
    with (
        (study.ATTEMPT / (name + ".stdout.log")).open("x") as stdout,
        (study.ATTEMPT / (name + ".stderr.log")).open("x") as stderr,
    ):
        result = subprocess.run(
            command, env=environment, stdout=stdout, stderr=stderr, timeout=seconds
        )
    study.write_x(
        study.ATTEMPT / (name + "_PROCESS.json"),
        {
            "command": command,
            "returncode": result.returncode,
            "timeout_seconds": seconds,
            "credentials_forwarded": False,
        },
    )
    if result.returncode:
        raise RuntimeError(name + " process exited " + str(result.returncode))


def execute(cap):
    ready = study.verify()
    if cap != study.CAP or study.ATTEMPT.exists():
        raise ValueError("exact unused attempt and1100 owner cap required")
    gpu = os.environ.get("CUDA_VISIBLE_DEVICES", "")
    if not gpu or "," in gpu or not os.environ.get("STRICT_RLM_CALIBRATION_API_KEY"):
        raise ValueError("MAIN must provide one GPU and inherited private native credential")
    started = time.time()
    deadline = started + cap
    native_deadline = started + study.PHASE_CAPS["native"]
    study.ATTEMPT.mkdir(parents=True)
    study.write_x(
        study.ATTEMPT / "OWNER_RUN.json",
        {
            "ready_identity": ready["identity"],
            "started_epoch": started,
            "phase_caps_seconds": study.PHASE_CAPS,
            "planned_native_calls": 128,
            "planned_optimizer_steps": 1,
            "gpu": gpu,
            "credential_values_persisted": False,
        },
    )
    service = study.ATTEMPT / "service"
    service.mkdir()
    errors, suite, released, attestation = [], None, False, None
    lifecycle = native_collect.lifecycle()

    def stop(number, _frame):
        raise TimeoutError("owner received signal " + str(number))

    previous = {
        number: signal.signal(number, stop)
        for number in (signal.SIGALRM, signal.SIGINT, signal.SIGTERM)
    }
    signal.setitimer(signal.ITIMER_REAL, cap)
    try:
        try:
            with study.aliases({"study": study}):
                suite = lifecycle.dependencies()
            suite.start_service(service, study.binding(), min(started + 180, native_deadline))
            descriptor = study.read(service / "service/endpoint-original.json")
            inference = study.read(service / "service/inference.json")
            audit = study.read(study.ROOT / "inputs/BUILD_AUDIT.json")
            study.write_x(
                study.ATTEMPT / "CONTEXT_BOUND.json",
                {
                    **context_receipt(inference, audit),
                    "inference_config_sha256": study.sha(service / "service/inference.json"),
                },
            )
            pid = study.read(service / "service/SERVER_START.json")["pid"]
            attestation = lifecycle.attest_engine(service, pid)
            endpoint = f"http://{descriptor['host']}:{descriptor['port']}/inference/v1/generate"
            native_collect.collect(endpoint, study.schedule(), study.ATTEMPT, native_deadline)
        except BaseException as error:
            errors.append({"stage": "native", "type": type(error).__name__, "message": str(error)})
        finally:
            signal.setitimer(signal.ITIMER_REAL, min(40, max(1, deadline - time.time())))
            if suite is not None:
                try:
                    suite.release_service(service)
                    receipt = study.read(service / "SERVICE_STOPPED.json")
                    released = bool(
                        receipt.get("all_owned_process_identities_exited")
                        and receipt.get("ports_free")
                    )
                    if not released:
                        raise RuntimeError("native release incomplete")
                except BaseException as error:
                    errors.append(
                        {"stage": "release", "type": type(error).__name__, "message": str(error)}
                    )
        signal.setitimer(signal.ITIMER_REAL, max(1, deadline - time.time()))
        if not errors and released and attestation is not None:
            study.write_x(
                study.ATTEMPT / "ENGINE_ATTESTATION.json",
                lifecycle.finalize_kernel_attestation(service, attestation, released),
            )
            env = numeric_environment()
            mask_env = {**env, "CUDA_VISIBLE_DEVICES": ""}
            remaining = deadline - time.time() - 20
            if remaining <= 0:
                raise TimeoutError("no remaining owner time for mask handoff")
            run_child(
                [str(study.NATIVE), str(study.ROOT / "prepare_masks.py")],
                "MASKS",
                min(study.PHASE_CAPS["masks"], remaining),
                mask_env,
            )
            remaining = deadline - time.time() - 20
            if remaining <= 0:
                raise TimeoutError("no remaining owner time for HF")
            run_child(
                [str(study.TRAIN_PYTHON), str(study.ROOT / "train_ag.py")],
                "HF",
                min(study.PHASE_CAPS["hf"], remaining),
                env,
            )
    except BaseException as error:
        errors.append(
            {"stage": "handoff_or_hf", "type": type(error).__name__, "message": str(error)}
        )
    finally:
        signal.setitimer(signal.ITIMER_REAL, 0)
        for number, handler in previous.items():
            signal.signal(number, handler)
    step_path = study.ATTEMPT / "OPTIMIZER_STEP.json"
    intent_path = study.ATTEMPT / "OPTIMIZER_INTENT.json"
    steps = (
        study.read(step_path)["completed_steps"]
        if step_path.exists()
        else (None if intent_path.exists() else 0)
    )
    result_path = study.ATTEMPT / "RESULT.json"
    if not result_path.exists():
        study.write_x(
            result_path,
            {
                "status": "STOP_FAILED",
                "optimizer_steps": steps,
                "errors": errors,
                "eligible_for_eval": False,
            },
        )
    result = study.read(result_path)
    terminal = {
        "complete": not errors and released and result["status"] == "UPDATED",
        "terminal_status": result["status"],
        "optimizer_steps": steps,
        "released_before_hf": released,
        "errors": errors,
        "elapsed_seconds": time.time() - started,
        "result_sha256": study.sha(result_path),
        "ready_identity": ready["identity"],
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
        result = execute(args.outer_seconds)
        print(json.dumps(result, sort_keys=True))
        raise SystemExit(0 if result["complete"] else 1)
