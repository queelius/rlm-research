"""Qualified native collection and strict per-protocol recheck reduction."""
import argparse
import asyncio
import importlib.util
from pathlib import Path
import sys

import protocol as p
import study as s


def implementation():
    path=s.SIDE/"leaf-adapter-by-granularity-v1/bg_collect.py"
    if s.sha(path)!="c9e1da5a697e6315ef20118d2afb2d70ad2f242bbcb0fc9b2cb89193d9c1bcd5": raise ValueError("qualified collector changed")
    old={name:sys.modules.get(name) for name in ("bg_study","bg_protocol")};sys.modules.update({"bg_study":s,"bg_protocol":p})
    try:
        spec=importlib.util.spec_from_file_location("selective_recheck_qualified_collect",path);module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
    finally:
        for name,value in old.items():
            if value is None:sys.modules.pop(name,None)
            else:sys.modules[name]=value
    return module


def summarize(rows,public,host,baselines):
    grouped={}
    for row in rows:grouped.setdefault((row["coordinate"]["context_id"],row["coordinate"]["selection_arm"]),[]).append(row)
    episodes=[]
    for episode in public:
        for arm in ("confidence","uniform"):
            values=sorted(grouped[(episode["id"],arm)],key=lambda x:x["coordinate"]["repack"]);merged=p.merge_selected(baselines[episode["id"]],values)
            result={"context_id":episode["id"],"cluster":episode["cluster"],"size":episode["size"],"selection_arm":arm,"status":merged["status"],"available":merged["available"],"valid":merged["valid"],"predicted_answer":None,"strict":None if not merged["available"] else False,"absolute_error":None,"merged_leaf_correct":None,"gold_answer":host[episode["id"]]["answers"]["J1"]}
            if merged["valid"]:
                spec=values[0]["coordinate"];reduction=p.reduce_j1(episode["records"],merged["labels"],spec);gold=p.reduce_j1(episode["records"],host[episode["id"]]["labels"],spec)
                result.update(predicted_answer=reduction["answer"],strict=reduction["answer"]==result["gold_answer"],absolute_error=abs(reduction["answer"]-result["gold_answer"]),merged_leaf_correct=sum(merged["labels"][key]==value for key,value in host[episode["id"]]["labels"].items()),predicted_qualifying_users=reduction["qualifying_users"],gold_qualifying_users=gold["qualifying_users"],contribution_errors={key:reduction["contributions"][key]-value for key,value in gold["contributions"].items()})
            episodes.append(result)
    return episodes


async def run(endpoint,output,deadline,transport=None):
    module=implementation();result=await module.run(endpoint,output,deadline,transport)
    episodes=summarize(result["rows"],s.read(s.ROOT/"inputs/PUBLIC.json"),s.read(s.ROOT/"inputs/HOST_GOLD.json"),s.read(s.ROOT/"inputs/BASELINE.json"))
    s.write(Path(output)/"EPISODES.json",episodes);s.write(Path(output)/"SUMMARY.json",{"planned":16,"valid":sum(x["valid"] for x in episodes),"null":sum(x["status"]=="null" for x in episodes),"observed_invalid":sum(x["status"]=="observed_invalid" for x in episodes),"strict":sum(x["strict"] is True for x in episodes),"root_model_calls":0,"runtime_fallback":False})
    return result


def main():
    ap=argparse.ArgumentParser();ap.add_argument("--endpoint",type=Path,required=True);ap.add_argument("--output",type=Path,required=True);ap.add_argument("--deadline",type=float,required=True);args=ap.parse_args();asyncio.run(run(args.endpoint,args.output,args.deadline))


if __name__=="__main__":main()
