"""Three-policy binding and frozen AG heldout schedule."""

import copy
import functools
import hashlib
import importlib.util
import json
from pathlib import Path


ROOT=Path(__file__).resolve().parent;SIDE=ROOT.parent;INPUTS=ROOT/"inputs"
BASELINE=SIDE/"helper-unseen-generalization-c32-baseline-v1"
REFERENCE_EVAL=SIDE/"helper-hf-fourstep-unseen-eval-v1"
REFERENCE_TRAIN=SIDE/"helper-hf-onpolicy-fourstep-v1"
AG_TRAIN=SIDE/"helper-agnews-onpolicy-fourstep-v1"
SOURCE_BINDING=SIDE/"root-qs6-feedback-diagnostic-v1/outputs/attempt-001/service/BINDING.json"
NATIVE=Path("/project/alex_phd/envs/prime-rl-5990b1b/bin/python")
MODEL=Path("/project/alex_phd/research-cache/models/Qwen--Qwen3-4B-Instruct-2507--cdbee75f17c01a7cc42f958dc650907174af0554")
CHILD_ALIAS="strict-rlm-qwen3-4b-role-sft-selected-v1";CAP=600;ARMS=("c32","reference_t1","ag_step4")


def read(path): return json.loads(Path(path).read_text())
def sha(path): return hashlib.sha256(Path(path).read_bytes()).hexdigest()
def digest(value): return hashlib.sha256(json.dumps(value,sort_keys=True,separators=(",", ":")).encode()).hexdigest()
def write_x(path,value):
    path=Path(path);path.parent.mkdir(parents=True,exist_ok=True);rendered=json.dumps(value,indent=2,sort_keys=True,allow_nan=False)+"\n"
    if path.exists():
        if path.read_text()!=rendered: raise ValueError("existing immutable file differs: "+str(path))
    else:
        with path.open("x") as stream: stream.write(rendered)


def load(name,path):
    spec=importlib.util.spec_from_file_location(name,path);module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module);return module


def schedule():
    public=read(INPUTS/"PUBLIC.json");requests=read(INPUTS/"REQUESTS.json");expected={x["id"] for x in public["records"]};rows=[];seen=[]
    for source in requests:
        schema=json.loads(source["schema_ordered_json"])
        if list(schema["properties"])!=source["ids"] or schema["required"]!=source["ids"]: raise ValueError("ordered AG schema differs")
        body=copy.deepcopy(source["body_template"]);body["sampling_params"]["structured_outputs"]["json"]=schema
        rows.append({"call_id":source["request_id"],"dataset":"ag_news","start":source["start"],"ids":source["ids"],"schema_ordered_json":source["schema_ordered_json"],"body":body});seen.extend(source["ids"])
    if len(rows)!=64 or len(seen)!=256 or len(set(seen))!=256 or set(seen)!=expected: raise ValueError("heldout schedule inventory differs")
    return rows


@functools.lru_cache(maxsize=1)
def baseline_study(): return load("ag_heldout_baseline_dependency",BASELINE/"unseen_panel_study.py")
def dependencies(): return baseline_study().dependencies()


def validate_training_result(result,output):
    output=Path(output);checkpoint=output/"checkpoint-0004"
    if result.get("status")!="COMPLETED_FOUR_UPDATES" or result.get("completed_optimizer_steps")!=4 or result.get("primary_checkpoint_available") is not True or result.get("primary_checkpoint_step")!=4 or Path(result.get("primary_checkpoint","")).resolve()!=checkpoint.resolve():
        raise ValueError("new AG evaluation requires exact completed step4")
    entries=result.get("checkpoints",[])
    if len(entries)!=4 or [x.get("step") for x in entries]!=[1,2,3,4]: raise ValueError("four ordered checkpoints required")
    if any(Path(entry.get("checkpoint","")).resolve()!=(output/f"checkpoint-{step:04d}").resolve() for step,entry in enumerate(entries,1)): raise ValueError("checkpoint paths differ")
    return checkpoint


def verify_ag_checkpoint():
    ready=read(AG_TRAIN/"READY.json")
    for raw,expected in ready["closure_sha256"].items():
        if sha(raw)!=expected: raise ValueError("AG training closure changed: "+raw)
    output=AG_TRAIN/"outputs/attempt-001";checkpoint=validate_training_result(read(output/"RESULT.json"),output)
    source_binding=read(SOURCE_BINDING)
    for step in range(1,5):
        cp=output/f"checkpoint-{step:04d}";state=read(cp/"state.json");commit=read(cp/"STEP_COMMIT.json")
        if state.get("step")!=step or state.get("cumulative_optimizer_steps")!=step or state.get("optimizer_state_steps")!=[step] or state.get("ready_identity")!=ready["identity"]: raise ValueError("AG checkpoint state differs")
        for name,expected in state["files_sha256"].items():
            if sha(cp/name)!=expected: raise ValueError("AG checkpoint file changed")
        for raw,expected in commit["files_sha256"].items():
            if sha(raw)!=expected: raise ValueError("AG step commit file changed")
    binding=read(checkpoint/"EVAL_BINDING.json");child=binding["models"][CHILD_ALIAS]
    if Path(child["path"]).resolve()!=checkpoint.resolve() or child["adapter_sha256"]!=sha(checkpoint/"adapter_model.safetensors"): raise ValueError("AG step4 child binding differs")
    if binding["models"][binding["role_map"]["root"]]!=source_binding["models"][source_binding["role_map"]["root"]]: raise ValueError("root binding changed")
    return binding


def binding(arm):
    if arm=="c32": return read(SOURCE_BINDING)
    if arm=="reference_t1":
        source=load("ag_heldout_reference_qualifier",REFERENCE_EVAL/"fourstep_panel_study.py")
        return source.qualify_fourstep()["binding"]
    if arm=="ag_step4": return verify_ag_checkpoint()
    raise ValueError("unknown arm")


def attempt(arm): return ROOT/"outputs"/(arm+"-001")
def ready_path(arm): return ROOT/("READY_"+arm.upper()+".json")
def plan(arm):
    return {"schema":"helper-agnews-heldout-eval-plan-v1","arm":arm,"output":str(attempt(arm)),"cap_seconds":CAP,"physical_calls":64,"records":256,"batch":4,"temperature":0.0,"schedule_sha256":digest(schedule()),"command":[str(NATIVE),str(ROOT/"owner.py"),"run","--arm",arm,"--outer-seconds",str(CAP)]}
def verify(arm):
    ready=read(ready_path(arm))
    for key,value in plan(arm).items():
        if ready.get(key)!=value: raise ValueError("eval plan changed: "+key)
    for raw,expected in ready["closure_sha256"].items():
        if sha(raw)!=expected: raise ValueError("sealed eval closure changed: "+raw)
    binding(arm)
    return ready
