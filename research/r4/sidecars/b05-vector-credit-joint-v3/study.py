"""Response-joint V3 binding; only trainer directory handshake differs from V2."""
import hashlib,importlib.util
from pathlib import Path
ROOT=Path(__file__).resolve().parent;LOCAL=ROOT.parent/"b05-vector-credit-local-v3/study.py"
expected=None
# The local V3 digest is asserted by the sealed joint closure; this import remains isolated.
spec=importlib.util.spec_from_file_location("vector_joint_v3_local_study",LOCAL);local=importlib.util.module_from_spec(spec);spec.loader.exec_module(local)
for name,value in vars(local).items():
    if not name.startswith("__"):globals()[name]=value
ROOT=Path(__file__).resolve().parent;FAILED_V1=ROOT.parent/"b05-vector-credit-local-v2"
READY=ROOT/"READY.json";OUTPUT=ROOT/"outputs/attempt-001";CREDIT_MODE="joint"
REWARD_DESCRIPTION="mean candidate correctness per response; response-joint G4 RLOO"
ALIAS="Qwen3-4B-Instruct-2507-b05-vector-credit-joint-step1-v3"
def validate_inputs(data):
    source_rewards={row["episode_id"]:row["joint_reward"] for row in data["episodes"]}
    patched=dict(data);patched["episodes"]=[]
    for source_row in data["episodes"]:
        row=dict(source_row);row["joint_reward"]=[row["joint_reward"]]*row["candidate_count"];patched["episodes"].append(row)
    rows=local.source.validate_for_mode(patched,CREDIT_MODE)
    for row in rows:row["joint_reward"]=source_rewards[row["episode_id"]]
    return rows
def load_sealed_inputs():return validate_inputs(read(INPUTS))
def verify():
    ready=read(READY);assert ready["identity"]==digest({k:v for k,v in ready.items() if k!="identity"})
    for path,want in ready["closure_sha256"].items():assert sha(path)==want,path
    validate_inputs(read(INPUTS));return ready
