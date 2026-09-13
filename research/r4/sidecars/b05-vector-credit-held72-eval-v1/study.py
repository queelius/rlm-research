"""Held-only base/local/joint readout on the already frozen 12x2 schedule."""
import copy,functools,importlib.util,types
from pathlib import Path
ROOT=Path(__file__).resolve().parent;ROLLOUT=ROOT.parent/"b05-varied-vector-rollouts-v1"
spec=importlib.util.spec_from_file_location("vector_credit_held_source",ROLLOUT/"study.py");source_study=importlib.util.module_from_spec(spec);spec.loader.exec_module(source_study)
for name in ("read","sha","digest","write_x","bytes_x","now","load","aliases","tokenizer","renderer","decode_response","base_owner","MUSIQUE","MODEL","NATIVE","SOURCE","TRAIN","source","normalize","interface"):
    globals()[name]=getattr(source_study,name)
EVAL=ROOT.parent/"b05-flat-selection-rl-eval-v1";FLAT=ROOT.parent/"b05-flat-selection-rl-v1"
LOCAL=ROOT.parent/"b05-vector-credit-local-v3";JOINT=ROOT.parent/"b05-vector-credit-joint-v3"
READY=ROOT/"READY.json";ATTEMPT=ROOT/"outputs/attempt-001";HOST=ROLLOUT/"HOST_GOLD.json";INPUTS=ROLLOUT/"HELD_PUBLIC.json"
BASE=source_study.MODEL;MAX_PHYSICAL=72;CONCURRENCY=4;SCIENCE_SECONDS=600;OWNER_SECONDS=700;EXTERNAL_SECONDS=800
ARMS=("base","local","joint")

@functools.lru_cache(None)
def tasks():return read(INPUTS)["tasks"]
def task(call):return next(row for row in tasks() if row["root_id"]==call["root_id"])
@functools.lru_cache(None)
def active_roots():return [{"root_id":row["root_id"],"split":"held"} for row in tasks()]
@functools.lru_cache(None)
def calls():
    result=[]
    for i,call in enumerate(read(INPUTS)["calls"]):
        order=ARMS[i%3:]+ARMS[:i%3]
        for arm in order:result.append({**call,"arm":arm,"split":"held"})
    return result
def call_id(call):return f"held-{call['root_id']}-r{call['repeat']}-{call['arm']}"
def prompt(call):return task(call)["prompt"]
def request_for(call):
    value=copy.deepcopy(source_study.request_body(prompt(call),call["seed"],call["max_tokens"]));value["model"]={"base":str(BASE),"local":local_alias(),"joint":joint_alias()}[call["arm"]];return value
def request_body(_prompt,_seed,_max_tokens):raise AssertionError("collector must use request_for")
def decode_response(body,response):
    fn=source_study.decode_response;scope={**fn.__globals__,"MODEL_ALIAS":body["model"]}
    return types.FunctionType(fn.__code__,scope,fn.__name__,fn.__defaults__,fn.__closure__)(body,response)
def b05():return source_study.interface
def gold():return {row["root_id"]:set(row["gold_ids"]) for row in read(HOST)["rows"] if row["split"]=="held"}
def local_alias():return load("vector_credit_held_local_study",LOCAL/"study.py").ALIAS
def joint_alias():return load("vector_credit_held_joint_study",JOINT/"study.py").ALIAS
def endpoint(root):
    arm=load(f"vector_credit_held_{root.name}_study",root/"study.py")
    with aliases({"study":arm},root):return load(f"vector_credit_held_{root.name}_checkpoint",root/"checkpoint.py").endpoint()
def binding():
    values={"local":endpoint(LOCAL),"joint":endpoint(JOINT)};models={}
    for name,value in values.items():
        b=value["binding"];models[b["alias"]]={"path":value["checkpoint"],"adapter_sha256":b["adapter_sha256"],"config_sha256":b["adapter_config_sha256"]}
    return {"schema":"b05-vector-credit-held72-dual-adapter-binding-v1","models":models,
        "role_map":{"root":local_alias(),"children":[local_alias(),joint_alias()]},"selection":"both fixed sole step1; no accuracy selection",
        "actual_released_base_model":str(BASE),"base_control_adapter":None}
def dependencies():
    eval_study=load("vector_credit_held_runtime",EVAL/"study.py");return eval_study.dependencies()
def verify():
    ready=read(READY);assert ready["identity"]==digest({k:v for k,v in ready.items() if k!="identity"})
    for path,want in ready["closure_sha256"].items():assert sha(path)==want,path
    assert len(tasks())==12 and len(calls())==72 and len({call_id(c) for c in calls()})==72
    assert {c["seed"] for c in calls()}=={c["seed"] for c in read(INPUTS)["calls"]}
    assert all(len(request_for(c)["token_ids"])+384<=8192 for c in calls());assert binding()==read(ROOT/"BINDING.json")
    dependencies();return ready
