"""Qualified whole-contract scorer rebound to fresh contexts."""

import protocol as p
import study as s


module = s.load("positional_anchor_new_context_scoring", s.PRIOR / "scoring.py", "e7c7c1d38350bb77d0c6afee8e5a9e378be7e824ada4f750f20700aec5301907", {"study": s, "protocol": p})
for name in dir(module):
    if not name.startswith("__"):
        globals()[name] = getattr(module, name)


def summarize(rows):
    cells = {}
    for arm in p.ARMS:
        values = [row for row in rows if row["coordinate"]["arm"] == arm]
        available = [row for row in values if row["score"]["available"]]
        cells[arm] = {"planned": len(values), "available": len(available), "null": len(values) - len(available), "strict_correct": sum(row["score"]["strict_correct"] for row in available), "early_correct": sum(row["score"]["early_correct"] or 0 for row in available), "late_correct": sum(row["score"]["late_correct"] or 0 for row in available), "contract_valid": sum(bool(row["score"]["contract_valid"]) for row in available)}
    context_interactions = {}
    output_only_context = {}
    for context_index in range(16):
        selected = [row for row in rows if row["coordinate"]["context_index"] == context_index and row["score"]["available"]]
        totals = {(row["coordinate"]["relation"], row["coordinate"]["input_row"], row["coordinate"]["output"]): row["score"]["late_correct"] or 0 for row in selected}
        interaction = output_only = 0
        for relation in p.RELATIONS:
            absent = totals.get((relation, "absent", "row_first"), 0) - totals.get((relation, "absent", "labels_only"), 0)
            present = totals.get((relation, "present", "row_first"), 0) - totals.get((relation, "present", "labels_only"), 0)
            interaction += present - absent; output_only += absent
        context_interactions[str(context_index)] = interaction
        output_only_context[str(context_index)] = output_only
    interaction_correct = sum(context_interactions.values())
    relation_present = {relation: cells[f"{relation}_present_row_first"]["late_correct"] - cells[f"{relation}_present_labels_only"]["late_correct"] for relation in p.RELATIONS}
    availability_loss = any(cells[f"{relation}_{input_row}_row_first"]["available"] < cells[f"{relation}_{input_row}_labels_only"]["available"] for relation in p.RELATIONS for input_row in p.INPUT_ROWS)
    positive_contexts = sum(value > 0 for value in context_interactions.values())
    effect = 100 * interaction_correct / (16 * 3 * 32)
    primary = {"late_interaction_correct": interaction_correct, "late_denominator": 16 * 3 * 32, "percentage_point_interaction": effect, "context_interactions": context_interactions, "positive_contexts": positive_contexts, "availability_loss": availability_loss, "promotion_threshold_met": effect >= 10 and positive_contexts >= 12 and not availability_loss, "present_row_first_minus_labels_only_by_relation": relation_present, "practical_general_remedy": all(value > 0 for value in relation_present.values())}
    secondary = {"output_only_late_correct": sum(output_only_context.values()), "late_denominator": 16 * 3 * 32, "context_differences": output_only_context, "positive_contexts": sum(value > 0 for value in output_only_context.values())}
    return {"cells": cells, "primary": primary, "secondary_output_only_original_gate": secondary, "cluster_unit": "16 fresh paired contexts; arms and labels within context are dependent"}
