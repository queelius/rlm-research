"""Secondary diagnostics from the sealed scorer's complete raw audit; no model calls."""
import hashlib
import json
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parent
STORE = ROOT.parent.parent
SIDE = STORE / "sidecars"
AUDIT = STORE / "analyses/helper-agnews-eightstep-live-audit-2026-09-12/outcomes/RAW_AUDIT-003.json"
read = lambda p: json.loads(Path(p).read_text())
sha = lambda p: hashlib.sha256(Path(p).read_bytes()).hexdigest()


def derive():
    audit = read(AUDIT)
    assert sha(AUDIT) == "57606da1e52a5b694cad6d39dbff9febf5c66a7f6783ce3cf99e440e961f7bbb"
    data = SIDE / "helper-agnews-broader-data-v1"
    gold = read(data / "inputs/HELDOUT_GOLD.json")["labels"]
    schedule = read(data / "inputs/HELDOUT_REQUESTS.json")
    assert len(gold) == 512 and len(schedule) == 128
    comparisons = {}
    for key, pair in audit["comparisons"].items():
        left, right = key.split("_vs_")
        before, after = (audit["arms"][a]["predictions"] for a in (left, right))
        assert pair["complete_primary_comparison"] and set(before) == set(after) == set(gold)
        classes = {}
        transitions = Counter()
        for label in sorted(set(gold.values())):
            ids = [i for i in gold if gold[i] == label]
            win = [i for i in ids if before[i] != gold[i] == after[i]]
            loss = [i for i in ids if before[i] == gold[i] != after[i]]
            wrong_churn = [i for i in ids if before[i] != after[i] and before[i] != gold[i] and after[i] != gold[i]]
            classes[label] = dict(planned=128, available=128, wins=len(win), losses=len(loss),
                                  net=len(win)-len(loss), wrong_to_different_wrong=len(wrong_churn),
                                  win_ids=win, loss_ids=loss, wrong_churn_ids=wrong_churn)
            for i in ids:
                if before[i] != after[i]:
                    transitions[(label, before[i], after[i])] += 1
        groups, matrix = [], [[0]*5 for _ in range(5)]
        for row in schedule:
            ids = row["requested_ids"]
            a, b = (sum(pred[i] == gold[i] for i in ids) for pred in (before, after))
            churn = sum(before[i] != after[i] for i in ids)
            matrix[a][b] += 1
            groups.append(dict(call_id=row["coordinate_id"], ids=ids, before_correct=a,
                               after_correct=b, net=b-a, changed_labels=churn))
        assert sum(x["wins"] for x in classes.values()) == pair["wins"]
        assert sum(x["losses"] for x in classes.values()) == pair["losses"]
        assert sum(x["changed_labels"] for x in groups) == pair["category_disagreements"]
        comparisons[key] = dict(primary=pair, by_class=classes, groups=groups,
            group_summary=dict(positive=sum(x["net"]>0 for x in groups),
                negative=sum(x["net"]<0 for x in groups), zero=sum(x["net"]==0 for x in groups),
                changed=sum(x["changed_labels"]>0 for x in groups),
                neutral_churn=sum(x["changed_labels"]>0 and x["net"]==0 for x in groups),
                incomplete=0), before_after_correct_5x5=matrix,
            changed_category_transitions=[dict(gold=a,before=b,after=c,count=n)
                                          for (a,b,c),n in sorted(transitions.items())])
    steps = [read(STORE / f"analyses/helper-agnews-eightstep-live-audit-2026-09-12/training/STEP-{s:03d}.json") for s in range(1,9)]
    rl = SIDE / "helper-agnews-native-hf-eightstep-v1/outputs/attempt-001"
    sft = SIDE / "helper-agnews-sft-eightstep-v1/outputs/attempt-001"
    training = dict(
        rl_full_owner_seconds=read(rl/"FINAL_RESULT.json")["elapsed_seconds"],
        rl_step_owner_seconds_sum=sum(s["owner_seconds"] for s in steps),
        rl_hf_seconds_sum=sum(s["hf_seconds"] for s in steps),
        rl_native_call_span_seconds_sum=sum(s["native_call_span_seconds"] for s in steps),
        rl_native_calls=1024, rl_label_decisions=4096, rl_unique_training_records=1024,
        rl_native_usage={k:sum(s["native_usage_observed"][k] for s in steps) for k in steps[0]["native_usage_observed"]},
        sft_training_seconds=read(sft/"RESULT.json")["elapsed_seconds"],
        sft_owner_seconds=read(sft/"OWNER_TERMINAL.json")["elapsed_seconds"],
        sft_teacher_maps=256,sft_unique_records=1024,sft_supervised_tokens=20591,
        phases_nested_not_additive=True, queue_wait_included=False,
        comparison="same1024data and8updates; not compute/action-exposure matched")
    eval_cost = {}
    for arm, value in audit["arms"].items():
        output = SIDE / f"helper-agnews-fresh512-eval-v1/outputs/{arm}-001"
        eval_cost[arm] = dict(**value["cost"], physical_calls=128, available_records=512,
                             owner_seconds=read(output/"OWNER_TERMINAL.json")["elapsed_seconds"])
    return dict(schema="fresh512-additive-interpretation-v1", source_audit=str(AUDIT),
        source_audit_sha256=sha(AUDIT), primary_scorer_sha256=sha(SIDE/"helper-agnews-fresh512-eval-v1/compare.py"),
        arm_metrics={a:dict(metrics=x["metrics"],per_class=x["per_class"],inventory=x["inventory"]) for a,x in audit["arms"].items()},
        comparisons=comparisons, evaluation_cost=eval_cost, training_cost=training,
        training_steps=steps, decision="candidate for same-data training-seed replication; not confirmed gain",
        boundary="complete512 available each; source-to-raw audit, not independent trainer replication; distinct-step reward scores not a learning curve")


if __name__ == "__main__":
    result = derive()
    with (ROOT / "FINDINGS.json").open("x") as stream:
        json.dump(result,stream,indent=2,sort_keys=True); stream.write("\n")
    print(json.dumps({k:result[k] for k in ("evaluation_cost","training_cost")},indent=2))
    print(json.dumps({k:v["group_summary"] for k,v in result["comparisons"].items()},indent=2))
