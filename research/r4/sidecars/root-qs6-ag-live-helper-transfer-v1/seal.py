"""Final bounded CPU qualification, source inventory and immutable READY."""

import importlib.metadata
import json
import os
import platform
import subprocess
import sys
import time

import prepare
import study


def package_version(name):
    try:
        return importlib.metadata.version(name)
    except importlib.metadata.PackageNotFoundError:
        return None  # For example PEFT belongs to the separate training environment, not this native owner.


def main():
    if os.environ.get("CUDA_VISIBLE_DEVICES") != "" or (study.ROOT / "READY.json").exists():
        raise ValueError("CUDAhidden unused source seal required")
    rebuilt = prepare.build()
    for name, value in zip(("PUBLIC.json", "HOST_GOLD.json", "PLANS.json", "HELPER_REQUESTS.json", "PROVENANCE.json", "MANIFEST.json"), rebuilt):
        if json.loads(json.dumps(value)) != study.read(study.INPUTS / name):
            raise ValueError("pinned exclusion/data rebuild differs: " + name)
    fixtures = study.ROOT / "cpu/fixture-001"
    argv = [str(study.NATIVE), "-m", "pytest", "-q", "-s", "-p", "no:cacheprovider",
            "--basetemp", str(fixtures), "test_transfer.py"]
    receipt_path = study.ROOT / "CPU_TESTS_V2.json"
    if receipt_path.exists():
        # Continue only the interrupted source-inventory step; never rerun/erase passed fixtures.
        receipt = study.read(receipt_path)
        if receipt["returncode"] != 0 or receipt["argv"] != argv or not fixtures.is_dir():
            raise ValueError("existing CPU qualification is not the exact passed fixture")
    else:
        if fixtures.exists():
            raise ValueError("CPU fixture directory already exists; preserve prior receipt")
        fixtures.parent.mkdir(parents=True, exist_ok=True)
        started = time.time()
        result = subprocess.run(argv, cwd=study.ROOT, env={**os.environ, "CUDA_VISIBLE_DEVICES": "",
            "PYTHONDONTWRITEBYTECODE": "1"}, capture_output=True, text=True, timeout=180)
        receipt = {"argv": argv, "returncode": result.returncode, "stdout": result.stdout,
            "stderr": result.stderr, "elapsed_seconds": time.time() - started,
            "scientific_model_calls": 0, "gpu_calls": 0, "authored_native_responses": 8,
            "real_owned_CPU_containers": 2, "two_fixture_definitions_three_cases": True,
            "data_rebuild": "all six artifacts equal after JSON key normalization; fixed exclusion snapshot",
            "fixture_sources_unsealed_during_test": True}
        study.write_x(receipt_path, receipt)
        if result.returncode:
            raise SystemExit(result.stdout + result.stderr)
    closure = {}
    for path in (study.EVIDENCE / "READY_V2.json", study.SHORT / "READY_V2.json",
                 study.HELPER / "READY_RL_STEP8.json", study.DATA_SOURCE / "DATA_READY.json"):
        ready = study.read(path)
        for key in ("closure_sha256", "source_sha256", "artifact_sha256", "input_sha256"):
            for source, pin in ready.get(key, {}).items():
                if isinstance(pin, str):
                    if source in closure and closure[source] != pin:
                        raise ValueError("predecessor closures disagree: " + source)
                    closure[source] = pin
        closure[str(path)] = study.sha(path)
    # Include the actual loaded sidecar seams, including the current native lifecycle facade.
    key = "STRICT_RLM_CALIBRATION_API_KEY"
    previous = os.environ.get(key)
    if previous is None:
        os.environ[key] = "cpu-source-inventory-no-model-call"
    try:
        study.sources()[2].lifecycle()  # constructors/closure only, never start_service
    finally:
        if previous is None:
            os.environ.pop(key, None)
    for module in list(sys.modules.values()):
        path = getattr(module, "__file__", None)
        if path and str(path).startswith(str(study.SIDE)) and str(path).endswith(".py"):
            closure[str(__import__("pathlib").Path(path).resolve())] = study.sha(path)
    for helper_arm in ("c32", "rl_step8"):
        binding = study.read(study.INPUTS / ("BINDING_" + helper_arm + ".json"))
        for value in binding["models"].values():
            checkpoint = __import__("pathlib").Path(value["path"])
            for name in ("adapter_model.safetensors", "adapter_config.json", "state.json", "STEP_COMMIT.json", "EVAL_BINDING.json"):
                if (checkpoint / name).is_file():
                    closure[str(checkpoint / name)] = study.sha(checkpoint / name)
    for path in sorted(study.ROOT.iterdir()):
        if path.is_file() and path.suffix in (".py", ".md", ".json"):
            closure[str(path)] = study.sha(path)
    for path in sorted(study.INPUTS.iterdir()):
        closure[str(path)] = study.sha(path)
    for path in sorted(fixtures.rglob("*.json")):
        closure[str(path)] = study.sha(path)
    for path, pin in closure.items():
        if study.sha(path) != pin:
            raise ValueError("predecessor source changed before seal: " + path)
    inventory = {"closure_sha256": dict(sorted(closure.items())), "python": sys.version,
        "executable": sys.executable, "platform": platform.platform(),
        "packages": {name: package_version(name) for name in
                     ("torch", "transformers", "peft", "vllm", "xgrammar", "verifiers", "numpy", "pyarrow")}}
    study.write_x(study.ROOT / "SOURCE_INVENTORY.json", inventory)
    closure[str(study.ROOT / "SOURCE_INVENTORY.json")] = study.sha(study.ROOT / "SOURCE_INVENTORY.json")
    ready = {"schema": "root-qs6-ag-live-helper-transfer-ready-v1", "status": "CPU_READY_MAIN_REVIEW_REQUIRED",
        "planned_episodes": 48, "unique_contexts": 8, "unique_records": 128, "paired_queries": 16,
        "arms": list(study.ARMS), "root_sha256": study.ROOT_SHA,
        "helper_c32_sha256": study.CHILD_SHA, "helper_rl8_seed1_sha256": study.RL_SHA,
        "owner_seconds": study.CAP, "external_seconds": study.OUTER_CAP,
        "maximum_physical_calls": 416, "maximum_helper_calls": 128,
        "output": str(study.ATTEMPT), "prior_best_seed_selection": False,
        "root_prefixes_identical_between_helper_arms": True, "host_solver_staged": False,
        "logical_wrapper_native_likelihood": None, "all_helper_calls_live": True,
        "two_sequential_two_LoRA_services": True, "runtime_kernel_and_clean_release_required": True,
        "closure_sha256": dict(sorted(closure.items())),
        "argv": [str(study.NATIVE), str(study.ROOT / "owner.py"), "run", "--owner-seconds", str(study.CAP)],
        "prepared_epoch": time.time()}
    ready["identity"] = study.digest(ready)
    study.write_x(study.ROOT / "READY.json", ready)
    print(json.dumps({"ready_sha256": study.sha(study.ROOT / "READY.json"), "identity": ready["identity"],
                      "pins": len(closure), "argv": ready["argv"], "cpu_elapsed": receipt["elapsed_seconds"]}))


if __name__ == "__main__":
    main()
