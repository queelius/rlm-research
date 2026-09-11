"""MAIN-only owner for 192 fresh-context positional-anchor calls."""

import argparse
import os
from pathlib import Path
import signal
import time

import protocol as p
import study as s


CLOCK = {"outer": 1800, "work": 1650, "owned": 1770, "startup": 180, "release": 90, "harvest": 30, "finalize": 30, "margin": 30}


def validate_argv(argv):
    expected = [str(s.NATIVE), str(s.ROOT / "collect.py"), "run", "--endpoint"]
    if len(argv) != 9 or argv[:4] != expected or argv[5] != "--output" or argv[7] != "--deadline":
        raise ValueError("exact collector CLI required")
    endpoint, output = Path(argv[4]), Path(argv[6])
    if endpoint.resolve() != s.ATTEMPT / "owned-service/service/endpoint-original.json" or output.resolve() != s.ATTEMPT / "rollout":
        raise ValueError("exact attempt namespace required")
    return {"endpoint": endpoint, "output": output, "deadline": float(argv[8])}


def collector_argv(stage, output, deadline):
    argv = [str(s.NATIVE), str(s.ROOT / "collect.py"), "run", "--endpoint", str(stage / "service/endpoint-original.json"), "--output", str(output / "rollout"), "--deadline", str(deadline)]
    validate_argv(argv)
    return argv


def credential():
    return s.base.load("positional_anchor_new_context_credential", s.base.RUNTIME / "credential_preflight.py", "2ff11844d7237f99d1d6080b2e599a1bacf34ad693e13acd98a41cddcaaa8110").require_provider_credential()


def binding():
    return {"schema": "released-base-single-model-binding-v1", "model": "qwen3", "checkpoint": s.MODEL, "weights_sha256": s.sha(s.base.FREE / "WEIGHTS.json"), "adapter": None}


def preflight(directory, value):
    import httpx

    endpoint = s.read(directory / "endpoint-original.json")
    s.service.validate_descriptor(endpoint, s.MODEL)
    config = s.read(directory / "inference.json")["vllm"]
    if config.get("enable_lora") is not False or config.get("enable_prefix_caching") is not False:
        raise ValueError("released base config differs")
    headers = {"Authorization": "Bearer " + os.environ[endpoint["api_key_env"]]}
    url = f'http://{endpoint["host"]}:{endpoint["port"]}'
    with httpx.Client(headers=headers, trust_env=False, timeout=30) as client:
        version, models = client.get(url + "/version"), client.get(url + "/v1/models")
        version.raise_for_status(); models.raise_for_status()
    if version.json().get("version") != "0.28.0":
        raise ValueError("unqualified vLLM")
    s.service.validate_models(models.json(), s.MODEL)
    s.write(directory.parent / "PREFLIGHT.json", {"version": version.json(), "models": models.json(), "binding_sha256": s.digest(value), "checked_epoch": time.time()})


def suite():
    value = s.base.load("positional_anchor_new_context_suite", s.SIDE / "leaf-post-sft-suite-v1/suite.py", "6fa84af486efbf5bad17352553d36cd590fb6f7e386c2273df27dd8deb7c8fd1")
    value.verify(); s.lifecycle.install(value); value.preflight = preflight
    value.SERVE = s.ROOT / "service_wrapper.py"
    value.life.__dict__["ALLOCATION_SERVICE"] = value.SERVE
    return value


def execute(output):
    private, ready = credential(), s.verify()
    if output.resolve() != s.ATTEMPT or output.exists():
        raise ValueError("unused exact attempt required")
    gpu = os.environ.get("CUDA_VISIBLE_DEVICES", "")
    if not gpu or "," in gpu:
        raise ValueError("MAIN must assign one owned GPU")
    runner = suite(); started = time.time(); work, owned = started + CLOCK["work"], started + CLOCK["owned"]
    output.mkdir(parents=True); stage = output / "owned-service"; stage.mkdir()
    s.write(output / "PLANNED_NULL_ENDPOINTS.json", [p.null_row(row, "before service startup") for row in s.read(s.ROOT / "PLAN.json")])
    s.write(output / "OWNER_RUN.json", {"identity": ready["identity"], "started_epoch": started, "work_deadline": work, "owned_deadline": owned, "clock": CLOCK, "gpu": gpu, **private})
    def expired(*_): raise TimeoutError("owned1770 deadline or MAIN termination")
    previous = {sig: signal.signal(sig, expired) for sig in (signal.SIGINT, signal.SIGTERM, signal.SIGALRM)}
    signal.setitimer(signal.ITIMER_REAL, max(0.001, owned - time.time()))
    error = release_error = terminal = None; released = False
    try:
        runner.start_service(stage, binding(), min(work, time.time() + CLOCK["startup"]))
        runner.command(stage, "mnli-position-anchor-new-context192-collect", collector_argv(stage, output, work), max(0.001, work - time.time()), work)
        terminal = s.read(output / "rollout/STATUS.json")
        if terminal["planned"] != 192 or terminal["recorded"] != 192:
            raise ValueError("collector must retain 192 slots")
    except BaseException as caught:
        error = {"type": type(caught).__name__, "message": str(caught)}
    finally:
        signal.setitimer(signal.ITIMER_REAL, max(0.001, min(owned - CLOCK["finalize"], time.time() + CLOCK["release"]) - time.time()))
        try: runner.release_service(stage); released = True
        except BaseException as caught: release_error = {"type": type(caught).__name__, "message": str(caught)}
        signal.setitimer(signal.ITIMER_REAL, max(0.001, owned - time.time()))
    result = {"complete": error is None and released, "error": error, "release_error": release_error, "released": released, "active_unreleased_service": None if released else str(stage), "collector_status": terminal, "planned": 192, "elapsed_seconds": time.time() - started, "no_retry": True}
    s.write(output / "OWNER_TERMINAL.json", result); signal.setitimer(signal.ITIMER_REAL, 0)
    for sig, handler in previous.items(): signal.signal(sig, handler)
    return result


if __name__ == "__main__":
    parser = argparse.ArgumentParser(); parser.add_argument("command", choices=("verify", "run")); parser.add_argument("--output", type=Path, default=s.ATTEMPT); args = parser.parse_args()
    if args.command == "verify": print(s.verify()["identity"])
    else:
        result = execute(args.output); print(result); raise SystemExit(0 if result["complete"] else 1)
