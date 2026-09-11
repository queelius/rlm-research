"""MAIN-launched one-service owner with shared 1,800-second inclusive envelope."""

from __future__ import annotations

import argparse
import importlib.util
import json
import os
import signal
import subprocess
import sys
import time
from pathlib import Path

import driver
import lifecycle_adapter
import service
import study as s

ATTEMPT = s.ROOT / "outputs/attempt-001"
RUNTIME = s.SIDE / "runtime-an27-5780-v1"
RUNTIME_SERVICE = RUNTIME / "service_wrapper_v2.py"
RUNTIME_LIFECYCLE_MANIFEST = RUNTIME / "LIFECYCLE_READY_V2.json"
SUITE = s.SIDE / "leaf-post-sft-suite-v1/suite.py"
SUITE_SHA256 = "6fa84af486efbf5bad17352553d36cd590fb6f7e386c2273df27dd8deb7c8fd1"
NATIVE = Path("/project/alex_phd/envs/prime-rl-5990b1b/bin/python")


def credential_preflight():
    path = RUNTIME / "credential_preflight.py"
    if s.sha(path) != "2ff11844d7237f99d1d6080b2e599a1bacf34ad693e13acd98a41cddcaaa8110":
        raise ValueError("credential preflight source changed")
    spec = importlib.util.spec_from_file_location("free_id_credential_preflight", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module.require_provider_credential()


def load_suite():
    if s.sha(SUITE) != SUITE_SHA256:
        raise ValueError("qualified service suite changed")
    spec = importlib.util.spec_from_file_location("free_id_owned_suite", SUITE)
    suite = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = suite
    spec.loader.exec_module(suite)
    suite.verify()
    lifecycle_adapter.install(suite)
    suite.preflight = base_preflight
    return suite


def base_preflight(directory, binding):
    import httpx

    endpoint = s.read(directory / "endpoint-original.json")
    service.validate_descriptor(endpoint, s.MODELS[s.MODEL])
    config = s.read(directory / "inference.json")["vllm"]
    if config.get("enable_lora") is not False or config.get("enable_prefix_caching") is not False:
        raise ValueError("base/no-cache service configuration changed")
    url = f"http://{endpoint['host']}:{endpoint['port']}"
    headers = {"Authorization": "Bearer " + os.environ[endpoint["api_key_env"]]}
    with httpx.Client(headers=headers, trust_env=False, timeout=30) as client:
        version = client.get(url + "/version")
        version.raise_for_status()
        models = client.get(url + "/v1/models")
        models.raise_for_status()
    if version.json().get("version") != "0.28.0":
        raise ValueError("unqualified vLLM version")
    service.validate_models(models.json(), s.MODELS[s.MODEL])
    s.write_once(directory.parent / "PREFLIGHT.json", {
        "version": version.json(), "models": models.json(),
        "inference_sha256": s.sha(directory / "inference.json"),
        "binding_sha256": s.digest(binding), "checked_epoch": time.time(),
    })


def verify():
    ready = s.read(s.ROOT / "READY.json")
    if s.digest({k: v for k, v in ready.items() if k != "identity"}) != ready["identity"]:
        raise ValueError("READY identity changed")
    for path, expected in ready["source_sha256"].items():
        if s.sha(path) != expected:
            raise ValueError("READY source changed: " + path)
    driver.verify(s.read(s.ROOT / "SPEC.json"))
    return ready


def binding():
    return {
        "schema": "released-base-single-model-binding-v1",
        "model": s.MODEL,
        "checkpoint": s.MODELS[s.MODEL],
        "weights_sha256": s.sha(s.ROOT / "WEIGHTS.json"),
        "adapter": None,
    }


def execute(output):
    credential = credential_preflight()
    if output.resolve() != ATTEMPT.resolve():
        raise ValueError("only exact attempt-001 output is authorized")
    if output.exists():
        raise FileExistsError("attempt exists; no overwrite or implicit retry")
    gpu = os.environ.get("CUDA_VISIBLE_DEVICES", "")
    if not gpu or "," in gpu:
        raise ValueError("MAIN must assign one exclusively owned GPU")
    ready = verify()
    suite = load_suite()
    started = time.time()
    work_deadline = started + 1680
    owned_deadline = started + 1770
    output.mkdir(parents=True, exist_ok=False)
    stage = output / "owned-service"
    stage.mkdir()
    s.write_once(output / "OWNER_RUN.json", {
        "started_epoch": started, "work_deadline_epoch": work_deadline,
        "owned_deadline_epoch": owned_deadline, "outer_seconds": 1800,
        "cleanup_seconds": 90, "gpu": gpu, "ready_identity": ready["identity"], **credential,
    })
    error = release_error = None
    released = False
    terminal = None

    def expired(sig, _frame):
        raise TimeoutError("owned inclusive deadline or MAIN termination: " + str(sig))

    previous = {sig: signal.signal(sig, expired) for sig in (signal.SIGINT, signal.SIGTERM, signal.SIGALRM)}
    signal.setitimer(signal.ITIMER_REAL, max(0.001, owned_deadline - time.time()))
    try:
        suite.start_service(stage, binding(), min(work_deadline, time.time() + 300))
        argv = [str(NATIVE), str(s.ROOT / "driver.py"), "run", "--endpoint",
                str(stage / "service/endpoint-original.json"), "--output",
                str(output / "rollout"), "--deadline", str(work_deadline)]
        suite.command(stage, "free-id-collect", argv, 1680, work_deadline)
        terminal = s.read(output / "rollout/STATUS.json")
        if terminal["planned"] != 96 or terminal["recorded"] != 96:
            raise ValueError("collector did not retain all planned coordinate records")
    except BaseException as caught:
        error = {"type": type(caught).__name__, "message": str(caught)[:1200]}
    finally:
        try:
            suite.release_service(stage)
            released = True
        except BaseException as caught:
            release_error = {"type": type(caught).__name__, "message": str(caught)[:1200]}
        signal.setitimer(signal.ITIMER_REAL, 0)
        for sig, handler in previous.items():
            signal.signal(sig, handler)
    result = {
        "complete": error is None and release_error is None and released,
        "error": error, "release_error": release_error, "released": released,
        "collector_status": terminal, "planned": 96, "elapsed_seconds": time.time() - started,
        "outer_seconds": 1800, "no_retry": True, "main_owns_gpu_and_lock": True,
    }
    s.write_once(output / "OWNER_TERMINAL.json", result)
    return result


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("command", choices=("verify", "run"))
    parser.add_argument("--output", type=Path, default=ATTEMPT)
    args = parser.parse_args()
    if args.command == "verify":
        print(json.dumps({"ready_identity": verify()["identity"], "gpu_calls": 0}))
        return
    result = execute(args.output)
    print(json.dumps(result), flush=True)
    raise SystemExit(0 if result["complete"] else 1)


if __name__ == "__main__":
    main()

