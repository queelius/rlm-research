"""Candidate-local V3 binding; only trainer directory handshake differs from V2."""
import hashlib,importlib.util
from pathlib import Path
ROOT=Path(__file__).resolve().parent
SOURCE=ROOT.parent/"b05-vector-credit-local-v2/study.py"
assert hashlib.sha256(SOURCE.read_bytes()).hexdigest()=="d9eadbde5f43c103df9cd36cf0eda1801a98bc10195fc2f91d5754fa9a6bf5dd"
spec=importlib.util.spec_from_file_location("vector_local_v3_source_study",SOURCE);source=importlib.util.module_from_spec(spec);spec.loader.exec_module(source)
for name,value in vars(source).items():
    if not name.startswith("__"):globals()[name]=value
ROOT=Path(__file__).resolve().parent;SHARED=ROOT.parent/"b05-vector-credit-shared-v3"
FAILED_V1=ROOT.parent/"b05-vector-credit-local-v2";READY=ROOT/"READY.json";OUTPUT=ROOT/"outputs/attempt-001"
ALIAS="Qwen3-4B-Instruct-2507-b05-vector-credit-local-step1-v3"
def verify():
    ready=read(READY);assert ready["identity"]==digest({k:v for k,v in ready.items() if k!="identity"})
    for path,expected in ready["closure_sha256"].items():assert sha(path)==expected,path
    validate_inputs(read(INPUTS));return ready
