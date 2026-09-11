"""Freeze the CPU-qualified bounded-view32 package; MAIN alone may launch it."""
import os
import subprocess
import time

import bv_study as s


def main():
    if (s.ROOT / "READY.json").exists():
        raise FileExistsError("bounded-view READY already exists")
    started = time.time()
    s.write(s.ROOT / "BINDING_sft24.json", s.binding())
    tests = ["test_inputs.py", "test_overlay.py", "test_entry.py", "test_owner.py"]
    argv = [
        str(s.NATIVE), "-m", "pytest", "-q", "-p", "no:cacheprovider", *tests,
        "--basetemp", str(s.ROOT / "qualification-final-001"),
    ]
    begin = time.time()
    result = subprocess.run(
        argv,
        cwd=s.ROOT,
        env={**os.environ, "CUDA_VISIBLE_DEVICES": "", "PYTHONDONTWRITEBYTECODE": "1"},
        capture_output=True,
        text=True,
        timeout=240,
    )
    s.write(
        s.ROOT / "CPU_REPORT.json",
        dict(
            argv=argv,
            returncode=result.returncode,
            stdout=result.stdout,
            stderr=result.stderr,
            elapsed_seconds=time.time() - begin,
            scientific_model_calls=0,
            gpu_calls=0,
            authored_native_root_calls=2,
            authored_native_child_calls=1,
            actual_root_child_root_policy_view_and_raw_harvest=True,
            actual_owner_service_wrapper_intercepted=True,
            full_raw_ledger_harvested_only_after_policy_rollout=True,
            synthetic_fixture_not_scientific_evidence=True,
            red_findings=[
                "actual composed engine truncator accepts one argument, not a configurable cap",
                "executor session directory was not task-finalizer-readable; task cwd is the mounted audit seam",
            ],
        ),
    )
    if result.returncode:
        raise RuntimeError(result.stdout + result.stderr)

    sources = {**s.base_ready["source_sha256"], str(s.BASE / "READY.json"): s.BASE_READY_SHA}
    inputs = {**s.base_ready["input_sha256"]}
    gate = s.read(s.ROOT / "inputs/MECHANISM_GATE.json")
    inputs.update(gate["source_sha256"])
    provenance = s.read(s.ROOT / "inputs/PROVENANCE.json")
    inputs.update(provenance["source_sha256"])
    inputs.update(provenance["seed_inventory_sha256"])
    idea = s.STORE / "ideas/2026-09-10-bounded-native-observation-view-feasibility.md"
    sources[str(idea)] = s.sha(idea)
    sources.update(
        {str(path): s.sha(path) for path in s.ROOT.iterdir() if path.is_file() and path.name != "READY.json"}
    )
    inputs.update({str(path): s.sha(path) for path in (s.ROOT / "inputs").glob("*.json")})
    inputs.update(
        {str(path): s.sha(path) for path in (s.ROOT / "qualification-final-001").rglob("*") if path.is_file()}
    )
    for path, pin in {**sources, **inputs}.items():
        s.dose.check(path, pin)
    ready = dict(
        schema="bounded-observation-view-ready-v1",
        status="CPU_READY_MAIN_ACCEPTANCE_REQUIRED",
        source_sha256=sources,
        input_sha256=inputs,
        owner_argv=[str(s.NATIVE), str(s.ROOT / "bv_owner.py"), "run", "--output", str(s.ATTEMPT)],
        verify_argv=[str(s.NATIVE), str(s.ROOT / "bv_owner.py"), "verify"],
        work_seconds=1650,
        owned_seconds=1770,
        outer_seconds=1800,
        startup_seconds=180,
        collection_seconds=1440,
        harvest_seconds=30,
        release_seconds=120,
        outer_margin_seconds=30,
        planned_full=32,
        paired_blocks=8,
        parent_clusters=4,
        sizes=[128, 256],
        return_arms=["B", "C"],
        view_bytes=[4096, 20000],
        policy="sft24",
        model_action_tokens=2048,
        model_context_tokens=8192,
        no_training=True,
        no_gold_or_reducer_injection=True,
        full_raw_analysis_ledger_not_policy_visible=True,
        conditional_mechanism_gate_satisfied=True,
        main_launch_only=True,
        created_epoch=time.time(),
    )
    ready["identity"] = s.digest(ready)
    s.write(s.ROOT / "READY.json", ready)
    s.verify()
    print(
        dict(
            ready_sha256=s.sha(s.ROOT / "READY.json"),
            identity=ready["identity"],
            sources=len(sources),
            inputs=len(inputs),
            tests=result.stdout,
            elapsed_seconds=time.time() - started,
        )
    )


if __name__ == "__main__":
    main()
