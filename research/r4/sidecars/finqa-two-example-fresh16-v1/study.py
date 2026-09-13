"""New hash-ranked pages/seeds; identical admitted two-example interface."""
import importlib.util
from pathlib import Path
ROOT=Path(__file__).resolve().parent
PARENT=ROOT.parent/"finqa-scalar-vs-dsl-v1"
PRIOR=ROOT.parent/"finqa-two-example-interface-v1"
spec=importlib.util.spec_from_file_location("finqa_fresh_parent_study",PARENT/"study.py")
parent=importlib.util.module_from_spec(spec);spec.loader.exec_module(parent)
for key in ("read","sha","digest","write_x","bytes_x","now","load","aliases","tokenizer","renderer","request_body","decode_response",
            "base_owner","call_id","MUSIQUE","MODEL","MODEL_ALIAS","NATIVE","SOURCE","source","REV","DATA","SOURCE_READY","SOURCE_READY_SHA"):
    globals()[key]=getattr(parent,key)
science=load("finqa_fresh_unchanged_interpreter",PARENT/"science.py")
ATTEMPT=ROOT/"outputs/attempt-001"
READY_RUN=ROOT/"CPU_READY.json"
INPUTS=ROOT/"PUBLIC_INPUTS.json"
HOST=ROOT/"HOST_TARGETS.json"
OWNER_SECONDS,SCIENCE_SECONDS,EXTERNAL_SECONDS=700,600,800
MAX_PHYSICAL,CONCURRENCY=32,4
PRIOR_READY=PRIOR/"CPU_READY.json"
PRIOR_READY_SHA="c7866cd040797d4fbb08cd0f6c36b41fcecb80cb6da0bbf3139007a4f327ede6"
PRIOR_RESULT_SHA="f9bd927aa2899b969e619d742d758980872b97886406787723d6e567f54439e2"
SEED_BASE=202609300000


def calls():return read(INPUTS)["calls"]


def verify():
    ready=read(READY_RUN)
    assert ready["identity"]==digest({k:v for k,v in ready.items() if k!="identity"})
    for path,want in ready["closure_sha256"].items():assert sha(Path(path))==want,path
    assert sha(PRIOR_READY)==PRIOR_READY_SHA and sha(PRIOR/"outputs/attempt-001/RESULT.json")==PRIOR_RESULT_SHA
    terminal=read(PRIOR/"outputs/attempt-001/OWNER_TERMINAL.json")
    assert all(terminal[k] for k in ("complete","released","runtime_qualified")) and terminal["result_sha256"]==PRIOR_RESULT_SHA
    old={r["filename"] for r in read(PRIOR/"PUBLIC_INPUTS.json")["contexts"]}
    new={r["filename"] for r in read(INPUTS)["contexts"]}
    assert len(old)==len(new)==16 and not old&new and len(calls())==32
    return ready
