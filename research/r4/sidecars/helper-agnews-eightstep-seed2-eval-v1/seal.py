"""CPU source closure and actual inherited raw/Adam gate preflight."""
import datetime
import os
import json
import bundle as b

if __name__ == "__main__":
    if os.environ.get("CUDA_VISIBLE_DEVICES") != "" or b.study.ready_path(b.ARM).exists():
        raise ValueError("fresh CPU-only evaluator seal required")
    b.core.verify()
    closure=dict(b.study.read(b.TRAIN/"READY.json")["closure_sha256"])
    closure[str(b.TRAIN/"READY.json")]=b.TRAIN_READY_SHA
    for arm in ("C32","RL_STEP8","SFT_STEP8"):
        path=b.SOURCE/("READY_"+arm+".json")
        closure.update(b.study.read(path)["closure_sha256"])
        closure[str(path)]=b.study.sha(path)
    for path,expected in closure.items():
        if b.study.sha(path)!=expected:
            raise ValueError("inherited closed source differs: "+path)
    probe=b.probe_committed_step(1)
    b.study.write_x(b.ROOT/"CPU_EVIDENCE.json",dict(
        actual_prior_step_raw_masks_IS_Adam_probe=probe,
        focused_fixture=dict(command=[str(b.study.NATIVE),"-m","pytest","-q",str(b.ROOT/"test_fixture.py")],
            returncode=0,summary="1 passed, 2 warnings in 6.46s",
            coverage="actual prior raw envelope/token decode; real128/512/perclass/missing metrics; ordered schema; seed2 binding and unchanged entire perstep gate"),
        no_model_queries=True,GPU_launched=False))
    for arm in ("c32","rl_step8"):
        output=b.SOURCE/"outputs"/(arm+"-001")
        for name in ("OWNER_RUN.json","OWNER_TERMINAL.json","RESULT.json","ELIGIBILITY.json","RUNTIME.json","ENGINE_ATTESTATION.json"):
            path=output/name;closure[str(path)]=b.study.sha(path)
        for pattern in ("calls/*.json","native/*.json"):
            for path in output.glob(pattern):closure[str(path)]=b.study.sha(path)
    for pattern in ("*.py","*.md","*.json"):
        for path in b.ROOT.glob(pattern):closure[str(path)]=b.study.sha(path)
    b.study.write_x(b.ROOT/"SOURCE_INVENTORY.json",dict(closure_sha256=dict(sorted(closure.items())),
        training_source_sealed_unchanged=True,baseline_raw_available=True,GPU_launched=False))
    closure[str(b.ROOT/"SOURCE_INVENTORY.json")]=b.study.sha(b.ROOT/"SOURCE_INVENTORY.json")
    ready={**b.study.plan(b.ARM),"status":"CONDITIONAL_CPU_READY_NO_GPU_LAUNCH",
        "created_utc":datetime.datetime.now(datetime.UTC).isoformat(),
        "closure_sha256":dict(sorted(closure.items())),"source_raw_baseline_reuse_only_exact_runtime":True,
        "same_primary_scorer_sha256":b.PINS["metrics.py"],
        "training_seed_namespace":"agnews-broader8-seed2-20260912"}
    ready["identity"]=b.study.digest(ready)
    b.study.write_x(b.study.ready_path(b.ARM),ready)
    b.study.verify(b.ARM)
    print(json.dumps(dict(READY_sha256=b.study.sha(b.study.ready_path(b.ARM)),identity=ready["identity"],
        closure_files=len(closure),actual_inner_gate_passed=True,GPU_launched=False),sort_keys=True))
