"""Seal additive V3 nested-verifier repair."""

from __future__ import annotations

import json
from pathlib import Path
import time

import checkpoint_v3 as checkpoint
import study_v3 as study


V2 = study.ROOT / "CPU_READY_V2.json"


def build():
    if study.READY.exists(): raise FileExistsError("CPU_READY_V3 already exists")
    prior = study.read(V2)
    if prior["identity"] != study.digest({k:v for k,v in prior.items() if k != "identity"}):
        raise ValueError("V2 READY changed")
    for raw, expected in prior["closure_sha256"].items():
        if study.sha(Path(raw)) != expected: raise ValueError("V2 closure changed: " + raw)
    checkpoint.verify_checkpoint(); study.terminal_hooks()
    added = [study.ROOT / name for name in ("study_v3.py", "checkpoint_v3.py", "collect_v3.py",
                                             "owner_v3.py", "prepare_v3.py", "test_repair_v3.py")]
    value = {**{k:v for k,v in prior.items() if k not in ("identity","created_epoch","closure_sha256","output","repair")},
             "schema":"openai-mrcr-procedural-sft32-onpolicy-screen-ready-v3", "created_epoch":time.time(),
             "repair":{"only_change":"bind flat-receipt verifier through wrapper and innermost inherited collector",
                       "v2_ready":str(V2),"v2_ready_sha256":study.sha(V2),"v2_identity":prior["identity"],
                       "science_schedule_changed":False,"sampling_changed":False,"checkpoint_changed":False,
                       "terminal_hooks_changed":False},
             "output":str(study.ROOT/"outputs/attempt-003"),
             "closure_sha256":{**prior["closure_sha256"],str(V2):study.sha(V2),
                               **{str(path):study.sha(path) for path in added}}}
    value["identity"] = study.digest(value); study.write_x(study.READY,value); return value


def verify():
    ready=study.read(study.READY)
    if ready["identity"] != study.digest({k:v for k,v in ready.items() if k != "identity"}): raise ValueError("V3 READY changed")
    for raw,expected in ready["closure_sha256"].items():
        if study.sha(Path(raw)) != expected: raise ValueError("V3 closure changed: "+raw)
    return ready


if __name__ == "__main__":
    value=verify() if study.READY.exists() else build()
    print(json.dumps({"identity":value["identity"],"sha256":study.sha(study.READY)},sort_keys=True))
