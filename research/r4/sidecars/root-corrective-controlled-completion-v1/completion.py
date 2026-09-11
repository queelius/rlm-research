"""Complete only the never-attempted controlled stage; preserve the failed parent."""
import argparse
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import signal
import sys
import time

ROOT = Path(__file__).resolve().parent
SOURCE = ROOT.parent / "root-corrective-reduction-sft-v1"
OLD_OUTPUT = SOURCE / "outputs/attempt-001"
OUTPUT = ROOT / "outputs/attempt-001"
NATIVE = Path("/project/alex_phd/envs/prime-rl-5990b1b/bin/python")
PINS = {
    "owner.py": "7bf0277c33eec649b7ccde985cb808bd881b9a0f5e6c23d0e3488d76d9eaa4e9",
    "binding.py": "b257d7d654330be0ccaac2ded2934effec3e643d6ab404cd2ec9fc28c1e7c1af",
    "collect.py": "b0c760dec08d3cb54db297da4daf89c47eef42592d0a9c9d4e50f2d6ab497443",
    "study.py": "5e509fcc7285acb443b43f81491377eb76dbfd58e5d194e9c676a641a16246de",
    "READY.json": "90f5df76eca02dbdfd47bb3e3ab0afb391e96f8acde95ee042731911ac7f0999",
    "inputs/CONTROLLED_PLAN.json": "6f91b09e954570e314d06a7b69c2eb24d9e901010f9e906d85acb572ad6d1de0",
    "outputs/attempt-001/training-corrective/SELECTION.json": "bc47670b233d3059cd3786f4cc9e8e8f4783085b4a1d26bb7ff1a814f1ae77fd",
    "outputs/attempt-001/OWNER_TERMINAL.json": "3b749f6d014ce1ef5b9cbc0ce55b34e5edd64a0d0f042d43fb5fd59abe1d7610",
}


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def read(path):
    return json.loads(Path(path).read_text())


def write(path, value):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("x") as handle:
        json.dump(value, handle, indent=2, sort_keys=True)
        handle.write("\n")


def check_original_inventory(terminal, control_exists):
    rows = [r for r in terminal["readout_inventory"]
            if r["arm"] == "corrective" and r["mode"] == "controlled"]
    if terminal["complete"] or control_exists or len(rows) != 16 or \
            len({r["coordinate_id"] for r in rows}) != 16 or any(r["recorded"] for r in rows):
        raise ValueError("completion is restricted to the entire never-attempted controlled panel")


def qualified():
    for name, expected in PINS.items():
        if sha(SOURCE / name) != expected:
            raise ValueError("original fixed source changed: " + name)
    check_original_inventory(read(OLD_OUTPUT / "OWNER_TERMINAL.json"),
                             (OLD_OUTPUT / "corrective/controlled").exists())
    sys.path.insert(0, str(SOURCE))
    spec = importlib.util.spec_from_file_location("controlled_completion_original_owner",
                                                SOURCE / "owner.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    module.s.verify()
    module.b.selected("corrective")
    return module


def verify():
    ready = read(ROOT / "READY.json")
    for path, expected in ready["source_sha256"].items():
        if sha(path) != expected:
            raise ValueError("controlled-completion input changed: " + path)
    qualified()
    return ready


def collector_argv(stage, output, deadline):
    if Path(output).resolve() != OUTPUT.resolve():
        raise ValueError("only the explicit fresh completion namespace is authorized")
    return [str(NATIVE), str(SOURCE / "collect.py"), "--mode", "controlled",
            "--plan", "CONTROLLED_PLAN.json", "--start", "0", "--stop", "16",
            "--binding", str(stage / "BINDING.json"), "--endpoint",
            str(stage / "service/endpoint-original.json"), "--output",
            str(output / "controlled"), "--deadline", str(deadline)]


def inventory(rows, output):
    result = []
    for row in rows:
        path = output / "controlled" / row["id"] / "RESULT.json"
        value = read(path) if path.exists() else {}
        result.append({"coordinate": row, "path": str(path), "recorded": path.exists(),
                       "available": value.get("available", False),
                       "reward": value.get("reward"),
                       "failure_artifact": str(path.with_name("FAILURE.json"))})
    return result


def execute(output):
    if output.resolve() != OUTPUT.resolve() or output.exists():
        raise ValueError("fresh controlled-completion attempt only; no overwrite/retry")
    ready = verify()
    old = qualified()
    old.s.runtime()  # Qualified private credential/device plumbing before creating output.
    gpu = os.environ.get("CUDA_VISIBLE_DEVICES", "")
    if not gpu or "," in gpu:
        raise ValueError("MAIN must assign one exclusively owned GPU")
    suite = old.dependencies()
    binding = old.b.binding("corrective", old.b.selected("corrective"))
    rows = read(SOURCE / "inputs/CONTROLLED_PLAN.json")
    started = time.time()
    work, owned = started + 480, started + 570
    output.mkdir(parents=True, exist_ok=False)
    stage = output / "service-corrective"
    stage.mkdir()
    write(output / "OWNER_RUN.json", {
        "started_epoch": started, "work_deadline_epoch": work, "owned_deadline_epoch": owned,
        "outer_seconds": 660, "cleanup_seconds": 90, "gpu": gpu,
        "ready_sha256": sha(ROOT / "READY.json"), "original_attempt_unchanged": str(OLD_OUTPUT),
        "old_controlled_unattempted": True, "planned": len(rows), "no_training": True,
        "no_free_reroll": True, "credential_value_logged": False})
    error = release_error = None
    released = False

    def expired(sig, _frame):
        raise TimeoutError("controlled-completion owned deadline or termination: " + str(sig))

    previous = {sig: signal.signal(sig, expired)
                for sig in (signal.SIGINT, signal.SIGTERM, signal.SIGALRM)}
    signal.setitimer(signal.ITIMER_REAL, max(0.001, owned - time.time()))
    try:
        suite.start_service(stage, binding, min(work, time.time() + 180))
        deadline = min(work, time.time() + 300)
        argv = collector_argv(stage, output, deadline)
        suite.command(stage, "controlled", argv, max(0.001, deadline - time.time()), deadline)
        terminal = read(output / "controlled/TERMINAL.json")
        if terminal["planned"] != 16 or terminal["recorded"] != 16:
            raise ValueError("collector did not preserve every planned coordinate")
    except BaseException as caught:
        error = {"type": type(caught).__name__, "message": str(caught)[:1600]}
    finally:
        try:
            suite.release_service(stage)
            released = True
        except BaseException as caught:
            release_error = {"type": type(caught).__name__, "message": str(caught)[:1600]}
        signal.setitimer(signal.ITIMER_REAL, 0)
        for sig, previous_handler in previous.items():
            signal.signal(sig, previous_handler)
    result = {"complete": error is None and release_error is None and released,
              "error": error, "release_error": release_error, "released": released,
              "elapsed_seconds": time.time() - started, "planned": 16,
              "inventory": inventory(rows, output), "no_training": True, "no_retry": True,
              "original_primary_inventory_unchanged": True,
              "interpretation": ready["interpretation"], "main_owns_gpu_and_lock": True}
    write(output / "OWNER_TERMINAL.json", result)
    return result


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("command", choices=("verify", "run"))
    parser.add_argument("--output", type=Path, default=OUTPUT)
    args = parser.parse_args()
    if args.command == "verify":
        ready = verify()
        print(json.dumps({"ready_sha256": sha(ROOT / "READY.json"), "planned": 16,
                          "gpu_calls": 0, "source_count": len(ready["source_sha256"])}))
    else:
        result = execute(args.output)
        print(json.dumps({k: result[k] for k in ("complete", "error", "release_error",
                                                "elapsed_seconds", "planned")}))
        raise SystemExit(0 if result["complete"] else 1)
