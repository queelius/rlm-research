"""Frozen downstream gate and descriptive label relevance metrics."""


def gate(old, new):
    if {row["cluster"] for row in old} != {0, 1, 2, 3}:
        raise ValueError("exact four old clusters")
    by_key_old = {(row["cluster"], row["size"]): row for row in old}
    by_key_new = {(row["cluster"], row["size"]): row for row in new}
    if by_key_old.keys() != by_key_new.keys() or len(by_key_old) != 8:
        raise ValueError("exact paired eight episodes")
    improvements = 0
    for cluster in range(4):
        old_sum = sum(by_key_old[(cluster, size)]["absolute_error"] for size in (64, 256))
        new_sum = sum(by_key_new[(cluster, size)]["absolute_error"] for size in (64, 256))
        improvements += new_sum < old_sum
    exact_gain = sum(row["strict"] is True for row in new) - sum(
        row["strict"] is True for row in old
    )
    availability = sum(row["final_available"] for row in new) >= sum(
        row["final_available"] for row in old
    )
    result = {"clusters_with_lower_sum_absolute_error": improvements,
              "exact_episode_gain": exact_gain, "no_availability_loss": availability}
    result["pass"] = improvements >= 3 and exact_gain >= 2 and availability
    return result


def task_relevance(predicted, gold, target, target_b):
    relevant = {target, target_b}
    ids = set(gold)
    return {"records": len(ids),
            "true_six_class_correct": sum(predicted.get(key) == gold[key] for key in ids),
            "target_membership_correct": sum((predicted.get(key) in relevant)
                                             == (gold[key] in relevant) for key in ids),
            "target_exact_correct": sum(predicted.get(key) == gold[key]
                                        for key in ids if gold[key] in relevant),
            "target_support": sum(gold[key] in relevant for key in ids)}
