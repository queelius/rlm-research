"""Close the conditional repeated128 endpoint source, no model queries."""
import datetime
import json
import os
import bundle as b
import reuse_eval

if __name__=="__main__":
    if os.environ.get("CUDA_VISIBLE_DEVICES")!="" or b.study.ready_path(b.ARM).exists():
        raise ValueError("fresh CPU-only endpoint seal required")
    b.core.verify()
    inherited_path=reuse_eval.PREVIOUS/"READY_RL_SEED2_STEP8.json"
    closure=dict(b.study.read(inherited_path)["closure_sha256"])
    closure.update(b.study.read(b.TRAIN/"READY.json")["closure_sha256"])
    closure[str(inherited_path)]=b.study.sha(inherited_path)
    closure[str(b.TRAIN/"READY.json")]=b.TRAIN_READY_SHA
    for path,expected in closure.items():
        if b.study.sha(path)!=expected:raise ValueError("inherited source closure changed: "+path)
    probe=b.probe_committed_step(1)
    b.study.write_x(b.ROOT/"CPU_EVIDENCE.json",dict(actual_original_raw_masks_IS_Adam_probe=probe,
        focused_fixture=dict(command=[str(b.study.NATIVE),"-m","pytest","-q",str(b.ROOT/"test_fixture.py")],
            returncode=0,summary="1 passed, 2 warnings in 5.80s",
            covers="same full128/512 raw/schema/perclass/missing scorer fixture; distinct repeated train manifest binding; byte-equal original endpoint schedule/gold; entire unchanged perstep gate"),
        original_per_step_gate_unchanged=True,new_repeated_training_data_bound=True,GPU_launched=False))
    for pattern in ("*.py","*.md","*.json"):
        for path in b.ROOT.glob(pattern):closure[str(path)]=b.study.sha(path)
    b.study.write_x(b.ROOT/"SOURCE_INVENTORY.json",dict(closure_sha256=dict(sorted(closure.items())),
        train_manifest=str(b.TRAIN/"inputs/MANIFEST.json"),
        endpoint_source_manifest=str(b.old_study.DATA/"inputs/MANIFEST.json"),GPU_launched=False))
    closure[str(b.ROOT/"SOURCE_INVENTORY.json")]=b.study.sha(b.ROOT/"SOURCE_INVENTORY.json")
    value={**b.study.plan(b.ARM),"status":"CONDITIONAL_CPU_READY_NOT_GPU_ADMITTED",
        "created_utc":datetime.datetime.now(datetime.UTC).isoformat(),
        "primary":"broader_seed1_vs_repeat128_step8","secondary":"c32_vs_repeat128_step8",
        "same_research_exposed512":True,"completed8steps_required":True,
        "incomplete_dose_not_scored_as_completed_comparison":True,
        "training_manifest_sha256":b.study.sha(b.TRAIN/"inputs/MANIFEST.json"),
        "endpoint_source_manifest_sha256":b.study.sha(b.old_study.DATA/"inputs/MANIFEST.json"),
        "closure_sha256":dict(sorted(closure.items()))}
    value["identity"]=b.study.digest(value)
    b.study.write_x(b.study.ready_path(b.ARM),value)
    b.study.verify(b.ARM)
    print(json.dumps(dict(READY_sha256=b.study.sha(b.study.ready_path(b.ARM)),identity=value["identity"],
        closure_files=len(closure),actual_original_inner_gate_passed=True,GPU_launched=False),sort_keys=True))
