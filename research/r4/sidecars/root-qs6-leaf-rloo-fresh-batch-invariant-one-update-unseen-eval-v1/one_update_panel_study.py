"""Strict conditional binding for the qualified fresh48 one-update checkpoint."""

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
TRAINING = SIDE / "root-qs6-leaf-rloo-fresh-batch-invariant-one-update-v1"
TRAIN_OUTPUT = TRAINING / "outputs/attempt-001"
SOURCE_BINDING = SIDE / "root-qs6-feedback-diagnostic-v1/outputs/attempt-001/service/BINDING.json"
RECOVERY = SIDE / "root-qs6-leaf-rloo-fresh-batch-invariant-hf-recovery-v1/outputs/attempt-001"
ATTEMPT = ROOT / "outputs/attempt-001"
CAP = 600
CHILD_ALIAS = "strict-rlm-qwen3-4b-role-sft-selected-v1"
CHILD_SHA = "c32de1293c01bba5104eb1f123867649c71dd38e5194661ace4b17dcbbe66ba3"
TRAIN_READY_SHA = "f60b71d283f7b83c86650f2005c4f8b0b937a7bab8963ebf83b6321c01098e71"
TRAIN_READY_IDENTITY = "954203303e89dd183870bbe37e583f24cbb326ea81f87dd2398910f8b9b865ae"
QUALIFICATION_SHA = "e4cd0f44099475cb9ea8e85964d9ec6cc8b9156148fe439101fa871fcc475689"


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
def source(): return load("qualified_one_update_unseen_c32_source",C32/"unseen_panel_study.py")


NATIVE=source().NATIVE;MODEL=source().MODEL;PANEL=source().PANEL
panel=source().panel;schedule=source().schedule;dependencies=source().dependencies


def verify_hash_map(mapping):
    if not isinstance(mapping,dict) or not mapping: raise ValueError("empty committed file inventory")
    for raw,expected in mapping.items():
        if sha(raw)!=expected: raise ValueError("committed file changed: "+raw)


def verify_optimizer_step(path):
    import torch
    value=torch.load(path,map_location="cpu",weights_only=False)
    observed=sorted({int(row["step"].item() if hasattr(row["step"],"item") else row["step"]) for row in value["state"].values()})
    del value
    if observed!=[1]: raise ValueError("serialized AdamW state is not exactly step1")


def verify_binding(checkpoint,state,source_binding):
    binding=read(checkpoint/"EVAL_BINDING.json");child=binding["models"][CHILD_ALIAS]
    expected_child={"path":str(checkpoint),"adapter_sha256":sha(checkpoint/"adapter_model.safetensors"),
        "config_sha256":sha(checkpoint/"adapter_config.json")}
    if child!=expected_child: raise ValueError("current child binding differs")
    update=binding.get("child_only_update",{})
    if (update.get("experiment")!=TRAINING.name or update.get("step")!=1 or
        update.get("state_sha256")!=sha(checkpoint/"state.json") or
        update.get("optimizer_sha256")!=sha(checkpoint/"optimizer.pt") or
        update.get("rng_sha256")!=sha(checkpoint/"rng_state.pt") or
        update.get("source_child")!=source_binding["models"][CHILD_ALIAS] or
        update.get("root_unchanged") is not True or
        update.get("qualified_offline_fresh48") is not True or
        update.get("qualification_sha256")!=QUALIFICATION_SHA):
        raise ValueError("child-only update metadata differs")
    expected=copy.deepcopy(source_binding);expected["models"][CHILD_ALIAS]=expected_child;expected["child_only_update"]=update
    if binding!=expected: raise ValueError("binding changed beyond authenticated child-only update")
    root=binding["role_map"]["root"]
    if binding["models"][root]!=source_binding["models"][root]: raise ValueError("root binding changed")
    return binding


def qualify_one_update(output=TRAIN_OUTPUT):
    output=Path(output);checkpoint=output/"checkpoint-0001"
    ready=read(TRAINING/"READY.json")
    if sha(TRAINING/"READY.json")!=TRAIN_READY_SHA or ready.get("identity")!=TRAIN_READY_IDENTITY or ready.get("status")!="CPU_READY_MAIN_REVIEW_REQUIRED":
        raise ValueError("unexpected sealed training READY")
    verify_hash_map(ready["closure_sha256"])
    result=read(output/"RESULT.json")
    if (result.get("status")!="UPDATED" or result.get("optimizer_steps")!=1 or
        Path(result.get("checkpoint","")).resolve()!=checkpoint.resolve() or
        result.get("ready_identity")!=ready["identity"] or
        result.get("qualification_sha256")!=QUALIFICATION_SHA):
        raise ValueError("evaluation requires exact UPDATED checkpoint-0001")
    replay_path=output/"GRADIENT_REPLAY_CHECK.json";replay=read(replay_path)
    episodes=replay.get("episodes")
    if (replay.get("computed_before_optimizer_step") is not True or replay.get("optimizer_steps")!=0 or
        replay.get("training_mode") is not True or replay.get("gradient_checkpointing_active") is not True or
        replay.get("dropout_modules_eval") is not True or replay.get("all48_passed") is not True or
        replay.get("token_tolerance")!=1e-5 or replay.get("sequence_tolerance")!=1e-4 or
        not isinstance(episodes,list) or len(episodes)!=48 or len({x.get("episode_id") for x in episodes})!=48 or
        not all(x.get("passed") is True and x.get("support") is True and
                math.isfinite(x.get("max_token_error",math.nan)) and x["max_token_error"]<=1e-5 and
                math.isfinite(x.get("sequence_error",math.nan)) and x["sequence_error"]<=1e-4 for x in episodes)):
        raise ValueError("complete all48 gradient replay gate did not pass")
    if result.get("gradient_replay_check_sha256")!=sha(replay_path): raise ValueError("RESULT replay hash differs")
    state_path=checkpoint/"state.json";commit_path=checkpoint/"STEP_COMMIT.json"
    state,commit=read(state_path),read(commit_path)
    if (state.get("schema")!="qualified-fresh48-leaf-rloo-checkpoint-v1" or
        state.get("step")!=1 or state.get("optimizer_steps")!=1 or state.get("optimizer_state_steps")!=[1] or
        state.get("starting_child_adapter_sha256")!=CHILD_SHA or state.get("qualification_sha256")!=QUALIFICATION_SHA or
        state.get("gradient_replay_check_sha256")!=sha(replay_path) or state.get("episodes")!=48 or state.get("groups")!=2 or
        state.get("child_loss_tokens")!=11901 or state.get("root_loss_tokens")!=0 or state.get("environment_loss_tokens")!=0 or
        state.get("batch_denominator")!=48 or state.get("sequence_reduction")!="sum" or
        state.get("importance_weight_clipping") is not None or state.get("importance_weight_self_normalization") is not None or
        state.get("learning_rate")!=1e-5 or state.get("weight_decay")!=0 or state.get("gradient_clip_norm")!=1.0 or
        not math.isfinite(state.get("gradient_norm_before_clip",math.nan)) or state["gradient_norm_before_clip"]<=0 or
        not math.isfinite(state.get("adapter_delta_l2",math.nan)) or state["adapter_delta_l2"]<=0):
        raise ValueError("checkpoint state differs from qualified one-step contract")
    for name,expected in state.get("files_sha256",{}).items():
        if sha(checkpoint/name)!=expected: raise ValueError("state-pinned checkpoint file changed")
    if (commit.get("status")!="UPDATED" or commit.get("step")!=1 or commit.get("optimizer_steps")!=1 or
        commit.get("ready_identity")!=ready["identity"]): raise ValueError("step commit header differs")
    verify_hash_map(commit.get("files_sha256"))
    required={str(path) for path in [checkpoint/name for name in ("adapter_model.safetensors","adapter_config.json","optimizer.pt","rng_state.pt","state.json","EVAL_BINDING.json")]+[output/"CAPTURE.json",replay_path]}
    if not required<=set(commit["files_sha256"]): raise ValueError("step commit lacks required artifacts")
    if (result.get("checkpoint_state_sha256")!=sha(state_path) or result.get("step_commit_sha256")!=sha(commit_path) or
        result.get("eval_binding_sha256")!=sha(checkpoint/"EVAL_BINDING.json")):
        raise ValueError("RESULT checkpoint hashes differ")
    verify_optimizer_step(checkpoint/"optimizer.pt")
    qualification=read(RECOVERY/"PRESTEP_QUALIFICATION.json")
    if (sha(RECOVERY/"PRESTEP_QUALIFICATION.json")!=QUALIFICATION_SHA or qualification.get("gate_passed") is not True or
        qualification.get("all_supported") is not True or qualification.get("all_finite") is not True or
        qualification.get("gate_failures")!=[] or qualification.get("n")!=48):
        raise ValueError("source qualification differs")
    binding=verify_binding(checkpoint,state,read(SOURCE_BINDING))
    return {"eligible":True,"primary_step":1,"training_ready_identity":ready["identity"],
        "training_result_sha256":sha(output/"RESULT.json"),"gradient_replay_sha256":sha(replay_path),
        "qualification_sha256":QUALIFICATION_SHA,"checkpoint":str(checkpoint),
        "checkpoint_state_sha256":sha(state_path),"step_commit_sha256":sha(commit_path),
        "binding":binding,"binding_sha256":sha(checkpoint/"EVAL_BINDING.json")}


def binding():
    receipt=qualify_one_update()
    if ATTEMPT.exists(): write_x(ATTEMPT/"ELIGIBILITY.json",receipt)
    return receipt["binding"]


def verify():
    ready=read(ROOT/"READY.json")
    if ready.get("status")!="CPU_READY_CONDITIONAL_ON_UPDATED_STEP1": raise ValueError("unexpected eval READY status")
    verify_hash_map(ready["closure_sha256"])
    if digest(schedule())!=ready["schedule_sha256"]: raise ValueError("frozen unseen schedule changed")
    qualify_one_update()
    return ready
