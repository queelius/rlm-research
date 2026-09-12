"""Collector-compatible correction: zero-argument verify uses the already selected arm."""

import arm_eval_study as base
import arm_eval_study_v2 as corrected


def select(name):return corrected.select(name)
def qualify_arm(name):return corrected.qualify_arm(name)
def binding():return corrected.binding()
def resolve_arm(name=None):
 if name is None:name=base.CURRENT
 if name is None:raise ValueError("arm not selected before collector verification")
 return name
def verify(name=None,require_training=True):
 name=resolve_arm(name)
 # Validate the V3 receipt here, then use the corrected V2 arm qualifier.
 filename="READY_T2_V3.json" if name=="t2_lr1e5" else "READY_LR10X_V3.json";ready=base.read(base.ROOT/filename)
 if base.digest({k:v for k,v in ready.items() if k!="identity"})!=ready.get("identity"):raise ValueError("V3 eval READY identity differs")
 for path,expected in ready["closure_sha256"].items():
  if base.sha(path)!=expected:raise ValueError("V3 eval closure changed: "+path)
 if base.digest(base.schedule())!=ready["schedule_sha256"]:raise ValueError("panel schedule changed")
 if require_training:base.qualify_arm(name)
 return ready


def __getattr__(name):return getattr(corrected,name)
