"""Qualified native collection plus prespecified derived policies."""
import argparse
import asyncio
import importlib.util
from pathlib import Path
import sys
import protocol as p
import study as s

def implementation():
    path=s.SIDE/"leaf-adapter-by-granularity-v1/bg_collect.py"
    if s.sha(path)!="c9e1da5a697e6315ef20118d2afb2d70ad2f242bbcb0fc9b2cb89193d9c1bcd5":raise ValueError("collector changed")
    old={n:sys.modules.get(n) for n in ("bg_study","bg_protocol")};sys.modules.update({"bg_study":s,"bg_protocol":p})
    try:
        spec=importlib.util.spec_from_file_location("taskaware_qualified_collect",path);module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
    finally:
        for n,v in old.items():
            if v is None:sys.modules.pop(n,None)
            else:sys.modules[n]=v
    return module

def summarize(rows,public,host,baselines):
    grouped={}
    for row in rows:
        c=row["coordinate"];grouped.setdefault((c["context_id"],c["selection_arm"],c["sample"]),[]).append(row)
    result=[]
    for episode in public:
        for arm in ("confidence","task_aware"):
            aa=sorted(grouped[(episode["id"],arm,"A")],key=lambda x:x["coordinate"]["repack"])
            bb=sorted(grouped[(episode["id"],arm,"B")],key=lambda x:x["coordinate"]["repack"])
            for policy,derived in (("single_a",p.derive_single(baselines[episode["id"]],aa)),("agreement_abstain_a_b",p.derive_agreement(baselines[episode["id"]],aa,bb))):
                row={"context_id":episode["id"],"cluster":episode["cluster"],"size":episode["size"],"selection_arm":arm,"derived_policy":policy,"status":derived["status"],"available":derived["available"],"valid":derived["valid"],"predicted_answer":None,"strict":None}
                if derived["valid"]:
                    spec=aa[0]["coordinate"];pred=p.reduce_j1(episode["records"],derived["labels"],spec);gold=p.reduce_j1(episode["records"],host[episode["id"]]["labels"],spec)
                    row.update(predicted_answer=pred["answer"],gold_answer=gold["answer"],strict=pred["answer"]==gold["answer"],overwritten=derived["overwritten"],abstentions=derived.get("abstentions",0))
                result.append(row)
    return result

async def run(endpoint,output,deadline,transport=None):
    module=implementation();value=await module.run(endpoint,output,deadline,transport)
    episodes=summarize(value["rows"],s.read(s.ROOT/"inputs/PUBLIC.json"),s.read(s.ROOT/"inputs/HOST_GOLD.json"),s.read(s.ROOT/"inputs/BASELINE.json"))
    s.write(Path(output)/"EPISODES.json",episodes);s.write(Path(output)/"SUMMARY.json",{"planned_physical_calls":48,"planned_derived_episodes":32,"valid":sum(x["valid"] for x in episodes),"null":sum(x["status"]=="null" for x in episodes),"observed_invalid":sum(x["status"]=="observed_invalid" for x in episodes),"root_model_calls":0,"runtime_fallback":False,"shared_derived_non_independent":True});return value
def main():
    ap=argparse.ArgumentParser();ap.add_argument("--endpoint",type=Path,required=True);ap.add_argument("--output",type=Path,required=True);ap.add_argument("--deadline",type=float,required=True);a=ap.parse_args();asyncio.run(run(a.endpoint,a.output,a.deadline))
if __name__=="__main__":main()

