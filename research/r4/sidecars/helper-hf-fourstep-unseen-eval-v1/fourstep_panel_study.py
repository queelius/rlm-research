"""Step-aware conditional binding for fixed checkpoint-0004 on the frozen unseen panel."""

from __future__ import annotations

import copy
import functools
import hashlib
import importlib.util
import json
import math
from pathlib import Path


ROOT = Path(__file__).resolve().parent
SIDE = ROOT.parent
C32 = SIDE / "helper-unseen-generalization-c32-baseline-v1"
TRAINING = SIDE / "helper-hf-onpolicy-fourstep-v1"
TRAIN_OUTPUT = TRAINING / "outputs/attempt-001"
SOURCE_BINDING = SIDE / "root-qs6-feedback-diagnostic-v1/outputs/attempt-001/service/BINDING.json"
ATTEMPT = ROOT / "outputs/attempt-001"
CAP = 600
CHILD_ALIAS = "strict-rlm-qwen3-4b-role-sft-selected-v1"
CHILD_SHA = "c32de1293c01bba5104eb1f123867649c71dd38e5194661ace4b17dcbbe66ba3"
TRAIN_READY_SHA = "1885e3c2b91acb51639aff88e39959dc06ee255662664f27e6b5e753a32d5289"
TRAIN_READY_IDENTITY = "f0e01f9999652ada7ec1187a59b6efd2694fb89a0bd5d9d2b543d86009e13648"


def read(path): return json.loads(Path(path).read_text())
def sha(path): return hashlib.sha256(Path(path).read_bytes()).hexdigest()
def digest(value): return hashlib.sha256(json.dumps(value,sort_keys=True,separators=(",", ":")).encode()).hexdigest()


def write_x(path,value):
    path=Path(path);path.parent.mkdir(parents=True,exist_ok=True)
    rendered=json.dumps(value,indent=2,sort_keys=True,allow_nan=False)+"\n"
    if path.exists():
        if path.read_text()!=rendered: raise ValueError("existing immutable file differs: "+str(path))
    else:
        with path.open("x") as stream: stream.write(rendered)


def load(name,path):
    spec=importlib.util.spec_from_file_location(name,path)
    if spec is None or spec.loader is None: raise RuntimeError("cannot load "+str(path))
    module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module);return module


@functools.lru_cache(maxsize=1)
def source(): return load("fourstep_unseen_c32_source_study",C32/"unseen_panel_study.py")


NATIVE=source().NATIVE;MODEL=source().MODEL;PANEL=source().PANEL
panel=source().panel;schedule=source().schedule;dependencies=source().dependencies


def validate_final_result(result,output=TRAIN_OUTPUT):
    checkpoint=Path(output)/"checkpoint-0004"
    if (result.get("status")!="COMPLETED_FOUR_UPDATES" or
        result.get("completed_optimizer_steps")!=4 or
        result.get("primary_checkpoint_available") is not True or
        result.get("primary_checkpoint_step")!=4 or
        Path(result.get("primary_checkpoint","")).resolve()!=checkpoint.resolve()):
        raise ValueError("evaluation requires exact completed primary step4")
    entries=result.get("checkpoints")
    if not isinstance(entries,list) or [x.get("step") for x in entries]!=[1,2,3,4]:
        raise ValueError("four ordered checkpoint entries required")
    for step,entry in enumerate(entries,1):
        expected=Path(output)/f"checkpoint-{step:04d}"
        if Path(entry.get("checkpoint","")).resolve()!=expected.resolve():
            raise ValueError("checkpoint entry path differs")
    return entries


def validate_lineage_header(step,state,commit,parent_identity,parent_commit,ready_identity):
    if (state.get("step")!=step or state.get("cumulative_optimizer_steps")!=step or
        state.get("optimizer_state_steps")!=[step] or state.get("ready_identity")!=ready_identity or
        state.get("parent_identity")!=parent_identity or state.get("parent_step_commit")!=parent_commit):
        raise ValueError("state step/optimizer/parent lineage differs")
    if (commit.get("step")!=step or commit.get("cumulative_optimizer_steps")!=step or
        commit.get("ready_identity")!=ready_identity or commit.get("parent_identity")!=parent_identity or
        commit.get("parent_step_commit")!=parent_commit or commit.get("status")!="UPDATED"):
        raise ValueError("step commit lineage differs")


def verify_hash_map(mapping):
    if not isinstance(mapping,dict) or not mapping: raise ValueError("empty committed file inventory")
    for raw,expected in mapping.items():
        if sha(raw)!=expected: raise ValueError("committed file changed: "+raw)


def verify_probability_group(group,index,replay):
    if group!=replay: raise ValueError("qualification differs from per-group replay")
    current,old=group.get("current_logprobs"),group.get("old_logprobs")
    if (group.get("passed") is not True or group.get("finite") is not True or
        group.get("batch_denominator")!=128 or group.get("sequence_reduction")!="sum" or
        not isinstance(current,list) or not isinstance(old,list) or len(current)!=4 or len(old)!=4):
        raise ValueError("probability group structure differs")
    token_error=0.0;sequence_error=0.0
    for a,b in zip(current,old,strict=True):
        if len(a)!=len(b) or not all(math.isfinite(x) for x in a+b):
            raise ValueError("unaligned or nonfinite probability rows")
        token_error=max(token_error,max((abs(x-y) for x,y in zip(a,b,strict=True)),default=0.0))
        sequence_error=max(sequence_error,abs(math.fsum(a)-math.fsum(b)))
    if (abs(token_error-group.get("maximum_token_logprob_error",math.inf))>1e-12 or
        abs(sequence_error-group.get("maximum_sequence_logprob_error",math.inf))>1e-12 or
        token_error>1e-5 or sequence_error>1e-4):
        raise ValueError("recomputed selected probability gate failed")
    support=group.get("support_maximum_logprob_error")
    if not math.isfinite(support) or support>1e-5: raise ValueError("support probability gate failed")
    if (index<4)!=(group.get("full_support_audited") is True):
        raise ValueError("first-four full-support audit set differs")


def verify_optimizer_steps(path,step):
    import torch
    value=torch.load(path,map_location="cpu",weights_only=False)
    observed=sorted({int(row["step"]) for row in value["state"].values()})
    del value
    if observed!=[step]: raise ValueError("serialized AdamW state is not cumulative step "+str(step))


def verify_binding(checkpoint,state,source_binding,step):
    binding=read(checkpoint/"EVAL_BINDING.json");child=binding["models"][CHILD_ALIAS]
    expected_child={"path":str(checkpoint),"adapter_sha256":sha(checkpoint/"adapter_model.safetensors"),
        "config_sha256":sha(checkpoint/"adapter_config.json")}
    if child!=expected_child: raise ValueError("current child binding files differ")
    update=binding.get("child_only_update",{})
    if (update.get("experiment")!=TRAINING.name or update.get("step")!=step or
        update.get("cumulative_optimizer_steps")!=step or update.get("root_unchanged") is not True or
        update.get("state_sha256")!=sha(checkpoint/"state.json") or
        update.get("optimizer_sha256")!=sha(checkpoint/"optimizer.pt") or
        update.get("rng_sha256")!=sha(checkpoint/"rng_state.pt") or
        update.get("source_child")!=source_binding["models"][CHILD_ALIAS]):
        raise ValueError("child-only update metadata differs")
    expected=copy.deepcopy(source_binding);expected["models"][CHILD_ALIAS]=expected_child;expected["child_only_update"]=update
    if binding!=expected: raise ValueError("binding changed beyond authenticated child-only update")
    if binding["models"][binding["role_map"]["root"]]!=source_binding["models"][source_binding["role_map"]["root"]]:
        raise ValueError("root binding changed")
    return binding


def qualify_fourstep(output=TRAIN_OUTPUT):
    output=Path(output);ready=read(TRAINING/"READY.json")
    if sha(TRAINING/"READY.json")!=TRAIN_READY_SHA or ready.get("identity")!=TRAIN_READY_IDENTITY or ready.get("status")!="CPU_READY_MAIN_REVIEW_REQUIRED":
        raise ValueError("unexpected sealed training READY identity")
    for raw,expected in ready["closure_sha256"].items():
        if sha(raw)!=expected: raise ValueError("training source closure changed: "+raw)
    # The training-only seal must not import evaluation examples or labels.
    forbidden=("helper-unseen-generalization-panel-v1/PUBLIC.json","helper-unseen-generalization-panel-v1/HOST_GOLD.json","helper-hf-onpolicy-eval-v1/inputs")
    if any(any(term in raw for term in forbidden) for raw in ready["closure_sha256"]):
        raise ValueError("training closure contains evaluation inventory")
    result_path=output/"RESULT.json";result=read(result_path);entries=validate_final_result(result,output)
    start=read(output/"START.json")
    if (start.get("ready_identity")!=ready["identity"] or start.get("requested_updates")!=4 or
        start.get("primary_checkpoint_step")!=4 or start.get("starting_child_adapter_sha256")!=CHILD_SHA):
        raise ValueError("training START identity differs")
    source_binding=read(SOURCE_BINDING)
    if source_binding["models"][CHILD_ALIAS]["adapter_sha256"]!=CHILD_SHA:
        raise ValueError("source c32 child differs")
    lineage=[];parent_identity=CHILD_SHA;parent_commit=None;previous_state=None;previous_commit=None
    frozen_ids={x["group_id"] for x in read(TRAINING/"inputs/GROUPS.json")}
    if len(frozen_ids)!=32: raise ValueError("training group inventory differs")
    final_binding=None
    for step,entry in enumerate(entries,1):
        checkpoint=output/f"checkpoint-{step:04d}";update=output/"updates"/f"update-{step:04d}"
        state_path=checkpoint/"state.json";commit_path=checkpoint/"STEP_COMMIT.json"
        if entry.get("state_sha256")!=sha(state_path) or entry.get("step_commit")!={"path":str(commit_path),"sha256":sha(commit_path)}:
            raise ValueError("final RESULT checkpoint receipt differs")
        state,commit=read(state_path),read(commit_path)
        validate_lineage_header(step,state,commit,parent_identity,parent_commit,ready["identity"])
        if (state.get("starting_child_adapter_sha256")!=CHILD_SHA or state.get("learning_rate")!=1e-5 or
            state.get("weight_decay")!=0 or state.get("gradient_clip_norm")!=1.0 or
            state.get("loss_reduction")!="sequence sum; mean over all128 freshly sampled actions" or
            state.get("root_loss_tokens")!=0 or state.get("environment_loss_tokens")!=0 or
            not math.isfinite(state.get("gradient_norm_before_clip",math.nan)) or state["gradient_norm_before_clip"]<=0 or
            not math.isfinite(state.get("adapter_delta_l2_from_parent",math.nan)) or state["adapter_delta_l2_from_parent"]<=0):
            raise ValueError("checkpoint training metadata differs")
        for name,expected in state["files_sha256"].items():
            if sha(checkpoint/name)!=expected: raise ValueError("state-pinned checkpoint file changed")
        if state["qualification_path"]!=str(update/"QUALIFICATION.json") or state["qualification_sha256"]!=sha(update/"QUALIFICATION.json") or state["collection_path"]!=str(update/"COLLECTION.json") or state["collection_sha256"]!=sha(update/"COLLECTION.json"):
            raise ValueError("state update artifact pins differ")
        verify_hash_map(commit["files_sha256"])
        required={str((checkpoint/name).resolve()) for name in ("adapter_model.safetensors","adapter_config.json","optimizer.pt","rng_state.pt","state.json","EVAL_BINDING.json")}
        required|={str((update/name).resolve()) for name in ("QUALIFICATION.json","COLLECTION.json")}
        if not required<=set(commit["files_sha256"]): raise ValueError("STEP_COMMIT lacks required files")
        verify_optimizer_steps(checkpoint/"optimizer.pt",step)
        start_update=read(update/"START.json");collection=read(update/"COLLECTION.json");qualification=read(update/"QUALIFICATION.json")
        if (start_update.get("step")!=step or start_update.get("parent_identity")!=parent_identity or
            start_update.get("ready_identity")!=ready["identity"] or len(start_update.get("group_ids",[]))!=32 or
            set(start_update["group_ids"])!=frozen_ids or len(set(start_update["group_ids"]))!=32):
            raise ValueError("fresh update permutation/source IDs differ")
        if (collection.get("groups")!=32 or collection.get("samples")!=128 or collection.get("fresh_actions") is not True or
            collection.get("optimizer_steps_at_collection")!=step-1 or collection.get("parent_identity")!=parent_identity or
            collection.get("start_sha256")!=sha(update/"START.json") or collection.get("start_rng_sha256")!=sha(update/"START_RNG.pt") or
            len(collection.get("group_commit_sha256",{}))!=32):
            raise ValueError("collection lineage/freshness differs")
        if (qualification.get("all_passed") is not True or qualification.get("computed_before_step") is not True or
            qualification.get("historical_behavior_probabilities_used") is not False or qualification.get("parent_identity")!=parent_identity or
            qualification.get("step")!=step or len(qualification.get("groups",[]))!=32):
            raise ValueError("complete pre-step qualification differs")
        for index,group_id in enumerate(start_update["group_ids"]):
            directory=update/"groups"/f"group-{index:03d}";group_commit=read(directory/"GROUP_COMMIT.json")
            if (group_commit.get("step")!=step or group_commit.get("group_index")!=index or group_commit.get("group_id")!=group_id or
                group_commit.get("parent_identity")!=parent_identity or group_commit.get("ready_identity")!=ready["identity"]):
                raise ValueError("group commit lineage differs")
            verify_hash_map(group_commit["files_sha256"])
            if collection["group_commit_sha256"].get(str(directory/"GROUP_COMMIT.json"))!=sha(directory/"GROUP_COMMIT.json"):
                raise ValueError("collection group-commit hash differs")
            verify_probability_group(qualification["groups"][index],index,read(directory/"REPLAY.json"))
        final_binding=verify_binding(checkpoint,state,source_binding,step)
        lineage.append({"step":step,"checkpoint":str(checkpoint),"state_sha256":sha(state_path),
            "step_commit_sha256":sha(commit_path),"collection_sha256":sha(update/"COLLECTION.json"),
            "qualification_sha256":sha(update/"QUALIFICATION.json"),"optimizer_sha256":sha(checkpoint/"optimizer.pt"),
            "rng_sha256":sha(checkpoint/"rng_state.pt")})
        previous_state=sha(state_path);previous_commit={"path":str(commit_path),"sha256":sha(commit_path)}
        parent_identity, parent_commit=previous_state,previous_commit
    checkpoint=output/"checkpoint-0004"
    return {"eligible":True,"primary_step":4,"training_ready_identity":ready["identity"],
        "training_result_sha256":sha(result_path),"lineage":lineage,"binding":final_binding,
        "binding_sha256":sha(checkpoint/"EVAL_BINDING.json"),"checkpoint":str(checkpoint),
        "checkpoint_state_sha256":sha(checkpoint/"state.json")}


def binding():
    receipt=qualify_fourstep()
    if ATTEMPT.exists(): write_x(ATTEMPT/"ELIGIBILITY.json",receipt)
    return receipt["binding"]


def verify():
    ready=read(ROOT/"READY.json")
    if ready.get("status")!="CPU_READY_CONDITIONAL_ON_COMPLETED_FOURSTEP_PRIMARY": raise ValueError("unexpected eval READY status")
    for raw,expected in ready["closure_sha256"].items():
        if sha(raw)!=expected: raise ValueError("sealed eval source changed: "+raw)
    if digest(schedule())!=ready["schedule_sha256"]: raise ValueError("frozen unseen schedule changed")
    qualify_fourstep()
    return ready
