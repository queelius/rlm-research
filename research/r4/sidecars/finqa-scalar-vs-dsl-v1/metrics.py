"""Fixed32 denominator, official provided-target equality; source truth is separate."""
import collections
import science
import study
with study.aliases({"runner_study":study},study.SOURCE):
    inherited=study.load("finqa_native_costs",study.SOURCE / "runner_metrics.py")


def summarize(output,runtime_qualified):
    plans=study.calls()
    expected={study.call_id(call):call for call in plans}
    records={path.stem:study.read(path) for path in (output / "calls").glob("*.json")}
    starts={path.stem:study.read(path) for path in (output / "starts").glob("*.json")}
    assert set(records)<=set(expected) and set(starts)<=set(expected)
    start_only=set(starts)-set(records)
    for key in start_only:
        records[key]={**starts[key],"status":"start_only_provider_unknown","usage":{},"transport_valid":False}
    public={row["id"]:row for row in study.read(study.INPUTS)["contexts"]}
    targets={row["id"]:row for row in study.read(study.HOST)["contexts"]}
    rows=[]
    for key,call in expected.items():
        record=records.get(key,{})
        target=targets[call["example_id"]]
        row={"call_id":key,"example_id":call["example_id"],"arm":call["kind"],"seed":call["seed"],
             "available":bool(record.get("transport_valid")),"correct_provided_target":False,
             "interpretation":None,"annotation_flag":target["annotation_flag"],"provided_target":target["exe_ans"]}
        if row["available"]:
            decoded=science.evaluate(record["text"],call["kind"],public[call["example_id"]]["public"])
            row["interpretation"]=decoded
            row["correct_provided_target"]=decoded["status"]=="valid" and decoded["value"]==target["exe_ans"]
        rows.append(row)
    arms={}
    for arm in ("direct_scalar","restricted_dsl"):
        selected=[row for row in rows if row["arm"]==arm]
        valid=[row for row in selected if row["interpretation"] and row["interpretation"]["status"]=="valid"]
        arm_records=[records.get(study.call_id(call),{}) for call in plans if call["kind"]==arm]
        arms[arm]={"planned":16,"available":sum(row["available"] for row in selected),"valid_outputs":len(valid),
                   "invalid_known":sum(row["available"] and row not in valid for row in selected),
                   "unknown":sum(not row["available"] for row in selected),
                   "correct_provided_target":sum(row["correct_provided_target"] for row in selected),
                   "source_operand_value_present":sum(row["interpretation"].get("source_operand_value_presence") is True for row in valid),
                   "cost":inherited.costs(arm_records,16)}
    pairs=[]
    for example_id in public:
        pair={row["arm"]:row for row in rows if row["example_id"]==example_id}
        a,b=pair["direct_scalar"],pair["restricted_dsl"]
        pairs.append({"example_id":example_id,"paired_known":a["available"] and b["available"],
                      "direct_correct":a["correct_provided_target"],"dsl_correct":b["correct_provided_target"]})
    known=[row for row in pairs if row["paired_known"]]
    return {"schema":"finqa-scalar-vs-restricted-json-dsl-result-v1","runtime_qualified":runtime_qualified,
            "complete":bool(runtime_qualified and set(records)==set(expected) and not start_only and all(row.get("transport_valid") for row in records.values())),
            "planned_coordinates":32,"context_units":16,"arms":arms,"rows":rows,"pairs":pairs,
            "paired_known":len(known),"dsl_wins":sum(not row["direct_correct"] and row["dsl_correct"] for row in known),
            "dsl_losses":sum(row["direct_correct"] and not row["dsl_correct"] for row in known),
            "physical_cost":inherited.costs(list(records.values()),32),"natural_model_calls_per_answer":1,
            "missing_call_ids":sorted(set(expected)-set(records)),"start_only_call_ids":sorted(start_only),
            "provided_target_metric_not_semantic_truth":True,"JSON_DSL_not_official_program_accuracy":True,
            "source_value_presence_not_identity_or_faithfulness":True,"recursive_planner_or_novelty_claim":False}
