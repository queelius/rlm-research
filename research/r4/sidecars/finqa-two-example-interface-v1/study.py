"""Two synthetic examples only; unchanged frozen FinQA16/native32 semantics."""
import importlib.util
from pathlib import Path

ROOT = Path(__file__).resolve().parent
PARENT = ROOT.parent / "finqa-scalar-vs-dsl-v1"
spec = importlib.util.spec_from_file_location("finqa_fewshot_parent_study",PARENT/"study.py")
parent = importlib.util.module_from_spec(spec);spec.loader.exec_module(parent)
for key in ("read","sha","digest","write_x","bytes_x","now","load","aliases","tokenizer","renderer","request_body","decode_response",
            "base_owner","call_id","MUSIQUE","MODEL","MODEL_ALIAS","NATIVE","SOURCE","source","REV","DATA","SOURCE_READY","SOURCE_READY_SHA"):
    globals()[key]=getattr(parent,key)
science = load("finqa_fewshot_unchanged_interpreter",PARENT/"science.py")
ATTEMPT = ROOT/"outputs/attempt-001"
READY_RUN = ROOT/"CPU_READY.json"
INPUTS = ROOT/"PUBLIC_INPUTS.json"
HOST = ROOT/"HOST_TARGETS.json"
OWNER_SECONDS,SCIENCE_SECONDS,EXTERNAL_SECONDS = 700,600,800
MAX_PHYSICAL,CONCURRENCY = 32,4
BASE_READY = PARENT/"CPU_READY.json"
BASE_READY_SHA = "6df8bd380dfc0837405304f0bfc34c55d04ea0dcdff3212a63fdf97d66e7d1e0"
BASE_RESULT_SHA = "7feeecaadd7c51cf27a345c75ee4e52dda7be2884fa7aab124b64da89b768474"


def calls():return read(INPUTS)["calls"]


def verify():
    ready=read(READY_RUN)
    assert ready["identity"]==digest({k:v for k,v in ready.items() if k!="identity"})
    for path,want in ready["closure_sha256"].items():assert sha(Path(path))==want,path
    assert sha(BASE_READY)==BASE_READY_SHA and sha(PARENT/"outputs/attempt-001/RESULT.json")==BASE_RESULT_SHA
    terminal=read(PARENT/"outputs/attempt-001/OWNER_TERMINAL.json")
    assert all(terminal[k] for k in ("complete","released","runtime_qualified")) and terminal["result_sha256"]==BASE_RESULT_SHA
    assert read(INPUTS)["calls"]==read(parent.INPUTS)["calls"] and read(INPUTS)["contexts"]==read(parent.INPUTS)["contexts"]
    assert read(HOST)==read(parent.HOST)
    return ready
