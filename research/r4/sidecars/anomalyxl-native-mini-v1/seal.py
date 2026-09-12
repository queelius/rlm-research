"""CPU-only freeze and two focused fixtures; never loads model weights or starts a service."""

import importlib.metadata
import json
import os
import platform
import subprocess
import time
from pathlib import Path

import mini as m
import native_service


def command(argv):
    result = subprocess.run(argv, capture_output=True, text=True, timeout=180, check=False)
    receipt = {
        "argv": argv,
        "returncode": result.returncode,
        "stdout": result.stdout,
        "stderr": result.stderr,
    }
    if result.returncode:
        m.write(m.ROOT / "CPU_FAILURE.json", receipt)
        raise RuntimeError("CPU qualification command failed")
    return receipt


def main():
    if os.environ.get("CUDA_VISIBLE_DEVICES") != "" or (m.ROOT / "READY.json").exists():
        raise ValueError("CPU-only fresh seal required")
    began = time.time()
    panel = m.prepare()
    if len(panel) != 10 or len(m.read(m.ROOT / "inputs/SCHEDULE.json")) != 20:
        raise ValueError("fixed denominator differs")
    from prime_rl.configs.inference import InferenceConfig

    config = native_service.configuration(m.ATTEMPT / "service")
    InferenceConfig.model_validate(config)
    m.write(m.ROOT / "inputs/EXPECTED_SERVICE_CONFIG.json", config)
    inventory = []
    for row in panel:
        data = m.read(m.ROOT / "inputs/direct" / (row["id"] + ".json"))
        body = m.body([{"role": "user", "content": data["prompt"]}], 2048)
        inventory.append(
            {
                "row_id": row["id"],
                "prompt_tokens": len(body["token_ids"]),
                "request_sha256": m.digest(body),
                **data["view"],
            }
        )
    m.write(m.ROOT / "inputs/DIRECT_INVENTORY.json", inventory)
    test = command([str(m.NATIVE), "-m", "pytest", str(m.ROOT / "test_mini.py"), "-q"])
    ruff = "/project/alex_phd/repos/rlm/.venv/bin/ruff"
    project_config = str(m.REPO / "pyproject.toml")
    lint = command([ruff, "check", str(m.ROOT), "--config", project_config])
    formatting = command([ruff, "format", "--check", str(m.ROOT), "--config", project_config])
    versions = {
        name: importlib.metadata.version(name)
        for name in (
            "torch",
            "transformers",
            "vllm",
            "xgrammar",
            "numpy",
            "pyarrow",
            "ipython",
            "pydantic",
            "pytest",
        )
    }
    commits = {}
    prime = Path("/project/alex_phd/research-cache/repos/prime-rl")
    for name, path in [("TimeRLM", m.OFFICIAL), ("rlm", m.REPO), ("prime_rl", prime)]:
        commits[name] = {
            "head": command(["git", "-C", str(path), "rev-parse", "HEAD"])["stdout"].strip(),
            "status": command(["git", "-C", str(path), "status", "--porcelain"])["stdout"],
        }
    m.write(
        m.ROOT / "ENVIRONMENT.json",
        {
            "python": platform.python_version(),
            "executable": str(m.NATIVE),
            "resolved_executable": str(m.NATIVE.resolve()),
            "packages": versions,
            "git": commits,
            "cuda_visible_devices_during_seal": "",
            "installed_nothing": True,
            "scipy": "Absent; prompts explicitly restrict numerical libraries to NumPy/stdlib.",
            "gpu_qualification": "NOT RUN",
            "driver_library": native_service.DRIVER,
            "batch_invariant_flag": "0",
        },
    )
    m.write(
        m.ROOT / "CPU_RECEIPT.json",
        {
            "pytest": test,
            "ruff": lint,
            "format": formatting,
            "elapsed_seconds": time.time() - began,
            "scorer_completely_read_before_import": True,
            "scope": "Two focused fixtures; current real CPU executor, no native model server.",
        },
    )
    files = set(m.ROOT.glob("*.py")) | set(m.ROOT.glob("*.md"))
    files.update(p for p in (m.ROOT / "inputs").rglob("*") if p.is_file())
    files.update((m.ROOT / name) for name in ("CPU_RECEIPT.json", "ENVIRONMENT.json"))
    files.update(m.REPO.glob("src/rlm/**/*.py"))
    files.update(prime.glob("src/prime_rl/inference/**/*.py"))
    files.update(prime.glob("packages/prime-rl-configs/src/prime_rl/configs/**/*.py"))
    files.update(prime.glob("src/prime_rl/utils/**/*.py"))
    files.update(p for p in m.MODEL.iterdir() if p.is_file())
    files.update(
        [
            m.DATA,
            m.DATA_ROOT / "local-research-manifest.json",
            m.DATA_ROOT / "anomalyxl-precise/manifest.json",
            m.SCORER,
            m.OFFICIAL / "LICENSE",
            m.OFFICIAL / "environments/timeseries_qa/ts_datasets/anomalyxl.py",
            m.OFFICIAL / "environments/timeseries_qa/ts_datasets/anomalyxl_coarse.py",
            m.OFFICIAL / "environments/timeseries_qa/tests/test_scorer_parity.py",
            m.OFFICIAL / "anomalyXL/scripts/generate_anomalyxl_sweep.py",
            native_service.TEMPLATE,
            native_service.ENV_SOURCE,
            m.NATIVE.resolve(),
            m.NATIVE.parent / "inference",
            m.STORE / "shared/environments/timerlm-anomalyxl-31fcd847.json",
            m.STORE / "ideas/2026-09-12-anomalyxl-native-mini-pilot.md",
        ]
    )
    site = m.NATIVE.parent.parent / "lib/python3.12/site-packages"
    files.update(site.glob("vllm/model_executor/models/qwen3_5*.py"))
    files.update(
        [
            site / "vllm/model_executor/models/registry.py",
            site / "vllm/sampling_params.py",
            site / "vllm/__init__.py",
        ]
    )
    closure = {str(p): m.sha(p) for p in sorted(files)}
    model_manifest = m.read(m.MODEL / "local-research-manifest.json")
    for name, expected in model_manifest["files"].items():
        if closure[str(m.MODEL / name)] != expected:
            raise ValueError("cached model disagrees with acquisition manifest")
    if closure[str(m.DATA)] != "23659b11e7181f8aebeb96c4a7f396ea76d33a2ffb86ec66182e712fdcdf20af":
        raise ValueError("cached data differs from approved source")
    if commits["TimeRLM"]["head"] != "31fcd847b7cb37a1f1e6859b1dca7973ed0eae74":
        raise ValueError("official source commit changed")
    ready = {
        "schema": "anomalyxl-native-mini-ready-v1",
        "status": "CPU_READY_MAIN_REVIEW_REQUIRED",
        "identity": m.digest(closure),
        "closure_sha256": closure,
        "owner_argv": [str(m.NATIVE), str(m.ROOT / "owner.py"), "run", "--outer-seconds", "1100"],
        "output": str(m.ATTEMPT),
        "owner_cap_seconds": 1100,
        "external_cap_seconds": 1200,
        "episodes": 20,
        "research_call_cap": 50,
        "engineering_call_cap": 2,
        "episode_work_seconds": 45,
        "context_tokens": 8192,
        "aggregate_output_tokens": 2048,
        "inspection_output_tokens": 512,
        "inspection_limit": 3,
        "final_output_allowance": "2048 minus actual generated inspection tokens",
        "stop_token_ids": m.body([{"role": "user", "content": "{}"}], 1)["sampling_params"][
            "stop_token_ids"
        ],
        "native_runtime_qualification": "Pending real exact-model startup and "
        "two engineering calls; no fallback.",
        "scoring_amendment": "Unchanged official score_precise extracts JSON from prose; "
        "whole-response strict JSON is separate, no repair.",
        "information_access": "Direct fixed uniform subsample; Python full rounded numerical data.",
        "recursion": "Disabled. Iterative Python inspection is not tree-depth learning.",
        "runtime_caveat": "New Qwen3.5 BF16 eager serial service, batch-invariant flag0; "
        "no pooling with c32 flag1 counts.",
        "exposure": "Ten metadata-selected public synthetic cases; no training performed; "
        "not a confirmatory heldout panel.",
        "limitations": "Exploratory feasibility/headroom, not RL or TimeRLM reproduction. "
        "Worker process is not filesystem sandboxed.",
        "sealed_epoch": time.time(),
    }
    m.write(m.ROOT / "READY.json", ready)
    print(
        json.dumps(
            {
                "ready_sha256": m.sha(m.ROOT / "READY.json"),
                "identity": ready["identity"],
                "closure_files": len(closure),
                "elapsed_seconds": time.time() - began,
            }
        )
    )


if __name__ == "__main__":
    main()
