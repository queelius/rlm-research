"""Synthesize the completed official-test four-arm source-to-raw audit."""

from __future__ import annotations

from collections import Counter
import hashlib
import json
from pathlib import Path


HERE = Path(__file__).resolve().parent
STORE = HERE.parents[1]
AUDIT_DIR = STORE / "analyses/helper-agnews-official-test-fresh512-independent-2026-09-12"
AUDIT = AUDIT_DIR / "RESULT.json"
AUDIT_TERMINAL = AUDIT_DIR / "WATCH_TERMINAL.json"
DATA = STORE / "sidecars/helper-agnews-official-test-fresh512-v1/inputs"
EVAL = STORE / "sidecars/helper-agnews-official-test-fresh512-eval-v1"
PRIOR = STORE / "analyses/helper-agnews-fresh512-interpretation-2026-09-12/FINDINGS.json"
PRIOR_SEEDS = STORE / "analyses/helper-agnews-seed-replication-findings-2026-09-12/FINDINGS.json"
SEED2_TRAIN = (
    STORE / "sidecars/helper-agnews-native-hf-eightstep-seed2-v1/outputs/attempt-001/FINAL_RESULT.json"
)
ARMS = ("c32", "rl_step8", "sft_step8", "rl_seed2_step8")
LABELS = ("World", "Sports", "Business", "Sci/Tech")


def read(path: Path | str):
    return json.loads(Path(path).read_text())


def sha(path: Path | str) -> str:
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def class_effect(before: dict, after: dict, gold: dict) -> dict:
    if set(before) != set(after) or not set(before) <= set(gold):
        raise ValueError("paired prediction inventories differ")
    result = {}
    for label in sorted(set(gold.values())):
        ids = [key for key in before if gold[key] == label]
        wins = sum(before[key] != label and after[key] == label for key in ids)
        losses = sum(before[key] == label and after[key] != label for key in ids)
        churn = sum(
            before[key] != after[key] and before[key] != label and after[key] != label
            for key in ids
        )
        transitions = Counter(
            (before[key], after[key]) for key in ids if before[key] != after[key]
        )
        result[label] = {
            "planned": sum(value == label for value in gold.values()),
            "paired": len(ids),
            "wins": wins,
            "losses": losses,
            "net": wins - losses,
            "wrong_to_different_wrong": churn,
            "changed": sum(count for count in transitions.values()),
            "transitions": [
                {"before": left, "after": right, "count": count}
                for (left, right), count in sorted(transitions.items())
            ],
        }
    return result


def seed_agreement(first: dict, second: dict, gold: dict) -> dict:
    available = set(first) & set(second) & set(gold)
    return {
        "paired_available": len(available),
        "same_prediction": sum(first[key] == second[key] for key in available),
        "different_prediction": sum(first[key] != second[key] for key in available),
        "both_correct": sum(first[key] == second[key] == gold[key] for key in available),
        "first_only_correct": sum(
            first[key] == gold[key] and second[key] != gold[key] for key in available
        ),
        "second_only_correct": sum(
            second[key] == gold[key] and first[key] != gold[key] for key in available
        ),
        "both_wrong": sum(
            first[key] != gold[key] and second[key] != gold[key] for key in available
        ),
    }


def group_summary(before: dict, after: dict, gold: dict, schedule: list[dict]) -> dict:
    groups = []
    for row in schedule:
        ids = row["ids"]
        request_id = row["request_id"]
        if not all(key in before and key in after for key in ids):
            groups.append({"call_id": request_id, "available": False})
            continue
        left = sum(before[key] == gold[key] for key in ids)
        right = sum(after[key] == gold[key] for key in ids)
        groups.append(
            {
                "call_id": request_id, "available": True,
                "before_correct": left, "after_correct": right, "net": right - left,
                "changed": sum(before[key] != after[key] for key in ids),
            }
        )
    return {
        "planned": len(schedule),
        "available": sum(row["available"] for row in groups),
        "positive": sum(row.get("net", 0) > 0 for row in groups),
        "negative": sum(row.get("net", 0) < 0 for row in groups),
        "zero": sum(row.get("net") == 0 for row in groups if row["available"]),
        "changed": sum(row.get("changed", 0) > 0 for row in groups),
        "groups": groups,
    }


def validate_audit(audit: dict, terminal: dict) -> None:
    if terminal.get("status") != "COMPLETE":
        raise ValueError("independent source-to-raw audit is not complete")
    if set(audit.get("arms", {})) != set(ARMS) or len(audit.get("comparisons", {})) != 6:
        raise ValueError("exact four-arm/six-comparison audit required")
    for arm in ARMS:
        value = audit["arms"][arm]
        inventory = value["inventory"]
        if (
            value.get("complete") is not True
            or inventory.get("expected_calls") != 128
            or inventory.get("expected_ids") != 512
            or inventory.get("valid_calls") != 128
            or value["metrics"].get("available_predictions") != 512
            or value["metrics"].get("unavailable_predictions") != 0
        ):
            raise ValueError("official-test arm is incomplete: " + arm)
    if any(value.get("available") is not True for value in audit["comparisons"].values()):
        raise ValueError("one of six fixed comparisons is unavailable")


def derive() -> dict:
    audit, terminal = read(AUDIT), read(AUDIT_TERMINAL)
    validate_audit(audit, terminal)
    gold = read(DATA / "HOST_GOLD.json")["labels"]
    schedule = read(DATA / "REQUESTS.json")
    prior, prior_seeds = read(PRIOR), read(PRIOR_SEEDS)
    if len(gold) != 512 or len(schedule) != 128:
        raise ValueError("official-test fixed512 inventory changed")
    arm_metrics, evaluation_cost = {}, {}
    for arm in ARMS:
        value = audit["arms"][arm]
        owner_path = EVAL / "outputs" / f"{arm}-001/OWNER_TERMINAL.json"
        owner = read(owner_path)
        arm_metrics[arm] = {
            "metrics": value["metrics"], "per_class": value["per_class"],
            "inventory": value["inventory"],
        }
        evaluation_cost[arm] = {
            **value["cost"],
            "physical_calls": value["inventory"]["attempted_calls"],
            "owner_seconds": owner["elapsed_seconds"],
            "owner_complete": owner["complete"],
            "runtime_qualified": owner["runtime_qualified"],
        }
    comparisons = {}
    for key, primary in audit["comparisons"].items():
        left, right = key.split("_vs_")
        before, after = audit["arms"][left]["predictions"], audit["arms"][right]["predictions"]
        classes = class_effect(before, after, gold)
        groups = group_summary(before, after, gold, schedule)
        if (
            sum(row["wins"] for row in classes.values()) != primary["wins"]
            or sum(row["losses"] for row in classes.values()) != primary["losses"]
            or sum(row["changed"] for row in classes.values()) != primary["category_disagreements"]
            or groups["available"] != primary["clusters"]
        ):
            raise ValueError("independent class/group derivation differs: " + key)
        comparisons[key] = {"primary": primary, "by_gold_class": classes, "groups": groups}
    prior_totals = {
        "c32": prior["arm_metrics"]["c32"]["metrics"]["correct"],
        "rl_step8": prior["arm_metrics"]["rl_step8"]["metrics"]["correct"],
        "sft_step8": prior["arm_metrics"]["sft_step8"]["metrics"]["correct"],
        "rl_seed2_step8": prior_seeds["arm_metrics"]["rl_seed2_step8"]["correct"],
    }
    seed2_training = read(SEED2_TRAIN)
    result = {
        "schema": "helper-agnews-official-test-transfer-findings-v1",
        "status": "complete_exploratory_within_dataset_transfer_readout",
        "source_audit": str(AUDIT),
        "source_audit_sha256": sha(AUDIT),
        "source_audit_terminal_sha256": sha(AUDIT_TERMINAL),
        "all_fixed_endpoints_reported": list(ARMS),
        "no_best_seed_or_checkpoint_selection": True,
        "official_test": {
            "arm_metrics": arm_metrics,
            "comparisons": comparisons,
            "rl_seed_agreement": seed_agreement(
                audit["arms"]["rl_step8"]["predictions"],
                audit["arms"]["rl_seed2_step8"]["predictions"], gold,
            ),
            "evaluation_cost": evaluation_cost,
        },
        "prior_research_exposed_panel": {
            "correct_of_512": prior_totals,
            "source": str(PRIOR), "source_sha256": sha(PRIOR),
            "seed2_source": str(PRIOR_SEEDS), "seed2_source_sha256": sha(PRIOR_SEEDS),
            "comparison_role": "context only; not pooled and panel difference is not causal",
        },
        "training_cost_context": {
            "rl_seed1": {
                "owner_seconds": prior["training_cost"]["rl_full_owner_seconds"],
                "native_calls": prior["training_cost"]["rl_native_calls"],
                "native_usage": prior["training_cost"]["rl_native_usage"],
            },
            "rl_seed2": {
                "owner_seconds": seed2_training["elapsed_seconds"],
                "native_calls": prior_seeds["training_cost"]["seed2"]["native_calls"],
                "native_usage": prior_seeds["training_cost"]["seed2"]["native_usage"],
            },
            "sft": {
                "owner_seconds": prior["training_cost"]["sft_owner_seconds"],
                "training_seconds": prior["training_cost"]["sft_training_seconds"],
                "supervised_tokens": prior["training_cost"]["sft_supervised_tokens"],
            },
            "not_compute_or_action_exposure_matched": True,
        },
        "qualitative_review": {
            "scope": "changed official-test records privately reviewed; no article text reproduced",
            "observed_pattern": (
                "both RL seeds add ten correct Sci/Tech classifications relative to c32, while "
                "also losing two Business and two-to-four World classifications; SFT changes only "
                "five labels and gains four correct answers with no correct-to-wrong flips"
            ),
            "interpretation": (
                "label changes are compatible with modest category-boundary preference shifts; "
                "they do not identify a mechanism or a broad capability change"
            ),
        },
        "decision": (
            "The official-test signal is materially weaker than the earlier exposed-panel signal. "
            "The two RL seeds are coherent relative to c32 but exceed SFT by only one and three "
            "answers, with both descriptive RL-vs-SFT intervals spanning zero. Require a "
            "prospectively frozen replication to beat matched SFT without trading away World or "
            "Business accuracy before interpreting this as an RL-specific transfer benefit."
        ),
        "limits": [
            "Official-test examples are new local examples from AG News, not a new task or domain.",
            "Absence from base-model pretraining is unknown.",
            "The descriptive bootstrap unit is the shared four-record request, not 512 independent items.",
            "Different results on exposed and official-test panels do not identify distribution-shift cause.",
            "One favorable answer among fixed arms is not evidence that RL meaningfully beats SFT.",
        ],
    }
    return result


def pct(value: float | None) -> str:
    return "NA" if value is None else f"{100 * value:.2f}%"


def report(result: dict) -> str:
    official = result["official_test"]
    lines = [
        "---", "title: Official-test AG News transfer findings", "date: 2026-09-12",
        "status: completed_exploratory_transfer_readout", "---", "",
        "# Official-test transfer: weaker, without a clear RL-SFT separation", "",
        "The independent source-to-raw audit retained all four predeclared endpoints; no training "
        "seed or checkpoint was selected using these outcomes. All arms have 512/512 available "
        "predictions from 128/128 valid four-record calls.", "", "## Fixed endpoints", "",
        "| Arm | Correct / 512 | Accuracy | World | Sports | Business | Sci/Tech | Owner s |",
        "|---|---:|---:|---:|---:|---:|---:|---:|",
    ]
    for arm in ARMS:
        value = official["arm_metrics"][arm]
        metrics, classes = value["metrics"], value["per_class"]
        lines.append(
            f"| `{arm}` | {metrics['correct']} | {pct(metrics['primary_accuracy'])} | "
            + " | ".join(str(classes[label]["correct"]) for label in LABELS)
            + f" | {official['evaluation_cost'][arm]['owner_seconds']:.2f} |"
        )
    lines += ["", "## Paired comparisons", "",
              "| Comparison | Wins / losses | Net | Changed labels | Cluster-bootstrap 95% interval |",
              "|---|---:|---:|---:|---:|"]
    for key, value in official["comparisons"].items():
        p = value["primary"]
        interval = p["descriptive_cluster_bootstrap_95_interval"]
        lines.append(
            f"| `{key}` | {p['wins']} / {p['losses']} | {p['net_correct_change']:+d} | "
            f"{p['category_disagreements']} | {pct(interval[0])} to {pct(interval[1])} |"
        )
    seeds = official["rl_seed_agreement"]
    prior = result["prior_research_exposed_panel"]["correct_of_512"]
    lines += [
        "", "The two fixed RL seeds make the same prediction on "
        f"{seeds['same_prediction']}/512 records and differ on {seeds['different_prediction']}; "
        f"{seeds['first_only_correct']} favor seed 1 and {seeds['second_only_correct']} favor seed 2. "
        "This is seed variation, not a model-selection opportunity.", "",
        "On the earlier research-exposed panel, the corresponding c32 / RL-seed1 / SFT / "
        f"RL-seed2 totals were {prior['c32']} / {prior['rl_step8']} / {prior['sft_step8']} / "
        f"{prior['rl_seed2_step8']}. The panels are not pooled, and their difference does not by "
        "itself reveal a distribution-shift mechanism.", "", "## Cost and interpretation", "",
    ]
    for arm in ARMS:
        cost = official["evaluation_cost"][arm]
        lines.append(
            f"- `{arm}` evaluation: {cost['physical_calls']} physical calls; "
            f"{cost['prompt_tokens_observed_subtotal']} prompt tokens "
            f"({cost['cached_prompt_tokens_observed_subtotal']} cached), "
            f"{cost['completion_tokens_observed_subtotal']} completion tokens; "
            f"{cost['unknown_usage_calls']} unknown-usage ledger; {cost['owner_seconds']:.2f}s owner time."
        )
    lines += [
        "", "Private review of changed records is consistent with modest movement at overlapping "
        "Business/Sci-Tech and World/topic boundaries. Both RL seeds gain ten Sci/Tech answers over "
        "c32, but lose two Business and two-to-four World answers. SFT changes only five labels, "
        "gaining four correct answers without a correct-to-wrong flip. These are category-boundary "
        "movements, not evidence for a new capability, a specific learned rule, or a causal "
        "explanation for the panel difference.", "",
        "The transfer signal is materially weaker than on the exposed panel. Do not claim a "
        "meaningful RL advantage over SFT: although the two RL seeds are coherent relative to c32, "
        "they exceed SFT by only one and three answers, and both descriptive RL-vs-SFT intervals "
        "span zero. A useful next decision is a prospectively frozen replication requiring both RL "
        "seeds to beat matched SFT by a preregistered margin without a compensating World/Business "
        "loss. Otherwise retire the broad RL-superiority interpretation and describe the result as "
        "modest boundary calibration.", "", "## Limits", "",
    ]
    lines.extend("- " + value for value in result["limits"])
    lines.append("")
    return "\n".join(lines)


def main() -> None:
    result = derive()
    with (HERE / "FINDINGS.json").open("x") as stream:
        json.dump(result, stream, indent=2, sort_keys=True)
        stream.write("\n")
    with (HERE / "FINDINGS.md").open("x") as stream:
        stream.write(report(result))
    print(json.dumps({arm: result["official_test"]["arm_metrics"][arm]["metrics"] for arm in ARMS}, sort_keys=True))


if __name__ == "__main__":
    main()
