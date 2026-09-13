"""Train-only form of the accepted exact/semantic eligible-ID metrics."""

import study as s

with s.aliases({"study": s}, s.SOURCE_EVAL):
    source = s.load("b05_id_rename_source_metrics", s.SOURCE_EVAL / "metrics.py")

grade = source.grade
costs = source.costs


def summarize(output, qualified):
    records = {path.stem: s.read(path) for path in (output / "calls").glob("*.json")}
    expected = {s.call_id(call) for call in s.calls()}
    starts = {path.stem: s.read(path) for path in (output / "starts").glob("*.json")}
    assert set(records) <= expected and set(starts) <= expected
    start_only = set(starts) - set(records)
    for key in start_only:
        records[key] = {**starts[key], "status": "start_only_provider_unknown",
                        "transport_valid": False, "usage": {}}
    rows = [grade(call, records.get(s.call_id(call), {})) for call in s.calls()]
    summary = {}
    for arm in ("base", "cp1"):
        items = [row for row in rows if row["arm"] == arm]
        semantic = [row for row in items if row["semantic_valid"]]
        summary[arm] = dict(planned=18, available=sum(row["available"] for row in items),
            unavailable=sum(not row["available"] for row in items),
            strict_valid=sum(row["strict_valid"] for row in items),
            strict_exact=sum(row["strict_exact"] for row in items), semantic_valid=len(semantic),
            semantic_exact=sum(row["semantic_exact"] for row in items),
            balanced_accuracy_mean=(sum(row["balanced_accuracy"] for row in semantic)/len(semantic)
                                    if semantic else None),
            BA_available_denominator=len(semantic),
            confusion={key: sum(row[key] for row in semantic) for key in ("tp", "fp", "fn", "tn")},
            cost=costs([records.get(row["call_id"], {}) for row in items], 18))
    pairs = []
    for base in [row for row in rows if row["arm"] == "base"]:
        cp1 = next(row for row in rows if row["root_id"] == base["root_id"]
                   and row["repeat"] == base["repeat"] and row["arm"] == "cp1")
        pairs.append(dict(root_id=base["root_id"], repeat=base["repeat"],
            available=base["available"] and cp1["available"], strict_base=base["strict_exact"],
            strict_cp1=cp1["strict_exact"], semantic_base=base["semantic_exact"],
            semantic_cp1=cp1["semantic_exact"], both_semantic_valid=base["semantic_valid"] and cp1["semantic_valid"],
            BA_change=(cp1["balanced_accuracy"]-base["balanced_accuracy"]
                       if base["semantic_valid"] and cp1["semantic_valid"] else None)))
    available = sum(row["available"] for row in rows)
    return dict(schema="b05-id-renaming-fixed-endpoint-native-readout-v1",
        complete=qualified and available == 36 and not start_only, runtime_qualified=qualified,
        planned36=36, available=available, summary=summary,
        paired=dict(contexts=9, planned_pairs=18,
                    available_pairs=sum(row["available"] for row in pairs), pairs=pairs),
        rows=rows, cost=costs(list(records.values()), 36), start_only=sorted(start_only),
        unattempted=sorted(expected-set(records)), primary="strict renamed eligible-ID-set exact",
        semantic_secondary="unordered known unique renamed IDs; BA over present classes",
        unknown_is_not_wrong=True, public_id_mapping_is_bijective=True)

