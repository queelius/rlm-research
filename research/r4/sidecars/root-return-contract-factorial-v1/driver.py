"""Parent-only owned dual-service factorial; CPU verify/prepare never launch a service."""

import argparse
import asyncio
import contextlib
import copy
import fcntl
import json
import os
import subprocess
import time
import urllib.request
from pathlib import Path

import study as s
import analysis
import campaign as coordinator
import campaign_lifecycle_v2 as lifecycle

c, capture = s.c, s.native.capture


@contextlib.contextmanager
def collector_adapters():
    q, base = capture.q, capture.base
    saved = q.make_context, q.request_metadata, base.with_prompt, base.crossover_metrics, base.summarize, base.STUDY
    q.make_context, q.request_metadata = capture.make_context, capture.native.request_metadata
    base.with_prompt, base.crossover_metrics = s.with_prompt, analysis.episode_metrics
    base.summarize, base.STUDY = analysis.summarize, s.ROOT.name
    try:
        yield
    finally:
        q.make_context, q.request_metadata, base.with_prompt, base.crossover_metrics, base.summarize, base.STUDY = saved


async def collect(spec_path, output):
    spec = s.verify_phase(spec_path)
    output = Path(output)
    audit = output.with_name(output.name + "-routing")
    if output.exists() or audit.exists():
        raise ValueError("new immutable capture paths required; no implicit retry")
    endpoint = spec["endpoint"]
    request = urllib.request.Request(endpoint["url"] + "/models",
        headers={"Authorization": "Bearer " + os.environ[endpoint["api_key_env"]]})
    with urllib.request.urlopen(request, timeout=15) as response:
        cards = {r["id"]: r for r in json.load(response)["data"]}
    for alias, model in spec["role_binding"]["models"].items():
        card = cards.get(alias, {})
        if Path(card.get("root", "")).resolve() != Path(model["path"]).resolve() or card.get("parent") != endpoint["renderer_model"]:
            raise ValueError("live /models alias/path/base differs from authenticated phase binding")
    os.environ["PATH"] = str(capture.q.ROOTLESS / "bin") + os.pathsep + os.environ.get("PATH", "")
    os.environ.setdefault("VERIFIERS_CACHE_DIR", "/project/alex_phd/cache/verifiers-prime")
    c.write_once(audit / "BINDING.json", {"binding": spec["role_binding"], "advertised": cards})
    with collector_adapters(), capture.installed_hooks(spec["role_binding"], audit):
        return await capture.base.run(argparse.Namespace(endpoint_url=None, output_dir=output, resume=False),
                                      copy.deepcopy(spec), s.make_tasks())


def verify_ready():
    spec = s.verify()
    lifecycle.verify_amendment()
    ready = c.read(s.ROOT / "READY.json")
    c.authenticate(ready["artifact_sha256"])
    if (ready["spec_sha256"] != c.file_hash(s.ROOT / "SPEC.json")
            or ready["driver_sha256"] != c.file_hash(Path(__file__)) or ready["planned"] != 96):
        raise ValueError("READY does not bind this exact study execution")
    proof = c.read(s.ROOT / "qualification-attempt-001/RESULT.json")
    if proof["provider_calls"] != 6 or proof["gpu_calls"] != 0 or proof["conditions"] != list(s.ARMS):
        raise ValueError("two-arm real CPU native qualification missing")
    return spec


def publish_ready():
    spec = s.verify()
    proof = c.read(s.ROOT / "qualification-attempt-001/RESULT.json")
    if proof["provider_calls"] != 6 or proof["gpu_calls"] != 0:
        raise ValueError("missing bounded CPU qualification")
    environment = {**os.environ, "CUDA_VISIBLE_DEVICES": "", "PYTHONDONTWRITEBYTECODE": "1"}
    command = [str(c.NATIVE_PYTHON), "-m", "unittest", "test_study", "-v"]
    started = time.time()
    result = subprocess.run(command, cwd=s.ROOT, env=environment, capture_output=True, text=True, timeout=120)
    c.write_once(s.ROOT / "FOCUSED_TESTS.json", {"command": command, "returncode": result.returncode,
        "stdout": result.stdout, "stderr": result.stderr, "seconds": time.time()-started, "gpu_calls": 0})
    if result.returncode:
        raise ValueError("focused tests failed; READY not published")
    files = [s.ROOT / "SPEC.json", s.ROOT / "FOCUSED_TESTS.json"]
    files += [p for p in (s.ROOT / "qualification-attempt-001").rglob("*.json") if p.is_file()]
    ready = {"schema": s.ROOT.name, "prepared_epoch": time.time(), "planned": 96,
        "spec_sha256": c.file_hash(s.ROOT / "SPEC.json"), "driver": str(s.ROOT / "driver.py"),
        "driver_sha256": c.file_hash(s.ROOT / "driver.py"), "python": str(c.NATIVE_PYTHON),
        "output": str(s.ROOT / "outputs/attempt-001"), "phase_order": spec["phase_order"],
        "global_cap_seconds": 3600, "model_or_gpu_calls_during_preparation": 0,
        "artifact_sha256": {str(p): c.file_hash(p) for p in files},
        "launch_command": f"PYTHONDONTWRITEBYTECODE=1 {c.NATIVE_PYTHON} {s.ROOT / 'driver.py'} run --output {s.ROOT / 'outputs/attempt-001'}",
        "environment": "Main must supply one exclusively assigned CUDA_VISIBLE_DEVICES and existing STRICT_RLM_CALIBRATION_API_KEY; values are not stored here.",
        "ownership": "run creates two owned dual-LoRA services serially and releases authenticated parents/observed descendants with frozen lifecycle V2; no attach/kill of unrelated service",
        "acceptance": "CPU ready only; main must inspect source before launch"}
    c.write_once(s.ROOT / "READY.json", ready)
    return ready


def run(output):
    spec = verify_ready()
    gpu = os.environ.get("CUDA_VISIBLE_DEVICES", "")
    if not gpu or "," in gpu or not os.environ.get("STRICT_RLM_CALIBRATION_API_KEY"):
        raise ValueError("main must assign one exclusive GPU and existing endpoint credential")
    output = Path(output).resolve()
    output.mkdir(parents=True, exist_ok=False)
    started = time.time()
    deadline = started + 3600
    c.write_once(output / "RUN.json", {"started_epoch": started, "deadline_epoch": deadline,
        "spec_sha256": c.file_hash(s.ROOT / "SPEC.json"), "ready_sha256": c.file_hash(s.ROOT / "READY.json"),
        "driver_sha256": c.file_hash(Path(__file__)), "gpu": gpu, "phase_order": spec["phase_order"],
        "scope": "inference only; no training; all source input coordinates frozen before launch"})
    lifecycle.install()
    s.native.binding_for = s.binding_for
    statuses, error = [], None
    try:
        for index, weight in enumerate(spec["phase_order"]):
            if time.time() >= deadline - 300:
                raise TimeoutError("global envelope lacks service/setup/cleanup reserve for next phase")
            service_dir = output / "services" / f"phase-{index}-{weight}"
            binding, endpoint = coordinator.start_service(service_dir, spec["policies"][weight], deadline-90)
            try:
                phase = output / f"phase-{weight}"
                phase.mkdir()
                cap = min(spec["phase_collection_cap_seconds"], deadline-time.time()-90)
                if cap <= 60:
                    raise TimeoutError("global envelope exhausted before native collection")
                bound = s.phase_spec(weight, binding, endpoint, phase / "CAPTURE_SPEC.json", cap)
                command = [str(c.NATIVE_PYTHON), str(Path(__file__).resolve()), "collect",
                    "--spec", str(phase / "CAPTURE_SPEC.json"), "--output", str(phase / "rollout")]
                c.write_once(phase / "COLLECT_COMMAND.json", {"command": command, "wall_cap": bound["wall_time_cap_seconds"], "gpu_visible_in_collector": False})
                coordinator.owned_command(command, phase / "collection.log", cap)
                status = c.read(phase / "rollout/STATUS.json")
                statuses.append({"weight": weight, **status})
                if status["recorded"] != 48 or status["stop_reason"] is not None:
                    raise RuntimeError("native phase incomplete/capped; retained, no retry or reward replacement")
            finally:
                lifecycle.stop_service(service_dir / "service")
    except BaseException as caught:
        error = {"type": type(caught).__name__, "message": str(caught)}
    terminal = {"complete": error is None, "error": error, "statuses": statuses,
        "elapsed_seconds": time.time()-started, "deadline_epoch": deadline,
        "owned_service_release_records": [str(p) for p in output.glob("services/*/SERVICE_STOPPED.json")],
        "global_cap_overrun_seconds": max(0, time.time()-deadline)}
    c.write_once(output / "TERMINAL.json", terminal)
    # Read-only projections after releasing the GPU never extend the GPU allocation.
    try:
        report = analysis.analyze(output)
        terminal["recorded"] = report["recorded"]
    except Exception as caught:
        c.write_once(output / "ANALYSIS_FAILURE.json", {"type": type(caught).__name__, "message": str(caught)})
    return terminal


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command", choices=("prepare", "publish-ready", "verify", "collect", "run"))
    parser.add_argument("--output", type=Path, default=s.ROOT / "outputs/attempt-001")
    parser.add_argument("--spec", type=Path)
    args = parser.parse_args()
    if args.command == "collect":
        raise SystemExit(asyncio.run(collect(args.spec, args.output)))
    if args.command == "run":
        with (s.ROOT / "COORDINATOR.lock").open("a") as lease:
            fcntl.flock(lease, fcntl.LOCK_EX | fcntl.LOCK_NB)
            result = run(args.output)
        print(json.dumps(result, sort_keys=True))
        raise SystemExit(0 if result["complete"] else 1)
    if args.command == "prepare":
        result = s.prepare()
    elif args.command == "publish-ready":
        result = publish_ready()
    else:
        result = verify_ready()
    print(json.dumps({"command": args.command, "planned": len(result.get("plan", [])) or result.get("planned"), "gpu_calls": 0}))
