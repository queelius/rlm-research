"""Static, call-free mechanism audit for the AG whole-RLM transfer experiment.

Generated Python is parsed as inert text.  This module never evaluates or executes it.
"""

from __future__ import annotations

import ast
import hashlib
import json
import re
from collections import Counter, defaultdict
from pathlib import Path


STORE = Path("/project/alex_phd/runs/rlm-research-r4")
SIDE = STORE / "sidecars/root-qs6-ag-live-helper-transfer-v1"
ATTEMPT = SIDE / "outputs/attempt-001"
SOURCE_REPORT = (
    STORE
    / "analyses/root-qs6-ag-live-helper-transfer-independent-2026-09-12/outcome/REPORT.json"
)
QS = STORE / "sidecars/root-question-sensitive-sft-v1"
QSR = STORE / "sidecars/root-question-sensitive-sft-recovery-v1"
OUT = STORE / "analyses/root-qs6-ag-live-helper-transfer-mechanism-2026-09-12"


def read(path: Path):
    return json.loads(path.read_text())


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def write_json(path: Path, value) -> None:
    path.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n")


def _has_call(tree: ast.AST, name: str) -> bool:
    return any(isinstance(node, ast.Call) and isinstance(node.func, ast.Name) and node.func.id == name
               for node in ast.walk(tree))


def _record_subscript(node: ast.AST, key: str) -> bool:
    return (
        isinstance(node, ast.Subscript)
        and isinstance(node.value, ast.Name)
        and node.value.id in {"record", "row"}
        and isinstance(node.slice, ast.Constant)
        and node.slice.value == key
    )


def _literal_user_scope(tree: ast.AST) -> list[str] | None:
    for node in ast.walk(tree):
        if not isinstance(node, ast.Compare) or not _record_subscript(node.left, "user"):
            continue
        if not any(isinstance(op, ast.In) for op in node.ops) or len(node.comparators) != 1:
            continue
        right = node.comparators[0]
        if isinstance(right, (ast.List, ast.Tuple)) and all(
            isinstance(x, ast.Constant) and isinstance(x.value, str) for x in right.elts
        ):
            return [x.value for x in right.elts]
    return None


def inspect_reducer(code: str, operator: str, target: str, records: list[dict], labels: dict) -> dict:
    """Recognize a narrow reducer and recompute it explicitly on trusted host data.

    The AST is only inspected.  No AST node or generated expression is evaluated.
    """
    try:
        tree = ast.parse(code)
    except SyntaxError:
        return {
            "ast_valid": False,
            "has_print": False,
            "supported": False,
            "users": None,
            "host_value_for_generated_scope": None,
            "host_value_for_question_scope": None,
            "scope_matches_question": None,
        }
    constants = {node.value for node in ast.walk(tree) if isinstance(node, ast.Constant)}
    has_print = _has_call(tree, "print")
    recognized = target in constants and (
        (operator == "count" and _has_call(tree, "len"))
        or (operator == "weight_sum" and _has_call(tree, "sum") and "weight" in constants)
    )
    users = _literal_user_scope(tree)
    all_users = sorted({record["user"] for record in records})

    def reduce(scope: set[str] | None) -> int:
        selected = [
            record
            for record in records
            if (scope is None or record["user"] in scope) and labels[record["id"]] == target
        ]
        return len(selected) if operator == "count" else sum(x["weight"] for x in selected)

    return {
        "ast_valid": True,
        "has_print": has_print,
        "supported": recognized,
        "users": users,
        "host_value_for_generated_scope": reduce(set(users)) if recognized and users else (
            reduce(None) if recognized else None
        ),
        "host_value_for_question_scope": reduce(None) if recognized else None,
        "scope_matches_question": (users is None or sorted(users) == all_users) if recognized else None,
    }


def root_python_calls(trace: dict) -> list[dict]:
    """Pair root ipython calls with the immediately returned tool observation."""
    calls = []
    pending = None
    for node_index, node in enumerate(trace["nodes"]):
        message = node["message"]
        if message.get("role") == "assistant":
            for call in message.get("tool_calls") or []:
                if call.get("name") == "ipython":
                    args = json.loads(call["arguments"])
                    pending = {"node": node_index, "code": args["code"], "output": None}
                    calls.append(pending)
        elif message.get("role") == "tool" and message.get("name") == "ipython" and pending:
            pending["output"] = message.get("content")
            pending = None
    return calls


def episode_audit(path: Path, report_row: dict, public: dict) -> dict:
    raw = read(path)
    coordinate = raw["coordinate"]
    if coordinate != report_row["coordinate"]:
        raise ValueError(f"coordinate mismatch: {path}")
    trace = raw["episode"]["traces"][0]
    calls = root_python_calls(trace)
    prediction = report_row["helper"].get("prediction")
    reducer = None
    if prediction and calls:
        reducer = inspect_reducer(
            calls[-1]["code"],
            coordinate["operator"],
            coordinate["target"],
            public[coordinate["context_id"]]["records"],
            prediction,
        )
    output = calls[-1]["output"] if calls else None
    output_kind = (
        "none"
        if output is None
        else "empty"
        if output == ""
        else "error"
        if "Traceback" in output or "Error" in output
        else "nonempty"
    )
    return {
        "arm": coordinate["arm"],
        "coordinate_id": coordinate["id"],
        "context_id": coordinate["context_id"],
        "query_index": coordinate["query_index"],
        "operator": coordinate["operator"],
        "target": coordinate["target"],
        "status": report_row["status"],
        "root_answer": report_row["parsed_answer"],
        "gold_answer": report_row["gold_answer"],
        "map_aggregate": report_row["helper"].get("aggregate"),
        "map_labels_correct": report_row["helper"].get("labels_correct"),
        "python_calls": len(calls),
        "last_tool_output_kind": output_kind,
        "last_code_sha256": hashlib.sha256(calls[-1]["code"].encode()).hexdigest() if calls else None,
        "reducer": reducer,
        "runtime_scalar_observed": bool(reducer and reducer["supported"] and output_kind == "nonempty"),
        "silent_reducer_assignment": bool(
            reducer and reducer["supported"] and not reducer["has_print"] and output_kind == "empty"
        ),
        "root_equals_generated_scope_value": bool(
            reducer
            and reducer["supported"]
            and report_row["parsed_answer"] == reducer["host_value_for_generated_scope"]
        ),
        "root_equals_full_map_aggregate": bool(
            prediction and report_row["parsed_answer"] == report_row["helper"].get("aggregate")
        ),
        "raw_path": str(path),
        "raw_sha256": sha(path),
    }


def training_target_audit() -> dict:
    plan = read(QS / "inputs/TRAIN_PLAN.json")
    counts = Counter()
    files = {}
    for index, coordinate in enumerate(plan):
        attempt = QS / "outputs/attempt-001" if index < 65 else QSR / "outputs/attempt-001"
        path = attempt / "capture" / coordinate["id"] / "EPISODE.json"
        teacher_path = attempt / "capture" / coordinate["id"] / "TEACHER.json"
        episode = read(path)
        teacher = read(teacher_path)
        if teacher["coordinate"] != coordinate:
            raise ValueError(f"training coordinate mismatch: {path}")
        trace = episode["traces"][0]
        calls = root_python_calls(trace)
        if len(calls) != 2:
            raise ValueError(f"expected two authored code actions: {path}")
        for call in calls:
            tree = ast.parse(call["code"])
            counts["python_actions"] += 1
            counts["python_actions_with_print"] += int(_has_call(tree, "print"))
            counts["python_actions_without_print"] += int(not _has_call(tree, "print"))
            counts["child_producer_actions"] += int("await rlm" in call["code"])
            counts["reducer_actions"] += int("await rlm" not in call["code"])
        counts["terminal_targets"] += int(bool(re.fullmatch(r"Answer: \d+", trace["root_reply"])))
        files[str(path)] = sha(path)
    return {
        "examples": len(plan),
        **dict(counts),
        "all_authored_python_actions_print": counts["python_actions"]
        == counts["python_actions_with_print"],
        "files_sha256": files,
        "protocol_source": str(QS / "qs_protocol.py"),
        "protocol_source_sha256": sha(QS / "qs_protocol.py"),
        "checkpoint_binding": str(SIDE / "inputs/BINDING_c32.json"),
        "checkpoint_binding_sha256": sha(SIDE / "inputs/BINDING_c32.json"),
    }


def main() -> None:
    report = read(SOURCE_REPORT)
    public_rows = read(SIDE / "inputs/PUBLIC.json")
    public = {row["id"]: row for row in public_rows}
    gold = read(SIDE / "inputs/HOST_GOLD.json")
    episode_rows = []
    maps_by_arm: dict[str, dict[str, dict]] = {"c32": {}, "rl_step8": {}}
    repeat_checks = defaultdict(list)
    for arm in ("c32", "rl_step8"):
        for row in report["arms"][arm]["episodes"]:
            path = ATTEMPT / arm / "episodes" / f"{row['coordinate']['id']}.json"
            episode_rows.append(episode_audit(path, row, public))
            prediction = row["helper"].get("prediction")
            if prediction:
                repeat_checks[(arm, row["coordinate"]["context_id"])].append(prediction)
        for (check_arm, context_id), values in repeat_checks.items():
            if check_arm == arm:
                if any(value != values[0] for value in values):
                    raise ValueError(f"repeated helper map mismatch: {arm} {context_id}")
                maps_by_arm[arm][context_id] = values[0]

    unique = {}
    for arm, maps in maps_by_arm.items():
        unique[arm] = {
            "contexts": len(maps),
            "unique_record_decisions": sum(len(value) for value in maps.values()),
            "correct_unique_record_decisions": sum(
                prediction[record_id] == gold[context_id]["labels"][record_id]
                for context_id, prediction in maps.items()
                for record_id in prediction
            ),
            "reported_repeated_decisions": sum(
                row["helper"].get("label_decisions", 0) for row in report["arms"][arm]["episodes"]
            ),
            "repeated_maps_identical_within_context": True,
        }

    changes = []
    questions_by_context = defaultdict(list)
    for row in report["arms"]["c32"]["episodes"]:
        questions_by_context[row["coordinate"]["context_id"]].append(row["coordinate"])
    for context_id in sorted(maps_by_arm["c32"]):
        c_map = maps_by_arm["c32"][context_id]
        r_map = maps_by_arm["rl_step8"][context_id]
        for record_id in c_map:
            if c_map[record_id] != r_map[record_id]:
                record = next(x for x in public[context_id]["records"] if x["id"] == record_id)
                affected = []
                for question in questions_by_context[context_id]:
                    c_question_row = next(
                        row
                        for row in report["arms"]["c32"]["episodes"]
                        if row["coordinate"]["context_id"] == context_id
                        and row["coordinate"]["query_index"] == question["query_index"]
                    )
                    r_question_row = next(
                        row
                        for row in report["arms"]["rl_step8"]["episodes"]
                        if row["coordinate"]["context_id"] == context_id
                        and row["coordinate"]["query_index"] == question["query_index"]
                    )
                    scale = 1 if question["operator"] == "count" else record["weight"]
                    c_contribution = scale if c_map[record_id] == question["target"] else 0
                    r_contribution = scale if r_map[record_id] == question["target"] else 0
                    if c_contribution != r_contribution:
                        affected.append(
                            {
                                "operator": question["operator"],
                                "target": question["target"],
                                "c32_contribution": c_contribution,
                                "rl_step8_contribution": r_contribution,
                                "map_observed_in_c32_query": "prediction" in c_question_row["helper"],
                                "map_observed_in_rl_step8_query": "prediction" in r_question_row["helper"],
                            }
                        )
                changes.append(
                    {
                        "context_id": context_id,
                        "record_id": record_id,
                        "gold": gold[context_id]["labels"][record_id],
                        "c32": c_map[record_id],
                        "rl_step8": r_map[record_id],
                        "affected_questions": affected,
                    }
                )

    aggregate_changes = []
    by_arm_coordinate = {
        arm: {row["coordinate"]["pair_id"]: row for row in report["arms"][arm]["episodes"]}
        for arm in ("c32", "rl_step8")
    }
    for pair_id, c_row in sorted(by_arm_coordinate["c32"].items()):
        r_row = by_arm_coordinate["rl_step8"][pair_id]
        ca = c_row["helper"].get("aggregate")
        ra = r_row["helper"].get("aggregate")
        if ca is not None and ra is not None and ca != ra:
            aggregate_changes.append(
                {
                    "pair_id": pair_id,
                    "context_id": c_row["coordinate"]["context_id"],
                    "operator": c_row["coordinate"]["operator"],
                    "target": c_row["coordinate"]["target"],
                    "gold": c_row["gold_answer"],
                    "c32": ca,
                    "rl_step8": ra,
                    "c32_absolute_error": abs(ca - c_row["gold_answer"]),
                    "rl_step8_absolute_error": abs(ra - c_row["gold_answer"]),
                    "root_c32": c_row["parsed_answer"],
                    "root_rl_step8": r_row["parsed_answer"],
                }
            )

    silent = [row for row in episode_rows if row["silent_reducer_assignment"]]
    result = {
        "schema": "root-qs6-ag-live-helper-transfer-mechanism-audit-v1",
        "call_free_static_audit": True,
        "generated_code_executed_by_auditor": False,
        "source": {
            "report": str(SOURCE_REPORT),
            "report_sha256": sha(SOURCE_REPORT),
            "ready": str(SIDE / "READY.json"),
            "ready_sha256": sha(SIDE / "READY.json"),
            "public_sha256": sha(SIDE / "inputs/PUBLIC.json"),
            "host_gold_sha256": sha(SIDE / "inputs/HOST_GOLD.json"),
        },
        "root_endpoint": {
            "c32": Counter(row["outcome"] for row in report["arms"]["c32"]["episodes"]),
            "rl_step8": Counter(row["outcome"] for row in report["arms"]["rl_step8"]["episodes"]),
            "paired": report["paired"]["c32->rl_step8"],
        },
        "helper_decisions": unique,
        "unique_label_changes": changes,
        "unique_label_change_summary": {
            "total": len(changes),
            "wrong_to_correct": sum(x["c32"] != x["gold"] and x["rl_step8"] == x["gold"] for x in changes),
            "correct_to_wrong": sum(x["c32"] == x["gold"] and x["rl_step8"] != x["gold"] for x in changes),
        },
        "aggregate_changes": aggregate_changes,
        "aggregate_change_summary": {
            "changed_queries": len(aggregate_changes),
            "absolute_error_improved": sum(
                row["rl_step8_absolute_error"] < row["c32_absolute_error"]
                for row in aggregate_changes
            ),
            "absolute_error_worsened": sum(
                row["rl_step8_absolute_error"] > row["c32_absolute_error"]
                for row in aggregate_changes
            ),
        },
        "aggregate_exact": {
            arm: {
                "exact": sum(row["helper"].get("aggregate_correct") is True for row in report["arms"][arm]["episodes"]),
                "available_maps": sum("aggregate" in row["helper"] for row in report["arms"][arm]["episodes"]),
            }
            for arm in ("c32", "rl_step8")
        },
        "root_programs": {
            "episodes": episode_rows,
            "silent_reducer_assignments": len(silent),
            "silent_reducer_coordinates": [
                {k: row[k] for k in ("arm", "context_id", "query_index", "operator", "target")}
                for row in silent
            ],
            "silent_reducers_with_empty_tool_observation": sum(
                row["last_tool_output_kind"] == "empty" for row in silent
            ),
            "runtime_scalar_observed": sum(row["runtime_scalar_observed"] for row in episode_rows),
            "observed_scalar_followed_by_matching_root_answer": sum(
                row["runtime_scalar_observed"] and row["root_equals_generated_scope_value"]
                for row in episode_rows
            ),
            "runtime_scalar_not_observed": sum(
                bool(row["reducer"] and row["reducer"]["supported"] and not row["runtime_scalar_observed"])
                for row in episode_rows
            ),
            "unsupported_or_absent_final_reducer": sum(
                not row["reducer"] or not row["reducer"]["supported"] for row in episode_rows
            ),
        },
        "qs6_training_targets": training_target_audit(),
        "interpretation_limits": [
            "Generated code was parsed as inert AST text and was never executed by this audit.",
            "A blank tool observation proves the computed scalar was not returned through the Python tool channel; it does not prove which latent heuristic produced the subsequent final token.",
            "Helper exact aggregates can arise through cancelling record-label errors and are not evidence of a faithful helper map.",
            "These eight AG contexts are research-exposed and do not establish independent generalization.",
        ],
    }
    # Counter is JSON-compatible but convert explicitly for a stable schema.
    result["root_endpoint"]["c32"] = dict(result["root_endpoint"]["c32"])
    result["root_endpoint"]["rl_step8"] = dict(result["root_endpoint"]["rl_step8"])
    OUT.mkdir(parents=True, exist_ok=True)
    write_json(OUT / "REPORT.json", result)


if __name__ == "__main__":
    main()
