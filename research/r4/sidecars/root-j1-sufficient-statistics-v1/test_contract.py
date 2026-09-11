import asyncio,importlib.util,json
from pathlib import Path
import httpx
from tokenizers import Tokenizer
ROOT=Path(__file__).parent
def load(name):
    spec=importlib.util.spec_from_file_location("ss_"+name,ROOT/f"{name}.py");m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);return m
def test_plan_mirrors_all_40_ceiling_chunks_without_gold_in_requests():
    value=load("prepare").build(write=False);assert len(value["plan"])==len(value["requests"])==40
    old=json.load(open(ROOT.parent/"root-lambda-supplied-plan-ceiling-v1/inputs/PLAN.json"))
    assert [(x["context_id"],x["record_ids"],x["seed"]) for x in value["plan"]]==[(x["context_id"],x["ids"],x["seed"]) for x in old]
    assert all(x["ids"]==x["users"] for x in value["plan"])
    assert all("gold" not in json.dumps(body).lower() for body in value["requests"].values())
def test_strict_stats_reject_irrelevant_user_and_missing_field():
    p=load("protocol");users=["u0","u1"]
    valid=json.dumps({"u0":{"has_target_a":True,"target_b_weight_sum":3},"u1":{"has_target_a":False,"target_b_weight_sum":2}})
    assert p.score(valid,users,{},True)["complete_map"]
    bad=json.dumps({"u0":{"has_target_a":True,"target_b_weight_sum":3},"u1":{"has_target_a":False,"target_b_weight_sum":2},"u9":{"has_target_a":False,"target_b_weight_sum":0}})
    assert not p.score(bad,users,{},True)["complete_map"]
    missing=json.dumps({"u0":{"has_target_a":True,"target_b_weight_sum":3},"u1":{"has_target_a":False}})
    assert not p.score(missing,users,{},True)["complete_map"]
def test_merge_handles_a_and_b_in_different_chunks_and_irrelevant_users():
    p=load("protocol");rows=[{"score":{"available":True,"complete_map":True,"stats":{"u0":{"has_target_a":True,"target_b_weight_sum":0},"u1":{"has_target_a":False,"target_b_weight_sum":7}}}},{"score":{"available":True,"complete_map":True,"stats":{"u0":{"has_target_a":False,"target_b_weight_sum":5},"u1":{"has_target_a":False,"target_b_weight_sum":11}}}}]
    got=p.merge_chunks(rows,["u0"]);assert got["answer"]==5 and got["has_target_a"]=={"u0":True} and got["target_b_weight_sum"]=={"u0":5}
    assert p.merge_chunks(rows+[{}],["u0"])["status"]=="null"
def test_nonempty_actual_transport_and_owner_wiring(tmp_path,monkeypatch):
    collect,prepare,owner=load("collect"),load("prepare"),load("owner");built=prepare.build(write=False);c=built["plan"][0];body=built["requests"][c["id"]]
    stats={u:{"has_target_a":False,"target_b_weight_sum":0} for u in c["users"]};tok=Tokenizer.from_file(str(prepare.TOKENIZER));ids=tok.encode(json.dumps(stats,separators=(",",":"))+"<|im_end|>",add_special_tokens=False).ids
    raw={"model":body["model"],"request_id":"fixture","choices":[{"index":0,"finish_reason":"stop","token_ids":ids,"logprobs":{"content":[{"token":f"token_id:{t}","logprob":0.,"top_logprobs":[]} for t in ids]}}],"usage":{"prompt_tokens":len(body["token_ids"]),"completion_tokens":len(ids),"prompt_tokens_details":{"cached_tokens":0}}}
    transport=httpx.MockTransport(lambda request:httpx.Response(200,json=raw));values={"PLAN.json":[c],"REQUESTS.json":{c["id"]:body},"HOST_GOLD.json":{c["context_id"]:{"labels":{}}},"PUBLIC.json":[],"endpoint.json":{"host":"x","port":1,"api_key_env":"FIXTURE_KEY"}}
    monkeypatch.setenv("FIXTURE_KEY","x");monkeypatch.setattr(collect.s,"verify",lambda:{"identity":"fixture"});old=collect.s.read;monkeypatch.setattr(collect.s,"read",lambda path:values[Path(path).name] if Path(path).name in values else old(path));monkeypatch.setattr(collect,"summarize",lambda *a:[])
    result=asyncio.run(collect.run(Path("endpoint.json"),tmp_path/"out",9999999999.,transport));assert result["rows"][0]["score"]["complete_map"]
    assert owner.collector_argv(Path("stage"),Path("out"),123.)[1]==str(ROOT/"collect.py") and owner.s.binding()["batch_granularity"]["planned"]==40

def test_collector_missing_last_required_chunk_is_null():
    collect=load("collect");users=["u0"];score={"available":True,"complete_map":True,"stats":{"u0":{"has_target_a":False,"target_b_weight_sum":0}}}
    rows=[{"coordinate":{"context_id":"e","batch":i,"users":users},"score":score} for i in range(3)]
    public=[{"id":"e","cluster":0,"size":64,"records":[]}];host={"e":{"labels":{}}}
    got=collect.summarize(rows,public,host);assert got[0]["status"]=="null" and got[0]["strict"] is None

def test_actual_owner_execute_starts_bound_service_and_releases(tmp_path,monkeypatch):
    owner,prepare=load("owner"),load("prepare");coordinate=prepare.build(write=False)["plan"][0];attempt=tmp_path/"attempt";seen={}
    class Suite:
        def start_service(self,stage,binding,deadline):seen["binding"]=binding
        def command(self,stage,name,argv,timeout,deadline):
            seen["argv"]=argv;d=attempt/"rollout/calls"/coordinate["id"];d.mkdir(parents=True);owner.s.write(d/"RESULT.json",{"coordinate":coordinate,"score":{"available":False,"complete_map":False,"strict_correct":None,"stats":None,"labels":None,"canonical_id_matches":None,"output_order_equal":None,"invalid_reason":None},"error":"CPU seam"})
        def release_service(self,stage):seen["released"]=True
    monkeypatch.setattr(owner.s,"ATTEMPT",attempt);monkeypatch.setattr(owner.s,"verify",lambda:{"identity":"fixture"});monkeypatch.setattr(owner.s,"dependencies",lambda:Suite());old=owner.s.read;monkeypatch.setattr(owner.s,"read",lambda path:[coordinate] if Path(path).name=="PLAN.json" else old(path));monkeypatch.setenv("CUDA_VISIBLE_DEVICES","fixture-gpu");monkeypatch.setenv("STRICT_RLM_CALIBRATION_API_KEY","fixture")
    got=owner.execute(attempt);assert got["complete"] and got["released"] and seen["released"]
    assert seen["binding"]["batch_granularity"]["planned"]==40 and seen["argv"][1]==str(ROOT/"collect.py")
