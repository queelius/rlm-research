"""CPU-only, gold-blind task-aware panel preparation."""
import copy
import hashlib
import json
from pathlib import Path
from tokenizers import Tokenizer
import study as s

NAMESPACE="root-task-aware-selective-recheck-v1"
TOKENIZER=Path("/project/alex_phd/research-cache/models/Qwen--Qwen3-4B-Instruct-2507--cdbee75f17c01a7cc42f958dc650907174af0554/tokenizer.json")
LABELS=("human being","location","abbreviation","entity","description and abstract concept","numeric value")
DEFINITIONS="""Classify the type of answer requested, not words mentioned in the question.
human being: a person, an organization or group of people, or a person's role, title or description.
location: a geographic place, including a city, country, state, mountain or other place.
abbreviation: a shortened form, or the expanded wording represented by a shortened form.
entity: a nonhuman, nongeographic thing or name, including objects, organisms, works, events, substances, methods or synonymous terms.
description and abstract concept: a definition, explanation, reason or manner of doing something, rather than a particular name or number.
numeric value: a quantity, count, measurement, date, duration, rank or numerical code."""

def hash_rank(salt,episode,record):
    return hashlib.sha256(json.dumps([salt,episode,record],separators=(",",":")).encode()).hexdigest()
def reduce_j1(records,labels,spec):
    users={r["user"] for r in records if r["user"] in spec["users"] and labels[r["id"]]==spec["target"]}
    return sum(r["weight"] for r in records if r["user"] in users and labels[r["id"]]==spec["target_b"])
def prompt(records):
    visible=[{"id":r["id"],"text":r["text"]} for r in records]
    return "Classify the type of answer requested by each question using these TREC definitions:\n"+DEFINITIONS+"\nReturn only one JSON object mapping every supplied id exactly once to one of the six full category labels listed above. No missing or extra ids.\nRecords: "+json.dumps(visible,separators=(",",":"),ensure_ascii=False)
def build(write=True):
    public=s.read(s.BASE/"inputs/PUBLIC.json");baseline=s.read(s.BASE/"inputs/BASELINE.json");host=s.read(s.BASE/"inputs/HOST_GOLD.json")
    confidence=s.read(s.BASE/"inputs/CONFIDENCE.json");oldsel={x["context_id"]:x for x in s.read(s.BASE/"inputs/SELECTIONS.json")}
    oldplan=s.read(s.BASE/"inputs/PLAN.json");oldrequests=s.read(s.BASE/"inputs/REQUESTS.json")
    tokenizer=Tokenizer.from_file(str(TOKENIZER));template=copy.deepcopy(next(iter(oldrequests.values())))
    decoded=tokenizer.decode(template["token_ids"],skip_special_tokens=False);marker="<|im_start|>user\n"
    start=decoded.index(marker)+len(marker);end=decoded.index("<|im_end|>\n<|im_start|>assistant",start);prefix,suffix=decoded[:start],decoded[end:]
    plan=[];requests={};selections=[]
    for ei,episode in enumerate(sorted(public,key=lambda x:(x["cluster"],x["size"]))):
        eid=episode["id"];records={r["id"]:r for r in episode["records"]};base=baseline[eid]
        spec=next(x for x in oldplan if x["context_id"]==eid);current=reduce_j1(episode["records"],base,spec)
        ranked=sorted(confidence[eid],key=lambda k:(confidence[eid][k],hash_rank(s.BASE.name+"/confidence-tie",eid,k)))
        uncertainty={k:(len(ranked)-i)/len(ranked) for i,k in enumerate(ranked)};influence={}
        for key in ranked:
            influence[key]=max(abs(reduce_j1(episode["records"],dict(base,**{key:alt}),spec)-current) for alt in LABELS if alt!=base[key])
        task=sorted(ranked,key=lambda k:(-uncertainty[k]*influence[k],-influence[k],confidence[eid][k],hash_rank(NAMESPACE+"/task-aware-tie",eid,k)))[:episode["size"]//4]
        arms={"confidence":oldsel[eid]["confidence"],"task_aware":task};overlap=sorted(set(arms["confidence"])&set(task))
        selections.append({"context_id":eid,"cluster":episode["cluster"],"size":episode["size"],"budget":episode["size"]//4,"confidence":arms["confidence"],"task_aware":task,"overlap":overlap,"influence":influence,"uncertainty_percentile":uncertainty})
        order={r["id"]:i for i,r in enumerate(episode["records"])}
        for arm in ("confidence","task_aware"):
            ordered=sorted(arms[arm],key=order.get)
            for sample_i,sample in enumerate(("A","B")):
                for offset in range(0,len(ordered),32):
                    ids=ordered[offset:offset+32];repack=offset//32;seed=1002050001+4*ei+2*sample_i+repack
                    row={k:spec[k] for k in ("cluster","size","family","operator","target","target_b","scope","users","threshold")}
                    row.update(context_id=eid,selection_arm=arm,sample=sample,repack=repack,seed=seed,n=len(ids),ids=ids,model_policy="c32",root_model_calls=0,dispatch_order=len(plan));row["id"]=s.digest([NAMESPACE,row]);plan.append(row)
                    body=copy.deepcopy(template);body["token_ids"]=tokenizer.encode(prefix+prompt([records[k] for k in ids])+suffix,add_special_tokens=False).ids;body["sampling_params"]["seed"]=seed
                    body["sampling_params"]["structured_outputs"]["json"]={"type":"object","properties":{k:{"type":"string","enum":list(LABELS)} for k in sorted(ids)},"required":ids,"additionalProperties":False}
                    if len(body["token_ids"])+2048>8192:raise ValueError("context admission")
                    requests[row["id"]]=body
    overlap=sum(len(x["overlap"]) for x in selections)/320
    value={"plan":plan,"requests":requests,"public":sorted(public,key=lambda x:(x["cluster"],x["size"])),"host":host,"baseline":baseline,"confidence":confidence,"selections":selections,"overlap_fraction":overlap}
    if write:
        for name,data in (("PLAN.json",plan),("REQUESTS.json",requests),("PUBLIC.json",value["public"]),("HOST_GOLD.json",host),("BASELINE.json",baseline),("CONFIDENCE.json",confidence),("SELECTIONS.json",selections)):s.write(s.ROOT/"inputs"/name,data)
        s.write(s.ROOT/"CPU_INPUT_NATIVE.json",{"planned_physical_calls":48,"planned_derived_episodes":32,"selected_labels_per_selection_sample":320,"selection_overlap_count":sum(len(x["overlap"]) for x in selections),"selection_overlap_fraction":overlap,"overlap_gate":.90,"overlap_gate_passed":overlap<=.90,"selection_uses_gold":False,"samples":["A","B"],"derived_policies":["single_a","agreement_abstain_a_b"]})
    return value
if __name__=="__main__":build()
