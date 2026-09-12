"""Freeze singleton inventory, run focused CPU tests, and seal two independent arms."""

import json
import os
from pathlib import Path
import subprocess
import time

import study


def main():
    if os.environ.get("CUDA_VISIBLE_DEVICES") != "": raise ValueError("CPU-only preparation")
    outputs = {"c32": study.ROOT / "READY_C32.json",
        "reference_step4": study.ROOT / "READY_REFERENCE_STEP4.json"}
    if any(path.exists() for path in outputs.values()): raise FileExistsError("READY already exists")
    rows=study.schedule(); source_schedule=study.SIZE_SOURCE/"inputs/SCHEDULE.json"
    manifest={"schema":"helper-hf-singleton-policy-comparison-input-v1",
        "source_schedule":str(source_schedule),"source_schedule_sha256":study.sha(source_schedule),
        "selection":"batch_size == 1","calls":256,"predictions":256,
        "schedule_sha256":study.digest(rows),
        "coordinates":[{"call_id":row["call_id"],"dataset":row["dataset"],"record_id":row["ids"][0],
            "seed":row["body"]["sampling_params"]["seed"],"request_body_sha256":study.digest(row["body"])} for row in rows]}
    manifest_path=study.ROOT/"INPUT_MANIFEST.json";study.write(manifest_path,manifest)
    tests=subprocess.run([str(study.NATIVE),"-m","pytest","-q","test_singleton.py"],cwd=study.ROOT,
        capture_output=True,text=True,timeout=120,env={**os.environ,"CUDA_VISIBLE_DEVICES":""})
    tests_path=study.ROOT/"CPU_TESTS.json";study.write(tests_path,{"returncode":tests.returncode,"stdout":tests.stdout,"stderr":tests.stderr})
    if tests.returncode:raise ValueError("tests failed")
    common=[study.ROOT/name for name in ("QUESTION.md","DESIGN.yaml","study.py","owner.py","test_singleton.py","prepare.py","INPUT_MANIFEST.json","CPU_TESTS.json")]
    common += [study.SIZE_SOURCE/"READY.json",source_schedule,study.SIZE_SOURCE/"size_study.py",
        study.SIZE_SOURCE/"owner.py",study.REFERENCE_EVAL/"READY.json",study.REFERENCE_EVAL/"fourstep_panel_study.py"]
    bindings={arm:study.binding(arm) for arm in study.ARMS}
    for arm,path in outputs.items():
        binding=bindings[arm];child=binding["models"][study.CHILD_ALIAS];closure={str(item):study.sha(item) for item in common}
        checkpoint=Path(child["path"])
        for name in ("adapter_model.safetensors","adapter_config.json"):
            closure[str(checkpoint/name)]=study.sha(checkpoint/name)
        if arm=="reference_step4":
            for name in ("state.json","STEP_COMMIT.json","EVAL_BINDING.json"):
                closure[str(checkpoint/name)]=study.sha(checkpoint/name)
        value={"schema":"helper-hf-singleton-policy-comparison-ready-v1","status":"CPU_READY_MAIN_GPU_LAUNCH_ONLY",
            "created_epoch":time.time(),"arm":arm,
            "question":"Does reference T1/LR1e-5 step4 outperform c32 under the singleton inference shape used in training?",
            "command":[str(study.NATIVE),str(study.ROOT/"owner.py"),"run","--arm",arm,"--outer-seconds","900"],
            "owner_cap_seconds":900,"external_cap_seconds":1000,"physical_calls":256,"predictions":256,
            "temperature":0,"schedule_sha256":study.digest(rows),"input_manifest_sha256":study.sha(manifest_path),
            "binding_sha256":study.digest(binding),"child_alias":study.CHILD_ALIAS,"child_binding":child,
            "service_policy":"fresh service per arm; batch-invariant runtime attested; release before next arm",
            "metric":"paired fixed-denominator correct/wrong/unavailable by dataset plus physical cost",
            "claim_boundary":"Adaptive research-exposed fixed256 singleton-shape interaction; not confirmatory generalization.",
            "closure_sha256":closure,"cpu_tests":tests.stdout.strip()}
        value["identity"]=study.digest(value);study.write(path,value)
    print(json.dumps({arm:{"path":str(path),"sha256":study.sha(path),"identity":study.read(path)["identity"]} for arm,path in outputs.items()},sort_keys=True))


if __name__=="__main__":main()
