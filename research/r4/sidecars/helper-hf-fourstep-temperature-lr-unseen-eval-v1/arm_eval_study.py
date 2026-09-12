"""Conditional fixed-step4 evaluator for the two sealed temperature/LR training arms."""

import copy
import functools
import hashlib
import importlib.util
import json
import math
from pathlib import Path


ROOT=Path(__file__).resolve().parent;SIDE=ROOT.parent
SOURCE_EVAL=SIDE/"helper-hf-fourstep-unseen-eval-v1"
TRAINING=SIDE/"helper-hf-onpolicy-fourstep-temperature-lr-v1"
REFERENCE=SIDE/"helper-hf-onpolicy-fourstep-v1"
C32=SIDE/"helper-unseen-generalization-c32-baseline-v1"
SOURCE_BINDING=SIDE/"root-qs6-feedback-diagnostic-v1/outputs/attempt-001/service/BINDING.json"
CHILD_ALIAS="strict-rlm-qwen3-4b-role-sft-selected-v1";CHILD_SHA="c32de1293c01bba5104eb1f123867649c71dd38e5194661ace4b17dcbbe66ba3";CAP=600
ARMS={
 "t2_lr1e5":{"temperature":2.0,"learning_rate":1e-5,"training_ready":"READY_T2.json","training_ready_sha256":"f5d8be7c077e43a2a77880fa7784523989caf2837b5f452dfb81c67b5c47aba3","training_ready_identity":"26c64663c376abafe127ca03ffe44579dc94a227fdce1bb358324afcd5ef3c0a","training_output":TRAINING/"arms/t2-lr1e5/outputs/attempt-001","attempt":ROOT/"arms/t2-lr1e5/outputs/attempt-001","ready":"READY_T2.json"},
 "t1_lr1e4":{"temperature":1.0,"learning_rate":1e-4,"training_ready":"READY_LR10X.json","training_ready_sha256":"d01afc57f04d4dd3f3ea2569a7e60c31d4755b47f448948c571bc88011bf3efd","training_ready_identity":"eb1a6449318eb301d213ed80c1c4b8d0c51257ab662957a35e06d6a7b5d5bbc3","training_output":TRAINING/"arms/t1-lr1e4/outputs/attempt-001","attempt":ROOT/"arms/t1-lr1e4/outputs/attempt-001","ready":"READY_LR10X.json"},
}
CURRENT=None;ATTEMPT=None


def read(path):return json.loads(Path(path).read_text())
def sha(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()
def digest(value):return hashlib.sha256(json.dumps(value,sort_keys=True,separators=(",", ":")).encode()).hexdigest()
def write_x(path,value):
 path=Path(path);path.parent.mkdir(parents=True,exist_ok=True);text=json.dumps(value,indent=2,sort_keys=True,allow_nan=False)+"\n"
 if path.exists():
  if path.read_text()!=text:raise ValueError("immutable file differs: "+str(path))
 else:
  with path.open("x") as stream:stream.write(text)
def load(name,path):
 spec=importlib.util.spec_from_file_location(name,path);module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module);return module


@functools.lru_cache(maxsize=1)
def source_eval():return load("arm_eval_original_fourstep_study",SOURCE_EVAL/"fourstep_panel_study.py")
@functools.lru_cache(maxsize=1)
def source():return source_eval().source()
NATIVE=source_eval().NATIVE;MODEL=source_eval().MODEL;PANEL=source_eval().PANEL
panel=source_eval().panel;schedule=source_eval().schedule;dependencies=source_eval().dependencies


def select(arm):
 global CURRENT,ATTEMPT
 if arm not in ARMS:raise ValueError("unknown arm")
 CURRENT=arm;ATTEMPT=ARMS[arm]["attempt"]


def experimental_arm(name):return {"name":name,"temperature":ARMS[name]["temperature"],"learning_rate":ARMS[name]["learning_rate"]}


def validate_arm_state(name,state):
 arm=ARMS[name];public=experimental_arm(name)
 if state.get("schema")!="helper-hf-onpolicy-fourstep-arm-state-v1" or state.get("experimental_arm")!=public or state.get("temperature")!=arm["temperature"] or state.get("learning_rate")!=arm["learning_rate"] or state.get("poststep_extra_forward_sweep") is not False:raise ValueError("arm-specific step state differs")


def verify_binding(checkpoint,state,source_binding,step,name):
 binding=read(checkpoint/"EVAL_BINDING.json");child=binding["models"][CHILD_ALIAS]
 expected_child={"path":str(checkpoint),"adapter_sha256":sha(checkpoint/"adapter_model.safetensors"),"config_sha256":sha(checkpoint/"adapter_config.json")}
 if child!=expected_child:raise ValueError("child binding files differ")
 update=binding.get("child_only_update",{});public=experimental_arm(name);seeds=read(TRAINING/ARMS[name]["training_ready"])["seeds"]
 if update.get("experiment")!=TRAINING.name or update.get("step")!=step or update.get("cumulative_optimizer_steps")!=step or update.get("root_unchanged") is not True or update.get("state_sha256")!=sha(checkpoint/"state.json") or update.get("optimizer_sha256")!=sha(checkpoint/"optimizer.pt") or update.get("rng_sha256")!=sha(checkpoint/"rng_state.pt") or update.get("source_child")!=source_binding["models"][CHILD_ALIAS] or update.get("experimental_arm")!=public or update.get("fixed_training_seeds")!=seeds:raise ValueError("arm child-only update differs")
 expected=copy.deepcopy(source_binding);expected["models"][CHILD_ALIAS]=expected_child;expected["child_only_update"]=update
 if binding!=expected:raise ValueError("binding changed beyond child arm")
 return binding


def qualify_arm(name):
 arm=ARMS[name];ready_path=TRAINING/arm["training_ready"];ready=read(ready_path);output=arm["training_output"]
 if sha(ready_path)!=arm["training_ready_sha256"] or ready.get("identity")!=arm["training_ready_identity"] or ready.get("arm")!=read(ready_path)["arm"]:raise ValueError("unexpected arm READY")
 for path,expected in ready["closure_sha256"].items():
  if sha(path)!=expected:raise ValueError("training closure changed: "+path)
 result_path=output/"RESULT.json";result=read(result_path);entries=source_eval().validate_final_result(result,output)
 receipt_path=output/"ARM_RUNTIME_RECEIPT.json";receipt=read(receipt_path);public=experimental_arm(name)
 if result.get("arm_runtime_receipt")!=str(receipt_path) or result.get("arm_runtime_receipt_sha256")!=sha(receipt_path) or receipt.get("ready_identity")!=ready["identity"] or receipt.get("experimental_arm")!=public or receipt.get("temperature_paths")!=["replay","rollout"] or receipt.get("poststep_extra_forward_sweep") is not False:raise ValueError("arm runtime receipt differs")
 start=read(output/"START.json")
 if start.get("ready_identity")!=ready["identity"] or start.get("requested_updates")!=4 or start.get("primary_checkpoint_step")!=4 or start.get("starting_child_adapter_sha256")!=CHILD_SHA or start.get("experimental_arm")!=public:raise ValueError("arm START differs")
 source_binding=read(SOURCE_BINDING);frozen_ids={x["group_id"] for x in read(REFERENCE/"inputs/GROUPS.json")}
 lineage=[];parent_identity=CHILD_SHA;parent_commit=None;final_binding=None
 for step,entry in enumerate(entries,1):
  checkpoint=output/f"checkpoint-{step:04d}";update=output/"updates"/f"update-{step:04d}";state_path=checkpoint/"state.json";commit_path=checkpoint/"STEP_COMMIT.json";state,commit=read(state_path),read(commit_path)
  if entry.get("state_sha256")!=sha(state_path) or entry.get("step_commit")!={"path":str(commit_path),"sha256":sha(commit_path)}:raise ValueError("RESULT checkpoint receipt differs")
  source_eval().validate_lineage_header(step,state,commit,parent_identity,parent_commit,ready["identity"]);validate_arm_state(name,state)
  if state.get("starting_child_adapter_sha256")!=CHILD_SHA or state.get("weight_decay")!=0 or state.get("gradient_clip_norm")!=1.0 or state.get("root_loss_tokens")!=0 or state.get("environment_loss_tokens")!=0 or not math.isfinite(state.get("gradient_norm_before_clip",math.nan)) or state["gradient_norm_before_clip"]<=0:raise ValueError("training metadata differs")
  for filename,expected in state["files_sha256"].items():
   if sha(checkpoint/filename)!=expected:raise ValueError("state-pinned file changed")
  source_eval().verify_hash_map(commit["files_sha256"]);source_eval().verify_optimizer_steps(checkpoint/"optimizer.pt",step)
  start_update=read(update/"START.json");collection=read(update/"COLLECTION.json");qualification=read(update/"QUALIFICATION.json")
  for item in (start_update,collection,qualification):
   if item.get("experimental_arm")!=public:raise ValueError("update artifact arm differs")
  if start_update.get("step")!=step or start_update.get("parent_identity")!=parent_identity or set(start_update.get("group_ids",[]))!=frozen_ids or len(start_update.get("group_ids",[]))!=32:raise ValueError("update START differs")
  if collection.get("groups")!=32 or collection.get("samples")!=128 or collection.get("fresh_actions") is not True or collection.get("optimizer_steps_at_collection")!=step-1 or collection.get("parent_identity")!=parent_identity or collection.get("poststep_extra_forward_sweep") is not False or collection.get("branching_entropy",{}).get("temperature")!=arm["temperature"]:raise ValueError("collection differs")
  if qualification.get("all_passed") is not True or qualification.get("computed_before_step") is not True or qualification.get("historical_behavior_probabilities_used") is not False or qualification.get("parent_identity")!=parent_identity or len(qualification.get("groups",[]))!=32:raise ValueError("qualification differs")
  for index,group_id in enumerate(start_update["group_ids"]):
   directory=update/"groups"/f"group-{index:03d}";group_commit=read(directory/"GROUP_COMMIT.json");replay=read(directory/"REPLAY.json")
   if group_commit.get("step")!=step or group_commit.get("group_id")!=group_id or group_commit.get("parent_identity")!=parent_identity:raise ValueError("group lineage differs")
   source_eval().verify_hash_map(group_commit["files_sha256"])
   if replay.get("experimental_arm")!=public or replay.get("temperature_path_attested") is not True:raise ValueError("replay arm differs")
   source_eval().verify_probability_group(qualification["groups"][index],index,replay)
  final_binding=verify_binding(checkpoint,state,source_binding,step,name)
  lineage.append({"step":step,"checkpoint":str(checkpoint),"state_sha256":sha(state_path),"step_commit_sha256":sha(commit_path),"collection_sha256":sha(update/"COLLECTION.json"),"qualification_sha256":sha(update/"QUALIFICATION.json"),"optimizer_sha256":sha(checkpoint/"optimizer.pt"),"rng_sha256":sha(checkpoint/"rng_state.pt")})
  parent_identity=sha(state_path);parent_commit={"path":str(commit_path),"sha256":sha(commit_path)}
 checkpoint=output/"checkpoint-0004"
 return {"eligible":True,"arm":public,"primary_step":4,"training_ready_identity":ready["identity"],"training_result_sha256":sha(result_path),"arm_runtime_receipt_sha256":sha(receipt_path),"lineage":lineage,"binding":final_binding,"binding_sha256":sha(checkpoint/"EVAL_BINDING.json"),"checkpoint":str(checkpoint),"checkpoint_state_sha256":sha(checkpoint/"state.json")}


def binding():
 if CURRENT is None:raise ValueError("arm not selected")
 receipt=qualify_arm(CURRENT)
 if ATTEMPT.exists():write_x(ATTEMPT/"ELIGIBILITY.json",receipt)
 return receipt["binding"]


def verify(name,require_training=True):
 select(name);arm=ARMS[name];ready=read(ROOT/arm["ready"])
 for path,expected in ready["closure_sha256"].items():
  if sha(path)!=expected:raise ValueError("eval closure changed: "+path)
 if digest(schedule())!=ready["schedule_sha256"]:raise ValueError("panel schedule changed")
 if require_training:qualify_arm(name)
 return ready
