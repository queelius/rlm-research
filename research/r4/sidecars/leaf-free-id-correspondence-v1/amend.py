"""Write the additive scoring/deadline/source-verification V2 launch manifest."""

import json
import os
import subprocess
from pathlib import Path

import study as s


OLD_READY_SHA256 = "d2500d2502028cf2596e59247376a8157c2cffe9a34ef422484aeefaa47904d4"
FRESH_SPEC = s.SOURCE / "SPEC.json"
MODEL_ROOT = Path(s.MODELS[s.MODEL]["path"])


def auxiliary_sources():
    """Select inherited non-tensor model and inference-template files from the frozen source."""
    source = s.read(FRESH_SPEC)["source_sha256"]
    chosen = {}
    for path, expected in source.items():
        candidate = Path(path)
        model_aux = candidate.parent == MODEL_ROOT and candidate.suffix != ".safetensors"
        inference_template = candidate.name == "inference-replica0.json"
        launcher = candidate.name == "launch.py" and "strict-rlm-temperature-adherence-v1" in path
        if model_aux or inference_template or launcher:
            if s.sha(candidate) != expected:
                raise ValueError("inherited auxiliary source changed: " + path)
            chosen[path] = expected
    required = {
        "config.json", "generation_config.json", "model.safetensors.index.json",
        "tokenizer.json", "tokenizer_config.json", "vocab.json", "merges.txt",
        "local-research-manifest.json",
    }
    present = {Path(path).name for path in chosen if Path(path).parent == MODEL_ROOT}
    if not required <= present:
        raise ValueError("missing inherited model auxiliary pins: " + repr(sorted(required - present)))
    if "inference-replica0.json" not in {Path(path).name for path in chosen}:
        raise ValueError("missing inherited inference-template pin")
    return chosen


def main():
    for name in ("SCORING_AMENDMENT.json", "CPU_TESTS_V2.json", "READY_V2.json"):
        if (s.ROOT / name).exists():
            raise FileExistsError("additive preparation requires absent " + name)
    if s.sha(s.ROOT / "READY.json") != OLD_READY_SHA256:
        raise ValueError("frozen unaccepted READY V1 changed")

    auxiliary = auxiliary_sources()
    amendment = {
        "schema": "leaf-free-id-correspondence-amendment-v2",
        "status": "ADDITIVE_SUPERSEDING_LAUNCH_CONTRACT",
        "preserved_ready_v1_sha256": OLD_READY_SHA256,
        "launch_manifest": "READY_V2.json",
        "headline_primary": (
            "Contract-valid correct labels on the planned denominator. Matching and constant arms "
            "require exact expected tags and ordered fields; plain requires its complete ordered "
            "label array. Completed contract-invalid outputs score zero; infrastructure-missing "
            "calls remain NULL with bounds."
        ),
        "diagnostics": (
            "Full-shape validity, positional label accuracy, emitted-ID position matches, wrong, "
            "duplicate, missing and extra IDs, omissions, and field order remain separate. No ID "
            "reordering or answer repair is permitted."
        ),
        "primary_justification": (
            "The causal question is whether usable correspondence survives free ID emission, so "
            "correct labels with unusable IDs cannot satisfy the primary mapping contract."
        ),
        "collection_deadline": "min(shared absolute work deadline, collection start + 1500 seconds)",
        "auxiliary_source_sha256": auxiliary,
        "tensor_verification": (
            "The preserved V1 stat identity remains the tensor check; this amendment deliberately "
            "does not rescan full tensor contents."
        ),
        "gpu_calls": 0,
        "model_calls": 0,
    }
    s.write_once(s.ROOT / "SCORING_AMENDMENT.json", amendment)

    command = ["/project/alex_phd/envs/prime-rl-5990b1b/bin/python", "-m", "pytest", "-q",
               "test_study.py", "test_owner.py", "test_scoring_v2.py", "test_owner_v2.py"]
    environment = {**os.environ, "CUDA_VISIBLE_DEVICES": "", "PYTHONDONTWRITEBYTECODE": "1"}
    result = subprocess.run(command, cwd=s.ROOT, env=environment, capture_output=True,
                            text=True, timeout=60)
    s.write_once(s.ROOT / "CPU_TESTS_V2.json", {
        "argv": command, "returncode": result.returncode, "stdout": result.stdout,
        "stderr": result.stderr, "gpu_calls": 0, "model_calls": 0,
    })
    if result.returncode:
        raise ValueError("focused V2 CPU tests failed")

    old_ready = s.read(s.ROOT / "READY.json")
    sources = dict(old_ready["source_sha256"])
    sources.update(auxiliary)
    for name in ("READY.json", "scoring_v2.py", "driver_v2.py", "owner_v2.py",
                 "test_scoring_v2.py", "test_owner_v2.py", "SCORING_AMENDMENT.json",
                 "CPU_TESTS_V2.json", "amend.py"):
        path = s.ROOT / name
        sources[str(path)] = s.sha(path)
    output = s.ROOT / "outputs/attempt-001"
    python = "/project/alex_phd/envs/prime-rl-5990b1b/bin/python"
    ready = {
        "status": "CPU_READY_FOR_MAIN_ACCEPTANCE_NOT_LAUNCHED",
        "schema": "leaf-free-id-correspondence-ready-v2",
        "supersedes_for_launch": OLD_READY_SHA256,
        "spec_sha256": old_ready["spec_sha256"],
        "amendment_sha256": s.sha(s.ROOT / "SCORING_AMENDMENT.json"),
        "source_sha256": sources,
        "output": str(output),
        "argv": [python, str(s.ROOT / "owner_v2.py"), "run", "--output", str(output)],
        "verify_argv": [python, str(s.ROOT / "owner_v2.py"), "verify"],
        "credential": old_ready["credential"],
        "service_wrapper": old_ready["service_wrapper"],
        "runtime_lifecycle_manifest": old_ready["runtime_lifecycle_manifest"],
        "actual_wrapper_identity_symmetric": True,
        "collection_deadline": "min(shared absolute work deadline, collection start + 1500 seconds)",
        "headline_primary": amendment["headline_primary"],
        "gpu_calls": 0,
        "model_calls": 0,
        "main_owns_gpu_lock_acceptance_and_launch": True,
    }
    ready["identity"] = s.digest(ready)
    s.write_once(s.ROOT / "READY_V2.json", ready)
    print(json.dumps({"ready_v2_sha256": s.sha(s.ROOT / "READY_V2.json"),
                      "identity": ready["identity"], "tests": result.stdout.strip(),
                      "direct_auxiliary_pins": len(auxiliary)}))


if __name__ == "__main__":
    main()
