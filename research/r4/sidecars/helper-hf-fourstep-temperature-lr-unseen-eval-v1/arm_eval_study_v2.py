"""Additive correction: arm binding experiment is the arm root name, not parent study name."""

import copy

import arm_eval_study as base


def verify_binding(checkpoint,state,source_binding,step,name):
 arm=base.ARMS[name];binding=base.read(checkpoint/"EVAL_BINDING.json");child=binding["models"][base.CHILD_ALIAS]
 expected_child={"path":str(checkpoint),"adapter_sha256":base.sha(checkpoint/"adapter_model.safetensors"),"config_sha256":base.sha(checkpoint/"adapter_config.json")}
 if child!=expected_child:raise ValueError("child binding files differ")
 update=binding.get("child_only_update",{});public=base.experimental_arm(name);seeds=base.read(base.TRAINING/arm["training_ready"])["seeds"]
 expected_experiment=arm["training_output"].parents[1].name
 if update.get("experiment")!=expected_experiment or update.get("step")!=step or update.get("cumulative_optimizer_steps")!=step or update.get("root_unchanged") is not True or update.get("state_sha256")!=base.sha(checkpoint/"state.json") or update.get("optimizer_sha256")!=base.sha(checkpoint/"optimizer.pt") or update.get("rng_sha256")!=base.sha(checkpoint/"rng_state.pt") or update.get("source_child")!=source_binding["models"][base.CHILD_ALIAS] or update.get("experimental_arm")!=public or update.get("fixed_training_seeds")!=seeds:raise ValueError("arm child-only update differs")
 expected=copy.deepcopy(source_binding);expected["models"][base.CHILD_ALIAS]=expected_child;expected["child_only_update"]=update
 if binding!=expected:raise ValueError("binding changed beyond child arm")
 return binding


base.verify_binding=verify_binding


def select(name):return base.select(name)
def qualify_arm(name):return base.qualify_arm(name)
def binding():return base.binding()
def verify(name,require_training=True):
 base.select(name);arm=base.ARMS[name];ready=base.read(base.ROOT/("READY_T2_V2.json" if name=="t2_lr1e5" else "READY_LR10X_V2.json"))
 if base.digest({k:v for k,v in ready.items() if k!="identity"})!=ready.get("identity"):raise ValueError("corrected eval READY identity differs")
 for path,expected in ready["closure_sha256"].items():
  if base.sha(path)!=expected:raise ValueError("corrected eval closure changed: "+path)
 if base.digest(base.schedule())!=ready["schedule_sha256"]:raise ValueError("panel schedule changed")
 if require_training:base.qualify_arm(name)
 return ready


def __getattr__(name):return getattr(base,name)
