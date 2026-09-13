"""Same held9 stage/seed units, fresh raw and public-normalized base calls."""
import importlib.util
from pathlib import Path
ROOT=Path(__file__).resolve().parent
SOURCE=ROOT.parent/"b05-recombination-feasibility-v1"
TRAIN=ROOT.parent/"b05-flat-selection-rl-v1"
spec=importlib.util.spec_from_file_location("b05_normalizer_native_study",SOURCE/"runner_study.py")
source=importlib.util.module_from_spec(spec);spec.loader.exec_module(source)
for name in ("read","sha","digest","write_x","bytes_x","now","load","aliases","tokenizer","renderer","request_body","decode_response","base_owner","call_id","MUSIQUE","MODEL","MODEL_ALIAS","NATIVE"):
    globals()[name]=getattr(source,name)
ATTEMPT=ROOT/"outputs/attempt-001";READY_RUN=ROOT/"CPU_READY.json";INPUTS=ROOT/"PUBLIC_INPUTS.json";HOST=ROOT/"HOST_GOLD.json"
OWNER_SECONDS,SCIENCE_SECONDS,EXTERNAL_SECONDS=700,600,800
MAX_PHYSICAL,CONCURRENCY=36,4
SERVICE_READY=ROOT.parent/"finqa-two-example-fresh16-v1/CPU_READY.json"
SERVICE_SHA="6fb1607ad82554dcccdf761fdff781ae939d6feda414bbdcaf0c57b6d227107f"
DATA_SHA="7a2fe51f53402604ad3c3f437fd61d96ff347423417859b99916e720c85d6aa5"


def calls():return read(INPUTS)["calls"]


def verify():
    ready=read(READY_RUN);assert ready["identity"]==digest({k:v for k,v in ready.items() if k!="identity"})
    for path,want in ready["closure_sha256"].items():assert sha(Path(path))==want,path
    assert sha(SERVICE_READY)==SERVICE_SHA and sha(TRAIN/"READY.json")==DATA_SHA
    terminal=read(SERVICE_READY.parent/"outputs/attempt-001/OWNER_TERMINAL.json")
    assert all(terminal[k] for k in ("complete","released","runtime_qualified"))
    assert terminal["result_sha256"]==sha(SERVICE_READY.parent/"outputs/attempt-001/RESULT.json")
    assert len(calls())==36 and len(read(INPUTS)["tasks"])==9
    return ready
