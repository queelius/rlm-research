"""CPU-only source/evidence seal, then conditional updated-evaluator seal."""

import datetime
import os
import subprocess

import ag_study as study
import eval_owner


def environment(python):
    program = (
        "import sys,json,importlib.metadata as m; "
        "names=['torch','numpy','transformers','peft','xgrammar','vllm']; "
        "installed={d.metadata['Name'].lower():d.version for d in m.distributions()}; "
        "print(json.dumps({'python':sys.version,'executable':sys.executable,"
        "'packages':{name:installed.get(name) for name in names}}))"
    )
    result = subprocess.run(
        [str(python), "-c", program],
        capture_output=True,
        text=True,
        check=True,
        timeout=30,
        env={**os.environ, "CUDA_VISIBLE_DEVICES": ""},
    )
    return study.json.loads(result.stdout)


def main():
    if os.environ.get("CUDA_VISIBLE_DEVICES") != "" or (study.ROOT / "READY.json").exists():
        raise ValueError("CPU-only unused READY required")
    sources = [
        study.SOURCE / "READY.json",
        study.SIDE / "root-qs6-leaf-rloo-fresh-batch-invariant-one-update-v2/READY.json",
        study.QUAL2 / "READY_V2.json",
        study.EVAL / "READY_C32_V2.json",
    ]
    closure = {}
    for path in sources:
        ready = study.read(path)
        for raw, expected in ready["closure_sha256"].items():
            if study.sha(raw) != expected:
                raise ValueError("sealed source changed: " + raw)
            if raw in closure and closure[raw] != expected:
                raise ValueError("source closure conflict: " + raw)
            closure[raw] = expected
        closure[str(path)] = study.sha(path)
    manifest = study.read(study.FROZEN / "MANIFEST.json")
    for field in ("artifacts_sha256", "source_closure_sha256"):
        for raw, expected in manifest[field].items():
            if study.sha(raw) != expected:
                raise ValueError("frozen data manifest changed: " + raw)
            closure[raw] = expected
    audit = study.read(study.ROOT / "inputs/BUILD_AUDIT.json")
    config_path = study.old.BATCH_ROOT / "outputs/attempt-003/service/service/inference.json"
    from owner import context_receipt

    context = context_receipt(study.read(config_path), audit)
    context["historical_actual_config_sha256"] = study.sha(config_path)
    context["live_runtime_rechecked_before_collection"] = True
    study.write_x(study.ROOT / "CONTEXT_BOUND_SOURCE.json", context)
    tests = []
    for python, name in (
        (study.NATIVE, "test_seed_replica.py"),
        (study.NATIVE, "test_native.py"),
        (study.TRAIN_PYTHON, "test_train.py"),
    ):
        command = [str(python), "-m", "pytest", "-q", str(study.ROOT / name)]
        result = subprocess.run(
            command,
            capture_output=True,
            text=True,
            timeout=120,
            cwd=study.ROOT,
            env={**os.environ, "CUDA_VISIBLE_DEVICES": ""},
        )
        tests.append(
            {
                "command": command,
                "returncode": result.returncode,
                "stdout": result.stdout,
                "stderr": result.stderr,
            }
        )
        if result.returncode:
            raise RuntimeError(result.stdout + result.stderr)
    study.write_x(
        study.ROOT / "CPU_TESTS.json",
        {
            "CUDA_VISIBLE_DEVICES": "",
            "tests": tests,
            "known_upstream_warnings": "native XGrammar import may emit SWIG deprecation warnings",
            "actual_native_four_key_mask_fixture": True,
            "actual_tiny_hf_importance_failure_replay_failure_and_optimizer_update": True,
        },
    )
    versions = {"native": environment(study.NATIVE), "training": environment(study.TRAIN_PYTHON)}
    study.write_x(study.ROOT / "ENVIRONMENT.json", versions)
    direct = [
        study.QUAL / "study.py",
        study.QUAL / "owner.py",
        study.QUAL / "collect.py",
        study.QUAL2 / "collect.py",
        study.V1 / "leaf_math.py",
        study.V1 / "prepare.py",
        study.V1 / "train.py",
        study.FAST / "train.py",
        config_path,
        study.EVAL / "owner_v2.py",
        study.EVAL / "owner.py",
        study.EVAL / "study.py",
        study.EVAL / "prepare_eval.py",
        study.FROZEN / "MANIFEST.json",
        study.SIDE / "helper-hf-fourstep-unseen-eval-v1/fourstep_panel_study.py",
        study.SIDE.parent / "ideas/2026-09-12-agnews-native-hf-one-update.md",
    ]
    for pattern in ("*.py", "*.md", "*.yaml", "*.json", "inputs/*.json"):
        direct.extend(study.ROOT.glob(pattern))
    closure.update({str(path.resolve()): study.sha(path) for path in direct})
    study.write_x(
        study.ROOT / "SOURCE_INVENTORY.json",
        {
            "closure_sha256": dict(sorted(closure.items())),
            "training_source": str(study.FROZEN / "TRAIN_PUBLIC.json"),
            "heldout_only_for_readout": str(study.EVAL / "inputs/REQUESTS.json"),
            "no_gpu_launched": True,
        },
    )
    closure[str(study.ROOT / "SOURCE_INVENTORY.json")] = study.sha(
        study.ROOT / "SOURCE_INVENTORY.json"
    )
    ready = {
        **study.plan(),
        "created_at": datetime.datetime.now(datetime.UTC).isoformat(),
        "closure_sha256": dict(sorted(closure.items())),
        "environment": versions,
        "data_manifest_sha256": study.sha(study.FROZEN / "MANIFEST.json"),
        "question_sha256": study.sha(study.ROOT / "QUESTION.yaml"),
        "gpu_launched": False,
        "claim_boundary": "exploratory package; no established gain or isolated causal factor",
    }
    ready["identity"] = study.digest(ready)
    study.write_x(study.ROOT / "READY.json", ready)
    study.verify()
    eval_closure = {**closure, str(study.ROOT / "READY.json"): study.sha(study.ROOT / "READY.json")}
    eval_ready = {
        **eval_owner.plan(),
        "created_at": datetime.datetime.now(datetime.UTC).isoformat(),
        "closure_sha256": dict(sorted(eval_closure.items())),
        "training_ready_sha256": study.sha(study.ROOT / "READY.json"),
        "training_ready_identity": ready["identity"],
        "gpu_launched": False,
        "status": "CONDITIONAL_ON_FULLY_QUALIFIED_UPDATED",
    }
    eval_ready["identity"] = study.digest(eval_ready)
    study.write_x(study.ROOT / "EVAL_READY.json", eval_ready)
    eval_owner.verify(False)
    print(
        {
            "training_ready_sha256": study.sha(study.ROOT / "READY.json"),
            "training_identity": ready["identity"],
            "training_pins": len(closure),
            "eval_ready_sha256": study.sha(study.ROOT / "EVAL_READY.json"),
            "eval_identity": eval_ready["identity"],
            "tests": tests,
        }
    )


if __name__ == "__main__":
    main()
