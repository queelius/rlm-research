"""One qualified offline child-only RLOO update over exact saved fresh48 V2 actions."""

import argparse
import copy
import hashlib
import importlib.util
import json
import math
import os
from pathlib import Path
import random
import signal
import sys
import time


ROOT=Path(__file__).resolve().parent;SIDE=ROOT.parent
REC=SIDE/"root-qs6-leaf-rloo-fresh-batch-invariant-hf-recovery-v1";REC_OUT=REC/"outputs/attempt-001"
DATASET=REC_OUT/"qualification-inputs/DATASET.json";MASKS=REC_OUT/"qualification-inputs/MASKS.npz";MASK_MANIFEST=REC_OUT/"qualification-inputs/MASK_MANIFEST.json";QUALIFICATION=REC_OUT/"PRESTEP_QUALIFICATION.json"
SOURCE_BINDING=SIDE/"root-qs6-feedback-diagnostic-v1/outputs/attempt-001/service/BINDING.json"
V1=SIDE/"root-qs6-leaf-rloo-onebatch-v1";SEED=202609121401;CAP=900;LR=1e-5;CLIP=1.0;TOKEN_TOL=1e-5;SEQUENCE_TOL=1e-4
QUALIFICATION_SHA="e4cd0f44099475cb9ea8e85964d9ec6cc8b9156148fe439101fa871fcc475689"


def read(path):return json.loads(Path(path).read_text())
def sha(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()
def write_x(path,value):
 path=Path(path);path.parent.mkdir(parents=True,exist_ok=True);text=json.dumps(value,indent=2,sort_keys=True,allow_nan=False)+"\n"
 if path.exists():raise FileExistsError("immutable output exists: "+str(path))
 with path.open("x") as stream:stream.write(text)
def load_source():
 if str(V1) not in sys.path:sys.path.insert(0,str(V1))
 spec=importlib.util.spec_from_file_location("qualified_fresh48_source_train",V1/"train.py");module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
 leaf_spec=importlib.util.spec_from_file_location("qualified_fresh48_leaf_math",V1/"leaf_math.py");leaf=importlib.util.module_from_spec(leaf_spec);leaf_spec.loader.exec_module(leaf);module.leaf_math=leaf
 return module


def objective_term(token_logprobs,ratio,advantage,denominator=48):
 import torch
 weight=torch.as_tensor(ratio,dtype=token_logprobs.dtype,device=token_logprobs.device).detach()
 return -(weight*float(advantage)*token_logprobs.sum())/denominator


def replay_difference(actual,expected):
 if len(actual)!=len(expected):return {"passed":False,"support":False,"max_token_error":math.inf,"sequence_error":math.inf}
 if not all(math.isfinite(float(x)) for x in list(actual)+list(expected)):return {"passed":False,"support":True,"max_token_error":math.inf,"sequence_error":math.inf}
 token=max((abs(float(x)-float(y)) for x,y in zip(actual,expected,strict=True)),default=0.0);sequence=abs(math.fsum(map(float,actual))-math.fsum(map(float,expected)))
 return {"passed":token<=TOKEN_TOL and sequence<=SEQUENCE_TOL,"support":True,"max_token_error":token,"sequence_error":sequence}


def replay_failure_result(replay_sha):
 return {"status":"NO_UPDATE_GRADIENT_REPLAY_FAILED","optimizer_steps":0,"gradient_replay_check_sha256":replay_sha,"no_retry":True}


def expected_output(output):
 expected=(ROOT/"outputs/attempt-001").resolve()
 if Path(output).resolve()!=expected:raise ValueError("exact sealed output required")
 return expected


def verify_ready():
 ready=read(ROOT/"READY.json")
 for path,expected in ready["closure_sha256"].items():
  if sha(path)!=expected:raise ValueError("sealed input changed: "+path)
 return ready


def load_inputs(source):
 import numpy as np
 dataset,manifest,qualification=read(DATASET),read(MASK_MANIFEST),read(QUALIFICATION)
 if sha(QUALIFICATION)!=QUALIFICATION_SHA or qualification.get("gate_passed") is not True or qualification.get("gate_failures")!=[] or qualification.get("all_supported") is not True or qualification.get("all_finite") is not True:raise ValueError("fresh48 qualification differs")
 if manifest["dataset_sha256"]!=sha(DATASET) or manifest["masks_npz_sha256"]!=sha(MASKS):raise ValueError("dataset/masks differ")
 records=dataset["records"]
 if len(records)!=48 or sum(len(r["action_ids"]) for r in records)!=11901 or qualification["episode_ids"]!=[r["episode_id"] for r in records]:raise ValueError("fresh48 inventory differs")
 advantages=source.leaf_math.rloo_advantages([r["reward"] for r in records],[r["group_id"] for r in records],reward_scale=16)
 if any(not math.isclose(a,r["advantage"],abs_tol=1e-12) for a,r in zip(advantages,records,strict=True)):raise ValueError("count-scaled RLOO differs")
 diagnostics=source.leaf_math.importance_diagnostics(qualification["current_token_logprobs"],[r["old_logprobs"] for r in records],[True]*48,ess_fraction_min=.8,max_normalized_weight_limit=.1)
 for key in ("ratios","log_ratios","ess","max_normalized_weight","gate_failures","gate_passed"):
  if diagnostics[key]!=qualification[key]:raise ValueError("frozen qualification field differs: "+key)
 return dataset,records,np.load(MASKS,allow_pickle=False),qualification


def child_binding(checkpoint,state_sha):
 source=read(SOURCE_BINDING);binding=copy.deepcopy(source);alias=binding["fixed_child"];root=binding["role_map"]["root"]
 if binding["role_map"]["children"]!=[alias]:raise ValueError("source is not fixed one-child binding")
 binding["models"][alias]={"path":str(checkpoint),"adapter_sha256":sha(checkpoint/"adapter_model.safetensors"),"config_sha256":sha(checkpoint/"adapter_config.json")}
 binding["child_only_update"]={"experiment":ROOT.name,"step":1,"state_sha256":state_sha,"optimizer_sha256":sha(checkpoint/"optimizer.pt"),"rng_sha256":sha(checkpoint/"rng_state.pt"),"source_child":source["models"][alias],"root_unchanged":True,"qualified_offline_fresh48":True,"qualification_sha256":QUALIFICATION_SHA}
 if binding["models"][root]!=source["models"][root] or binding["campaign_policy"]!=source["campaign_policy"]:raise ValueError("root/campaign changed")
 return binding


def run(output,cap_seconds):
 import numpy as np
 import torch
 from peft import PeftModel
 from transformers import AutoModelForCausalLM
 if cap_seconds!=CAP:raise ValueError("exact900 cap required")
 output=expected_output(output)
 if output.exists():raise FileExistsError("attempt exists; refusing rerun")
 if not os.environ.get("CUDA_VISIBLE_DEVICES") or torch.cuda.device_count()!=1:raise ValueError("MAIN must assign exactly one GPU")
 ready=verify_ready();source=load_source();dataset,records,masks,qualification=load_inputs(source);output.mkdir(parents=True)
 write_x(output/"START.json",{"started_epoch":time.time(),"ready_identity":ready["identity"],"seed":SEED,"cap_seconds":CAP,"optimizer_steps":0,"source_qualification_sha256":QUALIFICATION_SHA})
 started=time.monotonic();completed_optimizer_steps=0;previous=signal.signal(signal.SIGALRM,lambda *_:(_ for _ in ()).throw(TimeoutError("900-second cap")));signal.setitimer(signal.ITIMER_REAL,CAP)
 try:
  random.seed(SEED);np.random.seed(SEED);torch.manual_seed(SEED);torch.cuda.manual_seed_all(SEED);torch.set_num_threads(4);torch.cuda.reset_peak_memory_stats()
  base=AutoModelForCausalLM.from_pretrained(dataset["model"]["base"],local_files_only=True,dtype=torch.bfloat16,attn_implementation="sdpa",device_map={"":"cuda:0"});model=PeftModel.from_pretrained(base,dataset["model"]["child_start"],is_trainable=True,autocast_adapter_dtype=True)
  model.train();model.config.use_cache=False
  for module in model.modules():
   if isinstance(module,torch.nn.Dropout):module.eval()
  model.enable_input_require_grads();model.gradient_checkpointing_enable(gradient_checkpointing_kwargs={"use_reentrant":False})
  checkpointing=bool(getattr(model,"is_gradient_checkpointing",False))
  if not checkpointing:raise RuntimeError("gradient checkpointing is not active in training mode")
  trainable=[(name,value) for name,value in model.named_parameters() if value.requires_grad]
  if not trainable or any("lora_" not in name or value.dtype!=torch.float32 for name,value in trainable):raise ValueError("only FP32 LoRA may train")
  before={name:value.detach().cpu().clone() for name,value in trainable};optimizer=torch.optim.AdamW([value for _,value in trainable],lr=LR,weight_decay=0);optimizer.zero_grad(set_to_none=True)
  replay_rows=[];captures=[]
  for index,record in enumerate(records):
   array=masks[record["mask_key"]]
   if list(array.shape)!=record["mask_shape"] or hashlib.sha256(array.tobytes(order="C")).hexdigest()!=record["mask_raw_sha256"]:raise ValueError("mask differs")
   values=source._selected_logprobs(model,record,array,require_grad=True);actual=values.detach().float().cpu().tolist();check=replay_difference(actual,qualification["current_token_logprobs"][index]);replay_rows.append({"episode_id":record["episode_id"],**check})
   if check["passed"]:
    loss=objective_term(values,qualification["ratios"][index],record["advantage"],48);loss.backward();captures.append({"episode_id":record["episode_id"],"context_id":record["context_id"],"reward":record["reward"],"advantage":record["advantage"],"importance_ratio":qualification["ratios"][index],"action_tokens":len(record["action_ids"]),"unscaled_sequence_loss":float((loss*48).detach().cpu())})
   del values
  replay={"schema":"fresh48-gradient-path-replay-gate-v1","computed_before_optimizer_step":True,"training_mode":True,"gradient_checkpointing_active":checkpointing,"dropout_modules_eval":True,"token_tolerance":TOKEN_TOL,"sequence_tolerance":SEQUENCE_TOL,"episodes":replay_rows,"all48_passed":len(replay_rows)==48 and all(r["passed"] for r in replay_rows),"max_token_error":max(r["max_token_error"] for r in replay_rows),"max_sequence_error":max(r["sequence_error"] for r in replay_rows),"optimizer_steps":0}
  write_x(output/"GRADIENT_REPLAY_CHECK.json",replay)
  if not replay["all48_passed"]:
   result=replay_failure_result(sha(output/"GRADIENT_REPLAY_CHECK.json"));write_x(output/"RESULT.json",result);return result
  gradient=float(torch.nn.utils.clip_grad_norm_([v for _,v in trainable],CLIP,error_if_nonfinite=True).cpu())
  if not math.isfinite(gradient) or gradient<=0:raise ValueError("gradient norm invalid")
  optimizer.step();completed_optimizer_steps=1;torch.cuda.synchronize();delta=math.sqrt(sum(float((value.detach().cpu()-before[name]).double().square().sum()) for name,value in trainable))
  if not math.isfinite(delta) or delta<=0:raise ValueError("adapter did not change")
  checkpoint=output/"checkpoint-0001";checkpoint.mkdir();model.save_pretrained(checkpoint,safe_serialization=True);optimizer_state=optimizer.state_dict()
  optimizer_state_steps=sorted({int(value["step"].item() if hasattr(value["step"],"item") else value["step"]) for value in optimizer_state["state"].values()})
  if optimizer_state_steps!=[1]:raise ValueError("optimizer state is not exactly step1")
  torch.save(optimizer_state,checkpoint/"optimizer.pt");torch.save({"python":random.getstate(),"numpy":np.random.get_state(),"torch":torch.get_rng_state(),"cuda":torch.cuda.get_rng_state_all()},checkpoint/"rng_state.pt");write_x(output/"CAPTURE.json",captures)
  state={"schema":"qualified-fresh48-leaf-rloo-checkpoint-v1","step":1,"optimizer_steps":1,"optimizer_state_steps":optimizer_state_steps,"seed":SEED,"starting_child":dataset["model"]["child_start"],"starting_child_adapter_sha256":dataset["model"]["child_adapter_sha256"],"dataset_sha256":sha(DATASET),"masks_sha256":sha(MASKS),"qualification_sha256":QUALIFICATION_SHA,"gradient_replay_check_sha256":sha(output/"GRADIENT_REPLAY_CHECK.json"),"objective":"raw detached full-sequence IS weighted within-group RLOO score-function gradient","gradient_estimator":"unclipped detached full-sequence importance-weighted score-function estimator before optimizer gradient clipping","sequence_reduction":"sum","batch_denominator":48,"importance_weight_clipping":None,"importance_weight_self_normalization":None,"reward":"fraction correct over16","reward_scale":16,"learning_rate":LR,"weight_decay":0,"gradient_clip_norm":CLIP,"gradient_norm_before_clip":gradient,"adapter_delta_l2":delta,"episodes":48,"groups":2,"child_loss_tokens":11901,"root_loss_tokens":0,"environment_loss_tokens":0,"gradient_checkpointing_active":checkpointing,"optimizer_parameter_names":[name for name,_ in trainable],"elapsed_seconds":time.monotonic()-started,"peak_allocated_bytes":torch.cuda.max_memory_allocated(),"peak_reserved_bytes":torch.cuda.max_memory_reserved(),"capture_sha256":sha(output/"CAPTURE.json"),"files_sha256":{name:sha(checkpoint/name) for name in ("adapter_model.safetensors","adapter_config.json","optimizer.pt","rng_state.pt")}}
  write_x(checkpoint/"state.json",state);binding=child_binding(checkpoint,sha(checkpoint/"state.json"));write_x(checkpoint/"EVAL_BINDING.json",binding)
  committed=[checkpoint/name for name in ("adapter_model.safetensors","adapter_config.json","optimizer.pt","rng_state.pt","state.json","EVAL_BINDING.json")]+[output/"CAPTURE.json",output/"GRADIENT_REPLAY_CHECK.json"]
  commit={"schema":"qualified-fresh48-leaf-rloo-step-commit-v1","status":"UPDATED","step":1,"optimizer_steps":1,"ready_identity":ready["identity"],"files_sha256":{str(path):sha(path) for path in committed}};write_x(checkpoint/"STEP_COMMIT.json",commit)
  result={"status":"UPDATED","optimizer_steps":1,"checkpoint":str(checkpoint),"checkpoint_state_sha256":sha(checkpoint/"state.json"),"step_commit_sha256":sha(checkpoint/"STEP_COMMIT.json"),"eval_binding":str(checkpoint/"EVAL_BINDING.json"),"eval_binding_sha256":sha(checkpoint/"EVAL_BINDING.json"),"qualification_sha256":QUALIFICATION_SHA,"gradient_replay_check_sha256":sha(output/"GRADIENT_REPLAY_CHECK.json"),"ready_identity":ready["identity"]};write_x(output/"RESULT.json",result);return result
 except BaseException as error:
  failure=output/"FAILURE.json"
  if output.exists() and not failure.exists():write_x(failure,{"error_type":type(error).__name__,"error":str(error),"optimizer_steps":completed_optimizer_steps,"elapsed_seconds":time.monotonic()-started})
  raise
 finally:
  signal.setitimer(signal.ITIMER_REAL,0);signal.signal(signal.SIGALRM,previous)


if __name__=="__main__":
 parser=argparse.ArgumentParser();parser.add_argument("--output",type=Path,required=True);parser.add_argument("--cap-seconds",type=int,required=True);args=parser.parse_args();print(json.dumps(run(args.output,args.cap_seconds),sort_keys=True))
