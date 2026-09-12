"""CPU-only tests, source closure and conditional READY seal."""

import datetime
import json
import os
import subprocess

import sft_study as study


def main():
    if os.environ.get("CUDA_VISIBLE_DEVICES") != "" or study.ATTEMPT.exists() or (study.ROOT / "READY.json").exists():
        raise ValueError("CPU-only unused output/READY required")
    command = [str(study.TRAIN_PYTHON), "-m", "pytest", "-q", str(study.ROOT / "test_sft.py")]
    tested = subprocess.run(
        command,
        cwd=study.ROOT,
        env={**os.environ, "CUDA_VISIBLE_DEVICES": "", "PYTHONDONTWRITEBYTECODE": "1"},
        capture_output=True,
        text=True,
        timeout=120,
    )
    if tested.returncode:
        raise RuntimeError(tested.stdout + tested.stderr)
    study.write_x(
        study.ROOT / "CPU_TESTS.json",
        {
            "command": command,
            "returncode": tested.returncode,
            "stdout": tested.stdout,
            "stderr": tested.stderr,
            "CUDA_VISIBLE_DEVICES": "",
            "actual_pinned_tokenizer_teacher_schedule": True,
            "actual_torch_optimizer_contract": True,
            "local_owner_training_import_boundary": True,
        },
    )
    manifest = study.read(study.DATA / "inputs/MANIFEST.json")
    if study.sha(study.DATA / "inputs/MANIFEST.json") != study.DATA_MANIFEST_SHA256:
        raise ValueError("broader AG manifest changed")
    closure = {}
    for field in ("artifacts_sha256", "source_closure_sha256"):
        for path, expected in manifest[field].items():
            if study.sha(path) != expected:
                raise ValueError("broader AG source changed: " + path)
            closure[path] = expected
    source_ready_path = study.SOURCE / "READY.json"
    source_ready = study.read(source_ready_path)
    for path, expected in source_ready["closure_sha256"].items():
        if study.sha(path) != expected:
            raise ValueError("qualified c32/source closure changed: " + path)
        if path in closure and closure[path] != expected:
            raise ValueError("closure conflict: " + path)
        closure[path] = expected
    closure[str(source_ready_path)] = study.sha(source_ready_path)
    design = study.SIDE.parent / "ideas/2026-09-12-agnews-eightstep-sft-comparator.md"
    direct = [
        study.ROOT / name
        for name in (
            "sft_study.py", "train_sft.py", "owner.py", "test_sft.py", "seal.py",
            "QUESTION.yaml", "README.md", "EVALUATION_INTERFACE.md", "CPU_TESTS.json"
        )
    ] + [study.DATA / "inputs/MANIFEST.json", design]
    closure.update({str(path): study.sha(path) for path in direct})
    study.write_x(
        study.ROOT / "SOURCE_INVENTORY.json",
        {
            "schema": "agnews-eightstep-answer-only-sft-source-inventory-v1",
            "closure_sha256": dict(sorted(closure.items())),
            "training_source": str(study.DATA / "inputs/TRAIN_PUBLIC.json"),
            "host_gold_by_step": [str(study.DATA / f"inputs/step-{step:03d}/HOST_GOLD.json") for step in range(1, 9)],
            "heldout_loaded_by_trainer": False,
            "no_gpu_launched": True,
        },
    )
    closure[str(study.ROOT / "SOURCE_INVENTORY.json")] = study.sha(study.ROOT / "SOURCE_INVENTORY.json")
    environment = json.loads(
        subprocess.run(
            [str(study.TRAIN_PYTHON), "-c", "import json,sys,torch,transformers,peft;print(json.dumps({'python':sys.version,'torch':torch.__version__,'transformers':transformers.__version__,'peft':peft.__version__}))"],
            capture_output=True, text=True, check=True, timeout=30,
            env={**os.environ, "CUDA_VISIBLE_DEVICES": ""},
        ).stdout
    )
    ready = {
        **study.plan(),
        "created_at": datetime.datetime.now(datetime.UTC).isoformat(),
        "closure_sha256": dict(sorted(closure.items())),
        "source_inventory_sha256": study.sha(study.ROOT / "SOURCE_INVENTORY.json"),
        "question_sha256": study.sha(study.ROOT / "QUESTION.yaml"),
        "design_sha256": study.sha(design),
        "environment": environment,
        "gpu_launched": False,
    }
    ready["identity"] = study.digest(ready)
    study.write_x(study.ROOT / "READY.json", ready)
    study.verify()
    print(
        json.dumps(
            {
                "ready_sha256": study.sha(study.ROOT / "READY.json"),
                "identity": ready["identity"],
                "pins": len(closure),
                "tests": tested.stdout.strip(),
                "command": ready["command"],
            },
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
