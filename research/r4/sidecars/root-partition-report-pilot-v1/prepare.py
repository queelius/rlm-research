"""CPU-only immutable freeze using local tokenizer, never a model load."""

import importlib.metadata
import inspect
import json
import os
import platform
import subprocess
from pathlib import Path

import pilot
from run import ROOT, prompt_ids, read, save, sha

SIDE = ROOT.parent
STORE = ROOT.parents[1]
TRAIN = "/project/alex_phd/repos/rlm-bootstrap/.worktrees/a100-lora-roundtrip/gpu/training/.venv/bin/python"


def main():
    if os.environ.get("CUDA_VISIBLE_DEVICES") != "" or (ROOT / "READY.json").exists():
        raise ValueError("requires CPU-only fresh preparation")
    prior_weights = SIDE / "leaf-local-cue-replay-v1/WEIGHTS.json"
    if sha(prior_weights) != "7cde937f907b013321851e6e26e3d2af2fe96010ef757d03b109ab66c771e1d4":
        raise ValueError("prior weight manifest changed")
    weights = read(prior_weights)
    for path, identity in weights["stat_identity"].items():
        st = Path(path).stat()
        assert [st.st_size, st.st_mtime_ns, st.st_ino] == identity
    from transformers import AutoTokenizer
    from transformers.generation.utils import GenerationMixin
    from transformers.models.qwen3.modeling_qwen3 import Qwen3ForCausalLM

    tok = AutoTokenizer.from_pretrained(
        weights["checkpoint"]["path"], local_files_only=True, trust_remote_code=False
    )
    coordinates = pilot.plan()
    oracle = []
    for coordinate in coordinates:
        coordinate["static_requests"] = pilot.static_requests(coordinate)
        for request in coordinate["static_requests"]:
            request["frozen_prompt_token_ids"] = prompt_ids(tok, request["messages"])
        full, lossy = pilot.projections(
            [
                {"id": f"cpu-{i}", "content": json.dumps(chunk)}
                for i, chunk in enumerate(coordinate["chunks"])
            ],
            coordinate["chunks"],
        )
        oracle.append(
            {
                "id": coordinate["id"],
                "exact_nonrecursive_answer": pilot.solve(coordinate["records"]),
                "full_incidence_implied_answer": pilot.solve(
                    sum([report["evidence"] for report in full["reports"]], [])
                ),
                "local_winners_implied_answer": sorted(
                    set(sum([report["local_winners"] for report in lossy["reports"]], []))
                ),
                "chunk_sizes": list(map(len, coordinate["chunks"])),
                "gpu_calls": 0,
            }
        )
    seeds = sorted(
        set(pilot.GENERATOR_SEEDS + [seed + i for seed in pilot.SAMPLING_SEEDS for i in range(3)])
    )
    paths = {STORE / "analyses/research-factory-2026-09-09/CATALOG.json"}
    for directory in SIDE.iterdir():
        if directory.is_dir() and directory != ROOT:
            for pattern in (
                "*SPEC*.json",
                "*READY*.json",
                "*RECIPE*.json",
                "*CAMPAIGN*.json",
                "*SEED*.json",
                "*PANEL*.json",
                "inputs/*PLAN*.json",
            ):
                paths.update(p for p in directory.glob(pattern) if p.is_file())
    scan = subprocess.run(
        ["rg", "-n", r"\b(" + "|".join(map(str, seeds)) + r")\b", *map(str, sorted(paths))],
        text=True,
        capture_output=True,
        timeout=60,
    )
    if scan.returncode != 1:
        raise ValueError(
            "seed collision or scan failure: " + scan.stdout[:1000] + scan.stderr[:1000]
        )
    tests = subprocess.run(
        [TRAIN, "-m", "pytest", "-q", "-p", "no:cacheprovider", str(ROOT / "test_pilot.py")],
        text=True,
        capture_output=True,
        timeout=60,
    )
    if tests.returncode:
        raise ValueError(tests.stdout + tests.stderr)
    save(ROOT / "PLAN.json", coordinates)
    save(ROOT / "WORLDS.json", pilot.worlds())
    save(ROOT / "CPU_ORACLE.json", oracle)
    save(ROOT / "WEIGHTS.json", weights)
    save(
        ROOT / "SEED_AUDIT.json",
        {
            "seeds": seeds,
            "paths": list(map(str, sorted(paths))),
            "scan_exit": scan.returncode,
            "matches": scan.stdout,
            "scope": "Named sidecar spec/ready/recipe/campaign/seed/panel/input-plan catalogs plus research factory CATALOG; not global or pretraining freshness.",
        },
    )
    sources = {str(prior_weights): sha(prior_weights)}
    for path, expected in weights["weight"]["files_sha256"].items():
        if not path.endswith(".safetensors"):
            if sha(path) != expected:
                raise ValueError("model auxiliary file changed: " + path)
            sources[path] = expected
    manifest = Path(weights["checkpoint"]["path"]) / "local-research-manifest.json"
    assert sha(manifest) == weights["checkpoint"]["manifest_sha256"]
    sources[str(manifest)] = sha(manifest)
    for cls in (GenerationMixin, Qwen3ForCausalLM, type(tok)):
        path = inspect.getfile(cls)
        sources[path] = sha(path)
    versions = {
        key: importlib.metadata.version(key)
        for key in ("torch", "transformers", "tokenizers", "safetensors")
    }
    recipe = {
        "question_id": "rq:sufficient-interface",
        "checkpoint": weights["checkpoint"],
        "versions": versions,
        "python": platform.python_version(),
        "python_executable": TRAIN,
        "work_seconds": 1650,
        "cleanup_seconds": 120,
        "outer_seconds": 1800,
        "dtype": "bfloat16",
        "attention_backend": "sdpa",
        "planned_actual_calls": 88,
        "coordinate_count": 8,
        "world_count": 4,
        "sampling_seeds": pilot.SAMPLING_SEEDS,
        "generator_seeds": pilot.GENERATOR_SEEDS,
        "training": False,
        "adapters": None,
        "resume": False,
        "grammar": None,
        "primary_metric": "paired full-versus-ordinary exact-set correctness; both-partitions-correct worlds",
    }
    save(ROOT / "RECIPE.json", recipe)
    save(
        ROOT / "QUALIFICATION.json",
        {
            "tests": {"exit": tests.returncode, "stdout": tests.stdout, "stderr": tests.stderr},
            "model_loaded": False,
            "gpu_calls": 0,
            "native_static_prompts": 64,
            "max_static_input_tokens": max(
                len(r["frozen_prompt_token_ids"]) for c in coordinates for r in c["static_requests"]
            ),
            "exact_oracle": oracle,
            "no_model_outcome_selection": True,
        },
    )
    for path in ROOT.iterdir():
        if path.is_file():
            sources[str(path)] = sha(path)
    save(
        ROOT / "READY.json",
        {
            "status": "CPU_READY_MAIN_ACCEPTANCE_REQUIRED",
            "source_sha256": sources,
            "question_id": "rq:sufficient-interface",
            "metric": recipe["primary_metric"],
            "launch_argv": [
                TRAIN,
                str(ROOT / "run.py"),
                "--output",
                str(ROOT / "outputs/attempt-001"),
            ],
            "verify_argv": [TRAIN, str(ROOT / "run.py"), "--verify"],
            "cwd": str(ROOT),
            "outer_seconds": 1800,
            "work_seconds": 1650,
            "cleanup_seconds": 120,
            "checkpoint_policy": "immutable each physical request/output and each 11-call episode; no automatic retry/resume",
            "gpu_shape": "one A10040GB",
            "artifact_directory": str(ROOT / "outputs/attempt-001"),
            "model_loaded": False,
            "gpu_calls": 0,
        },
    )
    print(json.dumps({"ready_sha256": sha(ROOT / "READY.json"), "planned_calls": 88}))


if __name__ == "__main__":
    main()
