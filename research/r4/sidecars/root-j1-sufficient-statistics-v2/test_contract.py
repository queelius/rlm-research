import asyncio,importlib.util,json
from pathlib import Path
import httpx
from tokenizers import Tokenizer
ROOT=Path(__file__).parent
def load(n):
 spec=importlib.util.spec_from_file_location("v2_"+n,ROOT/f"{n}.py");m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);return m
def test_exact_40_mapping_and_requests():
 b=load("prepare").build(False);old=json.load(open(ROOT.parent/"root-lambda-supplied-plan-ceiling-v1/inputs/PLAN.json"));assert len(b["plan"])==40
 assert [(x["context_id"],x["record_ids"],x["seed"]) for x in b["plan"]]==[(x["context_id"],x["ids"],x["seed"]) for x in old]
 counts={}
 for x in b["plan"]:counts.setdefault((x["size"],x["context_id"]),[]).append(x["n"])
 assert all(v==[32,32] for (size,_),v in counts.items() if size==64);assert all(v==[32]*8 for (size,_),v in counts.items() if size==256)
def test_missing_one_of_two_size64_chunks_is_null():
 c=load("collect");plan=[{"id":"a","context_id":"e","users":["u0"]},{"id":"b","context_id":"e","users":["u0"]}];score={"available":True,"complete_map":True,"stats":{"u0":{"has_target_a":False,"target_b_weight_sum":0}}};rows=[{"coordinate":plan[0],"score":score}];public=[{"id":"e","cluster":0,"size":64,"records":[]}]
 got=c.summarize(rows,plan,public,{"e":{"labels":{}}})[0];assert got["status"]=="null" and got["strict"] is None and got["absolute_error"] is None
def test_cross_chunk_and_invalid_semantics():
 p=load("protocol");rows=[{"score":{"available":True,"complete_map":True,"stats":{"u0":{"has_target_a":True,"target_b_weight_sum":0}}}},{"score":{"available":True,"complete_map":True,"stats":{"u0":{"has_target_a":False,"target_b_weight_sum":5}}}}];assert p.merge_chunks(rows,["u0"])["answer"]==5
 bad=json.dumps({"u0":{"has_target_a":True,"target_b_weight_sum":1},"u9":{"has_target_a":False,"target_b_weight_sum":0}});assert not p.score(bad,["u0"],{},True)["complete_map"]
def test_actual_nonempty_transport(tmp_path,monkeypatch):
 c,prep=load("collect"),load("prepare");b=prep.build(False);coord=b["plan"][0];body=b["requests"][coord["id"]];stats={u:{"has_target_a":False,"target_b_weight_sum":0} for u in coord["users"]};tok=Tokenizer.from_file(str(prep.TOKENIZER));ids=tok.encode(json.dumps(stats,separators=(",",":"))+"<|im_end|>",add_special_tokens=False).ids;raw={"model":body["model"],"request_id":"fixture","choices":[{"index":0,"finish_reason":"stop","token_ids":ids,"logprobs":{"content":[{"token":f"token_id:{x}","logprob":0.,"top_logprobs":[]} for x in ids]}}],"usage":{"prompt_tokens":len(body["token_ids"]),"completion_tokens":len(ids),"prompt_tokens_details":{"cached_tokens":0}}};values={"PLAN.json":[coord],"REQUESTS.json":{coord["id"]:body},"HOST_GOLD.json":{coord["context_id"]:{"labels":{}}},"PUBLIC.json":[],"endpoint.json":{"host":"x","port":1,"api_key_env":"K"}};monkeypatch.setenv("K","x");monkeypatch.setattr(c.s,"verify",lambda:{"identity":"x"});old=c.s.read;monkeypatch.setattr(c.s,"read",lambda p:values[Path(p).name] if Path(p).name in values else old(p));monkeypatch.setattr(c,"summarize",lambda *a:[]);got=asyncio.run(c.run(Path("endpoint.json"),tmp_path/"o",9999999999.,httpx.MockTransport(lambda r:httpx.Response(200,json=raw))));assert got["rows"][0]["score"]["complete_map"]
def test_owner_registered_wrapper():
 o=load("owner");assert o.collector_argv(Path("s"),Path("o"),1.)[1]==str(ROOT/"collect.py") and o.s.binding()["batch_granularity"]["planned"]==40
