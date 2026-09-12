"""Unique local module bindings; unchanged qualified512 wire, metrics and step gates."""
import ast
import hashlib
import importlib.util
import inspect
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
SIDE = ROOT.parent
SOURCE = SIDE/"helper-agnews-fresh512-eval-v1"
TRAIN = SIDE/"helper-agnews-native-hf-eightstep-seed2-v1"
TRAIN_READY_SHA = "abafc45c35a038aee97ccb7a4dce4dee8c2ce03b111a9430bd2c17022ac20853"
ARM = "rl_seed2_step8"
PINS = {
    "study.py":"9deb777a789be6a9fa630d9d529f2ab8b89573012ff91e8d824467dea84ecf24",
    "eligibility.py":"b62864f9331f4794a4940ec8cc08460a64688c9ab16cede568f251c826bc68c8",
    "collect.py":"987eefb0c1aea3afa42167f4339f55a6229b6f636377d7fb0c04d99854e97ccf",
    "owner.py":"c0a125fcdc6eb394f0ee6e216aac7e6a544d4fe337f3eac459af2281d4409ed8",
    "metrics.py":"09aa59b6aa60a99d1d062612d2738800db7f94a68b020318233ac11fe8742ead",
    "compare.py":"09dc0db5e3067a46dbdd992da82b775f311bed4822e83eb88bab32bdf6b9d127",
    "test_fixture.py":"dd9d399c59dabb862003dcb909561981fe3123adce738bf4b6b629e820ba6d58",
}


def payload(name):
    raw = (SOURCE/name).read_bytes()
    if hashlib.sha256(raw).hexdigest() != PINS[name]:
        raise ValueError("sealed evaluation source differs: "+name)
    return raw.decode()


def direct(name,path):
    spec = importlib.util.spec_from_file_location(name,path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


reuse = direct("seed2_eval_training_reuse",TRAIN/"reuse.py")
prior_core = direct("seed2_eval_prior_core",reuse.PRIOR/"core.py")
core = prior_core.load_bound("seed2_eval_exact_core",TRAIN/"core.py",{"reuse":reuse})
if core.sha(TRAIN/"READY.json") != TRAIN_READY_SHA:
    raise ValueError("exact seed2 training READY differs")


def load(name,file,bindings):
    payload(file)
    return core.load_bound(name,SOURCE/file,bindings)


old_study = load("seed2_eval_original_study","study.py",{})
study = load("seed2_eval_current_study","study.py",{})
study.ROOT,study.RL,study.rl,study.ARMS = ROOT,TRAIN,core,(ARM,)
original_plan = study.plan


def plan(arm):
    value = original_plan(arm)
    value.update(schema="agnews-same512-training-seed-replica-eval-v1",
        same_exposed512=True,training_seed_replication_not_new_dataset=True,
        training_ready_sha256=TRAIN_READY_SHA)
    return value


study.plan = plan
eligibility = load("seed2_eval_current_eligibility","eligibility.py",{"study":study})
original_endpoint = inspect.getsource(eligibility.rl_endpoint)
# Only admission-launch metadata preceding FINAL_RESULT changes. The complete
# original8-step raw/mask/importance/replay/serialized-Adam loop is retained verbatim.
tail = original_endpoint.split('    final = study.read(',1)[1]
replacement = '''def rl_endpoint():
    ready = study.rl.verify()
    if study.sha(study.RL / "READY.json") != RL_REPAIR_SHA:
        raise ValueError("exact seed2 training closure differs")
    launch_path = study.rl.ATTEMPT / "segment-after-000-START.json"
    launch = study.read(launch_path)
    admission = launch["admission"]
    source_admission = study.read(admission["path"])
    if (admission["sha256"] != study.sha(admission["path"])
        or admission["receipt"] != source_admission
        or source_admission.get("cpu_fixture")
        or source_admission.get("authority") != "MAIN"
        or source_admission.get("decision") != "APPROVE_TRAINING_SEED_REPLICATION"
        or source_admission.get("training_ready_sha256") != RL_REPAIR_SHA
        or launch["planned_final_step"] != 8
        or launch["data_manifest_sha256"] != ready["data_manifest_sha256"]):
        raise ValueError("actual seed2 MAIN admission/start receipt differs")
    final = study.read(''' + tail
replacement = replacement.replace('"arm": "rl_step8"','"arm": "rl_seed2_step8"')
source_step_gate_text = original_endpoint.split("    for step in range(1, 9):",1)[1].split('    checkpoint = Path(parent["checkpoint"])',1)[0]
replica_step_gate_text = replacement.split("    for step in range(1, 9):",1)[1].split('    checkpoint = Path(parent["checkpoint"])',1)[0]
assert source_step_gate_text == replica_step_gate_text
eligibility.RL_REPAIR_SHA = TRAIN_READY_SHA
exec(compile(replacement,str(ROOT/"replica_endpoint_gate"),"exec"),eligibility.__dict__)


def qualify(arm):
    if arm != ARM:
        raise ValueError("only predeclared replica step8 is collected")
    return eligibility.rl_endpoint()


def fixed_endpoints(arm):
    if arm != ARM:
        raise ValueError("unknown replica arm")
    path = ROOT/"ENDPOINTS_FIXED.json"
    receipt = study.read(path)
    current = qualify(arm)
    if (receipt.get("authority") != "MAIN" or receipt.get("fixed_step") != 8
        or receipt.get("prior_seed1_panel_consulted") is not True
        or receipt.get("replica_checkpoint_consulted_before_fix") is not False
        or receipt.get("training_ready_sha256") != TRAIN_READY_SHA
        or receipt.get("data_manifest_sha256") != study.sha(study.DATA/"inputs/MANIFEST.json")):
        raise ValueError("truthful pre-query MAIN fixed replica receipt required")
    expected = receipt.get("trained_endpoints",{})
    if set(expected) != {ARM}:
        raise ValueError("fixed final replica only, no checkpoint selection")
    for key in ("checkpoint","state_sha256","step_commit_sha256","binding_sha256"):
        if expected[ARM].get(key) != current[key]:
            raise ValueError("fixed replica checkpoint/binding changed: "+key)
    return dict(fixed_receipt_path=str(path),fixed_receipt_sha256=study.sha(path),
                selected_endpoints={ARM:current},arm_eligibility=current)


eligibility.qualify,eligibility.fixed_endpoints = qualify,fixed_endpoints
collect = load("seed2_eval_current_collect","collect.py",{"study":study})
metrics = load("seed2_eval_unchanged_metrics","metrics.py",{})
bindings = {"study":study,"collect":collect,"metrics":metrics,"eligibility":eligibility}
owner = load("seed2_eval_current_owner","owner.py",bindings)
compare = load("seed2_eval_current_raw_audit","compare.py",bindings)


def original_audit():
    old_elig = load("seed2_eval_original_eligibility","eligibility.py",{"study":old_study})
    old_collect = load("seed2_eval_original_collect","collect.py",{"study":old_study})
    return load("seed2_eval_original_raw_audit","compare.py",
        {"study":old_study,"collect":old_collect,"metrics":metrics,"eligibility":old_elig})


def probe_committed_step(step):
    """CPU actual inner gate on an existing seed1 step; never admits replica endpoint."""
    tree = ast.parse(original_endpoint)
    loop = next(n for n in tree.body[0].body if isinstance(n,ast.For)
                and isinstance(n.target,ast.Name) and n.target.id == "step")
    function = ast.FunctionDef(name="probe",args=ast.arguments(posonlyargs=[],args=[ast.arg(arg="step")],
        kwonlyargs=[],kw_defaults=[],defaults=[]),body=loop.body,decorator_list=[])
    module = ast.fix_missing_locations(ast.Module(body=[function],type_ignores=[]))
    old_elig = load("seed2_eval_probe_original_eligibility","eligibility.py",{"study":old_study})
    scope = dict(old_elig.__dict__,ready=old_study.rl.verify())
    exec(compile(module,str(SOURCE/"eligibility.py"),"exec"),scope)
    scope["probe"](step)
    return dict(passed=True,step=step,actual_raw_masks_importance_and_Adam=True,
                unchanged_replica_inner_gate=True,replica_endpoint_admitted=False,GPU_launched=False)


def actual_step_gate(step):
    """Same complete inner gate, bound to the newly committed replica step."""
    import os
    import time
    if os.environ.get("CUDA_VISIBLE_DEVICES") != "":
        raise ValueError("step audit must hide CUDA")
    started=time.monotonic()
    ready=core.verify()
    parent=core.verify_commit(step)
    tree=ast.parse(original_endpoint)
    loop=next(n for n in tree.body[0].body if isinstance(n,ast.For)
              and isinstance(n.target,ast.Name) and n.target.id == "step")
    function=ast.parse("def probe(step, ready):\n    pass\n").body[0]
    function.body=loop.body
    scope=dict(eligibility.__dict__)
    exec(compile(ast.fix_missing_locations(ast.Module(body=[function],type_ignores=[])),
                 str(ROOT/"actual_replica_step_gate"),"exec"),scope)
    scope["probe"](step,ready)
    return dict(step=step,passed=True,actual_source_loader_importance_and_optimizer_exercised=True,
        authenticated_step_commit_sha256=parent["step_commit_sha256"],
        source_sha256=PINS["eligibility.py"],unchanged_full_per_step_gate=True,
        full8_endpoint_gate_modified=False,endpoint_admitted=False,GPU_or_model_forward=False,
        elapsed_seconds=time.monotonic()-started)
