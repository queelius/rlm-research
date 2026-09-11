"""Parent-accepted grammar160 using unchanged authenticated dual-LoRA lifecycle."""
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
STORE = ROOT.parents[1]
SUITE = ROOT.parent / "leaf-post-sft-suite-v1"
COORDINATOR = STORE / "operations/2026-09-09-queued-successors/coordinator.py"
PYTHON = "/project/alex_phd/envs/prime-rl-5990b1b/bin/python"
OLD_ALIAS = "strict-rlm-qwen3-4b-role-sft-selected-v1"
INDEXED_ALIAS = "strict-rlm-qwen3-4b-leaf-indexed-final-v1"
PINNED = {
    SUITE / "suite.py": "6fa84af486efbf5bad17352553d36cd590fb6f7e386c2273df27dd8deb7c8fd1",
    SUITE / "MANIFEST.json": "4f37ffa367c6e50f27034060543caf93680d5239f2d5a09fe56cb817ab84f642",
    COORDINATOR: "7d3294241939297741f26ca657782f757e43b520a717a17a6edac378f32873c1",
    ROOT / "driver.py": "17d46458875e2fdbb3f03d951ef6659ae54165cb3d420b5f4678886eb1857f67",
}


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def read(path):
    return json.loads(Path(path).read_text())


def load(name, path):
    if sha(path) != PINNED[path]:
        raise ValueError("qualified source changed: " + str(path))
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


def load_suite():
    if sha(SUITE / "MANIFEST.json") != PINNED[SUITE / "MANIFEST.json"]:
        raise ValueError("qualified lifecycle manifest changed")
    suite = load("grammar_owned_private_suite", SUITE / "suite.py")
    suite.verify()
    return suite


def service_binding(weights, weights_path):
    aliases = {"old_sft": OLD_ALIAS, "indexed_final": INDEXED_ALIAS}
    models = {aliases[w]: {"path": row["path"], "adapter_sha256": row["model_sha256"],
                          "config_sha256": row["config_sha256"]} for w, row in weights["models"].items()}
    return {"schema": "old-selected-and-indexed-fixed-final-semantic-dual-binding-v1", "models": models,
        "role_map": {"root": OLD_ALIAS, "children": [OLD_ALIAS, INDEXED_ALIAS]},
        "selection_path": str(weights_path), "selection_sha256": sha(weights_path),
        "selection_semantics": "old c32de validation-selected; indexed fixed-final epoch2/step204; no transfer-based weight choice",
        "descriptor_filename_semantics": {"endpoint-original.json": "old_sft", "endpoint-selected.json": "indexed_final"},
        "post_training_test_consulted_for_binding": False}


def execute(directory, suite, weights, weights_path=ROOT / "WEIGHTS.json"):
    started = time.time()
    directory.mkdir(parents=True, exist_ok=False)
    deadline = started + 2580
    output = ROOT / "outputs/attempt-001"
    suite.c.write_once(directory / "WRAPPER_ATTEMPT.json", {"started_epoch": started,
        "overall_deadline_epoch": started + 2700, "work_deadline_epoch": deadline,
        "cleanup_reserve_seconds": 120, "collector_output": str(output), "weights_sha256": sha(weights_path)})
    try:
        suite.start_service(directory, service_binding(weights, weights_path), deadline)
        bound = directory / "GRAMMAR-BOUND.json"
        bind = [suite.PYTHON, str(ROOT / "driver.py"), "bind", "--old-endpoint",
                str(directory / "service/endpoint-original.json"), "--indexed-endpoint",
                str(directory / "service/endpoint-selected.json"), "--spec-path", str(bound)]
        run = [suite.PYTHON, str(ROOT / "driver.py"), "run", "--spec-path", str(bound),
               "--output-dir", str(output), "--overall-start-epoch", str(started)]
        suite.command(directory, "grammar-bind", bind, 120, deadline)
        suite.command(directory, "grammar-run", run, 1830, deadline)
    except BaseException as error:
        suite.c.write_once(directory / "ERROR.json", {"type": type(error).__name__, "message": str(error), "epoch": time.time()})
        raise
    finally:
        try:
            suite.release_service(directory)
        finally:
            elapsed = time.time() - started
            suite.c.write_once(directory / "FINISH.json", {"elapsed_seconds": elapsed,
                "overall2700_exceeded": elapsed > 2700,
                "owned_release_marker": str(directory / "SERVICE_STOPPED.json"),
                "owned_release_completed": (directory / "SERVICE_STOPPED.json").exists(),
                "collector_status_path": str(output / "STATUS.json")})


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--operation-root", type=Path)
    parser.add_argument("--directory", type=Path)
    parser.add_argument("--verify", action="store_true")
    args = parser.parse_args()
    http = load("grammar_owned_private_http", ROOT / "driver.py")
    http.verify(read(ROOT / "SPEC.json"))
    suite = load_suite()
    if args.verify:
        print(json.dumps({"qualified_sources_verified": True, "http_ready_exists": (ROOT / "READY.json").exists(),
                          "owned_ready_exists": (ROOT / "OWNED_READY.json").exists(), "gpu_calls": 0}), flush=True)
        return
    if args.operation_root is None or args.directory is None:
        parser.error("explicit new operation root and unused owned directory required")
    operation = args.operation_root.resolve()
    directory = args.directory.resolve()
    if not directory.is_relative_to(operation):
        raise ValueError("owned directory must belong to the accepted operation")
    op = load("grammar_owned_private_acceptance", COORDINATOR)
    op.ROOT = operation
    plan = op.read(operation / "PLAN.json")
    op.validate_acceptance(op.read(operation / "ACCEPTANCE.json"), plan)
    required = {str(ROOT / n) for n in ["owned.py", "READY.json", "WEIGHTS.json", "OWNED_READY.json"]}
    if not required <= set(plan["acceptance_source_paths"]):
        raise ValueError("parent acceptance omits semantic weight/wrapper readiness")
    actual_argv = [sys.executable, str(Path(__file__).resolve()), *sys.argv[1:]]
    if not any(job["argv"] == actual_argv for job in plan["jobs"]):
        raise ValueError("this exact wrapper command was not accepted")
    for key, want in plan["required_inherited_environment"].items():
        if os.environ.get(key) != want:
            raise ValueError("wrong inherited environment: " + key)
    ready = read(ROOT / "OWNED_READY.json")
    for path, expected in ready["source_sha256"].items():
        if sha(path) != expected:
            raise ValueError("owned readiness source changed: " + path)
    weights = read(ROOT / "WEIGHTS.json")
    if weights != http.authenticate_weights():
        raise ValueError("actual fixed final checkpoint identity changed")

    def interrupted(sig, frame):
        raise KeyboardInterrupt(f"owned grammar signal{sig}; release authenticated service")

    signal.signal(signal.SIGTERM, interrupted)
    signal.signal(signal.SIGINT, interrupted)
    execute(directory, suite, weights)


if __name__ == "__main__":
    main()
