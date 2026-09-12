"""V2 conditional evaluator facade: unchanged panel, repaired-seed checkpoint only."""

import functools
import importlib.util
from pathlib import Path


ROOT = Path(__file__).resolve().parent
SIDE = ROOT.parent
SOURCE_EVAL = SIDE / "root-qs6-leaf-rloo-fresh-batch-invariant-one-update-unseen-eval-v1"
TRAINING = SIDE / "root-qs6-leaf-rloo-fresh-batch-invariant-one-update-v2"
TRAIN_OUTPUT = TRAINING / "outputs/attempt-001"
ATTEMPT = ROOT / "outputs/attempt-001"
TRAIN_READY_SHA = "c4a631fae66b535cdf681f45c41454bce5c6086e0ba0eee076e144d236350509"
TRAIN_READY_IDENTITY = "1f287356bac51be4222e29a6900f7c12f6d0cd24ded2db366e26e36c4b4688a9"


def _load_base():
    spec = importlib.util.spec_from_file_location("fresh48_one_update_eval_v1_sealed", SOURCE_EVAL / "one_update_panel_study.py")
    if spec is None or spec.loader is None: raise RuntimeError("cannot load sealed V1 evaluator")
    module = importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
    module.ROOT=ROOT;module.TRAINING=TRAINING;module.TRAIN_OUTPUT=TRAIN_OUTPUT;module.ATTEMPT=ATTEMPT
    module.TRAIN_READY_SHA=TRAIN_READY_SHA;module.TRAIN_READY_IDENTITY=TRAIN_READY_IDENTITY
    return module


base = _load_base()
read=base.read;sha=base.sha;digest=base.digest;write_x=base.write_x
C32=base.C32;NATIVE=base.NATIVE;MODEL=base.MODEL;PANEL=base.PANEL;CAP=base.CAP
SOURCE_BINDING=base.SOURCE_BINDING;CHILD_ALIAS=base.CHILD_ALIAS;QUALIFICATION_SHA=base.QUALIFICATION_SHA
panel=base.panel;schedule=base.schedule;dependencies=base.dependencies


def qualify_one_update(output=TRAIN_OUTPUT):
    result=base.qualify_one_update(Path(output))
    seeds=read(Path(output)/"RNG_SEEDS_ACTUAL.json")
    expected={"schema":"fresh48-one-update-rng-seeds-v2","master_seed_unchanged":True,
        "master_seed":202609121401,"python_seed":202609121401,"numpy_legacy_seed":745658489,
        "torch_seed":202609121401,"torch_cuda_all_seed":202609121401,"v1_failure_preserved":True}
    if any(seeds.get(key)!=value for key,value in expected.items()): raise ValueError("V2 RNG seed receipt differs")
    result={**result,"rng_seeds":seeds,"rng_seeds_sha256":sha(Path(output)/"RNG_SEEDS_ACTUAL.json")}
    return result


def binding():
    receipt=qualify_one_update()
    if ATTEMPT.exists(): write_x(ATTEMPT/"ELIGIBILITY.json",receipt)
    return receipt["binding"]


def verify():
    ready=read(ROOT/"READY.json")
    if ready.get("status")!="CPU_READY_CONDITIONAL_ON_UPDATED_STEP1_V2": raise ValueError("unexpected eval READY status")
    base.verify_hash_map(ready["closure_sha256"])
    if digest(schedule())!=ready["schedule_sha256"]: raise ValueError("frozen unseen schedule changed")
    qualify_one_update()
    return ready
