"""One parent-launched padding control; unchanged authenticated service lifecycle."""
import argparse
import hashlib
import importlib.util
import json
import os
import signal
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent
SUITE = ROOT.parent / "leaf-post-sft-suite-v1"
PYTHON = "/project/alex_phd/envs/prime-rl-5990b1b/bin/python"
PINNED = {
    SUITE / "suite.py": "6fa84af486efbf5bad17352553d36cd590fb6f7e386c2273df27dd8deb7c8fd1",
    SUITE / "MANIFEST.json": "4f37ffa367c6e50f27034060543caf93680d5239f2d5a09fe56cb817ab84f642",
}


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def load_suite():
    for p, expected in PINNED.items():
        if sha(p) != expected:
            raise ValueError("qualified lifecycle changed: " + str(p))
    loader = importlib.util.spec_from_file_location("padding_private_owned_suite", SUITE / "suite.py")
    suite = importlib.util.module_from_spec(loader)
    sys.modules[loader.name] = suite
    loader.loader.exec_module(suite)
    suite.verify()
    return suite


def service_binding(weights, weights_path, weights_sha):
    import study as s
    old = weights["models"]["old_sft"]
    return {"schema": "padding-control-single-old-adapter-binding-v1",
        "models": {s.ALIAS: {"path": old["path"], "adapter_sha256": old["model_sha256"],
                             "config_sha256": old["config_sha256"]}},
        "role_map": {"root": s.ALIAS, "children": [s.ALIAS]},
        "selection_path": str(weights_path), "selection_sha256": weights_sha,
        "selection_semantics": "Existing old c32de validation-selected child only; all128 inputs frozen before outputs",
        "post_training_test_consulted_for_binding": False}


def work_deadline(started):
    return started + 1680


def collection_command_cap(started, now):
    left = work_deadline(started) - now
    if left <= 0:
        raise TimeoutError("owned work deadline; preserve120-second cleanup reserve")
    return min(930, left)


def execute(directory, suite, weights, started):
    import study as s
    directory.mkdir(parents=True, exist_ok=False)
    output = ROOT / "outputs/attempt-001"
    s.write_once(directory / "WRAPPER_ATTEMPT.json", {"started_epoch": started,
        "overall_deadline_epoch": started + 1800, "work_deadline_epoch": work_deadline(started),
        "cleanup_reserve_seconds": 120, "collection_cap_seconds": 900, "collector_output": str(output),
        "weights_sha256": sha(ROOT / "WEIGHTS.json"), "service_model_count": 1})
    release_completed = False
    try:
        suite.start_service(directory, service_binding(weights, ROOT / "WEIGHTS.json", sha(ROOT / "WEIGHTS.json")), work_deadline(started))
        argv = [PYTHON, str(ROOT / "driver.py"), "run", "--endpoint",
            str(directory / "service/endpoint-original.json"), "--output-dir", str(output),
            "--overall-start-epoch", str(started)]
        suite.command(directory, "padding128-run", argv, collection_command_cap(started, time.time()), work_deadline(started))
    except BaseException as error:
        s.write_once(directory / "ERROR.json", {"type": type(error).__name__, "message": str(error), "epoch": time.time()})
        raise
    finally:
        try:
            suite.release_service(directory)
            release_completed = True
        finally:
            elapsed = time.time() - started
            s.write_once(directory / "FINISH.json", {"elapsed_seconds": elapsed,
                "overall1800_exceeded": elapsed > 1800, "owned_release_completed": release_completed,
                "collector_status_path": str(output / "STATUS.json")})


def main():
    started = time.time()
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--directory", type=Path, default=ROOT / "owned/attempt-001")
    parser.add_argument("--verify", action="store_true")
    args = parser.parse_args()
    import driver
    driver.verify(driver.s.read(ROOT / "SPEC.json"))
    ready = driver.s.read(ROOT / "READY.json")
    driver.s.anchor.sst.verify_hashes(ready["source_sha256"])
    weights = driver.s.read(ROOT / "WEIGHTS.json")
    if driver.weights() != weights:
        raise ValueError("old-adapter weight closure changed")
    suite = load_suite()
    if args.verify:
        print(json.dumps({"qualified_sources_verified": True, "single_adapter_binding": service_binding(weights, ROOT / "WEIGHTS.json", sha(ROOT / "WEIGHTS.json")), "gpu_calls": 0}), flush=True)
        return
    directory = args.directory.resolve()
    if directory.parent != ROOT / "owned" or directory.exists() or (ROOT / "outputs/attempt-001").exists():
        raise ValueError("one unused owned directory in this namespace and absent attempt output required")
    gpu = os.environ.get("CUDA_VISIBLE_DEVICES", "")
    if not gpu or "," in gpu or not os.environ.get("STRICT_RLM_CALIBRATION_API_KEY"):
        raise ValueError("parent must assign one exclusively owned GPU and the qualified API-key environment")
    def interrupted(sig, frame):
        raise KeyboardInterrupt(f"padding owned signal {sig}; release authenticated owned service")
    signal.signal(signal.SIGTERM, interrupted)
    signal.signal(signal.SIGINT, interrupted)
    execute(directory, suite, weights, started)


if __name__ == "__main__":
    main()
