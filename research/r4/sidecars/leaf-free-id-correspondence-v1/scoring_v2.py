"""Add contract-valid planned-denominator scoring without changing frozen V1 artifacts."""

import study as base

BASE_SCORE = base.score_content
BASE_MISSING = base.score_missing
BASE_SUMMARIZE = base.summarize


def _add_contract(score, gold):
    n = len(gold["records"])
    if not score["observed_policy_output"]:
        score.update(full_contract_valid=None,
                     contract_valid_correct_planned_denominator=None,
                     contract_valid_correct_bounds=[0, n])
        return score
    if gold["arm"] == "plain":
        valid = score["full_shape_valid"] is True
    elif gold["arm"] == "matching":
        valid = (
            score["full_shape_valid"] is True
            and score["field_order_valid"] is True
            and score["emitted_id_position_matches"] == n
            and score["duplicate_emitted_ids"] == []
            and score["missing_input_ids"] == []
            and score["extra_emitted_ids"] == []
        )
    elif gold["arm"] == "constant":
        valid = (
            score["full_shape_valid"] is True
            and score["field_order_valid"] is True
            and score["constant_tag_matches"] == n
        )
    else:
        raise ValueError("unknown output arm")
    correct = score["conditional_correct"] if valid else 0
    score.update(full_contract_valid=valid,
                 contract_valid_correct_planned_denominator=correct,
                 contract_valid_correct_bounds=[correct, correct])
    return score


def score_content(content, gold):
    return _add_contract(BASE_SCORE(content, gold), gold)


def score_missing(gold):
    return _add_contract(BASE_MISSING(gold), gold)


def summarize(design, records):
    analysis = BASE_SUMMARIZE(design, records)
    for coordinate in analysis["coordinates"]:
        row = coordinate["coordinate"]
        gold = design["batches"][row["batch_id"]]["gold"]
        score = coordinate["score"]
        if "full_contract_valid" not in score:
            coordinate["score"] = _add_contract(score, gold)
    for cell in analysis["cells"]:
        selected = [x for x in analysis["coordinates"]
                    if (x["coordinate"]["dataset"], x["coordinate"]["arm"],
                        x["coordinate"]["decoder"]) ==
                    (cell["dataset"], cell["arm"], cell["decoder"])]
        values = [x["score"]["contract_valid_correct_planned_denominator"] for x in selected]
        observed = [value for value in values if value is not None]
        missing = len(values) - len(observed)
        cell.update(
            full_contract_valid=sum(x["score"]["full_contract_valid"] is True for x in selected),
            contract_valid_correct_observed_sum=sum(observed),
            contract_valid_correct_planned_bounds=[sum(observed), sum(observed) + 64 * missing],
        )
    analysis["schema"] = "leaf-free-id-correspondence-analysis-v2"
    analysis["headline_primary"] = (
        "Contract-valid correct labels on the planned denominator: exact expected tags/constants, "
        "ordered fields, full shape and canonical positional labels. Completed invalid outputs score0; "
        "infrastructure missing is NULL with bounds."
    )
    analysis["decomposition_metrics"] = (
        "Full-shape validity and positional label correctness remain separate diagnostics; IDs never "
        "reorder or repair labels."
    )
    return analysis

