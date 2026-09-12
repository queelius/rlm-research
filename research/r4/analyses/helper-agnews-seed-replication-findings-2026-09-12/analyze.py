"""Secondary exact paired diagnostics from the single qualified raw scorer."""
import argparse
import hashlib
import json
import os
import time
from pathlib import Path

ROOT=Path(__file__).resolve().parent
STORE=ROOT.parent.parent
SIDE=STORE/"sidecars"
WATCH=ROOT.parent/"helper-agnews-eightstep-seed2-live-audit-2026-09-12"
ORIGINAL=ROOT.parent/"helper-agnews-eightstep-live-audit-2026-09-12/outcomes/RAW_AUDIT-003.json"
ARM="rl_seed2_step8"
read=lambda p:json.loads(Path(p).read_text())
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()


def derive(original,current,gold,groups):
    baseline=original["arms"]["c32"]
    seed1=original["arms"]["rl_step8"]
    seed2=current["arms"][ARM]
    if baseline["predictions"]!=current["arms"]["c32"]["predictions"] or seed1["predictions"]!=current["arms"]["rl_step8"]["predictions"]:
        raise ValueError("reused reference predictions changed")
    b,a,c=(x["predictions"] for x in (baseline,seed1,seed2))
    for arm in (baseline,seed1,seed2):
        pred=arm["predictions"]
        if (not set(pred)<=set(gold) or arm["metrics"]["available_predictions"]!=len(pred)
            or arm["metrics"]["correct"]!=sum(pred[i]==gold[i] for i in pred)):
            raise ValueError("saved arm correctness/availability differs from audited predictions")
    first=original["comparisons"]["c32_vs_rl_step8"]
    second=current["comparisons"]["c32_vs_"+ARM]
    between=current["comparisons"]["rl_step8_vs_"+ARM]
    common=set(gold)&set(b)&set(a)&set(c)
    win1={i for i in common if b[i]!=gold[i]==a[i]}
    win2={i for i in common if b[i]!=gold[i]==c[i]}
    loss1={i for i in common if b[i]==gold[i]!=a[i]}
    loss2={i for i in common if b[i]==gold[i]!=c[i]}
    if second.get("available"):
        assert len(win2)==second["wins"] and len(loss2)==second["losses"]
        assert sum(b[i]!=c[i] for i in common)==second["category_disagreements"]
    if len(common)==512:
        assert len(win1)==first["wins"] and len(loss1)==first["losses"]
    classes={}
    for label in sorted(set(gold.values())):
        ids={i for i in common if gold[i]==label}
        classes[label]=dict(planned=sum(x==label for x in gold.values()),paired_available=len(ids),
            c32_correct=sum(b[i]==gold[i] for i in ids),seed1_correct=sum(a[i]==gold[i] for i in ids),
            seed2_correct=sum(c[i]==gold[i] for i in ids),seed1_wins=len(win1&ids),seed1_losses=len(loss1&ids),
            seed2_wins=len(win2&ids),seed2_losses=len(loss2&ids),shared_wins=len(win1&win2&ids))
    group_rows=[]
    for row in groups:
        ids=row["requested_ids"]
        complete=all(i in common for i in ids)
        value=dict(call_id=row["coordinate_id"],ids=ids,complete=complete)
        if complete:
            scores=[sum(pred[i]==gold[i] for i in ids) for pred in (b,a,c)]
            value.update(c32_correct=scores[0],seed1_correct=scores[1],seed2_correct=scores[2],
                         seed2_net_vs_c32=scores[2]-scores[0],seed2_changed_vs_c32=sum(b[i]!=c[i] for i in ids))
        group_rows.append(value)
    complete_primary=bool(second.get("available") and second.get("complete_primary_comparison")
        and all(x["complete"] for x in (baseline,seed1,seed2)))
    net=second.get("net_correct_change") if complete_primary else None
    interval=second.get("descriptive_cluster_bootstrap_95_interval") if complete_primary else None
    if not complete_primary:
        decision="No replication conclusion: qualification/completeness/runtime comparison unavailable."
    elif net<=0:
        decision="The positive gain did not repeat on this training seed; retain both results without choosing the better seed."
    elif interval[0]<=0:
        decision="A positive point estimate repeats, but its descriptive uncertainty includes zero; evidence remains inconclusive."
    else:
        decision="The positive gain repeats on this same panel under a fresh training seed; this strengthens seed-robustness evidence, not new-data confirmation."
    overlap={name:sorted(value) for name,value in dict(seed1_wins=win1,seed2_wins=win2,
        shared_wins=win1&win2,seed1_only_wins=win1-win2,seed2_only_wins=win2-win1,
        seed1_losses=loss1,seed2_losses=loss2,shared_losses=loss1&loss2).items()}
    return dict(primary_complete=complete_primary,planned_records=512,paired_available=len(common),
        paired_unavailable=512-len(common),classes=classes,groups=group_rows,
        overlap={k:dict(count=len(v),ids=v) for k,v in overlap.items()},
        comparisons=dict(seed1_vs_c32=first,seed2_vs_c32=second,seed2_vs_seed1=between),
        wrong_to_different_wrong_seed2=sum(b[i]!=c[i] and b[i]!=gold[i] and c[i]!=gold[i] for i in common),
        group_summary=dict(planned=128,complete=sum(x["complete"] for x in group_rows),
            positive=sum(x.get("seed2_net_vs_c32",0)>0 for x in group_rows),
            negative=sum(x.get("seed2_net_vs_c32",0)<0 for x in group_rows),
            unchanged_net=sum(x["complete"] and x["seed2_net_vs_c32"]==0 for x in group_rows)),
        decision=decision,decision_rule="direction and reported descriptive cluster uncertainty; no required match to seed1 magnitude, no best-seed selection")


def execute():
    terminal=read(WATCH/"outcomes/WATCHER_TERMINAL.json")
    raw_path=WATCH/"outcomes/RAW_AUDIT.json"
    if terminal.get("status")!="REPLICA_EVAL_TERMINAL_RAW_AUDITED" or terminal.get("report_sha256")!=sha(raw_path):
        raise ValueError("completed authenticated raw audit required")
    if sha(ORIGINAL)!="57606da1e52a5b694cad6d39dbff9febf5c66a7f6783ce3cf99e440e961f7bbb":
        raise ValueError("original seed1 raw audit changed")
    original,current=read(ORIGINAL),read(raw_path)
    data=SIDE/"helper-agnews-broader-data-v1/inputs"
    result=derive(original,current,read(data/"HELDOUT_GOLD.json")["labels"],read(data/"HELDOUT_REQUESTS.json"))
    training_cost={}
    for seed,side,watch in (("seed1","helper-agnews-native-hf-eightstep-v1",ROOT.parent/"helper-agnews-eightstep-live-audit-2026-09-12"),
        ("seed2","helper-agnews-native-hf-eightstep-seed2-v1",WATCH)):
        output=SIDE/side/"outputs/attempt-001"
        final=read(output/"FINAL_RESULT.json")
        reports=[read(watch/f"training/STEP-{step:03d}.json") for step in range(1,9)]
        if final["status"]!="UPDATED_STEP8" or not all(x["actual_endpoint_inner_step_probe"]["passed"] for x in reports):
            raise ValueError("full eight-step independent training audit required")
        for step,report in enumerate(reports,1):
            if (report["state_sha256"]!=sha(output/f"step-{step:03d}/checkpoint-{step:04d}/state.json")
                or report["collection_sha256"]!=sha(output/f"step-{step:03d}/COLLECTION.json")):
                raise ValueError("training diagnostic state/collection provenance differs")
        training_cost[seed]=dict(owner_seconds=final["elapsed_seconds"],hf_seconds=sum(x["hf_seconds"] for x in reports),
            native_call_span_seconds=sum(x["native_call_span_seconds"] for x in reports),native_calls=1024,
            unique_records=1024,native_usage={k:sum(x["native_usage_observed"][k] for x in reports) for k in reports[0]["native_usage_observed"]},
            mixed_groups_by_step=[x["mixed_groups"] for x in reports],ess_by_step=[x["ess"] for x in reports],
            final_result_sha256=sha(output/"FINAL_RESULT.json"),steps=reports)
    eval_cost={}
    for arm in ("c32","rl_step8",ARM):
        source="helper-agnews-eightstep-seed2-eval-v1" if arm==ARM else "helper-agnews-fresh512-eval-v1"
        output=SIDE/source/"outputs"/(arm+"-001")
        endpoint=read(output/"OWNER_TERMINAL.json")
        eval_cost[arm]=dict(**current["arms"][arm]["cost"],owner_seconds=endpoint["elapsed_seconds"],
                           physical_calls=128,new_calls_in_replication=128 if arm==ARM else 0)
    result.update(schema="fixed512-seed-replication-additive-findings-v1",
        source_audits={str(ORIGINAL):sha(ORIGINAL),str(raw_path):sha(raw_path)},
        source_raw_watcher_terminal_sha256=sha(WATCH/"outcomes/WATCHER_TERMINAL.json"),
        primary_scorer_unchanged=True,new_model_queries=0,training_cost=training_cost,evaluation_cost=eval_cost,
        arm_metrics={k:v["metrics"] for k,v in current["arms"].items()},
        arm_inventory={k:v["inventory"] for k,v in current["arms"].items()},
        source_to_raw_audit_not_independent_trainer_implementation=True,
        boundary="same exposed512 and same1024 training data; only seeds differ; 128sharedB4 clusters; no pooling as1024 independent test items")
    write_x(ROOT/"FINDINGS.json",json.dumps(result,indent=2,sort_keys=True)+"\n")
    write_x(ROOT/"FINDINGS.md",markdown(result))
    return result


def write_x(path,text):
    path.parent.mkdir(parents=True,exist_ok=True)
    with path.open("x") as stream:stream.write(text)


def markdown(r):
    lines=["# Fixed512 training-seed replication","",r["decision"],"",
        "The predeclared finalstep8 is used in both runs; no better-seed or checkpoint selection.","",
        "| Arm | Correct /512 | Available | Unavailable |","|---|---:|---:|---:|"]
    for arm,m in r["arm_metrics"].items():lines.append(f"| {arm} | {m['correct']}/512 | {m['available_predictions']} | {m['unavailable_predictions']} |")
    lines += ["","| Paired contrast | Gains / losses | Net | Changed labels | Descriptive95% interval |",
              "|---|---:|---:|---:|---|"]
    for key,p in r["comparisons"].items():
        if p.get("available"):
            ci=p.get("descriptive_cluster_bootstrap_95_interval")
            interval=f"{100*ci[0]:+.2f} to {100*ci[1]:+.2f} pp" if ci else "unavailable"
            lines.append(f"| {key} | {p['wins']} / {p['losses']} | {p['net_correct_change']:+d} | {p['category_disagreements']} | {interval} |")
        else:lines.append(f"| {key} | unavailable | — | — | {p['reason']} |")
    o=r["overlap"]
    lines += ["",f"The two seeds share **{o['shared_wins']['count']} corrections** versus c32; "
        f"{o['seed1_only_wins']['count']} occur only in seed1 and {o['seed2_only_wins']['count']} only in seed2. "
        f"They share {o['shared_losses']['count']} regressions. Seed2 has {r['wrong_to_different_wrong_seed2']} "
        "wrong→different-wrong changes. Exact IDs and all128 group diagnostics are in FINDINGS.json.","",
        "| Host class | c32 | Seed1 | Seed2 | Seed2 gains / losses |","|---|---:|---:|---:|---:|"]
    for label,x in r["classes"].items():lines.append(f"| {label} | {x['c32_correct']}/128 | {x['seed1_correct']}/128 | {x['seed2_correct']}/128 | {x['seed2_wins']} / {x['seed2_losses']} |")
    g=r["group_summary"]
    lines += ["",f"Seed2's shared B4 groups: {g['positive']} positive, {g['negative']} negative, "
              f"{g['unchanged_net']} zero net; {128-g['complete']} incomplete.","",
        "| Cost | Seed1 | Seed2 |","|---|---:|---:|"]
    a,b=r["training_cost"]["seed1"],r["training_cost"]["seed2"]
    for label,key in (("Training owner s","owner_seconds"),("HF stage s (nested)","hf_seconds")):
        lines.append(f"| {label} | {a[key]:.2f} | {b[key]:.2f} |")
    for key in ("prompt_tokens","completion_tokens","cached_prompt_tokens"):
        lines.append(f"| Native training {key} | {a['native_usage'][key]} | {b['native_usage'][key]} |")
    new=r["evaluation_cost"][ARM]
    lines += ["",f"Each trainer uses1024 native maps on the SAME1024 training articles. Seed2 endpoint "
        f"adds128 physical calls, owner {new['owner_seconds']:.2f}s, "
        f"{new['prompt_tokens_observed_subtotal']} prompt and {new['completion_tokens_observed_subtotal']} "
        "completion tokens. Both saved references are reused, not re-queried or charged as new calls. "
        "Full per-phase costs and unknown-usage counts are in JSON; nested phases are not added to owner time.","",
        f"Mixed groups across the eight distinct blocks were seed1 {a['mixed_groups_by_step']} and "
        f"seed2 {b['mixed_groups_by_step']}. All eight source/raw/mask/importance/replay/Adam audits passed. "
        "Distinct-block reward scores are not a learning curve.","",
        "Limits: same now-research-exposed512, one additional training seed, and128shared request clusters—not "
        "1024 independent test articles. Intervals are descriptive cluster bootstraps, not independent-item p-values. "
        "This is a source-to-raw audit, not an independently implemented trainer. No broad helper, recursion or planner claim follows.","",
        "Next decision: retain both seeds; assess the fixed repeated-first128 arm only if separately admitted, "
        "with retention/controller priorities unchanged. A partial-dose stop cannot answer the completed8-update mechanism contrast."]
    return "\n".join(lines)+"\n"


if __name__=="__main__":
    parser=argparse.ArgumentParser();parser.add_argument("--wait",action="store_true")
    args=parser.parse_args()
    if os.environ.get("CUDA_VISIBLE_DEVICES")!="":raise ValueError("CPU-only findings")
    if args.wait:
        deadline=time.monotonic()+14400
        while not (WATCH/"outcomes/WATCHER_TERMINAL.json").exists():
            if time.monotonic()>=deadline:raise TimeoutError("bounded4h findings wait expired")
            time.sleep(30)
    result=execute()
    print(json.dumps(dict(decision=result["decision"],FINDINGS_sha256=sha(ROOT/"FINDINGS.json")),sort_keys=True))
