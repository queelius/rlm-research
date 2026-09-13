"""Unordered known unique-ID exact/BA; sorted-format diagnostic separately."""
import json
import study
with study.aliases({"runner_study":study},study.SOURCE):costs=study.load("normalizer_native_costs",study.SOURCE/"runner_metrics.py").costs


def unique(items):
    result={}
    for k,v in items:
        if k in result:raise ValueError("duplicate key")
        result[k]=v
    return result


def grade(call,record,known,gold):
    row={**call,"call_id":study.call_id(call),"available":bool(record.get("transport_valid")),"semantic_valid":False,"strict_valid":False,"exact":False,"strict_exact":False,"balanced_accuracy":None,"ids":None}
    if not row["available"]:return row
    try:
        obj=json.loads(record["text"],object_pairs_hook=unique);assert type(obj) is dict and set(obj)=={"eligible_ids"}
        ids=obj["eligible_ids"];assert type(ids) is list and all(type(v) is str for v in ids)
        assert len(ids)==len(set(ids)) and set(ids)<=known
        pred=set(ids);tp=len(pred&gold);fp=len(pred-gold);fn=len(gold-pred);tn=len(known-gold-pred)
        recalls=([tp/len(gold)] if gold else [])+([tn/len(known-gold)] if known-gold else [])
        row.update(semantic_valid=True,strict_valid=ids==sorted(ids),exact=pred==gold,strict_exact=pred==gold and ids==sorted(ids),ids=ids,
                   tp=tp,fp=fp,fn=fn,tn=tn,balanced_accuracy=sum(recalls)/len(recalls),precision=tp/len(pred) if pred else None,recall=tp/len(gold) if gold else None)
    except (ValueError,TypeError,AssertionError,KeyError) as error:row["error"]=f"{type(error).__name__}: {error}"
    return row


def summarize(output,qualified):
    plan=study.read(study.INPUTS);gold={r["root_id"]:set(r["gold_ids"]) for r in study.read(study.HOST)["rows"]};tasks={r["root_id"]:r for r in plan["tasks"]}
    records={p.stem:study.read(p) for p in (output/"calls").glob("*.json")};starts={p.stem:study.read(p) for p in (output/"starts").glob("*.json")}
    expected={study.call_id(c) for c in plan["calls"]};assert set(records)<=expected and set(starts)<=expected
    start_only=set(starts)-set(records)
    for key in start_only:records[key]={**starts[key],"transport_valid":False,"usage":{},"status":"start_only_provider_unknown"}
    rows=[grade(c,records.get(study.call_id(c),{}),set(tasks[c["root_id"]]["known_ids"]),gold[c["root_id"]]) for c in plan["calls"]]
    arms={};pairs=[]
    for arm in ("raw","normalized"):
        selected=[r for r in rows if r["arm"]==arm];valid=[r for r in selected if r["semantic_valid"]]
        confusion={k:sum(r[k] for r in valid) for k in ("tp","fp","fn","tn")};tp,fp,fn=confusion["tp"],confusion["fp"],confusion["fn"]
        arms[arm]={"planned":18,"available":sum(r["available"] for r in selected),"unknown":sum(not r["available"] for r in selected),
                   "unordered_exact":sum(r["exact"] for r in selected),"semantic_valid":len(valid),"invalid_known":sum(r["available"] and not r["semantic_valid"] for r in selected),
                   "strict_valid":sum(r["strict_valid"] for r in selected),"strict_exact":sum(r["strict_exact"] for r in selected),"confusion":confusion,
                   "BA_valid_set_mean":sum(r["balanced_accuracy"] for r in valid)/len(valid) if valid else None,"BA_valid_set_denominator":len(valid),
                   "micro_precision_valid_sets":tp/(tp+fp) if tp+fp else None,"micro_recall_valid_sets":tp/(tp+fn) if tp+fn else None,
                   "cost":costs([records.get(r["call_id"],{}) for r in selected],18)}
    for a in [r for r in rows if r["arm"]=="raw"]:
        b=next(r for r in rows if r["arm"]=="normalized" and (r["root_id"],r["repeat"])==(a["root_id"],a["repeat"]))
        assert a["seed"]==b["seed"]
        pairs.append({"root_id":a["root_id"],"repeat":a["repeat"],"seed":a["seed"],"paired_known":a["available"] and b["available"],"raw_exact":a["exact"],"normalized_exact":b["exact"],"BA_change":b["balanced_accuracy"]-a["balanced_accuracy"] if a["semantic_valid"] and b["semantic_valid"] else None})
    known=[p for p in pairs if p["paired_known"]];available=sum(r["available"] for r in rows)
    return {"schema":"b05-public-mechanical-normalization-held9-result-v1","complete":bool(qualified and available==36 and not start_only),"runtime_qualified":qualified,
            "planned":36,"available":available,"unknown":36-available,"context_units":9,"paired_seed_units":18,"arms":arms,"pairs":pairs,"rows":rows,
            "normalized_wins":sum(not p["raw_exact"] and p["normalized_exact"] for p in known),"normalized_losses":sum(p["raw_exact"] and not p["normalized_exact"] for p in known),
            "cost":costs(list(records.values()),36),"start_only":sorted(start_only),"unattempted":sorted(expected-set(records)),"unknown_is_not_wrong":True,
            "primary":"unordered known unique-ID exact; BA/precision/recall on explicitly valid-ID-set denominator","strict_sorted_format_separate":True,
            "no_eligibility_computation_in_normalizer":True,"natural_model_calls_per_answer":1,"token_costs_not_matched":True,"not_learned_decomposition":True}
