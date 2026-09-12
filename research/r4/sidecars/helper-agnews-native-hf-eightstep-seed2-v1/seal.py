"""Seal thin CPU-qualified seed-only reuse; no GPU admission is granted here."""
import datetime
import json
import os
import subprocess
import core
import reuse


def main():
    if os.environ.get("CUDA_VISIBLE_DEVICES") != "" or (core.ROOT/"READY.json").exists():
        raise ValueError("fresh CPU-only seal required")
    original = core.read(reuse.PRIOR/"READY.json")
    repair = core.read(reuse.PRIOR/"READY_V2.json")
    closure = dict(repair["closure_sha256"])
    for name in ("READY_V2.json","READY.json","outputs/attempt-001/FINAL_RESULT.json"):
        closure[str(reuse.PRIOR/name)] = core.sha(reuse.PRIOR/name)
    outcome = core.SIDE.parent/"analyses/helper-agnews-eightstep-live-audit-2026-09-12/outcomes/RAW_AUDIT-003.json"
    closure[str(outcome)] = core.sha(outcome)
    for path, expected in closure.items():
        if core.sha(path) != expected:
            raise ValueError("predecessor closure changed: " + path)
    env_source = core.load_bound("ag_seed2_environment_source",core.SOURCE/"seal.py",
        {"ag_study":core.original,"eval_owner":core.load_bound("ag_seed2_env_eval",core.SOURCE/"eval_owner.py",{"ag_study":core.original})})
    environment = {"native":env_source.environment(core.original.NATIVE),
                   "training":env_source.environment(core.original.TRAIN_PYTHON)}
    if environment != original["environment"]:
        raise ValueError("replica Python/package versions differ from qualified original")
    core.write_x(core.ROOT/"ENVIRONMENT.json",environment)
    for pattern in ("*.py","*.md","*.json","inputs/*.json","inputs/step-*/*.json"):
        for path in core.ROOT.glob(pattern):
            closure[str(path)] = core.sha(path)
    core.write_x(core.ROOT/"SOURCE_INVENTORY.json",dict(closure_sha256=dict(sorted(closure.items())),
        unchanged_numeric_sources=reuse.PINS,predecessor_sources_unchanged=True,GPU_launched=False))
    closure[str(core.ROOT/"SOURCE_INVENTORY.json")] = core.sha(core.ROOT/"SOURCE_INVENTORY.json")
    ready = {**{k:v for k,v in original.items() if k not in (
        "identity","created_utc","closure_sha256","command","output","evaluation_interface",
        "source_one_step_tiny_positive_prioritizes_seed_replication")},
        "schema":"agnews-native-hf-eightstep-seed-replica-ready-v1",
        "created_utc":datetime.datetime.now(datetime.UTC).isoformat(),
        "output":str(core.ATTEMPT),"status":"CPU_READY_MAIN_ADMISSION_REQUIRED",
        "command":[str(core.original.NATIVE),str(core.ROOT/"owner.py"),"run","--owner-seconds","5000",
                   "--admission-json",str(core.ROOT/"ADMISSION.json")],
        "seed_namespace":"agnews-broader8-seed2-20260912",
        "native_seed_range":[20260912900000,20260912901023],"hf_initial_seed":20260912910000,
        "same1024_records_and_order":True,"same_research_exposed512_endpoint":True,
        "training_seed_replication_not_new_dataset":True,
        "only_behavioral_change":"fresh native/HF training seeds; unchanged policy/data/objective",
        "qualified_v2_alias_scope_preserved":True,
        "environment":environment,"closure_sha256":dict(sorted(closure.items()))}
    ready["identity"] = core.digest(ready)
    core.write_x(core.ROOT/"READY.json",ready)
    core.verify()
    fixture = dict(authority="MAIN",cpu_fixture=True,not_gpu_authority=True,
        training_ready_sha256=core.sha(core.ROOT/"READY.json"),
        decision="APPROVE_TRAINING_SEED_REPLICATION",endpoint="fixed-step8-versus-c32-on-same-exposed512",
        start="fresh-original-c32-not-seed1-continuation",prior_seed1_heldout512_consulted=True,
        replica_checkpoint_evaluated_before_training_complete=False,
        data_manifest_sha256=ready["data_manifest_sha256"],seed_namespace=ready["seed_namespace"],
        reason="synthetic CPU-only actual admission function regression, never GPU authority",
        reviewed_evidence_sha256={str(p):core.sha(p) for p in (
            reuse.PRIOR/"READY_V2.json",reuse.PRIOR/"outputs/attempt-001/FINAL_RESULT.json",outcome)})
    fixture_path = core.ROOT/"CPU_FIXTURE_ADMISSION.json"
    core.write_x(fixture_path,fixture)
    command = [str(core.original.NATIVE),str(core.ROOT/"owner.py"),"check-admission",
               "--admission-json",str(fixture_path)]
    result = subprocess.run(command,env={**os.environ,"CUDA_VISIBLE_DEVICES":"","PYTHONDONTWRITEBYTECODE":"1"},
                            capture_output=True,text=True,timeout=120)
    receipt = dict(command=command,returncode=result.returncode,stdout=result.stdout,stderr=result.stderr,
        ready_sha256=core.sha(core.ROOT/"READY.json"),fixture_sha256=core.sha(fixture_path),
        source_sealed_before_actual_CPU_qualification=True,GPU_launched=False)
    core.write_x(core.ROOT/"CPU_ADMISSION.json",receipt)
    if result.returncode:
        raise RuntimeError(result.stdout+result.stderr)
    core.verify()
    print(json.dumps(dict(READY_sha256=core.sha(core.ROOT/"READY.json"),identity=ready["identity"],
        closure_files=len(closure),actual_admission_receipt_sha256=core.sha(core.ROOT/"CPU_ADMISSION.json"),
        passed=True,GPU_launched=False),sort_keys=True))


if __name__ == "__main__":
    main()
