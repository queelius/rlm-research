"""Frozen identity for HF-only recovery over the already collected V2 fresh48 batch."""

import hashlib
import json
from pathlib import Path


ROOT=Path(__file__).resolve().parent
SIDE=ROOT.parent
ATTEMPT=ROOT/"outputs/attempt-001"
SOURCE=SIDE/"root-qs6-leaf-rloo-fresh-batch-invariant-qualification-v2"
SOURCE_ATTEMPT=SOURCE/"outputs/attempt-001"
V1=SIDE/"root-qs6-leaf-rloo-onebatch-v1"
BASE_MODEL=Path("/project/alex_phd/research-cache/models/Qwen--Qwen3-4B-Instruct-2507--cdbee75f17c01a7cc42f958dc650907174af0554")
CHILD_START=SIDE/"trec-leaf-sft-v1/outputs/attempt-001/checkpoint-0128"
NATIVE=Path("/project/alex_phd/envs/prime-rl-5990b1b/bin/python")
TRAIN_PYTHON=Path("/project/alex_phd/repos/rlm-bootstrap/.worktrees/a100-lora-roundtrip/gpu/training/.venv/bin/python")
CAP=360


def read(path):return json.loads(Path(path).read_text())
def sha(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()
def digest(value):return hashlib.sha256(json.dumps(value,sort_keys=True,separators=(",", ":")).encode()).hexdigest()
def write_x(path,value):
    path=Path(path);path.parent.mkdir(parents=True,exist_ok=True);text=json.dumps(value,indent=2,sort_keys=True,allow_nan=False)+"\n"
    if path.exists():
        if path.read_text()!=text:raise ValueError("immutable file differs: "+str(path))
    else:
        with path.open("x") as stream:stream.write(text)


def verify():
    ready=read(ROOT/"READY.json")
    if digest({k:v for k,v in ready.items() if k!="identity"})!=ready.get("identity"):raise ValueError("READY identity differs")
    for path,expected in ready["closure_sha256"].items():
        if sha(path)!=expected:raise ValueError("sealed recovery input differs: "+path)
    return ready
