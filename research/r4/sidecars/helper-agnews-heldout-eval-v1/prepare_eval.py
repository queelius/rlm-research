"""Build batch-four temperature-zero requests for the frozen AG heldout256."""

import copy
import hashlib
import importlib.util
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parent
SIDE = ROOT.parent
FROZEN = SIDE / "helper-agnews-data-vs-mechanics-v1/inputs"
BUILDER = SIDE / "helper-unseen-generalization-panel-v1/build_panel.py"
BATCH_SOURCES = SIDE / "root-c32-helper-batchsize-v1/inputs/SOURCES.json"
MODEL = Path(
    "/project/alex_phd/research-cache/models/"
    "Qwen--Qwen3-4B-Instruct-2507--cdbee75f17c01a7cc42f958dc650907174af0554"
)
CHILD_ALIAS = "strict-rlm-qwen3-4b-role-sft-selected-v1"


def read(path): return json.loads(Path(path).read_text())
def sha(path): return hashlib.sha256(Path(path).read_bytes()).hexdigest()
def digest(value): return hashlib.sha256(json.dumps(value,sort_keys=True,separators=(",", ":")).encode()).hexdigest()


def load_builder():
    spec=importlib.util.spec_from_file_location("ag_eval_standard_builder",BUILDER)
    module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module);return module


def make_inputs():
    from transformers import AutoTokenizer
    builder=load_builder();public=read(FROZEN/"HELDOUT_PUBLIC.json");gold=read(FROZEN/"HELDOUT_GOLD.json")
    records=public["records"]
    if public.get("contains_gold") is not False or len(records)!=256 or set(gold["labels"])!={x["id"] for x in records}:
        raise ValueError("frozen heldout inventory differs")
    tokenizer=AutoTokenizer.from_pretrained(MODEL,local_files_only=True)
    historical=read(BATCH_SOURCES)["contexts"]["question-sensitive-sft-train-05"]["partitions"]["4"]["0"]
    old_ids=tokenizer.encode(historical["request_text"],add_special_tokens=False);body=historical["body"]
    hits=[i for i in range(len(body["token_ids"])-len(old_ids)+1) if body["token_ids"][i:i+len(old_ids)]==old_ids]
    if len(hits)!=1: raise ValueError("historical request subsequence differs")
    offset=hits[0];prefix=body["token_ids"][:offset];suffix=body["token_ids"][offset+len(old_ids):]
    requests=[]
    for start in range(0,256,4):
        group=records[start:start+4];request_text,labels=builder.prompt("ag_news",group);ids=[x["id"] for x in group]
        schema={"type":"object","properties":{i:{"type":"string","enum":labels} for i in ids},"required":ids,"additionalProperties":False}
        schema_text=json.dumps(schema,separators=(",", ":"),ensure_ascii=False)
        request_body={"model":CHILD_ALIAS,"token_ids":prefix+tokenizer.encode(request_text,add_special_tokens=False)+suffix,
            "sampling_params":{**body["sampling_params"],"temperature":0.0,"seed":202609121900+len(requests),"max_tokens":1024,"structured_outputs":{"json":schema}},"cache_salt":"0"}
        requests.append({"request_id":hashlib.sha256(f"agnews-heldout-v1|{start}".encode()).hexdigest(),"dataset":"ag_news","start":start,"ids":ids,"request_text":request_text,"schema_ordered_json":schema_text,"body_template":request_body})
    return {"public":public,"gold":gold,"requests":requests,"audit":{"calls":64,"records":256,"batch":4,"temperature":0.0,"standard_builder":str(BUILDER),"standard_builder_sha256":sha(BUILDER),"gold_prompted":False}}


def write_x(path,value,sort_keys=True):
    path=Path(path);path.parent.mkdir(parents=True,exist_ok=True)
    with path.open("x") as stream: stream.write(json.dumps(value,indent=2,sort_keys=sort_keys,ensure_ascii=False)+"\n")


def main():
    if (ROOT/"inputs").exists(): raise ValueError("immutable eval inputs exist")
    bundle=make_inputs();write_x(ROOT/"inputs/PUBLIC.json",bundle["public"]);write_x(ROOT/"inputs/HOST_GOLD.json",bundle["gold"])
    write_x(ROOT/"inputs/REQUESTS.json",bundle["requests"],sort_keys=False);write_x(ROOT/"inputs/BUILD_AUDIT.json",bundle["audit"])


if __name__=="__main__": main()
