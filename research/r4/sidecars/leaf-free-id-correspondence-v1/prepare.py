"""Freeze the approved CPU-only factorial and its runnable ownership closure."""

import json
import os
import subprocess
from copy import deepcopy
from pathlib import Path

import study as s


def main():
    for name in ("DATA.json", "REQUESTS.json", "PROMPT_IDS.json", "DISPATCH.json",
                 "WEIGHTS.json", "SPEC.json", "CPU_TESTS.json", "READY.json"):
        if (s.ROOT / name).exists():
            raise FileExistsError("fresh preparation requires absent " + name)

    data = s.build_data()
    s.write_once(s.ROOT / "DATA.json", data)
    design = s.build_design(data)
    source_spec = s.read(s.SOURCE / "SPEC.json")
    if s.sha(s.SOURCE / "SPEC.json") != s.SOURCE_SPEC_SHA256:
        raise ValueError("frozen fresh96 SPEC changed")

    requests = {}
    rendered = {}
    source_rows = {r["id"]: r for r in source_spec["design"]["plan"]}
    for row in design["plan"]:
        body = s.make_request(design, row)
        old_id = row["source_coordinate_id"]
        old_body = source_spec["requests"][old_id]
        if row["decoder"] == "exact" and s.serialize(body) != s.serialize(old_body):
            raise ValueError("exact arm no longer reproduces fresh96 request")
        if row["decoder"] == "free" and {k: v for k, v in old_body.items()
                                           if k != "structured_outputs"} != body:
            raise ValueError("free arm changes more than structured_outputs")
        old_row = source_rows[old_id]
        for key in ("dataset", "context_index", "arm", "seed", "repeat"):
            if row[key] != old_row[key]:
                raise ValueError("source coordinate join changed")
        requests[row["id"]] = body
        rendered[row["id"]] = deepcopy(source_spec["design"]["rendered_prompts"][old_id])
    design["rendered_prompts"] = rendered
    s.write_once(s.ROOT / "REQUESTS.json", requests)
    s.write_once(s.ROOT / "PROMPT_IDS.json", rendered)
    s.write_once(s.ROOT / "DISPATCH.json", {
        "max_concurrent_calls": 4,
        "order": [{"dispatch_order": r["dispatch_order"], "id": r["id"],
                   "dataset": r["dataset"], "context_index": r["context_index"],
                   "seed": r["seed"], "arm": r["arm"], "decoder": r["decoder"]}
                  for r in design["plan"]],
        "pairing": "Free/exact adjacent; first decoder alternates by inherited source batch parity.",
    })
    weights = {
        "schema": "released-qwen3-4b-no-adapter-binding-v1",
        "models": s.MODELS,
        "selected_model": s.MODEL,
        "adapter": None,
        "weight_stat_identity": {
            path: identity for path, identity in source_spec["weight_stat_identity"].items()
            if s.MODELS[s.MODEL]["path"] in path
        },
        "source_manifest_sha256": s.MODELS[s.MODEL]["manifest_sha256"],
    }
    s.write_once(s.ROOT / "WEIGHTS.json", weights)

    source_paths = [
        s.ROOT / name for name in ("study.py", "driver.py", "service.py", "owner.py",
                                   "service_wrapper_v2.py", "lifecycle_adapter.py",
                                   "test_study.py", "test_owner.py", "DESIGN.md", "RUNBOOK.md",
                                   "DATA.json", "REQUESTS.json", "PROMPT_IDS.json", "DISPATCH.json",
                                   "WEIGHTS.json")
    ] + [
        s.SOURCE / name for name in ("study.py", "driver.py", "service.py", "owned.py",
                                     "DATA.json", "SPEC.json", "REQUESTS.json", "PROMPT_IDS.json",
                                     "CPU_QUALIFICATION.json", "WEIGHTS.json")
    ] + [
        s.SIDE / "leaf-qwen35-identity-v1/source/serve.py",
        s.SIDE / "leaf-post-sft-suite-v1/suite.py",
        s.SIDE / "root-rlvr-campaign-v1/campaign_lifecycle_v2.py",
        s.SIDE / "runtime-an27-5780-v1/credential_preflight.py",
        s.SIDE / "runtime-an27-5780-v1/LIFECYCLE_READY_V2.json",
    ]
    sources = {str(path): s.sha(path) for path in source_paths}
    spec = {
        "schema": "leaf-free-id-correspondence-spec-v1",
        "question": "Does the forced source-ID correspondence advantage survive when released Qwen3-4B must emit IDs freely?",
        "design": design,
        "requests": requests,
        "request_sha256": {key: s.digest(value) for key, value in requests.items()},
        "ordered_request_sha256": {key: __import__("hashlib").sha256(s.serialize(value).encode()).hexdigest()
                                   for key, value in requests.items()},
        "source_sha256": sources,
        "weight_stat_identity": weights["weight_stat_identity"],
        "model": s.MODELS[s.MODEL],
        "frozen_before_inference": True,
        "budget": {"real_calls": 96, "workers": 4, "max_tokens_per_call": 3072,
                   "collector_seconds": 1500, "shared_work_seconds": 1680,
                   "owned_seconds": 1770, "outer_seconds": 1800},
        "scoring": {
            "primary": "Strict positional labels and full-shape validity on the planned denominator.",
            "completed_invalid": "Observed policy failure; zero strict correct labels, never NULL.",
            "infrastructure_missing": "NULL with [0,64] per-call correctness bounds.",
            "secondary": "Literal emitted-ID alignment, duplicate/missing/extra IDs, field order, conditional label-only position accuracy.",
            "forbidden": ["ID-based reordering", "answer repair", "prefix rescue", "invalid-only selection"],
        },
        "scope": "Exact reused fresh96 AG/SST contexts and seeds; exposed paired study, not an independent fresh replication.",
        "control_caveat": "Within-arm free-minus-exact isolates decoder support. Across free arms, matching IDs versus constant/plain also changes emitted content and generation difficulty.",
        "prior_overlap": "Closest free-ID study used trained adapters and batch-local TREC IDs; no released no-adapter Qwen3 test on these contexts is complete.",
    }
    spec["spec_id"] = s.digest(spec)
    s.write_once(s.ROOT / "SPEC.json", spec)

    command = ["/project/alex_phd/envs/prime-rl-5990b1b/bin/python", "-m", "pytest", "-q",
               "test_study.py", "test_owner.py"]
    environment = {**os.environ, "CUDA_VISIBLE_DEVICES": "", "PYTHONDONTWRITEBYTECODE": "1"}
    result = subprocess.run(command, cwd=s.ROOT, env=environment, capture_output=True,
                            text=True, timeout=60)
    s.write_once(s.ROOT / "CPU_TESTS.json", {"argv": command, "returncode": result.returncode,
                "stdout": result.stdout, "stderr": result.stderr, "gpu_calls": 0,
                "model_calls": 0})
    if result.returncode:
        raise ValueError("focused CPU tests failed")

    ready_sources = dict(sources)
    for path in (s.ROOT / "SPEC.json", s.ROOT / "CPU_TESTS.json", s.ROOT / "prepare.py"):
        ready_sources[str(path)] = s.sha(path)
    ready = {
        "status": "CPU_READY_FOR_MAIN_ACCEPTANCE_NOT_LAUNCHED",
        "schema": "leaf-free-id-correspondence-ready-v1",
        "spec_sha256": s.sha(s.ROOT / "SPEC.json"),
        "source_sha256": ready_sources,
        "output": str(s.ROOT / "outputs/attempt-001"),
        "argv": [str(Path(command[0])), str(s.ROOT / "owner.py"), "run", "--output",
                 str(s.ROOT / "outputs/attempt-001")],
        "verify_argv": [str(Path(command[0])), str(s.ROOT / "owner.py"), "verify"],
        "credential": "MAIN privately exports nonempty STRICT_RLM_CALIBRATION_API_KEY before verify/run; value is never serialized.",
        "service_wrapper": str(s.ROOT / "service_wrapper_v2.py"),
        "runtime_lifecycle_manifest": str(s.SIDE / "runtime-an27-5780-v1/LIFECYCLE_READY_V2.json"),
        "actual_wrapper_identity_symmetric": True,
        "gpu_calls": 0,
        "model_calls": 0,
        "main_owns_gpu_lock_acceptance_and_launch": True,
    }
    ready["identity"] = s.digest(ready)
    s.write_once(s.ROOT / "READY.json", ready)
    print(json.dumps({"ready_sha256": s.sha(s.ROOT / "READY.json"),
                      "identity": ready["identity"], "tests": result.stdout.strip()}))


if __name__ == "__main__":
    main()

