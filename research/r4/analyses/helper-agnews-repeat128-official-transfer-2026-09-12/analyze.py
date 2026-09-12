"""Independent source-to-raw fifth-arm audit on the frozen official-test panel."""

import hashlib
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
STORE = HERE.parents[1]
EVAL = STORE / "sidecars/helper-agnews-repeat128-official-test-eval-v1"
REFERENCE = STORE / "analyses/helper-agnews-official-test-fresh512-independent-2026-09-12/RESULT.json"
REFERENCE_SHA = "b39f2dc263615812c2831a7f6d6328dde91253fbd4ab5bd3ff257b53f2d0643a"
ARM = "rl_repeat128_step8"
REFERENCES = ("c32", "rl_step8", "sft_step8", "rl_seed2_step8")


def read(path):
    return json.loads(Path(path).read_text())


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def write_x(path, value):
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    with Path(path).open("x") as stream:
        json.dump(value, stream, indent=2, sort_keys=True)
        stream.write("\n")


def paired_counts(before, after, gold):
    shared = set(before) & set(after) & set(gold)
    wins = sum(before[key] != gold[key] and after[key] == gold[key] for key in shared)
    losses = sum(before[key] == gold[key] and after[key] != gold[key] for key in shared)
    return {
        "planned": len(gold),
        "paired_available": len(shared),
        "unavailable_either": len(gold) - len(shared),
        "wins": wins,
        "losses": losses,
        "ties": len(shared) - wins - losses,
        "changed_predictions": sum(before[key] != after[key] for key in shared),
        "net_correct_change": wins - losses,
    }


def load_bundle():
    sys.path.insert(0, str(EVAL))
    sys.modules.pop("bundle", None)
    import bundle

    return bundle


def execute():
    if sha(REFERENCE) != REFERENCE_SHA:
        raise ValueError("qualified saved four-arm audit changed")
    reference = read(REFERENCE)
    if set(reference.get("arms", {})) != set(REFERENCES):
        raise ValueError("saved four-arm inventory differs")
    for arm in REFERENCES:
        value = reference["arms"][arm]
        if not value.get("complete") or value["metrics"].get("available_predictions") != 512:
            raise ValueError("saved reference arm is incomplete: " + arm)

    b = load_bundle()
    from transformers import AutoTokenizer

    tokenizer = AutoTokenizer.from_pretrained(b.study.MODEL, local_files_only=True)
    repeated, runtime, provenance = b.repeat.compare.audited_arm(ARM, tokenizer)
    if not repeated.get("complete") or repeated["metrics"].get("available_predictions") != 512:
        raise ValueError("repeat128 official-test arm is incomplete")
    gold = b.study.gold()["labels"]
    if set(repeated["predictions"]) != set(gold):
        raise ValueError("repeat prediction inventory differs from official gold")
    comparisons = {
        name + "_vs_" + ARM: paired_counts(
            reference["arms"][name]["predictions"], repeated["predictions"], gold
        )
        for name in REFERENCES
    }
    terminal = read(b.study.attempt(ARM) / "OWNER_TERMINAL.json")
    result = {
        "schema": "agnews-repeat128-official-test-transfer-audit-v1",
        "status": "COMPLETE",
        "panel": "already frozen official-test512",
        "checkpoint_selection": "none; fixed completed repeat128 step8",
        "repeat128": repeated,
        "saved_reference_arms": {
            arm: {
                "metrics": reference["arms"][arm]["metrics"],
                "per_class": reference["arms"][arm]["per_class"],
            }
            for arm in REFERENCES
        },
        "comparisons": comparisons,
        "runtime": runtime,
        "cost": {
            "physical_calls": repeated["inventory"]["attempted_calls"],
            "usage": repeated["cost"],
            "owner_seconds": terminal["elapsed_seconds"],
            "reference_calls_reused_not_regenerated": 128 * len(REFERENCES),
        },
        "provenance": {
            "repeat_raw": provenance,
            "reference_audit": str(REFERENCE),
            "reference_audit_sha256": REFERENCE_SHA,
            "ready_sha256": sha(EVAL / "READY_RL_REPEAT128_STEP8.json"),
        },
        "limits": [
            "Same AG News task; not domain transfer or absence from base pretraining.",
            "The repeated checkpoint was already scored on the research-exposed panel.",
            "This fixed official-panel readout adds no checkpoint selection but is one training run.",
            "Accuracy pairs share four-record request clusters; item-level independence is not assumed.",
        ],
    }
    return result


def markdown(value):
    rows = [
        "# Repeat128 checkpoint on the frozen official-test panel",
        "",
        "All five endpoints are fixed; the four saved reference arms were not regenerated.",
        "",
        "| Arm | Correct / 512 | Available |",
        "|---|---:|---:|",
    ]
    for arm, source in value["saved_reference_arms"].items():
        metric = source["metrics"]
        rows.append(f"| `{arm}` | {metric['correct']} | {metric['available_predictions']} |")
    metric = value["repeat128"]["metrics"]
    rows.append(f"| `{ARM}` | {metric['correct']} | {metric['available_predictions']} |")
    rows += ["", "| Comparison (reference → repeat128) | Wins | Losses | Net | Changed |", "|---|---:|---:|---:|---:|"]
    for name, pair in value["comparisons"].items():
        rows.append(
            f"| `{name}` | {pair['wins']} | {pair['losses']} | "
            f"{pair['net_correct_change']:+d} | {pair['changed_predictions']} |"
        )
    rows += [
        "",
        "Interpretation is bounded: persistence of the broader-versus-repeat contrast supports a "
        "breadth hypothesis, while disappearance revises it toward panel-specific boundary shifts. "
        "Neither outcome identifies breadth causally from one run.",
        "",
        "## Limits",
        "",
        *["- " + item for item in value["limits"]],
    ]
    return "\n".join(rows) + "\n"


if __name__ == "__main__":
    result = execute()
    write_x(HERE / "RESULT.json", result)
    with (HERE / "REPORT.md").open("x") as stream:
        stream.write(markdown(result))
    print(json.dumps({"status": result["status"], "result_sha256": sha(HERE / "RESULT.json")}, sort_keys=True))

